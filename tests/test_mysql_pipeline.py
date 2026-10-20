"""The whole pipeline on a real MySQL 8, with a few rows of every reference table it joins.

Runs when BIO_TEST_MYSQL_URL points at a scratch database whose name ends in "test" (the CI job
starts one, see .github/workflows/ci.yml). The reference tables are created as TEXT columns, the way
pandas.to_sql loads them, and every table the tests create is dropped afterwards.
"""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, make_url

from app import db, pipeline, reports
from app.main import app as api
from tests.conftest import REPORT_TABLES, create_table

URL = os.environ.get("BIO_TEST_MYSQL_URL")
pytestmark = pytest.mark.skipif(not URL, reason="BIO_TEST_MYSQL_URL is not set")

DATA = Path(__file__).parent / "data"
VCF_USER, ARRAY_USER = "e2e_vcf", "e2e_array"


def frequencies(alt: float) -> dict:
    """The 1000 Genomes columns, stored as allele frequency maps such as "{'0': 0.75, '1': 0.25}"."""
    return {code: str({"0": round(1 - alt, 2), "1": alt}) for code, _, _ in reports.POPULATIONS}


def gwas(snp: str, effect_allele: str, odds: str | None, ci: str | None, trait: str) -> dict:
    rs = snp.split("-")[0]
    return {
        "STRONGEST_SNP": snp,
        "SNPS": rs,
        "EFFECT_ALLELE": effect_allele,
        "OR": odds,
        "CI": ci,
        "DISEASE_TRAIT": trait,
        "var_type": "intron_variant",
        "LINK": f"https://www.ebi.ac.uk/gwas/variants/{rs}",
        "AUTHOR": "Kim",
        "JOURNAL": "Nature",
        "STUDY": f"GWAS of {trait.lower()}",
    }


def uniprot(rs: str, gene: str, change: str, ref: str, alt: str) -> dict:
    return {
        "SOURCE DB ID": rs,
        "GENENAME": gene,
        "VARIANT AA CHANGE": change,
        "CONSEQUENCE TYPE": "missense",
        "UNIPROT_REF": ref,
        "UNIPROT_ALT": alt,
    }


# tests/data/sample.vcf calls 1-10177-A-AC (A/AC) and 2-20000-G-T (T/T);
# tests/data/sample_array.txt calls rs3094315 (A/G, chromosome 1) and rs11928389 (A/A, chromosome MT)
ANNOTATION_TABLES = {
    "dbsnp37_chr1": [
        {"connect_key": "1-10177-A-AC", "rsID": "rs367896724", "rsID_ALT": "rs367896724-AC"},
        {"connect_key": "1-10352-T-TA", "rsID": "rs555500075", "rsID_ALT": "rs555500075-TA"},
    ],
    "dbsnp37_chr2": [{"connect_key": "2-20000-G-T", "rsID": "rs1", "rsID_ALT": "rs1-T"}],
    "grch37_dbsnp_chr1": [{"rsID": "rs3094315", "rsID_ALT": "rs3094315-G", "connect_key": "1-752566-A-G"}],
    "grch37_dbsnp_chrmt": [{"rsID": "rs11928389", "rsID_ALT": "rs11928389-A", "connect_key": "MT-3000-G-A"}],
    "gwas_catelog": [
        gwas("rs367896724-AC", "AC", "1.5", "[1.2-1.8]", "Asthma"),
        gwas("rs367896724-AC", "AC", "0.02", "[0.01-0.03] unit increase", "Body mass index"),
        gwas("rs367896724-AC", "AC", "", "", "Eczema"),  # no effect size reported
        gwas("rs1-T", "T", "0.5", "[0.4-0.6]", "Asthma"),
        gwas("rs1-T", "T", None, None, "Height"),  # an empty cell, loaded as NULL
        gwas("rs3094315-G", "G", "1.3", "[1.1-1.5]", "Asthma"),
        gwas("rs11928389-A", "A", "2.1", "[1.5-2.9]", "Type 2 diabetes"),
    ],
    "1000genome_chr1": [
        {"connect_key": "1-10177-A-AC", **frequencies(0.25)},
        {"connect_key": "1-752566-A-G", **frequencies(0.6)},
    ],
    "1000genome_chr2": [{"connect_key": "2-20000-G-T", **frequencies(0.1)}],
    "1000genome_chrmt": [{"connect_key": "MT-3000-G-A", **frequencies(0.5)}],
    "uniprot": [
        uniprot("rs367896724", "DDX11L1", "p.Lys5Asn", "A", "AC"),
        uniprot("rs3094315", "ADRB2", "p.Arg16Gly", "A", "G"),
        uniprot("rs1", "TP53", "p.Gly12Val", "G", "C"),  # an allele the sample (T/T) does not carry
    ],
}
# the per-chromosome tables without seeded rows exist too, empty, as in a full load
PER_CHROMOSOME = ("dbsnp37_chr", "grch37_dbsnp_chr", "1000genome_chr")


