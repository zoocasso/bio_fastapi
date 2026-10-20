import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from app import db
from app.reports import POPULATIONS, result_table

USER = "sample01"
FREQUENCY = "{'0': 0.75, '1': 0.25}"

# a small slice of every reference table the reports read
REPORT_TABLES = {
    "medlineplus": [
        {
            "topic_name": "Asthma",
            "title": "summary",
            "content": "Asthma is a chronic disease of the airways.",
            "link_title": None,
            "link": None,
        },
        {
            "topic_name": "Asthma",
            "title": "Diagnosis and Tests",
            "content": None,
            "link_title": "['Spirometry', 'Peak flow']",
            "link": "['https://a.example', 'https://b.example']",
        },
    ],
    "pharmdbk_tkm_relation": [{"kinds": "Asthma", "tkm_name": "Ephedra"}],
    "tkm_ref_tb": [{"tkm_key": "T1", "tkm_eng": "Ephedra"}, {"tkm_key": "T2", "tkm_eng": "Ginseng"}],
    "medicine": [{"TKM_KEY": "T1", "name": "Mahwang-tang"}],
    **{
        f"oasis_{part}": [{"tkm_key": "T1", "note": f"{part} note"}]
        for part in ("clinical", "preclinical", "reference")
    },
    "ncbi_ref": [{"symbol": "ADRB2", "geneid": "154"}],
    "ncbi": [{"geneid": "154", "title": "Summary", "content": "Beta-2 adrenergic receptor."}],
}


def insert(conn, table: str, rows: list[dict]) -> None:
    columns = ", ".join(f"`{c}`" for c in rows[0])
    values = ", ".join(f":p{i}" for i in range(len(rows[0])))
    for row in rows:
        conn.execute(
            text(f"INSERT INTO `{table}` ({columns}) VALUES ({values})"),
            {f"p{i}": v for i, v in enumerate(row.values())},
        )


def create_table(conn, table: str, rows: list[dict]) -> None:
    """A table of TEXT columns, the way pandas.to_sql loads a reference file."""
    conn.exec_driver_sql(f"CREATE TABLE `{table}` ({', '.join(f'`{c}` TEXT' for c in rows[0])})")
    insert(conn, table, rows)


def _seed(conn) -> None:
    for table, rows in REPORT_TABLES.items():
        create_table(conn, table, rows)
    variant = {
        "DISEASE_TRAIT": "Asthma",
        "risk_score": "30%",
        "risk_level": "Slightly Increased",
        "risk_type": "OR",
        "CI": "1.1-1.5",
        "VARIANT AA CHANGE": "p.R16G",
        "GENENAME": "ADRB2",
        "var_type": "missense",
        "EFFECT_ALLELE": "G",
        "ALLELE_1": "A",
        "ALLELE_2": "G",
        "LINK": "https://doi.org/x",
        "AUTHOR": "Kim",
        "JOURNAL": "Nature",
        "STUDY": "GWAS of asthma",
        **{code: FREQUENCY for code, _, _ in POPULATIONS},
    }
    create_table(conn, result_table(USER), [{"SNPS": "rs1", **variant}, {"SNPS": "rs2", **variant}])


@pytest.fixture
def engine(monkeypatch):
    """An in-memory SQLite database holding a small slice of every table the reports read."""
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    with eng.begin() as conn:
        _seed(conn)
    monkeypatch.setattr(db, "get_engine", lambda: eng)
    return eng
