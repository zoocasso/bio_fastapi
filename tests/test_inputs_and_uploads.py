import io
from pathlib import Path

import pytest
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.testclient import TestClient

from app import pipeline, uploads
from app.inputs import normalize_chrom, read_array, read_vcf
from app.main import app as api
from app.viewer import app as viewer

DATA = Path(__file__).parent / "data"


def test_read_vcf_keeps_called_genotypes():
    df = read_vcf(DATA / "sample.vcf")
    rows = {r["connect_key"]: r for r in df.to_dict("records")}
    assert len(df) == 5  # the ./. record has no called genotype
    first = rows["1-10177-A-AC"]
    assert (first["allele_1"], first["allele_2"]) == ("A", "AC")
    assert first["filter"] == "PASS" and first["sample_data"] == "0/1;12"
    assert (rows["2-20000-G-T"]["allele_1"], rows["2-20000-G-T"]["allele_2"]) == ("T", "T")
    assert rows["2-20000-G-T"]["filter"] == "q10"


def test_a_vcf_variant_is_keyed_by_the_alt_the_person_carries():
    rows = {r["pos"]: r for r in read_vcf(DATA / "sample.vcf").to_dict("records")}
    assert rows[30000]["connect_key"] == "1-30000-G-C"  # 0/2 with ALT A,C: the C, not ALT[0]
    assert rows[30000]["filter"] == "."  # filters not applied is not PASS
    # 0/. keeps ALT[0]; the GWAS stage finds its copies unknown
    assert (rows[40000]["connect_key"], rows[40000]["allele_2"]) == ("1-40000-C-T", ".")


@pytest.mark.parametrize(
    ("name", "chrom"),
    [
        ("1", "1"),
        ("chr1", "1"),
        ("CHR22", "22"),
        ("x", "X"),
        ("chrX", "X"),
        ("chrM", "MT"),
        ("M", "MT"),
        ("MT", "MT"),
        ("23", "X"),
        ("24", "Y"),
        ("25", "X"),
        ("XY", "X"),
        ("26", "MT"),
        (" chrY ", "Y"),
    ],
)
def test_chromosome_names_are_normalized(name, chrom):
    assert normalize_chrom(name) == chrom


def test_a_chr_prefixed_vcf_reads_like_a_plain_one(tmp_path):
    lines = (DATA / "sample.vcf").read_text().splitlines(keepends=True)
    prefixed = tmp_path / "prefixed.vcf"
    prefixed.write_text("".join(x if x.startswith("#") else "chr" + x for x in lines))
    assert read_vcf(prefixed).equals(read_vcf(DATA / "sample.vcf"))


def test_read_array_skips_comments_and_splits_genotypes():
    df = read_array(DATA / "sample_array.txt")
    assert list(df["rsID"]) == ["rs4477212", "rs3094315", "rs3131972", "rs900001", "rs900005", "rs900004", "rs11928389"]
    assert list(zip(df["allele_1"], df["allele_2"], strict=True)) == [
        ("A", "A"),
        ("A", "G"),
        ("-", "-"),
        ("-", "-"),
        ("G", "A"),
        ("C", "T"),
        ("A", "A"),
    ]
    assert list(df["CHR"]) == ["1", "1", "1", "1", "1", "X", "MT"]  # chip code 23 is X


def test_chip_genotypes_are_upper_cased(tmp_path):
    export = tmp_path / "lower.txt"
    export.write_text("rs1\tchrx\t5\tag\n")
    assert read_array(export).to_dict("records") == [
        {"CHR": "X", "POS": 5, "rsID": "rs1", "allele_1": "A", "allele_2": "G"}
    ]


def upload(name: str, body: bytes = b"x") -> UploadFile:
    return UploadFile(file=io.BytesIO(body), filename=name, size=len(body))


@pytest.mark.parametrize("name", ["../../etc/passwd.vcf", "/tmp/evil.vcf", "sub/dir/user01.vcf"])
def test_upload_stays_in_the_upload_folder(tmp_path, monkeypatch, name):
    monkeypatch.setattr(uploads, "UPLOAD_DIRECTORY", tmp_path)
    path, user = uploads.save_upload(upload(name, b"##fileformat=VCFv4.1\n"))
    assert path.parent == tmp_path and path.read_bytes() == b"##fileformat=VCFv4.1\n"
    assert user == Path(name).stem


@pytest.mark.parametrize(("name", "status"), [("notes.pdf", 400), ("bad name.vcf", 400), ("x;y.vcf", 400)])
def test_bad_uploads_are_rejected(tmp_path, monkeypatch, name, status):
    monkeypatch.setattr(uploads, "UPLOAD_DIRECTORY", tmp_path)
    with pytest.raises(HTTPException) as e:
        uploads.save_upload(upload(name))
    assert e.value.status_code == status
    assert list(tmp_path.iterdir()) == []


def limited_app(max_bytes: int) -> TestClient:
    app = FastAPI()
    app.add_middleware(uploads.BodySizeLimit, max_bytes=max_bytes)

    @app.post("/upload")
    def upload(file: UploadFile) -> dict:
        return {"size": len(file.file.read())}

    return TestClient(app)


def test_a_body_over_the_limit_is_refused_by_its_length():
    client = limited_app(max_bytes=1000)
    assert client.post("/upload", files={"file": ("a.vcf", b"x" * 100)}).json() == {"size": 100}
    r = client.post("/upload", files={"file": ("a.vcf", b"x" * 2000)})
    assert r.status_code == 413 and r.json() == {"detail": "file too large"}


def test_a_chunked_body_is_refused_once_it_passes_the_limit():
    client = limited_app(max_bytes=1000)
    boundary = "b0undary"
    body = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="a.vcf"\r\n\r\n'.encode()
        + b"x" * 5000
        + f"\r\n--{boundary}--\r\n".encode()
    )
    chunks = (body[i : i + 512] for i in range(0, len(body), 512))  # no Content-Length
    r = client.post("/upload", content=chunks, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    assert r.status_code == 413


def test_both_apps_limit_uploads():
    for app in (api, viewer):
        assert any(m.cls is uploads.BodySizeLimit for m in app.user_middleware)


def test_an_upload_none_of_whose_variants_is_in_dbsnp_is_a_422(tmp_path, monkeypatch):
    monkeypatch.setattr(uploads, "UPLOAD_DIRECTORY", tmp_path)

    def run(kind, path, user):
        raise pipeline.NotInDbsnp("none of the 2 variants in x.vcf is in dbSNP (GRCh37)")

    monkeypatch.setattr(pipeline, "run", run)
    r = TestClient(api).post("/uploadfile/", files={"file": ("x.vcf", b"##fileformat=VCFv4.1\n")})
    assert r.status_code == 422 and "dbSNP" in r.json()["detail"]
