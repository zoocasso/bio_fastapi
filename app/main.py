import get_bio_everything
from vcf_annotation import vcf_annotation
from array_annotation import array_annotation

import os
import uvicorn
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

## fastapi 인스턴스 저장
app = FastAPI()

## static 폴더 mounting작업
app.mount("/static",StaticFiles(directory=Path(__file__).absolute().parent.parent.absolute() / "static"),name="static")

## 템플릿 구성을 위해 Jinja2 활용
templates = Jinja2Templates(directory="templates")

@app.post('/uploadfile/')
async def uploadfile(request: Request, file: UploadFile):
    UPLOAD_DIRECTORY = "./input_data"
    contents = await file.read()
    with open(os.path.join(UPLOAD_DIRECTORY, file.filename), "wb") as f:
        f.write(contents)
    vcf_annotation.vcf_annotation("./input_data/"+file.filename)
    return "uploaded vcf file"

@app.post('/uploadfile/array/')
async def uploadfile(request: Request, file: UploadFile):
    UPLOAD_DIRECTORY = "./input_data"
    contents = await file.read()
    with open(os.path.join(UPLOAD_DIRECTORY, file.filename), "wb") as f:
        f.write(contents)
    array_annotation.array_annotation("./input_data/"+file.filename)
    return "uploaded array file"

# 메인페이지
@app.get("/")
async def root(request:Request):
    return templates.TemplateResponse("index.html", {"request":request})

@app.get("/disease_trait")
# @app.get("/")
async def root(request:Request, user:str):
    disease_trait = get_bio_everything.get_disease_trait(user)
    return templates.TemplateResponse("disease_trait.html", {"request":request, "disease_trait":disease_trait, "user":user})

@app.get("/overview_page")
async def overview_page(request:Request, bio_input:str, user:str):
    summary = get_bio_everything.get_summary(bio_input)
    snps_riskscore_1kgp = get_bio_everything.get_snps_riskscore_1kgp(bio_input,user)
    snps_cnt = get_bio_everything.get_count_snps(bio_input,user)[0]['count(distinct SNPS)']
    medlineplus = get_bio_everything.get_medlineplus(bio_input)
    tkm = get_bio_everything.get_tkm(bio_input)
    medicine = get_bio_everything.get_medicine(tkm)
    return templates.TemplateResponse("overview_page.html", {"request":request, "bio_input":bio_input, "summary":summary, "snps_cnt":snps_cnt, "snps_riskscore_1kgp":snps_riskscore_1kgp, "medlineplus":medlineplus, "tkm":tkm, "medicine":medicine, "user":user})

@app.get("/scientific_detail_page")
async def scientific_detail_page(request:Request, bio_input:str, user:str):
    summary = get_bio_everything.get_summary(bio_input)
    scientific_detail = get_bio_everything.get_scientific_detail(bio_input,user)
    reference = get_bio_everything.get_reference(bio_input,user)
    return templates.TemplateResponse("scientific_detail_page.html", {"request":request, "bio_input":bio_input, "summary":summary, "scientific_detail":scientific_detail,"reference":reference, "user":user})

@app.get("/igsr")
async def igsr(request:Request, snps:str, user:str):
    igsr = get_bio_everything.get_igsr(snps,user)
    return templates.TemplateResponse("igsr.html", {"request":request, "igsr":igsr})

@app.get("/oasis")
async def oasis(request:Request, tkm_key:str):
    oasis_clinical, oasis_preclinical, oasis_reference = get_bio_everything.get_oasis(tkm_key)
    return templates.TemplateResponse("oasis.html", {"request":request, "oasis_clinical":oasis_clinical, "oasis_preclinical":oasis_preclinical, "oasis_reference":oasis_reference})


@app.get("/ncbi")
async def igsr(request:Request, genename:str):
    try:
        ncbi_gene = get_bio_everything.get_ncbi(genename)
        return templates.TemplateResponse("ncbi.html", {"request":request, "ncbi_gene":ncbi_gene})
    except:
        return f'genename is not exist'

if __name__ == "__main__":
    uvicorn.run(app, host = '127.0.0.1', port = 8000)