<div align="center">

# 🧬 Bio FastAPI — Genomic Variant Annotation Platform

**Variant annotation & risk-report backend over ~1 TB of public genomic reference data**

[![EN](https://img.shields.io/badge/Language-English-blue?style=flat-square)](#-english)
[![KR](https://img.shields.io/badge/언어-한국어-red?style=flat-square)](#-한국어)

</div>

---

## 🇺🇸 English

The backend of a genomic variant annotation and risk-report system, built at Vision Inside for an international collaboration between Kyung Hee University's College of Korean Medicine and a Canadian bio research lab (Aug 2022 – Sep 2023). I was the **sole developer of the data pipeline and backend**; a separate developer built the user-facing frontend.

### 📋 Project Overview

The system turns a person's genomic data (VCF or genotyping-array file) into disease/trait reports by annotating it against a large, multi-source public reference database.

- **Role:** Sole developer — data pipeline, reference database, FastAPI backend, deployment
- **Reference data:** ~1 TB of public sources — dbSNP GRCh37/38 (237 GB), 1000 Genomes (770 GB), GWAS Catalog, UniProt variants
- **Annotation:** 4-stage SQL join keyed on (chrom, pos, ref, alt): dbSNP → GWAS → 1KGP → UniProt
- **This repository:** the FastAPI service (result viewer and, from Sep 2023, a JSON API for the separate frontend). The variant-calling pipeline and the reference-DB build scripts lived in separate internal projects.

### 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI, Python (pandas, NumPy, SQLAlchemy, PyVCF) |
| **Database** | MySQL (composite keys and indexes) |
| **Result viewer** | Jinja2 templates, Tabulator.js |
| **Upstream pipeline** | BWA, samtools, Picard, GATK (FASTQ → VCF) |
| **Deployment** | Docker, Harbor private registry, Ubuntu server (DNS/HTTPS via Let's Encrypt) |
| **Crawling** | BeautifulSoup4, Requests (MedlinePlus, MeSH, NCBI) |

### 🚀 What I Built

#### 1. Reference Database (~1 TB)
- **Chromosome-wise ingestion** — Split the large dbSNP and 1000 Genomes files by chromosome with `sed`/`split`, then loaded them into MySQL with chunked pandas/SQLAlchemy writes to stay within memory.
- **Composite keys** — Unified dbSNP, GWAS, 1KGP, and UniProt records with keys such as `connect_key` (chrom-pos-ref-alt) and `rsID_ALT`, indexed for lookup.
- **Data cleansing** — Parsed semicolon-delimited GWAS Catalog fields and computed allele frequencies for the 26 1000 Genomes populations.

#### 2. Annotation & Report Logic
- **Input normalization** — Normalized heterogeneous VCF/array inputs with `PyVCF` and regular expressions.
- **4-stage SQL join** — Cascaded joins across the reference tables to produce the final annotation table.
- **Rule-based risk scores** — Matched the user's genotype against GWAS effect alleles and scored disease/trait risk from GWAS odds ratios/betas (a rule-based score, not an ML prediction). Added 26-population allele-frequency comparisons and drug/herbal-medicine lookups (MedlinePlus, MeSH, ATC, PharmDB-K, OASIS).

#### 3. FastAPI Service
- **Endpoints** — Genomic file upload, per-disease summaries, and population-distribution data.
- **Result viewer** — A Tabulator.js grid for querying, filtering, and sorting annotation results in the browser.

#### 4. Deployment
- **Docker + Harbor** — Packaged the service with a `Dockerfile` and shipped images through a Harbor private registry I set up on a Korea IDC Ubuntu server (domain and HTTPS via Let's Encrypt).
- **Access** — The production server allowed internal IPs only; the system was not publicly launched.

<div align="right"><a href="#-한국어">🇰🇷 한국어로 보기 ↓</a></div>

---

## 🇰🇷 한국어

비전인사이드에서 경희대 한의대 × 캐나다 바이오 연구소 국제 협업 과제(2022.08 ~ 2023.09)를 위해 만든 유전체 변이 주석·위험도 리포트 시스템의 백엔드입니다. **데이터 파이프라인과 백엔드는 단독 개발**했고, 사용자용 프론트엔드는 별도 개발자가 맡았습니다.

### 📋 프로젝트 개요

개인의 유전체 데이터(VCF 또는 칩 array 파일)를 대규모 공개 레퍼런스 DB와 대조해 질병·형질 리포트로 만드는 시스템입니다.

- **역할:** 단독 개발 — 데이터 파이프라인, 레퍼런스 DB, FastAPI 백엔드, 배포
- **레퍼런스 데이터:** 공개 데이터 약 1 TB — dbSNP GRCh37/38(237 GB), 1000 Genomes(770 GB), GWAS Catalog, UniProt 변이
- **주석:** (chrom, pos, ref, alt) 기준 4단계 SQL 조인 — dbSNP → GWAS → 1KGP → UniProt
- **이 저장소:** FastAPI 서비스(결과 뷰어, 2023-09부터는 별도 프론트엔드용 JSON API). 변이 호출 파이프라인과 레퍼런스 DB 구축 스크립트는 사내 별도 프로젝트에 있었습니다.

### 🛠 기술 스택

| 계층 | 기술 |
|---|---|
| **백엔드** | FastAPI, Python (pandas, NumPy, SQLAlchemy, PyVCF) |
| **데이터베이스** | MySQL (복합 키·인덱스) |
| **결과 뷰어** | Jinja2 템플릿, Tabulator.js |
| **상위 파이프라인** | BWA, samtools, Picard, GATK (FASTQ → VCF) |
| **배포** | Docker, Harbor 사설 레지스트리, Ubuntu 서버 (Let's Encrypt로 도메인·HTTPS) |
| **크롤링** | BeautifulSoup4, Requests (MedlinePlus, MeSH, NCBI) |

### 🚀 구현한 것

#### 1. 레퍼런스 DB (약 1 TB)
- **염색체 단위 적재** — 대용량 dbSNP·1000 Genomes 파일을 `sed`/`split`으로 염색체별로 나눈 뒤, pandas·SQLAlchemy 청크 적재로 메모리 한도 안에서 MySQL에 넣었습니다.
- **복합 키** — `connect_key`(chrom-pos-ref-alt), `rsID_ALT` 같은 키로 dbSNP·GWAS·1KGP·UniProt 레코드를 연결하고 인덱스를 걸었습니다.
- **데이터 정제** — GWAS Catalog의 세미콜론 구분 필드를 분리하고, 1000 Genomes 26개 집단별 대립유전자 빈도를 계산했습니다.

#### 2. 주석·리포트 로직
- **입력 정규화** — `PyVCF`와 정규표현식으로 형식이 제각각인 VCF·array 입력을 정규화했습니다.
- **4단계 SQL 조인** — 레퍼런스 테이블을 연쇄 조인해 최종 주석 테이블을 만들었습니다.
- **규칙형 위험점수** — 사용자 유전형을 GWAS effect allele과 대조하고, GWAS 오즈비·베타로 질병·형질 위험점수를 계산했습니다(ML 예측이 아닌 규칙 기반). 1000 Genomes 26개 집단 빈도 비교와 의약품·한약재 정보(MedlinePlus, MeSH, ATC, PharmDB-K, OASIS) 조회도 넣었습니다.

#### 3. FastAPI 서비스
- **엔드포인트** — 유전체 파일 업로드, 질병별 요약, 집단별 분포 데이터
- **결과 뷰어** — Tabulator.js 그리드로 브라우저에서 주석 결과를 조회·필터·정렬

#### 4. 배포
- **Docker + Harbor** — `Dockerfile`로 서비스를 패키징하고, Korea IDC Ubuntu 서버에 직접 구축한 Harbor 사설 레지스트리로 이미지를 배포했습니다(Let's Encrypt로 도메인·HTTPS).
- **접근 범위** — 운영서버는 내부 IP 접근만 허용했고, 외부에 공개하지는 않았습니다.

<div align="right"><a href="#-english">🇺🇸 View in English ↑</a></div>

---

## 📸 Visualization

<img width="1205" height="758" alt="Variant association visualization" src="https://github.com/user-attachments/assets/733231dd-d3b9-4da8-a79d-2b4e28637bca" />
