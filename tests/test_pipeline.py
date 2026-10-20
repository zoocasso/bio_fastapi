"""The pipeline's order of work, checked against a connection that records its statements.

The stage SQL goes through PyMySQL's own cursor, with only the network round trip replaced, so
what PyMySQL would do to it is checked here. tests/test_mysql_pipeline.py runs it on MySQL.
"""

from pathlib import Path

import pandas as pd
import pymysql
import pytest

from app import db, pipeline, reports

DATA = Path(__file__).parent / "data"


class Result:
    def __init__(self, value):
        self.value = value

    def scalar(self):
        return self.value


class RecordingCursor(pymysql.cursors.Cursor):
    """PyMySQL's cursor: execute() decides whether to %-format the query, _query() would send it."""

    def _query(self, q):
        recorder = self.connection.recorder
        recorder.statements.append(q)
        recorder.sent.append(q)
        if recorder.fail_on and recorder.fail_on in q:
            raise pymysql.err.ProgrammingError(1146, "stage failed")
        return 0


class RecordingConnection:
    def __init__(self, fail_on=None, column_length=None, result_exists=False):
        self.statements, self.sent, self.events = [], [], []
        self.fail_on, self.column_length, self.result_exists = fail_on, column_length, result_exists
        # a real PyMySQL connection object that never connects; its cursors record their queries
        self.connection = pymysql.connections.Connection(defer_connect=True, cursorclass=RecordingCursor)
        self.connection.recorder = self

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def exec_driver_sql(self, sql, params=None):
        self.statements.append(sql)
        if self.fail_on and self.fail_on in sql:
            raise RuntimeError("stage failed")
        if "information_schema.COLUMNS" in sql:
            return Result(self.column_length)
        if "information_schema.TABLES" in sql:
            return Result(int(self.result_exists))
        return Result(1)

    def commit(self):
        self.events.append("commit")

    def rollback(self):
        self.events.append("rollback")


@pytest.fixture
def conn(monkeypatch):
    def make(**kw):
        c = RecordingConnection(**kw)
        monkeypatch.setattr(db, "get_engine", lambda: type("E", (), {"connect": lambda self: c})())

        def to_sql(df, name, con, **options):
            c.statements.append(f"LOAD {name}")
            c.events.append(("dtype", name, options["dtype"]))

        monkeypatch.setattr(pd.DataFrame, "to_sql", to_sql)
        return c

    return make


def test_split_statements_skips_blank_tails():
    assert pipeline.split_statements("create table a\nselect 1\n;\n\ninsert into a select 2\n;\n") == [
        "create table a\nselect 1",
        "insert into a select 2",
    ]


def test_staging_tables_include_the_temporary_ones():
    tables = pipeline.staging_tables(pipeline.VCF)
    assert tables[0] == "vcf"
    assert {"connect_vcf_dbsnp_gwas_temp", "connect_vcf_dbsnp_gwas_temp2"} <= set(tables)
    assert tables[-2:] == ["connect_vcf_dbsnp_gwas_1kgp_uniprot", pipeline.PREVIOUS_RESULT]


@pytest.mark.parametrize("p", pipeline.PIPELINES.values(), ids=pipeline.PIPELINES)
def test_per_chromosome_statements_join_their_own_chromosome(p):
    statements = pipeline.stage_statements(p, p.stages[2])  # 1000 Genomes
    assert len(statements) == len(pipeline.CHROMOSOMES) == 25
    assert f"create table {p.stages[2].table}" in statements[0].lower()
    for chrom, statement in zip(pipeline.CHROMOSOMES, statements, strict=True):
        assert f"= '{chrom}'" in statement and f"`1000genome_chr{chrom}`" in statement
        assert "{chrom}" not in statement
    assert all(f"insert into `{p.stages[2].table}`" in s for s in statements[1:])
    dbsnp = pipeline.stage_statements(p, p.stages[0])
    assert [s.split("_chr")[1].split()[0] for s in dbsnp] == list(pipeline.CHROMOSOMES)


