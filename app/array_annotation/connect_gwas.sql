create table __bio_db.connect_vcf_dbsnp_gwas_temp
SELECT 
	a.CHR,a.pos,a.allele_1,a.allele_2,b.*,a.connect_key,
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
FROM __bio_db.connect_vcf_dbsnp_petra AS a
JOIN __bio_db.gwas_catelog AS b
ON a.rsID_ALT = b.STRONGEST_SNP
;

create table __bio_db.connect_vcf_dbsnp_gwas_temp2
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

create table __bio_db.connect_vcf_dbsnp_gwas_petra
SELECT
	a.*,
	case
		when risk_type ="OR" and cast(replace(risk_score , "%", "") AS SIGNED) <= -100 then 'Significantly Decreased'
		when risk_type ="OR" and cast(replace(risk_score , "%", "") AS SIGNED) > -100 AND cast(replace(risk_score , "%", "") AS SIGNED) <= -25 then 'Significantly Decreased'
		when risk_type ="OR" and cast(replace(risk_score , "%", "") AS SIGNED) > -25 AND cast(replace(risk_score , "%", "") AS SIGNED) <= 24 then 'Average Risk'
		when risk_type ="OR" and cast(replace(risk_score , "%", "") AS SIGNED) > 24 AND cast(replace(risk_score , "%", "") AS SIGNED) < 100 then 'Slightly Increased'
		when risk_type ="OR" and cast(replace(risk_score , "%", "") AS SIGNED) >= 100 then 'Significantly Increased'
	END AS risk_level
FROM __bio_db.connect_vcf_dbsnp_gwas_temp2 AS a
;

drop table __bio_db.connect_vcf_dbsnp_gwas_temp
;

drop table __bio_db.connect_vcf_dbsnp_gwas_temp2
;