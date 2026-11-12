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
from app.viewer import app as viewer
from tests.conftest import REPORT_TABLES, create_table

URL = os.environ.get("BIO_TEST_MYSQL_URL")
pytestmark = pytest.mark.skipif(not URL, reason="BIO_TEST_MYSQL_URL is not set")

DATA = Path(__file__).parent / "data"
VCF_USER, ARRAY_USER, OTHER_USER = "e2e_vcf", "e2e_array", "e2e_other"


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


# What the samples call, and what each case checks:
# tests/data/sample.vcf
#   1-10177 A/AC    rs367896724  risk allele AC (ALT): OR, BETA and no effect size
#   1-10352 T/TA    rs555500075  risk allele T, the REF: a carrier gets the association
#   1-30000 G/C     rs900002     0/2 with ALT A,C: keyed by the C the person carries
#   1-40000 C/.     rs900003     0/.: copies unknown, not 0
#   2-20000 T/T     rs1          two copies; a UniProt variant the person does not carry
# tests/data/sample_array.txt
#   rs3094315  A/G   chromosome 1: a risk allele that is REF, and dbSNP has two ALTs for it
#   rs900001   --    a no-call
#   rs900005   G/A   dbSNP says C>T: the other strand, so copies are unknown
#   rs900004   C/T   chip chromosome 23, which is X
#   rs11928389 A/A   chromosome MT
ANNOTATION_TABLES = {
    "dbsnp37_chr1": [
        {"connect_key": "1-10177-A-AC", "rsID": "rs367896724", "rsID_ALT": "rs367896724-AC"},
        {"connect_key": "1-10352-T-TA", "rsID": "rs555500075", "rsID_ALT": "rs555500075-TA"},
        {"connect_key": "1-30000-G-A", "rsID": "rs900002", "rsID_ALT": "rs900002-A"},
        {"connect_key": "1-30000-G-C", "rsID": "rs900002", "rsID_ALT": "rs900002-C"},
        {"connect_key": "1-40000-C-T", "rsID": "rs900003", "rsID_ALT": "rs900003-T"},
    ],
    "dbsnp37_chr2": [{"connect_key": "2-20000-G-T", "rsID": "rs1", "rsID_ALT": "rs1-T"}],
    "grch37_dbsnp_chr1": [
        {"rsID": "rs3094315", "rsID_ALT": "rs3094315-G", "connect_key": "1-752566-A-G"},
        {"rsID": "rs3094315", "rsID_ALT": "rs3094315-C", "connect_key": "1-752566-A-C"},
        {"rsID": "rs900001", "rsID_ALT": "rs900001-T", "connect_key": "1-900001-C-T"},
        {"rsID": "rs900005", "rsID_ALT": "rs900005-T", "connect_key": "1-900005-C-T"},
    ],
    "grch37_dbsnp_chrx": [{"rsID": "rs900004", "rsID_ALT": "rs900004-T", "connect_key": "X-900004-C-T"}],
    "grch37_dbsnp_chrmt": [{"rsID": "rs11928389", "rsID_ALT": "rs11928389-A", "connect_key": "MT-3000-G-A"}],
    "gwas_catelog": [
        gwas("rs367896724-AC", "AC", "1.5", "[1.2-1.8]", "Asthma"),
        gwas("rs367896724-AC", "AC", "0.02", "[0.01-0.03] unit increase", "Body mass index"),
        gwas("rs367896724-AC", "AC", "", "", "Eczema"),  # no effect size reported
        gwas("rs555500075-T", "T", "1.4", "[1.1-1.7]", "Asthma"),
        gwas("rs900002-C", "C", "1.2", "[1.0-1.4]", "Asthma"),
        gwas("rs900002-A", "A", "3.0", "[2.0-4.0]", "Asthma"),  # the other ALT, which the person does not carry
        gwas("rs900003-T", "T", "1.5", "[1.2-1.8]", "Asthma"),
        gwas("rs1-T", "T", "0.5", "[0.4-0.6]", "Asthma"),
        gwas("rs1-T", "T", None, None, "Height"),  # an empty cell, loaded as NULL
        gwas("rs3094315-G", "G", "1.3", "[1.1-1.5]", "Asthma"),
        gwas("rs3094315-A", "A", "1.2", "[1.0-1.4]", "Height"),
        gwas("rs900001-T", "T", "1.6", "[1.3-1.9]", "Asthma"),
        gwas("rs900005-T", "T", "1.3", "[1.1-1.5]", "Asthma"),
        gwas("rs900004-T", "T", "1.1", "[1.0-1.2]", "Type 2 diabetes"),
        gwas("rs11928389-A", "A", "2.1", "[1.5-2.9]", "Type 2 diabetes"),
    ],
    "1000genome_chr1": [
        {"connect_key": "1-10177-A-AC", **frequencies(0.25)},
        {"connect_key": "1-752566-A-G", **frequencies(0.6)},
    ],
    "1000genome_chr2": [{"connect_key": "2-20000-G-T", **frequencies(0.1)}],
    "1000genome_chrx": [{"connect_key": "X-900004-C-T", **frequencies(0.3)}],
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
    suffixes = [c.lower() for c in pipeline.CHROMOSOMES]
    empty = [
        (f"{family}{c}", f"{family}{next(x for x in suffixes if f'{family}{x}' in tables)}")
        for family in PER_CHROMOSOME
        for c in suffixes
        if f"{family}{c}" not in tables
    ]
    created = [*tables, *(name for name, _ in empty)]
    results = [reports.result_table(u) for u in (VCF_USER, ARRAY_USER, OTHER_USER)]

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
            "SELECT SNPS, DISEASE_TRAIT, `OR`, risk_type, copies, risk_score, risk_level, JPT, GENENAME "
            f"FROM `{reports.result_table(user)}` ORDER BY SNPS, DISEASE_TRAIT"
        ).mappings()
        return [dict(r) for r in rows]


