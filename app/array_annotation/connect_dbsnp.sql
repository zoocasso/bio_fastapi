create table __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr1 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr2 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr3 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr4 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr5 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr6 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr7 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr8 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr9 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr10 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr11 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr12 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr13 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr14 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr15 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr16 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr17 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr18 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr19 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr20 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr21 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chr22 as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chrx as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chry as b
ON a.rsID = b.rsID
;

insert into __bio_db.connect_vcf_dbsnp_petra
SELECT a.*,b.rsID_ALT, b.connect_key FROM __bio_db.vcf_petra as a
JOIN __bio_db.grch37_dbsnp_chrmt as b
ON a.rsID = b.rsID
;