@pytest.fixture
def mysql(monkeypatch):
    url = make_url(URL)
    if not (url.database or "").endswith("test"):
        pytest.fail(f"BIO_TEST_MYSQL_URL must name a scratch database ending in 'test', not {url.database!r}")
    engine = create_engine(url)
    tables = {**REPORT_TABLES, **ANNOTATION_TABLES}
    empty = [
        (f"{family}{c}", f"{family}{next(x for x in pipeline.CHROMOSOMES if f'{family}{x}' in tables)}")
        for family in PER_CHROMOSOME
        for c in pipeline.CHROMOSOMES
        if f"{family}{c}" not in tables
    ]
    created = [*tables, *(name for name, _ in empty)]
    results = [reports.result_table(u) for u in (VCF_USER, ARRAY_USER)]

    def drop_all():
        with engine.begin() as conn:
            for t in [*created, *results]:
                conn.exec_driver_sql(f"DROP TABLE IF EXISTS `{t}`")

    drop_all()
    with engine.begin() as conn:
        for table, rows in tables.items():
            create_table(conn, table, rows)
        for name, like in empty:
            conn.exec_driver_sql(f"CREATE TABLE `{name}` LIKE `{like}`")
    monkeypatch.setattr(db, "get_engine", lambda: engine)
    yield engine
    drop_all()
    engine.dispose()


def result_rows(engine, user: str) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.exec_driver_sql(
            "SELECT SNPS, DISEASE_TRAIT, risk_type, risk_score, risk_level, JPT, GENENAME, ALLELE_1, ALLELE_2 "
            f"FROM `{reports.result_table(user)}` ORDER BY SNPS, DISEASE_TRAIT"
        ).mappings()
        return [dict(r) for r in rows]


def assert_no_stage_tables(engine) -> None:
    left = set(inspect(engine).get_table_names())
    for p in pipeline.PIPELINES.values():
        assert not left & set(pipeline.staging_tables(p))


