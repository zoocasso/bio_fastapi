# Genomic variant annotation and risk reports

[![tests](https://github.com/zoocasso/bio_fastapi/actions/workflows/ci.yml/badge.svg)](https://github.com/zoocasso/bio_fastapi/actions/workflows/ci.yml)

Joins a person's genotypes to **public genomic references** (dbSNP, 1000 Genomes, GWAS Catalog, UniProt) in four SQL stages and serves a report per disease or trait. Built at Vision Inside, Aug 2022 – Sep 2023.

**Write-up:** [English](https://zoocasso.github.io/en/work/genomics/) · [한국어](https://zoocasso.github.io/work/genomics/)

| At&nbsp;a&nbsp;glance | |
| :--- | :--- |
| **What** | The backend of a genomic variant annotation and risk-report system, built at Vision Inside for an international project between Kyung Hee University's College of Korean Medicine and a Canadian bio research institute |
| **My part** | Implemented the pipeline, the backend and the user-facing frontend (the frontend is not in this repository). Deployed the service with Docker and a Harbor registry I set up, on a server reachable only from the company network |
| **Others** | The pipeline algorithm was designed together with my team lead |
| **Numbers** | Aug 2022 – Sep 2023 · 4 SQL stages · allele frequencies in 26 populations |
| **Stack** | Python, FastAPI, SQLAlchemy, MySQL, pandas, PyVCF3, Docker, Harbor; upstream BWA, samtools, Picard, GATK |
| **Run · tests** | [Run](#run) · pytest without a database (SQLite slice of the references), and the whole pipeline on MySQL 8.0 and 8.4 in GitHub Actions |

## Data flow

<img src="docs/diagram.png" alt="Data flow: sequencing reads and customer uploads go through input parsing, four SQL stages joined with public references, and a FastAPI JSON API and HTML viewer to the frontend" width="800">

<sub>Solid blue: built by me · dashed blue: algorithm designed with my team lead, implemented by me · white: data sources.</sub>

## Key design decisions

**In the live service (2022–2023)**

- **Public references in MySQL, joined in stages.** dbSNP and 1000 Genomes were loaded one table per chromosome, and the annotation runs as four SQL stages: dbSNP and 1000 Genomes are joined on position and alleles, the GWAS Catalog and UniProt on rsID (and alleles). Each stage writes a table that the next stage reads.
- **A rule-based score, not a prediction.** The risk score comes straight from the published GWAS effect sizes with a fixed rule (below), so each score can be traced to the study behind it.
- **A JSON API for a separate frontend.** In Sep 2023 the pages that the server rendered itself were split into a JSON API, so the frontend could be built on its own.
- **Deployed with Docker** through a Harbor registry I set up, on a server reachable only from the company network.

**Added in this repository**

- **One run at a time, and a report is never missing.** The stage tables are shared, so a run holds a MySQL named lock, and the finished result replaces the user's old one in a single `RENAME TABLE`.
- **Unknown is not zero.** A no-call, or a genotype that is not the variant's REF or ALT (the other strand, I/D coding), gets unknown copies and no score instead of 0. An upload with none of its variants in dbSNP, usually another genome build, is refused with `422`.
- **Tested with and without a database.** Report queries run against an in-memory SQLite slice of the references; the whole pipeline runs on MySQL 8.0 and 8.4 in GitHub Actions.

## What a report contains

A report shows, per disease or trait, the GWAS effect sizes behind it with a rule-of-thumb score, the frequency of each variant in the 26 populations of 1000 Genomes, and related drugs and herbal medicines (MedlinePlus, ATC, PharmDB-K, OASIS). The joins use GRCh37 coordinates.

<img src="docs/live-1000g-populations.png" alt="Live service page: a variant's ratio in each of the 26 populations of 1000 Genomes, with superpopulation and population name" width="400">

<sub>A page of the live service, from the May 2023 project slides: a variant's ratio in each of the 26 populations of 1000 Genomes.</sub>

> **Research use only, not a diagnosis.** For an odds ratio the score is (OR − 1) × 100 × risk-allele copies, put into fixed bands: large increase (≥ 100), moderate increase (25 to 99), little change (−24 to 24) and decrease (≤ −25). The bands are cut-offs, not a statistical test. A BETA is in its trait's own unit and gets no score. The pages show the same notice.

**Not in this repository:** the variant calling upstream (BWA, samtools, Picard, GATK), the loading of the reference tables, and the frontend. The live service ran on an internal server; the code here has only run on test fixtures and in CI.

## Prototype: herbal medicines from disease topics (LDA)

<img src="docs/lda-intertopic-map.png" alt="pyLDAvis view of the LDA model: intertopic distance map of 40 topics and the 30 most salient terms" width="820">

<sub>pyLDAvis view of the topic model (May 2023): 40 topics over MedlinePlus disease summaries, and the 30 most salient terms.</sub>

For a disease or trait with no herbal-medicine entry in PharmDB-K, the prototype weighted each topic's herbal medicines by the disease's topic proportions. It was an experiment in May 2023 and is not part of the service code here.

## Run

```bash
cp .env.example .env              # point BIO_DATABASE_URL at the MySQL with the reference tables
pip install -r requirements.txt
set -a; . ./.env; set +a          # export the settings in .env
uvicorn app.main:app              # JSON API
uvicorn app.viewer:app            # or the HTML viewer
```

With Docker: `docker build -t bio-reports .` and `docker run --env-file .env -p 8000:8000 bio-reports`.

Tests: `pip install -r requirements-dev.txt` and `python -m pytest -q`. To run the whole pipeline on MySQL as well, point `BIO_TEST_MYSQL_URL` at a scratch database whose name ends in `test`:

```bash
docker run -d --rm -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=bio_test mysql:8.0
BIO_TEST_MYSQL_URL=mysql+pymysql://root:root@127.0.0.1:3306/bio_test python -m pytest -q
```

<details>
<summary><b>How it works, file by file</b></summary>

```
upload (VCF or chip export)  ->  input table  ->  dbSNP  ->  GWAS Catalog  ->  1000 Genomes  ->  UniProt  ->  result table per user
```

- [`app/inputs.py`](app/inputs.py) reads the genotypes (PyVCF3 for VCF, pandas for chip exports) into rows keyed by chromosome-position-ref-alt or by rsID. It normalizes chromosome names (`chr1` → `1`, `chrM` → `MT`, chip codes 23–26 and `XY` → X, Y, X, MT) and alleles (upper case), so the SQL compares them exactly. A VCF variant is keyed by the ALT the person carries, so a `0/2` call is not read as the first ALT.
- [`app/pipeline.py`](app/pipeline.py) runs the four SQL stages in [`app/sql/`](app/sql/). Each stage builds the next table from the previous one with an index on the next join key. dbSNP and 1000 Genomes are one table per chromosome, so their stage files are templates run for chromosomes 1–22, X, Y and MT. A run takes a MySQL named lock, clears the stage tables before and after, and renames the final table to the user's result table, `result_<user>`.
- The GWAS stage keeps an association when its risk allele is the variant's REF or ALT, and counts the person's copies of it.
- [`app/reports.py`](app/reports.py) holds every report query. Request values are bound parameters; the user id that names a result table is validated first.
- [`app/main.py`](app/main.py) serves the reports as JSON for the frontend; [`app/viewer.py`](app/viewer.py) serves the same reports as HTML pages with Tabulator grids.
- Uploads keep only the last part of the file name, so a path in it cannot escape the upload folder. The file name's stem is the user id; uploading the same name again replaces that user's report once the new run has finished.
- There is no login: the service is meant for an internal network only. Browsers may read the JSON API only from the origins in `BIO_CORS_ORIGINS` (none by default), and a request body over 200 MB is refused with `413` while it arrives.
- Without a database, the tests run the report queries on an in-memory SQLite slice of the reference tables and check the pipeline's statements in order, sent through PyMySQL's own cursor. [`tests/test_mysql_pipeline.py`](tests/test_mysql_pipeline.py) runs the whole pipeline on MySQL against a few seeded reference rows.

</details>

<details>
<summary><b>API</b></summary>

| Method and path | Returns |
|---|---|
| `POST /uploadfile/`, `POST /uploadfile/array/` | annotates a VCF or a chip export; `{"user": …, "variants": …}` |
| `GET /disease_trait?user=` | the traits found for a user |
| `GET /overview_page?bio_input=&user=` | risk scores, summary, links, herbal medicines and drugs for a trait |
| `GET /scientific_detail_page?bio_input=&user=` | the variants behind a trait and their studies |
| `GET /igsr?snps=&user=` | the variant's frequency in each 1000 Genomes population |
| `GET /oasis?tkm_key=`, `GET /ncbi?genename=` | OASIS records for a medicine, NCBI summary for a gene |
| `GET /healthz` | `{"status": "ok"}` when the database answers |

An unknown user is `404` and an invalid user id `400`. An upload is `422` when it has no usable genotypes or none of them is in dbSNP, `413` over 200 MB, and `503` when the annotation lock is not free within an hour.

</details>

---

<sub>This code is a 2026 cleanup and rewrite of the 2022–2023 original, so the commits are dated 2026.</sub>
