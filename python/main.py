import get_bio_everything

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path


## fastapi 인스턴스 저장
app = FastAPI()

## static 폴더 mounting작업
app.mount("/static",StaticFiles(directory=Path(__file__).parent.parent.absolute() / "static"),name="static",)

## 템플릿 구성을 위해 Jinja2 활용
templates = Jinja2Templates(directory="templates")

## 메인페이지
@app.get("/")
async def root(request:Request):
    return templates.TemplateResponse("index.html", {"request":request})

@app.get("/overview_page")
async def root(request:Request, bio_input:str):
    summary = get_bio_everything.get_summary(bio_input)
    snps_riskscore_1kgp = get_bio_everything.get_snps_riskscore_1kgp(bio_input)
    snps_cnt = get_bio_everything.get_count_snps(bio_input)
    medlineplus = get_bio_everything.get_medlineplus(bio_input)
    tkm = get_bio_everything.get_tkm(bio_input)
    medicine = get_bio_everything.get_medicine(tkm)
    return templates.TemplateResponse("overview_page.html", {"request":request, "bio_input":bio_input, "summary":summary, "snps_cnt":snps_cnt, "snps_riskscore_1kgp":snps_riskscore_1kgp, "medlineplus":medlineplus, "tkm":tkm, "medicine":medicine})

@app.get("/scientific_detail_page")
async def root(request:Request, bio_input:str):
    summary = get_bio_everything.get_summary(bio_input)
    scientific_detail = get_bio_everything.get_scientific_detail(bio_input)
    return templates.TemplateResponse("scientific_detail_page.html", {"request":request, "bio_input":bio_input, "summary":summary, "scientific_detail":scientific_detail})


uvicorn.run(app, host = '127.0.0.1', port = 8000)