def assert_no_stage_tables(engine) -> None:
    left = set(inspect(engine).get_table_names())
    for p in pipeline.PIPELINES.values():
        assert not left & set(pipeline.staging_tables(p))


def by_association(rows: list[dict]) -> dict:
    return {(r["SNPS"], r["DISEASE_TRAIT"]): r for r in rows}


def test_vcf_end_to_end(mysql):
    assert pipeline.run("vcf", DATA / "sample.vcf", VCF_USER) == 5
    stored = result_rows(mysql, VCF_USER)
    rows = by_association(stored)
    assert len(stored) == len(rows)  # one row per association
    assert {k: (r["risk_type"], r["copies"], r["risk_score"], r["risk_level"]) for k, r in rows.items()} == {
        ("rs367896724", "Asthma"): ("OR", 1, 50, "Moderate increase"),
        ("rs367896724", "Body mass index"): ("BETA", 1, None, None),  # a BETA gets no score
        ("rs367896724", "Eczema"): ("", 1, None, None),  # no effect size reported
        ("rs555500075", "Asthma"): ("OR", 1, 40, "Moderate increase"),  # the risk allele is the REF
        ("rs900002", "Asthma"): ("OR", 1, 20, "Little change"),  # not the A association
        ("rs900003", "Asthma"): ("OR", None, None, None),  # 0/.: unknown copies
        ("rs1", "Asthma"): ("OR", 2, -100, "Decrease"),
        ("rs1", "Height"): ("", 2, None, None),  # NULL and '' both mean no effect size
    }
    assert rows[("rs1", "Asthma")]["JPT"] == "{'0': 0.9, '1': 0.1}"  # from 1000genome_chr2
    assert rows[("rs555500075", "Asthma")]["JPT"] is None  # no 1000 Genomes record
    assert rows[("rs367896724", "Asthma")]["GENENAME"] == "DDX11L1"
    assert rows[("rs1", "Asthma")]["GENENAME"] is None  # its UniProt variant needs a C, but the row stays
    assert_no_stage_tables(mysql)


def test_a_chr_prefixed_vcf_gives_the_same_result(mysql, tmp_path):
    lines = (DATA / "sample.vcf").read_text().splitlines(keepends=True)
    prefixed = tmp_path / "prefixed.vcf"
    prefixed.write_text("".join(x if x.startswith("#") else "chr" + x for x in lines))
    pipeline.run("vcf", DATA / "sample.vcf", VCF_USER)
    pipeline.run("vcf", prefixed, OTHER_USER)
    assert result_rows(mysql, OTHER_USER) == result_rows(mysql, VCF_USER)


