-- run once per chromosome (CHROMOSOMES in app/pipeline.py): the run for chromosome 1 creates the
-- table and the others insert into it
create table connect_vcf_dbsnp_array_all
SELECT a.*, b.rsID_ALT, b.connect_key,
	-- connect_key is chromosome-position-REF-ALT
	SUBSTRING_INDEX(SUBSTRING_INDEX(b.connect_key, '-', 3), '-', -1) AS ref,
	SUBSTRING_INDEX(b.connect_key, '-', -1) AS alt
FROM vcf_array AS a
JOIN grch37_dbsnp_chr{suffix} AS b
ON a.rsID = b.rsID
;

-- dbSNP has a row per ALT allele, so a multi-allelic SNP joins once per ALT: keep one row per chip
-- SNP, preferring the one whose REF and ALT are the chip's two alleles
create table connect_vcf_dbsnp_array
SELECT CHR, POS, rsID, allele_1, allele_2, rsID_ALT, connect_key, ref, alt
FROM (
	SELECT a.*, ROW_NUMBER() OVER (
		PARTITION BY a.rsID
		ORDER BY (a.allele_1 IN (a.ref, a.alt) AND a.allele_2 IN (a.ref, a.alt)) DESC, a.connect_key
	) AS n
	FROM connect_vcf_dbsnp_array_all AS a
) AS ranked
WHERE n = 1
;

drop table connect_vcf_dbsnp_array_all
;
