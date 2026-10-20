"""Report queries over a user's annotated variants and the reference tables.

Every value from a request is passed to the database as a bound parameter. The one name that
cannot be a parameter, the user's result table, is built only from a validated user id.
"""

import ast
import json
import math
import re
from typing import Any

from sqlalchemy import bindparam, inspect, text

from app import db

Row = dict[str, Any]

# the pipeline's stage tables all start with "vcf" or "connect_", so no user id can name one of
# them; MySQL table names are at most 64 characters
RESULT_PREFIX = "result_"
USER_ID = re.compile(rf"^[A-Za-z0-9_]{{1,{64 - len(RESULT_PREFIX)}}}$")

# 1000 Genomes populations, in the column order of the result table
POPULATIONS = [
    ("ACB", "AFR", "African Caribbean"),
    ("ASW", "AFR", "African Ancestry SW"),
    ("BEB", "SAS", "Bengali"),
    ("CDX", "EAS", "Dai Chinese"),
    ("CEU", "EUR", "CEPH"),
    ("CHB", "EAS", "Han Chinese"),
    ("CHS", "EAS", "Southern Han Chinese"),
    ("CLM", "AMR", "Colombian"),
    ("ESN", "AFR", "Esan"),
    ("FIN", "EUR", "Finnish"),
    ("GBR", "EUR", "British"),
    ("GIH", "SAS", "Gujarati"),
    ("GWD", "AFR", "Gambian Mandinka"),
    ("IBS", "EUR", "Iberian"),
    ("ITU", "SAS", "Telugu"),
    ("JPT", "EAS", "Japanese"),
    ("KHV", "EAS", "Kinh Vietnamese"),
    ("LWK", "AFR", "Luhya"),
    ("MSL", "AFR", "Mende"),
    ("MXL", "AMR", "Mexican Ancestry"),
    ("PEL", "AMR", "Peruvian"),
    ("PJL", "SAS", "Punjabi"),
    ("PUR", "AMR", "Puerto Rican"),
    ("STU", "SAS", "Tamil"),
    ("TSI", "EUR", "Toscani"),
    ("YRI", "AFR", "Yoruba"),
]
POPULATION_COLUMNS = ",".join(code for code, _, _ in POPULATIONS)


class UnknownUser(ValueError):
    """The user id cannot name a result table."""


class NoReport(LookupError):
    """The user has no result table yet."""


def result_table(user: str) -> str:
    if not USER_ID.match(user):
        raise UnknownUser(f"invalid user id: {user!r}")
    return RESULT_PREFIX + user


def users() -> list[str]:
    """Everyone with a result table, for the viewer's list."""
    names = inspect(db.get_engine()).get_table_names()
    return sorted(n[len(RESULT_PREFIX) :] for n in names if n.startswith(RESULT_PREFIX))


def require_report(user: str) -> str:
    if not inspect(db.get_engine()).has_table(result_table(user)):
        raise NoReport(f"no report for {user}")
    return user


def _rows(sql: str, **params: Any) -> list[Row]:
    with db.get_engine().connect() as conn:
        return [dict(r) for r in conn.execute(text(sql), params).mappings()]


def _in_rows(sql: str, name: str, values: list[Any]) -> list[Row]:
    stmt = text(sql).bindparams(bindparam(name, expanding=True))
    with db.get_engine().connect() as conn:
        return [dict(r) for r in conn.execute(stmt, {name: values}).mappings()]


def disease_traits(user: str) -> list[Row]:
    return _rows(f"SELECT DISTINCT DISEASE_TRAIT FROM `{result_table(user)}`")


def summary(topic: str) -> str:
    rows = _rows(
        "SELECT content FROM medlineplus WHERE topic_name = :topic AND title = 'summary'",
        topic=topic,
    )
    return rows[0]["content"] if rows else ""


def risk_scores(trait: str, user: str) -> list[Row]:
    return _rows(
        "SELECT DISEASE_TRAIT, SNPS, risk_score, risk_level, risk_type, CI, "
        f"{POPULATION_COLUMNS} FROM `{result_table(user)}` WHERE DISEASE_TRAIT = :trait",
        trait=trait,
    )