def test_stage_sql_reaches_pymysql_unformatted(conn):
    c = conn()
    pipeline.run("vcf", DATA / "sample.vcf", "sample01")
    pipeline.run("array", DATA / "sample_array.txt", "sample02")
    expected = [
        s for p in (pipeline.VCF, pipeline.ARRAY) for stage in p.stages for s in pipeline.stage_statements(p, stage)
    ]
    assert c.sent == expected  # every statement, exactly as written
    with_percent = [s for s in expected if "%" in s]
    assert len(with_percent) >= 4  # LIKE '%increase', REPLACE(risk_score, "%", "")
    # what SQLAlchemy's exec_driver_sql did before: it passes {} and PyMySQL then %-formats
    cursor = c.connection.cursor()
    for statement in with_percent:
        with pytest.raises((TypeError, ValueError, pymysql.err.ProgrammingError)):
            cursor.mogrify(statement, {})


def test_a_run_is_locked_cleaned_and_renamed(conn):
    c = conn()
    assert pipeline.run("vcf", DATA / "sample.vcf", "sample01") == 2
    s = c.statements
    assert s[0].startswith("SELECT GET_LOCK") and s[-1].startswith("SELECT RELEASE_LOCK")
    load = s.index("LOAD vcf")
    assert all(x.startswith("DROP TABLE IF EXISTS") for x in s[1:load])  # stale stage tables first
    stages = [i for i, x in enumerate(s) if x.lower().startswith("create table")]
    assert stages == sorted(stages) and stages[0] > load
    rename = next(i for i, x in enumerate(s) if x.startswith("RENAME TABLE"))
    assert s[rename] == "RENAME TABLE `connect_vcf_dbsnp_gwas_1kgp_uniprot` TO `result_sample01`"
    assert any(x.startswith("DROP TABLE IF EXISTS `vcf`") for x in s[rename:])  # and cleaned after
    assert "rollback" not in c.events


def test_an_earlier_result_is_swapped_out_in_one_rename(conn):
    c = conn(result_exists=True)
    pipeline.run("vcf", DATA / "sample.vcf", "sample01")
    swap = (
        "RENAME TABLE `result_sample01` TO `connect_previous_result`, "
        "`connect_vcf_dbsnp_gwas_1kgp_uniprot` TO `result_sample01`"
    )
    assert swap in c.statements
    assert c.statements[c.statements.index(swap) + 1] == "DROP TABLE `connect_previous_result`"
    assert not any("result_sample01" in x for x in c.statements if x.startswith("DROP"))  # never missing


def test_a_failed_stage_rolls_back_and_still_cleans_up(conn):
    c = conn(fail_on="gwas_catelog")
    with pytest.raises(pymysql.err.ProgrammingError):
        pipeline.run("vcf", DATA / "sample.vcf", "sample01")
    assert "rollback" in c.events
    assert not any(x.startswith("RENAME TABLE") for x in c.statements)
    assert c.statements[-2].startswith("DROP TABLE IF EXISTS") and c.statements[-1].startswith("SELECT RELEASE_LOCK")


def test_an_empty_input_is_refused_before_touching_the_database(conn, tmp_path):
    c = conn()
    empty = tmp_path / "empty.txt"
    empty.write_text("# no genotypes\n")
    with pytest.raises(ValueError):
        pipeline.run("array", empty, "empty")
    assert c.statements == []


@pytest.mark.parametrize(("p", "path"), [(pipeline.VCF, "sample.vcf"), (pipeline.ARRAY, "sample_array.txt")])
def test_every_input_column_gets_a_declared_type(conn, p, path):
    c = conn()
    columns = list(p.read(DATA / path).columns)
    pipeline.run(p.kind, DATA / path, "sample01")
    assert ("dtype", p.input_table, p.input_columns) in c.events
    assert list(p.input_columns) == columns  # nothing left for pandas to make TEXT on its own


@pytest.mark.parametrize(
    ("length", "key"), [(65535, "`connect_key`(255)"), (1000, "`connect_key`(255)"), (64, "`connect_key`")]
)
def test_long_string_columns_are_indexed_on_a_prefix(conn, length, key):
    c = conn(column_length=length)
    pipeline.run("vcf", DATA / "sample.vcf", "sample01")
    assert f"ALTER TABLE `vcf` ADD INDEX `connect_key` ({key})" in c.statements


@pytest.mark.parametrize("p", pipeline.PIPELINES.values(), ids=pipeline.PIPELINES)
def test_no_user_id_can_name_a_stage_table(p):
    staging = pipeline.staging_tables(p)
    assert not [t for t in staging if t.startswith(reports.RESULT_PREFIX)]
    # the ids that used to collide: "temp" named a stage table, "array" the array pipeline's final table
    assert reports.result_table("temp") not in staging and reports.result_table("array") not in staging
