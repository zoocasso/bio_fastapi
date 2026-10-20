"""JSON API, read by the report frontend.

    uvicorn app.main:app

The same reports as HTML pages are served by app.viewer. There is no login: the service is for
an internal network only, and browsers may read it only from the origins in BIO_CORS_ORIGINS.
"""

import os
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app import db, reports, uploads


def cors_origins(value: str | None) -> list[str]:
    """The frontend's origins, comma-separated, e.g. "http://reports.internal:3000"; none by default."""
    return [origin.strip() for origin in (value or "").split(",") if origin.strip()]


app = FastAPI(title="Genomic variant reports")
app.add_middleware(uploads.BodySizeLimit)

# the frontend is served from another origin; any other site open in a browser on the internal
# network must not be able to read genomic reports through it
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(os.environ.get("BIO_CORS_ORIGINS")),
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(uploads.router)


ReportUser = Annotated[str, Depends(reports.require_report)]


@app.exception_handler(reports.NoReport)
async def no_report(request: Request, exc: reports.NoReport) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(reports.UnknownUser)
async def unknown_user(request: Request, exc: reports.UnknownUser) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/disease_trait")
def disease_trait(user: ReportUser) -> dict:
    return {"user": user, "disease_trait": reports.disease_traits(user)}


@app.get("/overview_page")
def overview_page(bio_input: str, user: ReportUser) -> dict:
    return reports.overview(bio_input, user)


@app.get("/scientific_detail_page")
def scientific_detail_page(bio_input: str, user: ReportUser) -> dict:
    return reports.scientific_detail(bio_input, user)


@app.get("/igsr")
def igsr(snps: str, user: ReportUser) -> dict:
    return {"igsr": reports.population_frequencies(snps, user)}


@app.get("/oasis")
def oasis(tkm_key: str) -> dict:
    return {f"oasis_{part}": rows for part, rows in reports.oasis(tkm_key).items()}


@app.get("/ncbi")
def ncbi(genename: str) -> dict:
    gene = reports.gene_summary(genename)
    if gene is None:
        raise HTTPException(status_code=404, detail=f"unknown gene: {genename}")
    return {"ncbi_gene": gene}


@app.get("/healthz")
def healthz() -> dict:
    with db.get_engine().connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok"}
