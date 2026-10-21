import pytest
from fastapi.testclient import TestClient

from app import reports
from app.main import app as api
from app.main import cors_origins
from app.viewer import app as viewer
from tests.conftest import USER


def test_overview_combines_every_source(engine):
    data = reports.overview("Asthma", USER)
    assert data["summary"].startswith("Asthma is")
    assert data["snps_cnt"] == 2
    assert {r["SNPS"] for r in data["snps_riskscore_1kgp"]} == {"rs1", "rs2"}
    assert [link["link_title"] for link in data["medlineplus"]] == ["Spirometry", "Peak flow"]
    assert [m["tkm_eng"] for m in data["tkm"]] == ["Ephedra"]
    assert [d["name"] for d in data["medicine"]] == ["Mahwang-tang"]


def test_population_frequencies_are_labelled(engine):
    freqs = {f["key"]: f for f in reports.population_frequencies("rs1", USER)}
    assert len(freqs) == 26
    assert freqs["STU"]["pop_name"] == "Tamil" and freqs["TSI"]["pop_name"] == "Toscani"
    assert freqs["JPT"]["value"] == 25


def test_risk_rows_carry_the_effect_size_and_copies(engine):
    [row, _] = reports.risk_scores("Asthma", USER)
    assert (row["OR"], row["copies"], row["risk_score"], row["risk_level"]) == ("1.3", "1", "30", "Moderate increase")


def test_a_variant_without_1000_genomes_data_has_no_frequency(engine):
    with engine.begin() as conn:
        conn.exec_driver_sql(f"UPDATE `{reports.result_table(USER)}` SET JPT = NULL WHERE SNPS = 'rs1'")
    freqs = {f["key"]: f["value"] for f in reports.population_frequencies("rs1", USER)}
    assert freqs["JPT"] is None and freqs["CEU"] == 25  # "no data", not 0%


def test_request_values_are_never_part_of_the_sql(engine):
    # a quote in the trait would have ended the string in the old f-string query
    assert reports.risk_scores('Asthma" OR "1"="1', USER) == []


@pytest.mark.parametrize("user", ["x; DROP TABLE medicine", "../x", "", "a" * 58, "alice\n"])
def test_invalid_user_ids_cannot_name_a_table(user):
    with pytest.raises(reports.UnknownUser):
        reports.result_table(user)


def test_result_table_names_fit_mysql():
    assert len(reports.result_table("a" * 57)) == 64  # MySQL's limit for a table name


def test_users_lists_result_tables(engine):
    assert reports.users() == [USER]


def test_no_herbal_medicine_means_no_drugs(engine):
    assert reports.herbal_medicines("Unknown trait") == []
    assert reports.drugs([]) == []


# ---------- the two apps ----------


def test_api_returns_the_overview(engine):
    r = TestClient(api).get("/overview_page", params={"bio_input": "Asthma", "user": USER})
    assert r.status_code == 200
    assert r.json()["snps_cnt"] == 2


def test_api_status_codes(engine):
    client = TestClient(api)
    assert client.get("/disease_trait", params={"user": "nobody"}).status_code == 404
    assert client.get("/disease_trait", params={"user": "bad id"}).status_code == 400
    assert client.get("/ncbi", params={"genename": "NOPE"}).status_code == 404
    assert client.get("/ncbi", params={"genename": "ADRB2"}).json() == {"ncbi_gene": "Beta-2 adrenergic receptor."}
    assert client.get("/healthz").json() == {"status": "ok"}


def test_viewer_renders_the_pages(engine):
    client = TestClient(viewer)
    index = client.get("/")
    assert index.status_code == 200 and f'value="{USER}"' in index.text
    for path, params in [
        ("/disease_trait", {"user": USER}),
        ("/overview_page", {"bio_input": "Asthma", "user": USER}),
        ("/scientific_detail_page", {"bio_input": "Asthma", "user": USER}),
        ("/igsr", {"snps": "rs1", "user": USER}),
        ("/oasis", {"tkm_key": "T1"}),
        ("/ncbi", {"genename": "ADRB2"}),
    ]:
        r = client.get(path, params=params)
        assert r.status_code == 200, path


def test_cors_origins_come_from_a_comma_separated_list():
    assert cors_origins(None) == [] and cors_origins("") == []
    assert cors_origins(" http://a.internal:3000 , ,http://b.internal ") == [
        "http://a.internal:3000",
        "http://b.internal",
    ]


def test_no_browser_origin_may_read_the_api_by_default(engine):
    r = TestClient(api).get("/healthz", headers={"Origin": "http://elsewhere.example"})
    assert r.status_code == 200
    assert "access-control-allow-origin" not in r.headers
