create table connect_vcf_dbsnp_gwas_temp
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
FROM connect_vcf_dbsnp AS a
JOIN gwas_catelog AS b
ON a.rsID_ALT = b.STRONGEST_SNP
;

create table connect_vcf_dbsnp_gwas_temp2
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
FROM connect_vcf_dbsnp_gwas_temp AS a
;

create table connect_vcf_dbsnp_gwas
SELECT
	a.*,
	-- a level only for an odds-ratio score such as "50%" or "-100%",
	-- and every score at or below -25% counts as significantly decreased
	CASE WHEN a.risk_type = 'OR' AND a.risk_score REGEXP '^-?[0-9]+%$' THEN
		CASE
			WHEN CAST(REPLACE(a.risk_score, "%", "") AS SIGNED) <= -25 THEN 'Significantly Decreased'
			WHEN CAST(REPLACE(a.risk_score, "%", "") AS SIGNED) <= 24 THEN 'Average Risk'
			WHEN CAST(REPLACE(a.risk_score, "%", "") AS SIGNED) < 100 THEN 'Slightly Increased'
			ELSE 'Significantly Increased'
		END
	END AS risk_level
FROM connect_vcf_dbsnp_gwas_temp2 AS a
;

drop table connect_vcf_dbsnp_gwas_temp
;

drop table connect_vcf_dbsnp_gwas_temp2
;
