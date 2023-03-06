create table __bio_db.connect_vcf_dbsnp_gwas_temp
SELECT 
	a.chrom,a.pos,a.id,a.ref,a.alt,a.qual,a.filter,a.info,a.`format`,a.sample_data,a.allele_1,a.allele_2,b.*,a.connect_key,
	CASE
		WHEN b.EFFECT_ALLELE = '?' THEN '?'
		WHEN b.EFFECT_ALLELE = a.allele_1 AND b.EFFECT_ALLELE = a.allele_2 THEN '2'
		WHEN b.EFFECT_ALLELE != a.allele_1 AND b.EFFECT_ALLELE = a.allele_2 THEN '1'
		WHEN b.EFFECT_ALLELE = a.allele_1 AND b.EFFECT_ALLELE != a.allele_2 THEN '1'
		ELSE '0'
	END AS copies,
	CASE
		WHEN b.OR = "" THEN ""
		WHEN b.CI LIKE '%increase' THEN 'BETA'
		WHEN b.CI LIKE '%decrease' THEN 'BETA'
		ELSE 'OR'
	END AS risk_type
FROM __bio_db.connect_vcf_dbsnp AS a
JOIN __bio_db.gwas_catelog AS b
ON a.rsID_ALT = b.STRONGEST_SNP
;

create table __bio_db.connect_vcf_dbsnp_gwas
SELECT
	a.*,
	CASE
		WHEN a.`OR` = '' THEN ''
		WHEN a.copies = '?' THEN '?'
		WHEN a.copies = '0' THEN '0%'
		WHEN a.risk_type = 'OR' THEN CONCAT(CAST((CAST(a.`OR` AS FLOAT) - 1) * 100 * CAST(a.copies AS FLOAT) AS signed),"%")
		WHEN a.risk_type = 'BETA' and a.CI LIKE '%increase' THEN CONCAT(CAST(CAST(a.`OR` AS FLOAT) * 100 * CAST(a.copies AS FLOAT) AS signed),"%")
		WHEN a.risk_type = 'BETA' and a.CI LIKE '%decrease' THEN CONCAT("-",CAST(CAST(a.`OR` AS FLOAT) * 100 * CAST(a.copies AS FLOAT) AS SIGNED),"%")
		ELSE ''
	END AS risk_score
FROM __bio_db.connect_vcf_dbsnp_gwas_temp AS a
;

drop table __bio_db.connect_vcf_dbsnp_gwas_temp
;