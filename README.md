# Genomic variant annotation and risk reports

[![tests](https://github.com/zoocasso/bio_fastapi/actions/workflows/ci.yml/badge.svg)](https://github.com/zoocasso/bio_fastapi/actions/workflows/ci.yml)

Joins a person's genotypes to about 1 TB of public references in four SQL stages and serves a report per disease or trait. Built at Vision Inside in 2022–2023.<br>
개인 유전형을 공개 레퍼런스 약 1 TB와 4단계 SQL로 이어 질병·형질별 리포트를 만듭니다. 2022~2023년 비전인사이드에서 만들었습니다.

```mermaid
flowchart LR
    fastq["Sequencing reads<br/>FASTQ"]:::ext
    up["Customer upload<br/>VCF or chip export"]:::ext
    ref["Public references, ~1 TB<br/>dbSNP 237 GB<br/>1000 Genomes 770 GB<br/>GWAS Catalog, UniProt"]:::ext
    vcall["Variant calling<br/>BWA → samtools<br/>→ Picard → GATK<br/>not in this repository"]:::shared
    load["Reference loading<br/>into MySQL, by chromosome<br/>in pandas chunks<br/>not in this repository"]:::shared
    subgraph repo["This repository"]
        inp["Input parsing<br/>PyVCF3 · pandas"]:::mine
        sql["4 SQL stages<br/>dbSNP → GWAS Catalog<br/>→ 1000 Genomes → UniProt"]:::shared
        api["FastAPI JSON API<br/>and HTML viewer"]:::mine
    end
    fe["Frontend<br/>not in this repository"]:::mine
    fastq --> vcall
    vcall -->|"VCF"| inp
    up --> inp
    ref --> load
    inp -->|"input table"| sql
    load -->|"reference tables"| sql
    sql -->|"result table per user"| api
    api -->|"JSON"| fe
    classDef mine fill:#EEF2FF,stroke:#2450F0,stroke-width:2px,color:#0B0D12
    classDef shared fill:#EEF2FF,stroke:#2450F0,stroke-width:2px,stroke-dasharray:4 3,color:#0B0D12
    classDef ext fill:#FFFFFF,stroke:#CBD1DA,stroke-width:1px,color:#3F4654
```

<sub>Solid blue: built by me · dashed blue: algorithm designed with my team lead, implemented by me · white: data sources.<br>
파란 실선: 제가 구현 · 파란 점선: 팀장과 함께 설계하고 제가 구현 · 흰색: 데이터 소스.</sub>

[English](#english) · [한국어](#한국어)

## English

| At a glance | |
| :--- | :--- |
| **What** | The backend of a genomic variant annotation and risk-report system, built at Vision Inside for an international project between Kyung Hee University's College of Korean Medicine and a Canadian bio research institute |
| **My part** | Implemented the pipeline, the backend and the user-facing frontend (the frontend is not in this repository). Deployed the service with Docker and a Harbor registry I set up, on a server reachable only from the company network |
| **Others** | The pipeline algorithm was designed together with my team lead |
| **Numbers** | Aug 2022 – Sep 2023 · about 1 TB of public references (dbSNP 237 GB, 1000 Genomes 770 GB) · 4 SQL stages · allele frequencies in 26 populations |
| **Stack** | Python, FastAPI, SQLAlchemy, MySQL, pandas, PyVCF3, Docker, Harbor; upstream BWA, samtools, Picard, GATK |
| **Run · tests** | [Run](#run) · pytest without a database (SQLite slice of the references), and the whole pipeline on MySQL 8.0 and 8.4 in GitHub Actions |
| **Write-up** | [zoocasso.github.io/en/work/genomics](https://zoocasso.github.io/en/work/genomics/) |

A person's genotypes, from a VCF or a genotyping-chip export, are joined to about **1 TB of public references**: dbSNP (237 GB), 1000 Genomes (770 GB), the GWAS Catalog and UniProt variants. The result is a report per disease or trait: the GWAS effect sizes behind it with a rule-of-thumb score, allele frequencies in the 26 populations of 1000 Genomes, and related drugs and herbal medicines (MedlinePlus, ATC, PharmDB-K, OASIS). The joins use GRCh37 coordinates: the pipeline reads the GRCh37 tables of dbSNP.

> **Research use only, not a diagnosis.** For an odds ratio the score is (OR − 1) × 100 × risk-allele copies, put into fixed bands: large increase (≥ 100), moderate increase (25 to 99), little change (−24 to 24) and decrease (≤ −25). The bands are cut-offs, not a statistical test. A BETA is in its trait's own unit and gets no score. The pages show the same notice.

This repository holds the service code. The variant-calling steps upstream of it (BWA, samtools, Picard, GATK) and the loading of the reference tables are not in this repository. The service was built at Vision Inside in 2022–2023, with the pipeline algorithm designed together with the team lead, and ran on an internal server reachable only from the company network; the code in this repository has only run on test fixtures and in CI.

### How it works

```
upload (VCF or chip export)  ->  input table  ->  dbSNP  ->  GWAS Catalog  ->  1000 Genomes  ->  UniProt  ->  result table per user
```

- [`app/inputs.py`](app/inputs.py) reads the genotypes (PyVCF3 for VCF, pandas for chip exports) into rows keyed by chromosome-position-ref-alt or by rsID. It normalizes chromosome names (`chr1` → `1`, `chrM` → `MT`, chip codes 23–26 and `XY` → X, Y, X, MT) and alleles (upper case), so the SQL compares them exactly. A VCF variant is keyed by the ALT the person carries, so a `0/2` call is not read as the first ALT.
- [`app/pipeline.py`](app/pipeline.py) runs the four SQL stages in [`app/sql/`](app/sql/). Each stage builds the next table from the previous one with an index on the next join key. dbSNP and 1000 Genomes are one table per chromosome, so their stage files are templates run for chromosomes 1–22, X, Y and MT. The stage tables are shared, so a run takes a MySQL named lock, clears them before and after, and renames the final table to the user's result table, `result_<user>`.
- The GWAS stage keeps an association when its risk allele is the variant's REF or ALT, and counts the person's copies of it. A no-call, or a genotype that is not the variant's REF and ALT (the other strand, I/D coding), has unknown copies and no score rather than 0. An upload with none of its variants in dbSNP, usually another genome build, is refused with `422`.
- [`app/reports.py`](app/reports.py) holds every report query. Request values are bound parameters; the user id that names a result table is validated first.
- [`app/main.py`](app/main.py) serves the reports as JSON for the frontend; [`app/viewer.py`](app/viewer.py) serves the same reports as HTML pages with Tabulator grids.
- Uploads keep only the last part of the file name, so a path in it cannot escape the upload folder. The file name's stem is the user id; uploading the same name again replaces that user's report once the new run has finished, in one atomic `RENAME TABLE`, so the report is never missing.
- There is no login: the service is meant for an internal network only. Browsers may read the JSON API only from the origins in `BIO_CORS_ORIGINS` (none by default), and a request body over 200 MB is refused with `413` while it arrives.

### Run

```bash
cp .env.example .env              # point BIO_DATABASE_URL at the MySQL with the reference tables
pip install -r requirements.txt
set -a; . ./.env; set +a          # export the settings in .env
uvicorn app.main:app              # JSON API
uvicorn app.viewer:app            # or the HTML viewer
```

With Docker: `docker build -t bio-reports .` and `docker run --env-file .env -p 8000:8000 bio-reports`.

Tests: `pip install -r requirements-dev.txt` and `python -m pytest -q`. Without a database, the report queries run against an in-memory SQLite slice of the reference tables, and the pipeline's statements are checked in order, sent through PyMySQL's own cursor. With `BIO_TEST_MYSQL_URL` set to a scratch database whose name ends in `test`, the whole pipeline also runs on MySQL against a few seeded reference rows ([`tests/test_mysql_pipeline.py`](tests/test_mysql_pipeline.py)); CI does this on MySQL 8.0 and 8.4.

```bash
docker run -d --rm -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=bio_test mysql:8.0
BIO_TEST_MYSQL_URL=mysql+pymysql://root:root@127.0.0.1:3306/bio_test python -m pytest -q
```

### API

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

## 한국어

| 한눈에 보기 | |
| :--- | :--- |
| **무엇** | 비전인사이드에서 경희대 한의대 × 캐나다 바이오 연구소 국제 협업 과제를 위해 만든 유전체 변이 주석·위험도 리포트 시스템의 백엔드 |
| **제가 한 일** | 파이프라인·백엔드·사용자용 프런트엔드 구현(프런트엔드는 이 저장소에 없음). 직접 구축한 Harbor 레지스트리와 Docker로, 사내망에서만 접근할 수 있는 서버에 배포 |
| **다른 사람** | 파이프라인 알고리즘은 팀장과 함께 설계 |
| **수치** | 2022.08 ~ 2023.09 · 공개 레퍼런스 약 1 TB(dbSNP 237 GB, 1000 Genomes 770 GB) · SQL 4단계 · 26개 집단 대립유전자 빈도 |
| **기술** | Python, FastAPI, SQLAlchemy, MySQL, pandas, PyVCF3, Docker, Harbor. 앞단 BWA, samtools, Picard, GATK |
| **실행·테스트** | [Run](#run) · DB 없이 pytest(레퍼런스 일부를 담은 SQLite), GitHub Actions에서 MySQL 8.0·8.4로 파이프라인 전체 실행 |
| **상세** | [zoocasso.github.io/work/genomics](https://zoocasso.github.io/work/genomics/) |

개인의 유전형(VCF 또는 유전자 칩 export)을 **공개 레퍼런스 약 1 TB**(dbSNP 237 GB, 1000 Genomes 770 GB, GWAS Catalog, UniProt 변이)와 조인해 질병·형질별 리포트를 만듭니다. 조인은 GRCh37 좌표 기준이며, 파이프라인은 dbSNP의 GRCh37 테이블을 읽습니다. 리포트에는 근거가 된 GWAS 효과 크기와 어림 점수, 1000 Genomes 26개 집단의 대립유전자 빈도, 관련 의약품·한약재 정보(MedlinePlus, ATC, PharmDB-K, OASIS)가 들어갑니다.

> **연구용이며 진단이 아닙니다.** 오즈비의 점수는 (OR − 1) × 100 × 위험 대립유전자 수이고, 고정 구간으로 나눕니다: 크게 증가(≥ 100), 다소 증가(25~99), 변화 작음(−24~24), 감소(≤ −25). 구간은 정해 둔 기준일 뿐 통계 검정이 아닙니다. BETA는 형질마다 단위가 달라 점수를 매기지 않습니다. 페이지에도 같은 안내가 나옵니다.

이 저장소에는 서비스 코드가 있습니다. 앞단의 변이 호출(BWA, samtools, Picard, GATK)과 레퍼런스 테이블 적재 코드는 이 저장소에 없습니다. 서비스는 2022~2023년 비전인사이드에서 만들었고(파이프라인 알고리즘은 팀장과 함께 설계), 사내망에서만 접근할 수 있는 내부 서버에서 운영했습니다. 이 저장소의 코드는 테스트 데이터와 CI에서만 실행했습니다.

- **입력**: [`app/inputs.py`](app/inputs.py)가 유전형을 읽습니다. VCF는 PyVCF3, 칩 export는 pandas를 씁니다. 염색체 이름(`chr1` → `1`, `chrM` → `MT`, 칩 코드 23–26과 `XY` → X, Y, X, MT)과 대립유전자(대문자)를 정규화해 SQL이 정확히 비교하게 합니다. VCF 변이는 본인이 가진 ALT로 키를 만들어, `0/2`가 첫 번째 ALT로 읽히지 않습니다.
- **GWAS 단계**: 위험 대립유전자가 그 변이의 REF나 ALT이면 연관을 남기고, 본인이 가진 개수를 셉니다. 콜이 없거나 유전형이 그 변이의 REF·ALT가 아니면(반대 가닥, I/D 표기) 개수는 0이 아니라 '알 수 없음'이고 점수도 없습니다. 변이가 하나도 dbSNP에 없으면(대개 다른 게놈 빌드) 업로드를 `422`로 거절합니다.
- **파이프라인**: [`app/pipeline.py`](app/pipeline.py)가 [`app/sql/`](app/sql/)의 4단계 SQL을 돌립니다. dbSNP와 1000 Genomes는 염색체별 테이블이라 해당 단계 SQL은 1–22, X, Y, MT 염색체마다 실행되는 템플릿입니다. 단계 테이블은 공유되므로 MySQL 이름 잠금을 잡고, 실행 전후로 정리한 뒤, 최종 테이블을 사용자 결과 테이블(`result_<user>`)로 바꿉니다.
- **리포트**: [`app/reports.py`](app/reports.py)에 모든 조회가 있습니다. 요청 값은 바인딩 매개변수로만 전달하고, 결과 테이블 이름이 되는 사용자 ID는 먼저 검증합니다.
- **API·뷰어**: [`app/main.py`](app/main.py)는 프런트엔드용 JSON을, [`app/viewer.py`](app/viewer.py)는 같은 리포트를 HTML로 제공합니다.
- **업로드·보안**: 파일 이름의 마지막 부분만 쓰고, 그 이름(확장자 제외)이 사용자 ID가 됩니다. 같은 이름으로 다시 올리면 새 실행이 끝난 뒤 `RENAME TABLE` 한 번으로 그 사용자의 리포트를 원자적으로 교체하므로, 리포트가 비는 순간이 없습니다. 로그인은 없고 사내망 전용입니다. 브라우저에서는 `BIO_CORS_ORIGINS`에 적은 출처(기본값 없음)만 JSON API를 읽을 수 있고, 200 MB를 넘는 요청 본문은 받는 도중에 `413`으로 거절합니다.
- **테스트**: DB 없이도 돌아갑니다. 리포트 조회는 레퍼런스 테이블 일부를 담은 SQLite에서 실제로 실행하고, 파이프라인은 PyMySQL 커서를 거쳐 보내지는 문장과 순서를 검증합니다. `BIO_TEST_MYSQL_URL`에 이름이 `test`로 끝나는 테스트용 DB를 지정하면 레퍼런스 몇 행을 넣은 MySQL에서 파이프라인 전체를 실행하며, CI는 이를 MySQL 8.0과 8.4에서 돌립니다.

실행 방법은 위의 [Run](#run)과 같습니다.

---

<sub>This code is a 2026 cleanup and rewrite of the 2022–2023 original, so the commits are dated 2026.<br>
이 코드는 2022~2023년 원본을 2026년에 정리해 다시 쓴 것이라 커밋 날짜가 2026년입니다.</sub>