def test_vcf_end_to_end(mysql):
    assert pipeline.run("vcf", DATA / "sample.vcf", VCF_USER) == 2
    assert result_rows(mysql, VCF_USER) == [
        {
            "SNPS": "rs1",
            "DISEASE_TRAIT": "Asthma",
            "risk_type": "OR",
            "risk_score": "-100%",
            "risk_level": "Significantly Decreased",
            "JPT": "{'0': 0.9, '1': 0.1}",  # from 1000genome_chr2
            "GENENAME": None,  # its UniProt variant needs a C, so none is joined, but the row stays
            "ALLELE_1": "T",
            "ALLELE_2": "T",
        },
        {
            "SNPS": "rs1",
            "DISEASE_TRAIT": "Height",
            "risk_type": "OR",
            "risk_score": None,
            "risk_level": None,
            "JPT": "{'0': 0.9, '1': 0.1}",
            "GENENAME": None,
            "ALLELE_1": "T",
            "ALLELE_2": "T",
        },
        {
            "SNPS": "rs367896724",
            "DISEASE_TRAIT": "Asthma",
            "risk_type": "OR",
            "risk_score": "50%",
            "risk_level": "Slightly Increased",
            "JPT": "{'0': 0.75, '1': 0.25}",
            "GENENAME": "DDX11L1",
            "ALLELE_1": "A",
            "ALLELE_2": "AC",
        },
        {
            "SNPS": "rs367896724",
            "DISEASE_TRAIT": "Body mass index",
            "risk_type": "BETA",
            "risk_score": "2%",
            "risk_level": None,  # levels are for odds ratios only
            "JPT": "{'0': 0.75, '1': 0.25}",
            "GENENAME": "DDX11L1",
            "ALLELE_1": "A",
            "ALLELE_2": "AC",
        },
        {
            "SNPS": "rs367896724",
            "DISEASE_TRAIT": "Eczema",
            "risk_type": "",
            "risk_score": "",
            "risk_level": None,
            "JPT": "{'0': 0.75, '1': 0.25}",
            "GENENAME": "DDX11L1",
            "ALLELE_1": "A",
            "ALLELE_2": "AC",
        },
    ]
    assert_no_stage_tables(mysql)


def test_array_end_to_end(mysql):
    assert pipeline.run("array", DATA / "sample_array.txt", ARRAY_USER) == 4
    rows = {r["SNPS"]: r for r in result_rows(mysql, ARRAY_USER)}
    assert rows.keys() == {"rs3094315", "rs11928389"}
    assert (rows["rs3094315"]["risk_score"], rows["rs3094315"]["risk_level"]) == ("30%", "Slightly Increased")
    assert rows["rs3094315"]["GENENAME"] == "ADRB2"
    assert (rows["rs11928389"]["risk_score"], rows["rs11928389"]["risk_level"]) == ("220%", "Significantly Increased")
    assert rows["rs11928389"]["JPT"] == "{'0': 0.5, '1': 0.5}"  # from 1000genome_chrmt
    assert_no_stage_tables(mysql)


def test_reports_read_a_fresh_vcf_result(mysql):
    pipeline.run("vcf", DATA / "sample.vcf", VCF_USER)
    client = TestClient(api)
    overview = client.get("/overview_page", params={"bio_input": "Asthma", "user": VCF_USER})
    assert overview.status_code == 200
    data = overview.json()
    assert data["snps_cnt"] == 2 and data["summary"].startswith("Asthma is")
    assert {r["SNPS"]: r["risk_level"] for r in data["snps_riskscore_1kgp"]} == {
        "rs1": "Significantly Decreased",
        "rs367896724": "Slightly Increased",
    }
    igsr = {f["key"]: f["value"] for f in client.get("/igsr", params={"snps": "rs1", "user": VCF_USER}).json()["igsr"]}
    assert igsr["JPT"] == 10
    assert client.get("/disease_trait", params={"user": "nobody"}).status_code == 404


def test_rerun_replaces_the_result_and_a_failed_run_keeps_it(mysql):
    pipeline.run("vcf", DATA / "sample.vcf", VCF_USER)
    pipeline.run("vcf", DATA / "sample.vcf", VCF_USER)  # the same file name again overwrites
    assert len(result_rows(mysql, VCF_USER)) == 5

    with mysql.begin() as conn:
        conn.exec_driver_sql("RENAME TABLE `uniprot` TO `uniprot_away`")
    try:
        with pytest.raises(Exception, match="uniprot"):
            pipeline.run("vcf", DATA / "sample.vcf", VCF_USER)
    finally:
        with mysql.begin() as conn:
            conn.exec_driver_sql("RENAME TABLE `uniprot_away` TO `uniprot`")
    assert len(result_rows(mysql, VCF_USER)) == 5  # the last good result is still there
    assert_no_stage_tables(mysql)