def test_a_file_with_nothing_in_dbsnp_is_refused(mysql, tmp_path):
    other_build = tmp_path / "other_build.vcf"
    header = "".join(x for x in (DATA / "sample.vcf").read_text().splitlines(keepends=True) if x.startswith("#"))
    other_build.write_text(header + "1\t999\t.\tA\tG\t50\tPASS\t.\tGT:DP\t0/1:10\n")
    with pytest.raises(pipeline.NotInDbsnp, match="none of the 1 variants"):
        pipeline.run("vcf", other_build, OTHER_USER)
    assert not inspect(mysql).has_table(reports.result_table(OTHER_USER))
    assert_no_stage_tables(mysql)


def test_array_end_to_end(mysql):
    assert pipeline.run("array", DATA / "sample_array.txt", ARRAY_USER) == 7
    stored = result_rows(mysql, ARRAY_USER)
    rows = by_association(stored)
    assert len(stored) == len(rows)  # rs3094315 joins two dbSNP rows, but its associations appear once
    assert {k: (r["copies"], r["risk_score"], r["risk_level"]) for k, r in rows.items()} == {
        ("rs3094315", "Asthma"): (1, 30, "Moderate increase"),
        ("rs3094315", "Height"): (1, 20, "Little change"),  # the risk allele is the REF
        ("rs900001", "Asthma"): (None, None, None),  # a no-call is unknown, not 0 copies
        ("rs900005", "Asthma"): (None, None, None),  # the other strand
        ("rs900004", "Type 2 diabetes"): (1, 10, "Little change"),
        ("rs11928389", "Type 2 diabetes"): (2, 220, "Large increase"),
    }
    assert rows[("rs900004", "Type 2 diabetes")]["JPT"] == "{'0': 0.7, '1': 0.3}"  # chip 23: 1000genome_chrx
    assert rows[("rs11928389", "Type 2 diabetes")]["JPT"] == "{'0': 0.5, '1': 0.5}"  # from 1000genome_chrmt
    assert rows[("rs3094315", "Asthma")]["GENENAME"] == "ADRB2"
    assert_no_stage_tables(mysql)


def test_reports_read_a_fresh_vcf_result(mysql):
    pipeline.run("vcf", DATA / "sample.vcf", VCF_USER)
    client = TestClient(api)
    overview = client.get("/overview_page", params={"bio_input": "Asthma", "user": VCF_USER})
    assert overview.status_code == 200
    data = overview.json()
    assert data["snps_cnt"] == 5 and data["summary"].startswith("Asthma is")
    assert {r["SNPS"]: (r["OR"], r["copies"], r["risk_level"]) for r in data["snps_riskscore_1kgp"]} == {
        "rs1": ("0.5", 2, "Decrease"),
        "rs367896724": ("1.5", 1, "Moderate increase"),
        "rs555500075": ("1.4", 1, "Moderate increase"),
        "rs900002": ("1.2", 1, "Little change"),
        "rs900003": ("1.5", None, None),
    }
    igsr = {f["key"]: f["value"] for f in client.get("/igsr", params={"snps": "rs1", "user": VCF_USER}).json()["igsr"]}
    assert igsr["JPT"] == 10
    no_data = client.get("/igsr", params={"snps": "rs555500075", "user": VCF_USER}).json()["igsr"]
    assert {f["value"] for f in no_data} == {None}
    assert client.get("/disease_trait", params={"user": "nobody"}).status_code == 404
    page = TestClient(viewer).get("/overview_page", params={"bio_input": "Asthma", "user": VCF_USER})
    assert page.status_code == 200 and "Research use only, not a diagnosis." in page.text


def test_rerun_replaces_the_result_and_a_failed_run_keeps_it(mysql):
    pipeline.run("vcf", DATA / "sample.vcf", VCF_USER)
    pipeline.run("vcf", DATA / "sample.vcf", VCF_USER)  # the same file name again overwrites
    assert len(result_rows(mysql, VCF_USER)) == 8

    with mysql.begin() as conn:
        conn.exec_driver_sql("RENAME TABLE `uniprot` TO `uniprot_away`")
    try:
        with pytest.raises(Exception, match="uniprot"):
            pipeline.run("vcf", DATA / "sample.vcf", VCF_USER)
    finally:
        with mysql.begin() as conn:
            conn.exec_driver_sql("RENAME TABLE `uniprot_away` TO `uniprot`")
    assert len(result_rows(mysql, VCF_USER)) == 8  # the last good result is still there
    assert_no_stage_tables(mysql)
