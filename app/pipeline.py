"""The annotation pipeline: a person's variants joined to about 1 TB of public references.

    input  ->  dbSNP (rsID)  ->  GWAS Catalog (risk)  ->  1000 Genomes (population frequency)  ->  UniProt

Each stage is a SQL file in app/sql/<kind>/ that builds the next table from the previous one. dbSNP
and 1000 Genomes are split into one table per chromosome, so a statement that names ``{chrom}`` (the
chromosome as app/inputs.py writes it, such as "X") or ``{suffix}`` (its table suffix, "x") is run
once for each of CHROMOSOMES: the run for the first creates the table, the others insert into it.
The stage tables are shared, so runs are serialized with a MySQL named lock, cleared before and after
each run, and the final table is renamed to the user's result table.
"""

import logging
import re
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sqlalchemy import BigInteger, String, Text
from sqlalchemy.engine import Connection
from sqlalchemy.types import TypeEngine

from app import db
from app.inputs import read_array, read_vcf
from app.reports import result_table

log = logging.getLogger(__name__)

SQL_DIR = Path(__file__).parent / "sql"
LOCK_NAME = "bio_annotation"
LOCK_TIMEOUT_S = 3600
CHROMOSOMES = (*(str(n) for n in range(1, 23)), "X", "Y", "MT")
# MySQL indexes a TEXT column only on a prefix (error 1170), and a long VARCHAR would pass the
# 3072-byte key limit, so string columns longer than this are indexed on their first characters
INDEX_PREFIX = 255
# a user's earlier result, renamed out of the way while the new one takes its name
PREVIOUS_RESULT = "connect_previous_result"


@dataclass(frozen=True)
class Stage:
    name: str
    table: str  # the table the stage's SQL creates
    index: str | None  # the column the next stage joins on


@dataclass(frozen=True)
class Pipeline:
    kind: str
    read: Callable[[Path], pd.DataFrame]
    input_table: str
    input_columns: dict[str, TypeEngine]  # the column types of the input table
    input_index: str
    stages: tuple[Stage, ...]

    def sql_path(self, stage: Stage) -> Path:
        return SQL_DIR / self.kind / f"{stage.name}.sql"

    @property
    def final_table(self) -> str:
        return self.stages[-1].table


# keys and short fields are VARCHAR; alleles stay TEXT, since an indel allele can be thousands of
# bases long, and so does connect_key, which contains them
VCF = Pipeline(
    kind="vcf",
    read=read_vcf,
    input_table="vcf",
    input_columns={
        "chrom": String(64),
        "pos": BigInteger(),
        "id": Text(),
        "ref": Text(),
        "alt": Text(),
        "qual": String(32),
        "filter": String(255),
        "info": Text(),
        "format": String(255),
        "sample_data": Text(),
        "allele_1": Text(),
        "allele_2": Text(),
        "connect_key": Text(),
    },
    input_index="connect_key",
    stages=(
        Stage("dbsnp", "connect_vcf_dbsnp", "rsID"),
        Stage("gwas", "connect_vcf_dbsnp_gwas", "connect_key"),
        Stage("1kgp", "connect_vcf_dbsnp_gwas_1kgp", "SNPS"),
        Stage("uniprot", "connect_vcf_dbsnp_gwas_1kgp_uniprot", None),
    ),
)

ARRAY = Pipeline(
    kind="array",
    read=read_array,
    input_table="vcf_array",
    input_columns={
        "CHR": String(64),
        "POS": BigInteger(),
        "rsID": String(255),
        "allele_1": String(1),
        "allele_2": String(1),
    },
    input_index="rsID",
    stages=(
        Stage("dbsnp", "connect_vcf_dbsnp_array", "rsID"),
        Stage("gwas", "connect_vcf_dbsnp_gwas_array", "connect_key"),
        Stage("1kgp", "connect_vcf_dbsnp_gwas_1kgp_array", "SNPS"),
        Stage("uniprot", "connect_vcf_dbsnp_gwas_1kgp_uniprot_array", None),
    ),
)

PIPELINES = {p.kind: p for p in (VCF, ARRAY)}

_CREATE = re.compile(r"\bcreate\s+table\s+`?([A-Za-z0-9_]+)`?", re.IGNORECASE)


def split_statements(sql: str) -> list[str]:
    """The statements of a stage file, which end with a semicolon at the end of a line."""
    return [s.strip() for s in re.split(r";\s*(?:\n|$)", sql) if s.strip()]


def _per_chromosome(statement: str) -> list[str]:
    create = _CREATE.search(statement)
    if create is None:
        raise ValueError(f"a statement run per chromosome must create its table: {statement[:80]!r}")
    insert = f"{statement[: create.start()]}insert into `{create.group(1)}`{statement[create.end() :]}"
    first, *rest = CHROMOSOMES
    return [_render(statement, first), *(_render(insert, c) for c in rest)]


def _render(statement: str, chrom: str) -> str:
    return statement.replace("{chrom}", chrom).replace("{suffix}", chrom.lower())


