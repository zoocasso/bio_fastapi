create table __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr1 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr2 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr3 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr4 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr5 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr6 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr7 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr8 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr9 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr10 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr11 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr12 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr13 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr14 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr15 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr16 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr17 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr18 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr19 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr20 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr21 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chr22 AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chrx AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chry AS b
ON a.connect_key = b.connect_key
;

insert into __bio_db.connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM __bio_db.vcf AS a
JOIN __bio_db.dbsnp37_chrmt AS b
ON a.connect_key = b.connect_key
;