import get_bio_everything
# import vcf_annotation.annotation

import os
import uvicorn
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path


## fastapi 인스턴스 저장
app = FastAPI()

## static 폴더 mounting작업
app.mount("/static",StaticFiles(directory=Path(__file__).parent.parent.absolute() / "static"),name="static")

## 템플릿 구성을 위해 Jinja2 활용
templates = Jinja2Templates(directory="templates")

@app.post('/uploadfile/')
async def uploadfile(request: Request, file: UploadFile):
    UPLOAD_DIRECTORY = "./input_data"
    contents = await file.read()
    with open(os.path.join(UPLOAD_DIRECTORY, file.filename), "wb") as f:
        f.write(contents)
    vcf_annotation.annotation.vcf_annotation("./input_data/"+file.filename)
    return "uploaded vcf file"

# 메인페이지
@app.get("/")
async def root(request:Request):
    return templates.TemplateResponse("index.html", {"request":request})

@app.get("/disease_trait")
# @app.get("/")
async def root(request:Request):
    disease_trait = get_bio_everything.get_disease_trait()
    return templates.TemplateResponse("disease_trait.html", {"request":request, "disease_trait":disease_trait})

@app.get("/overview_page")
async def overview_page(request:Request, bio_input:str):
    summary = get_bio_everything.get_summary(bio_input)
    snps_riskscore_1kgp = get_bio_everything.get_snps_riskscore_1kgp(bio_input)
    snps_cnt = get_bio_everything.get_count_snps(bio_input)
    medlineplus = get_bio_everything.get_medlineplus(bio_input)
    tkm = get_bio_everything.get_tkm(bio_input)
    medicine = get_bio_everything.get_medicine(tkm)
    return templates.TemplateResponse("overview_page.html", {"request":request, "bio_input":bio_input, "summary":summary, "snps_cnt":snps_cnt, "snps_riskscore_1kgp":snps_riskscore_1kgp, "medlineplus":medlineplus, "tkm":tkm, "medicine":medicine})

@app.get("/scientific_detail_page")
async def scientific_detail_page(request:Request, bio_input:str):
    summary = get_bio_everything.get_summary(bio_input)
    scientific_detail = get_bio_everything.get_scientific_detail(bio_input)
    reference = get_bio_everything.get_reference(bio_input)
    return templates.TemplateResponse("scientific_detail_page.html", {"request":request, "bio_input":bio_input, "summary":summary, "scientific_detail":scientific_detail,"reference":reference})

@app.get("/oasis")
async def oasis(request:Request, tkm_key:str):
    oasis_clinical, oasis_preclinical, oasis_reference = get_bio_everything.get_oasis(tkm_key)
    return templates.TemplateResponse("oasis.html", {"request":request, "oasis_clinical":oasis_clinical, "oasis_preclinical":oasis_preclinical, "oasis_reference":oasis_reference})

uvicorn.run(app, host = '0.0.0.0', port = 8000)