def stage_statements(pipeline: Pipeline, stage: Stage) -> list[str]:
    """The statements of a stage in the order they run, with the per-chromosome ones expanded."""
    statements = []
    for statement in split_statements(pipeline.sql_path(stage).read_text(encoding="utf-8")):
        per_chromosome = "{chrom}" in statement or "{suffix}" in statement
        statements += _per_chromosome(statement) if per_chromosome else [statement]
    return statements


def staging_tables(pipeline: Pipeline) -> list[str]:
    """Every table a run creates, including the temporary ones inside the stage files."""
    tables = [pipeline.input_table]
    for stage in pipeline.stages:
        for name in _CREATE.findall(pipeline.sql_path(stage).read_text(encoding="utf-8")):
            if name not in tables:
                tables.append(name)
    return [*tables, PREVIOUS_RESULT]


@contextmanager
def _named_lock(conn: Connection) -> Iterator[None]:
    got = conn.exec_driver_sql("SELECT GET_LOCK(%s, %s)", (LOCK_NAME, LOCK_TIMEOUT_S)).scalar()
    if got != 1:
        raise TimeoutError("another annotation is still running")
    try:
        yield
    finally:
        conn.exec_driver_sql("SELECT RELEASE_LOCK(%s)", (LOCK_NAME,))


def _drop(conn: Connection, tables: list[str]) -> None:
    for t in tables:
        conn.exec_driver_sql(f"DROP TABLE IF EXISTS `{t}`")


def _execute(conn: Connection, statement: str) -> None:
    """Sends a stage statement as written.

    It goes to the DBAPI cursor with no arguments. PyMySQL applies %-formatting whenever arguments
    are passed, and SQLAlchemy always passes some (an empty dict), which breaks the stage SQL's
    LIKE '%increase' and REPLACE(risk_score, "%", "").
    """
    with conn.connection.cursor() as cursor:
        cursor.execute(statement)


def _count(conn: Connection, table: str) -> int:
    return conn.exec_driver_sql(f"SELECT COUNT(*) FROM `{table}`").scalar()


def _add_index(conn: Connection, table: str, column: str) -> None:
    """Indexes a join column. The stage tables take their column types from the reference
    tables, so the column's length is looked up rather than assumed."""
    length = conn.exec_driver_sql(
        "SELECT CHARACTER_MAXIMUM_LENGTH FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s",
        (table, column),
    ).scalar()
    key = f"`{column}`({INDEX_PREFIX})" if length is not None and length > INDEX_PREFIX else f"`{column}`"
    conn.exec_driver_sql(f"ALTER TABLE `{table}` ADD INDEX `{column}` ({key})")


def _publish(conn: Connection, final: str, target: str) -> None:
    """Gives the final table the user's result name. An earlier result is swapped out in the same
    RENAME TABLE, which MySQL runs atomically, so a reader finds the old report or the new one."""
    exists = conn.exec_driver_sql(
        "SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s",
        (target,),
    ).scalar()
    if exists:
        conn.exec_driver_sql(f"RENAME TABLE `{target}` TO `{PREVIOUS_RESULT}`, `{final}` TO `{target}`")
        conn.exec_driver_sql(f"DROP TABLE `{PREVIOUS_RESULT}`")
    else:
        conn.exec_driver_sql(f"RENAME TABLE `{final}` TO `{target}`")


class NotInDbsnp(ValueError):
    """None of the uploaded variants is in dbSNP, usually another genome build or naming."""


def run(kind: str, path: Path, user: str) -> int:
    """Annotates one uploaded file and stores the result as the user's result table.

    A user's earlier result is replaced only once the new run has finished. Returns the number of
    input variants. MySQL commits DDL statements implicitly, so the stage tables are dropped in a
    finally block rather than rolled back.
    """
    pipeline = PIPELINES[kind]
    target = result_table(user)
    variants = pipeline.read(path)
    if variants.empty:
        raise ValueError(f"{path.name} has no usable genotypes")

    engine = db.get_engine()
    staging = staging_tables(pipeline)
    started = time.perf_counter()
    with engine.connect() as conn, _named_lock(conn):
        _drop(conn, staging)
        try:
            variants.to_sql(
                pipeline.input_table,
                conn,
                if_exists="replace",
                index=False,
                chunksize=10_000,
                dtype=pipeline.input_columns,
            )
            _add_index(conn, pipeline.input_table, pipeline.input_index)
            for stage in pipeline.stages:
                t0 = time.perf_counter()
                for statement in stage_statements(pipeline, stage):
                    _execute(conn, statement)
                if stage is pipeline.stages[0] and not _count(conn, stage.table):
                    raise NotInDbsnp(
                        f"none of the {len(variants)} variants in {path.name} is in dbSNP (GRCh37): "
                        "check the genome build and the chromosome names"
                    )
                if stage.index:
                    _add_index(conn, stage.table, stage.index)
                log.info("%s %s: %.1f s", kind, stage.name, time.perf_counter() - t0)
            _publish(conn, pipeline.final_table, target)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            _drop(conn, staging)
            conn.commit()
    log.info("%s for %s: %d variants in %.1f s", kind, user, len(variants), time.perf_counter() - started)
    return len(variants)
