-- an association is kept when its risk allele is this variant's REF or ALT, so a person who carries
-- a REF risk allele gets the association too
create table connect_vcf_dbsnp_gwas_temp
SELECT
	a.chrom,a.pos,a.id,a.ref,a.alt,a.qual,a.filter,a.info,a.`format`,a.sample_data,a.allele_1,a.allele_2,b.*,a.connect_key,
	CASE
		-- a no-call, or alleles that are not this variant's REF and ALT (the other strand, I/D
		-- coding, another ALT): the number of risk-allele copies is unknown, not 0
		WHEN NOT (a.allele_1 IN (a.ref, a.alt) AND a.allele_2 IN (a.ref, a.alt)) THEN NULL
		ELSE (a.allele_1 = b.EFFECT_ALLELE) + (a.allele_2 = b.EFFECT_ALLELE)
	END AS copies,
	CASE
		WHEN b.`OR` IS NULL OR b.`OR` = '' THEN ''
		WHEN b.CI LIKE '%increase' OR b.CI LIKE '%decrease' THEN 'BETA'
		ELSE 'OR'
	END AS risk_type
FROM connect_vcf_dbsnp AS a
JOIN gwas_catelog AS b
ON b.STRONGEST_SNP IN (CONCAT(a.rsID, '-', a.ref), CONCAT(a.rsID, '-', a.alt))
;

-- risk_score is a rule of thumb, (OR - 1) x 100 x copies, for odds ratios with known copies only; a
-- BETA is in its trait's own unit and gets no score. risk_level puts the score in fixed bands; it is
-- not a statistical test
create table connect_vcf_dbsnp_gwas
SELECT
	s.*,
	CASE
		WHEN s.risk_score IS NULL THEN NULL
		WHEN s.risk_score >= 100 THEN 'Large increase'
		WHEN s.risk_score >= 25 THEN 'Moderate increase'
		WHEN s.risk_score > -25 THEN 'Little change'
		ELSE 'Decrease'
	END AS risk_level
FROM (
	SELECT
		a.*,
		CASE WHEN a.risk_type = 'OR' AND a.copies IS NOT NULL
			THEN CAST((CAST(a.`OR` AS DOUBLE) - 1) * 100 * a.copies AS SIGNED)
		END AS risk_score
	FROM connect_vcf_dbsnp_gwas_temp AS a
) AS s
;

drop table connect_vcf_dbsnp_gwas_temp
;
