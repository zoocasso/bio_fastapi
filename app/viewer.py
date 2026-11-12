"""HTML viewer for the same reports: upload a file, then browse traits, variants and populations.

uvicorn app.viewer:app
"""

from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import reports, uploads

ROOT = Path(__file__).resolve().parent.parent

app = FastAPI(title="Genomic variant reports (viewer)", docs_url=None, redoc_url=None)
app.add_middleware(uploads.BodySizeLimit)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
app.include_router(uploads.router)
templates = Jinja2Templates(directory=ROOT / "templates")


def page(request: Request, name: str, context: dict) -> HTMLResponse:
    # tojson in the templates needs plain values (MySQL returns Decimal for DECIMAL columns)
    return templates.TemplateResponse(request, name, jsonable_encoder(context))


ReportUser = Annotated[str, Depends(reports.require_report)]


@app.exception_handler(reports.NoReport)
async def no_report(request: Request, exc: reports.NoReport) -> HTMLResponse:
    return HTMLResponse(str(exc), status_code=404)


@app.exception_handler(reports.UnknownUser)
async def unknown_user(request: Request, exc: reports.UnknownUser) -> HTMLResponse:
    return HTMLResponse(str(exc), status_code=400)


@app.get("/")
def index(request: Request) -> HTMLResponse:
    return page(request, "index.html", {"users": reports.users()})


@app.get("/disease_trait")
def disease_trait(request: Request, user: ReportUser) -> HTMLResponse:
    return page(request, "disease_trait.html", {"user": user, "disease_trait": reports.disease_traits(user)})


@app.get("/overview_page")
def overview_page(request: Request, bio_input: str, user: ReportUser) -> HTMLResponse:
    return page(request, "overview_page.html", reports.overview(bio_input, user))


@app.get("/scientific_detail_page")
def scientific_detail_page(request: Request, bio_input: str, user: ReportUser) -> HTMLResponse:
    return page(request, "scientific_detail_page.html", reports.scientific_detail(bio_input, user))


@app.get("/igsr")
def igsr(request: Request, snps: str, user: ReportUser) -> HTMLResponse:
    return page(request, "igsr.html", {"igsr": reports.population_frequencies(snps, user)})


@app.get("/oasis")
def oasis(request: Request, tkm_key: str) -> HTMLResponse:
    parts = reports.oasis(tkm_key)
    return page(request, "oasis.html", {f"oasis_{part}": rows for part, rows in parts.items()})


@app.get("/ncbi")
def ncbi(request: Request, genename: str) -> HTMLResponse:
    gene = reports.gene_summary(genename)
    if gene is None:
        raise HTTPException(status_code=404, detail=f"unknown gene: {genename}")
    return page(request, "ncbi.html", {"ncbi_gene": gene})
