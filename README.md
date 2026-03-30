# 💻 Genomic Data Annotation & Visualization System
> **대용량 생물정보 데이터(VCF/Array) 처리 파이프라인 및 통합 분석 시스템 구축**

본 프로젝트는 대용량 유전체 원천 데이터를 정제하여 자체 DB를 구축하고, 사용자 데이터와의 매칭 로직을 통해 질병 분석 결과를 도출하는 **백엔드 파이프라인 및 풀스택 웹 시스템 개발**에 집중.

---

## 🛠 Tech Stack
- **Backend:** FastAPI, Python (Pandas, NumPy, SQLAlchemy, PyVCF)
- **Database:** MySQL (DB Indexing & Query Optimization)
- **Frontend:** HTML/JS, Tabulator.js (Dynamic Data Grid)
- **DevOps:** Docker, Docker-compose, Linux (Bash, Sed/Split)
- **Crawling:** BeautifulSoup4, Requests

---

## 🚀 Core Engineering Tasks

### 1. Big Data ETL & Database Optimization
100GB가 넘는 대용량 생물정보 원천 데이터를 효율적으로 처리하기 위한 데이터 가공 프로세스를 직접 구현.
- **데이터 전처리 자동화:** `Linux sed`와 `split` 명령어를 활용하여 114GB 이상의 대형 VCF/TXT 파일을 Chromosome 단위로 분할 처리하여 메모리 부하를 방지.
- **복합 인덱싱 및 조인 최적화:** 흩어져 있는 dbSNP, GWAS, 1KGP, UniProt 데이터를 통합하기 위해 `connect_key` (chrom-pos-ref-alt) 및 `rsID_ALT` 등의 복합 키를 설계하고 인덱싱하여 검색 속도를 최적화.
- **데이터 정제 로직:** GWAS Catalog의 세미콜론(`;`) 구분 데이터 분리, 1KGP 인종별 분포도 계산 로직 등 복잡한 데이터 변환을 Python으로 구현.

### 2. Genomic Annotation Pipeline Development
사용자가 업로드한 유전체 데이터를 실시간으로 분석하는 파이프라인을 구축.
- **VCF/Array Parsing:** `PyVCF` 라이브러리와 정규표현식(`re`)을 사용하여 서로 다른 형식의 사용자 유전체 데이터를 표준화된 포맷으로 파싱.
- **Multi-stage Join Logic:** 파싱된 데이터와 자체 구축한 4단계(dbSNP -> GWAS -> 1KGP -> UniProt) DB를 SQL 쿼리문으로 연쇄 조인하여 최종 분석 테이블을 생성하는 로직을 개발.
- **Genotype Matching:** 유전형(Allele) 정보와 GWAS의 Effect Allele를 대조하여 `risk_score`를 산출하는 백엔드 로직을 구현.

### 3. Full-Stack Implementation (FastAPI)
백엔드 로직과 실시간으로 연동되는 비동기 웹 화면을 구성.
- **Interactive Data Grid:** `Tabulator.js`를 도입하여 수만 건의 어노테이션 결과를 웹 환경에서 지연 없이 조회, 필터링, 정렬할 수 있도록 구현.
- **RESTful API 설계:** 유전체 파일 업로드, 질병별 요약 정보 조회, 인종별 분포도 데이터 전송을 위한 API 엔드포인트를 설계.

### 4. Containerized Infrastructure & Deployment
일관된 개발 환경 유지와 운영 서버 배포를 위해 컨테이너 기술을 적용.
- **Dockerization:** 프로젝트 환경을 `Dockerfile`로 관리하고 `docker-compose`를 통해 서버를 실행.
- **Private Registry 관리:** Harbor를 활용한 이미지 태깅 및 푸시/풀 프로세스를 통해 이미지를 관리하고 배포.

---

## 💡 Technical Achievements
- **대용량 데이터 처리 경험:** 100GB+급 Raw 데이터를 유실 없이 DB에 적재하고 인덱싱을 통한 쿼리 최적화 수행.
- **복합 파이프라인 구축:** 기획된 분석 흐름을 Python과 SQL의 유기적인 결합을 통해 실시간 분석 시스템으로 구체화.
- **인프라 자동화:** Docker 기반의 배포 프로세스 수립으로 운영 서버 구축 효율성 증대.

<img width="1205" height="758" alt="image" src="https://github.com/user-attachments/assets/733231dd-d3b9-4da8-a79d-2b4e28637bca" />
[AI를 활용하여 연관성 시각화]
