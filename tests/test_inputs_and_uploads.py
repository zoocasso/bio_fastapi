import io
from pathlib import Path

import pytest
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.testclient import TestClient

from app import uploads
from app.inputs import read_array, read_vcf
from app.main import app as api
from app.viewer import app as viewer

DATA = Path(__file__).parent / "data"


def test_read_vcf_keeps_called_genotypes():
    df = read_vcf(DATA / "sample.vcf")
    assert len(df) == 2  # the ./. record has no called genotype
    first, second = df.to_dict("records")
    assert (first["allele_1"], first["allele_2"]) == ("A", "AC")
    assert first["connect_key"] == "1-10177-A-AC"
    assert first["filter"] == "PASS" and first["sample_data"] == "0/1;12"
    assert (second["allele_1"], second["allele_2"]) == ("T", "T")
    assert second["filter"] == "q10"


def test_read_array_skips_comments_and_splits_genotypes():
    df = read_array(DATA / "sample_array.txt")
    assert list(df["rsID"]) == ["rs4477212", "rs3094315", "rs3131972", "rs11928389"]
    assert list(zip(df["allele_1"], df["allele_2"], strict=True)) == [("A", "A"), ("A", "G"), ("-", "-"), ("A", "A")]


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