def snp_count(trait: str, user: str) -> int:
    rows = _rows(
        f"SELECT COUNT(DISTINCT SNPS) AS n FROM `{result_table(user)}` WHERE DISEASE_TRAIT = :trait",
        trait=trait,
    )
    return int(rows[0]["n"])


def medlineplus_links(topic: str) -> list[Row]:
    rows = _rows(
        "SELECT title, link_title, link FROM medlineplus WHERE topic_name = :topic "
        "AND title IN ('Diagnosis and Tests', 'Treatments and Therapies')",
        topic=topic,
    )
    # link titles and links are stored as Python list literals, one pair per link
    return [
        {"title": r["title"], "link_title": t, "link": link}
        for r in rows
        for t, link in zip(ast.literal_eval(r["link_title"]), ast.literal_eval(r["link"]), strict=True)
    ]


def herbal_medicines(trait: str) -> list[Row]:
    """Traditional Korean medicines (PharmDB-K) related to a trait."""
    names = [
        r["tkm_name"] for r in _rows("SELECT tkm_name FROM pharmdbk_tkm_relation WHERE kinds = :trait", trait=trait)
    ]
    if not names:
        return []
    return _in_rows("SELECT * FROM tkm_ref_tb WHERE tkm_eng IN :names", "names", names)


def drugs(medicines: list[Row]) -> list[Row]:
    keys = [m["tkm_key"] for m in medicines]
    if not keys:
        return []
    return _in_rows("SELECT * FROM medicine WHERE TKM_KEY IN :keys", "keys", keys)


def variant_details(trait: str, user: str) -> list[Row]:
    return _rows(
        "SELECT DISEASE_TRAIT, SNPS, `VARIANT AA CHANGE`, GENENAME, var_type, EFFECT_ALLELE, ALLELE_1, ALLELE_2 "
        f"FROM `{result_table(user)}` WHERE DISEASE_TRAIT = :trait",
        trait=trait,
    )


def references(trait: str, user: str) -> list[Row]:
    return _rows(
        f"SELECT DISTINCT LINK, AUTHOR, JOURNAL, STUDY FROM `{result_table(user)}` WHERE DISEASE_TRAIT = :trait",
        trait=trait,
    )


def oasis(tkm_key: str) -> dict[str, list[Row]]:
    """Clinical, preclinical and reference records for a medicine (OASIS)."""
    return {
        part: _rows(f"SELECT * FROM oasis_{part} WHERE tkm_key = :key", key=tkm_key)
        for part in ("clinical", "preclinical", "reference")
    }


def _alt_frequency(value: Any) -> int:
    """Percent of the alternative allele, from a stored frequency map such as "{'0': 0.8, '1': 0.2}"."""
    if not isinstance(value, str):
        return 0
    try:
        return math.floor(json.loads(value.replace("'", '"'))["1"] * 100)
    except (ValueError, KeyError, TypeError):
        return 0


def population_frequencies(snp: str, user: str) -> list[Row]:
    rows = _rows(f"SELECT {POPULATION_COLUMNS} FROM `{result_table(user)}` WHERE SNPS = :snp", snp=snp)
    if not rows:
        return []
    return [
        {"key": code, "value": _alt_frequency(rows[0][code]), "superpopulation": sp, "pop_name": name}
        for code, sp, name in POPULATIONS
    ]


def gene_summary(symbol: str) -> str | None:
    rows = _rows(
        "SELECT n.content FROM ncbi_ref AS r JOIN ncbi AS n ON n.geneid = r.geneid "
        "WHERE r.symbol = :symbol AND n.title = 'Summary'",
        symbol=symbol,
    )
    return rows[0]["content"] if rows else None


def overview(trait: str, user: str) -> dict[str, Any]:
    medicines = herbal_medicines(trait)
    return {
        "bio_input": trait,
        "user": user,
        "summary": summary(trait),
        "snps_cnt": snp_count(trait, user),
        "snps_riskscore_1kgp": risk_scores(trait, user),
        "medlineplus": medlineplus_links(trait),
        "tkm": medicines,
        "medicine": drugs(medicines),
    }


def scientific_detail(trait: str, user: str) -> dict[str, Any]:
    return {
        "bio_input": trait,
        "user": user,
        "summary": summary(trait),
        "scientific_detail": variant_details(trait, user),
        "reference": references(trait, user),
    }
