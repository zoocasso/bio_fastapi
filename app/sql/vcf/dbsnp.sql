-- run once per chromosome, with the chrom placeholder set to 1-22, x, y and mt (CHROMOSOMES in app/pipeline.py):
-- the run for chromosome 1 creates the table and the others insert into it
create table connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM vcf AS a
JOIN dbsnp37_chr{chrom} AS b
ON a.connect_key = b.connect_key
;
