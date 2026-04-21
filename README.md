<div align="center">

# 🧬 Bio FastAPI — Genomic Variant Annotation Platform

**Big-Data Bioinformatics Pipeline & Full-Stack Analysis System**

[![EN](https://img.shields.io/badge/Language-English-blue?style=flat-square)](#-english)
[![KR](https://img.shields.io/badge/언어-한국어-red?style=flat-square)](#-한국어)

</div>

---

## 🇺🇸 English

A full-stack genomic variant annotation platform that ingests raw bioinformatics data (VCF/Array) at scale, builds an optimized in-house reference database, and delivers real-time disease-risk analysis through a FastAPI web interface.

### 📋 Project Overview

An end-to-end bioinformatics system covering the full lifecycle — from raw-data ingestion and database construction to user-facing annotation and visualization. The platform annotates user-uploaded genomic data by cross-referencing it against a curated, multi-source variant database and produces disease-association reports in real time.

- **Scope:** Backend pipeline, database engineering, full-stack web system
- **Data Scale:** 100GB+ raw genomic source data
- **Architecture:** 4-stage SQL join pipeline (dbSNP → GWAS → 1KGP → UniProt)

### 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI, Python (Pandas, NumPy, SQLAlchemy, PyVCF) |
| **Database** | MySQL (composite indexing, query optimization) |
| **Frontend** | HTML/JS, Tabulator.js (interactive data grid) |
| **DevOps** | Docker, Docker Compose, Harbor Registry, Linux (Bash, sed, split) |
| **Crawling** | BeautifulSoup4, Requests |

### 🚀 Core Engineering Contributions

#### 1. Big-Data ETL & Database Optimization
- **Memory-Safe Preprocessing** — Split 114GB+ VCF/TXT files by chromosome using Linux `sed` and `split`, preventing out-of-memory failures during ingestion.
- **Composite Indexing** — Designed compound keys (`connect_key` = chrom-pos-ref-alt, `rsID_ALT`) to unify fragmented dbSNP, GWAS, 1KGP, and UniProt sources, dramatically accelerating lookup performance.
- **Data Cleansing Logic** — Implemented Python routines for semicolon-delimited GWAS Catalog parsing and per-ethnicity 1KGP distribution calculation.

#### 2. Genomic Annotation Pipeline
- **VCF/Array Parsing** — Built a normalizer using `PyVCF` and regular expressions that standardizes heterogeneous user inputs into a unified internal format.
- **4-Stage SQL Join** — Developed cascading join logic across the 4-tier reference database (dbSNP → GWAS → 1KGP → UniProt) to produce the final annotation table.
- **Risk Scoring** — Implemented genotype-vs-effect-allele matching logic that computes a `risk_score` per variant for downstream disease-association analysis.

#### 3. Full-Stack Implementation (FastAPI)
- **Interactive Data Grid** — Integrated `Tabulator.js` to enable lag-free query, filter, and sort operations over tens of thousands of annotation rows in the browser.
- **RESTful API Design** — Designed endpoints for genomic file upload, per-disease summary retrieval, and ethnicity-distribution data delivery.

#### 4. Containerized Infrastructure
- **Dockerization** — Managed the full environment via `Dockerfile` and `docker-compose`, ensuring reproducible deployment across dev and production.
- **Private Registry** — Operated image tagging, push, and pull workflows through Harbor for controlled internal distribution.

### 💡 Technical Achievements

- Handled **100GB+ raw data** ingestion with zero loss, backed by index-driven query optimization.
- Translated a multi-stage analysis design into a production real-time system through tight Python–SQL integration.
- Established a Docker-based deployment workflow that measurably reduced environment setup and release overhead.

<div align="right"><a href="#-한국어">🇰🇷 한국어로 보기 ↓</a></div>

---

## 🇰🇷 한국어

대용량 생물정보 데이터(VCF/Array)를 수집·정제하여 최적화된 자체 레퍼런스 DB를 구축하고, FastAPI 웹 인터페이스를 통해 실시간 질병 위험도 분석을 제공하는 풀스택 유전체 변이 어노테이션 플랫폼입니다.

### 📋 프로젝트 개요

원천 데이터 수집과 DB 구축에서부터 사용자 대상 어노테이션 및 시각화까지 전체 수명주기를 아우르는 end-to-end 생물정보 시스템입니다. 사용자가 업로드한 유전체 데이터를 다중 소스 기반으로 큐레이션된 변이 DB와 대조하여 질병 연관성 리포트를 실시간으로 생성합니다.

- **범위:** 백엔드 파이프라인, 데이터베이스 엔지니어링, 풀스택 웹 시스템
- **데이터 규모:** 100GB+ 원천 유전체 데이터
- **아키텍처:** 4단계 SQL Join 파이프라인 (dbSNP → GWAS → 1KGP → UniProt)

### 🛠 기술 스택

| 계층 | 기술 |
|---|---|
| **백엔드** | FastAPI, Python (Pandas, NumPy, SQLAlchemy, PyVCF) |
| **데이터베이스** | MySQL (복합 인덱싱, 쿼리 최적화) |
| **프론트엔드** | HTML/JS, Tabulator.js (동적 데이터 그리드) |
| **DevOps** | Docker, Docker Compose, Harbor Registry, Linux (Bash, sed, split) |
| **크롤링** | BeautifulSoup4, Requests |

### 🚀 핵심 엔지니어링 기여

#### 1. 대용량 ETL 및 데이터베이스 최적화
- **메모리 안전 전처리** — 114GB+ VCF/TXT 파일을 `sed`, `split`을 활용해 Chromosome 단위로 분할 처리하여 메모리 부하 및 적재 중 OOM을 방지했습니다.
- **복합 인덱싱 설계** — 흩어진 dbSNP, GWAS, 1KGP, UniProt 데이터를 통합하기 위해 `connect_key` (chrom-pos-ref-alt), `rsID_ALT` 등의 복합 키를 설계·인덱싱하여 조회 속도를 대폭 개선했습니다.
- **데이터 정제 로직** — GWAS Catalog의 세미콜론(`;`) 구분 데이터 분리, 1KGP 인종별 분포 계산 등 복잡한 변환을 Python으로 구현했습니다.

#### 2. 유전체 어노테이션 파이프라인
- **VCF/Array 파싱** — `PyVCF`와 정규표현식(`re`)을 활용해 이질적인 사용자 입력을 표준화된 내부 포맷으로 정규화하는 파서를 구축했습니다.
- **4단계 SQL Join** — 자체 구축한 4단계 레퍼런스 DB(dbSNP → GWAS → 1KGP → UniProt)를 연쇄 조인하여 최종 어노테이션 테이블을 생성하는 로직을 개발했습니다.
- **위험도 산출** — 사용자 유전형(Allele)과 GWAS의 Effect Allele을 대조하여 변이별 `risk_score`를 산출하는 백엔드 로직을 구현했습니다.

#### 3. 풀스택 구현 (FastAPI)
- **인터랙티브 데이터 그리드** — `Tabulator.js`를 도입해 수만 건의 어노테이션 결과를 브라우저 환경에서 지연 없이 조회·필터링·정렬할 수 있도록 구현했습니다.
- **RESTful API 설계** — 유전체 파일 업로드, 질병별 요약 정보 조회, 인종별 분포도 데이터 전송을 위한 엔드포인트를 설계했습니다.

#### 4. 컨테이너 기반 인프라
- **Dockerization** — `Dockerfile`과 `docker-compose`로 전체 환경을 관리하여 개발·운영 환경 간의 재현성을 확보했습니다.
- **Private Registry** — Harbor를 활용한 이미지 태깅, Push/Pull 워크플로우를 운영하여 이미지 배포를 체계화했습니다.

### 💡 주요 성과

- **100GB+ 원천 데이터**를 유실 없이 적재하고 인덱싱 기반 쿼리 최적화를 수행했습니다.
- 다단계 분석 설계를 Python–SQL의 유기적 결합을 통해 실시간 운영 시스템으로 구체화했습니다.
- Docker 기반 배포 워크플로우를 수립하여 환경 구성 및 릴리즈 부담을 체계적으로 절감했습니다.

<div align="right"><a href="#-english">🇺🇸 View in English ↑</a></div>

---

## 📸 Visualization

<img width="1205" height="758" alt="Variant association visualization" src="https://github.com/user-attachments/assets/733231dd-d3b9-4da8-a79d-2b4e28637bca" />
