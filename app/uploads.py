"""Uploading a genome file and annotating it.

The file name is reduced to its last component, so a name such as "../../etc/x" cannot write
outside the upload folder, and its stem becomes the user id that names the result table. Uploading
the same file name again re-annotates it and replaces that user's report once the new run is done.
"""

import os
import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app import pipeline
from app.reports import USER_ID

UPLOAD_DIRECTORY = Path(os.environ.get("BIO_UPLOAD_DIR", "input_data"))
ALLOWED_SUFFIXES = {".vcf", ".txt", ".tsv"}  # VCF, or a tab-separated chip export
MAX_BYTES = 200 * 1024 * 1024

router = APIRouter()


class BodySizeLimit:
    """Refuses a request body over max_bytes with 413 while it arrives.

    Starlette reads a whole multipart upload to a temporary file before the endpoint runs, so the
    limit has to be applied here: by Content-Length up front, and by counting for a chunked body.
    """

    def __init__(self, app: ASGIApp, max_bytes: int = MAX_BYTES) -> None:
        self.app, self.max_bytes = app, max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        length = Headers(scope=scope).get("content-length", "")
        if length.isdigit() and int(length) > self.max_bytes:
            await JSONResponse({"detail": "file too large"}, status_code=413)(scope, receive, send)
            return
        received = 0

        async def counted() -> Message:
            nonlocal received
            message = await receive()
            received += len(message.get("body", b""))
            if received > self.max_bytes:
                raise HTTPException(status_code=413, detail="file too large")
            return message

        await self.app(scope, counted, send)


def save_upload(file: UploadFile) -> tuple[Path, str]:
    name = Path(file.filename or "").name
    stem, suffix = Path(name).stem, Path(name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=400, detail=f"expected one of {sorted(ALLOWED_SUFFIXES)}")
    if not USER_ID.match(stem):
        raise HTTPException(status_code=400, detail="the file name may use only letters, digits and _")
    UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
    target = UPLOAD_DIRECTORY / name
    # written to a temporary file first, so a half-written upload never replaces a good one
    with tempfile.NamedTemporaryFile(dir=UPLOAD_DIRECTORY, delete=False) as tmp:
        try:
            shutil.copyfileobj(file.file, tmp)
        except BaseException:
            Path(tmp.name).unlink(missing_ok=True)
            raise
    Path(tmp.name).replace(target)
    return target, stem


def _annotate(kind: str, file: UploadFile) -> dict:
    path, user = save_upload(file)
    try:
        variants = pipeline.run(kind, path, user)
    except TimeoutError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return {"user": user, "variants": variants}


# annotation runs for minutes and blocks on MySQL, so these are plain functions FastAPI runs in a
# worker thread; the service is an internal tool with a handful of users, so no job queue
@router.post("/uploadfile/")
def upload_vcf(file: UploadFile) -> dict:
    return _annotate("vcf", file)


@router.post("/uploadfile/array/")
def upload_array(file: UploadFile) -> dict:
    return _annotate("array", file)
