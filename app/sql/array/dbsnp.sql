-- run once per chromosome, with the chrom placeholder set to 1-22, x, y and mt (CHROMOSOMES in app/pipeline.py):
-- the run for chromosome 1 creates the table and the others insert into it
create table connect_vcf_dbsnp_array
SELECT a.*,b.rsID_ALT, b.connect_key FROM vcf_array as a
JOIN grch37_dbsnp_chr{chrom} as b
ON a.rsID = b.rsID
;
