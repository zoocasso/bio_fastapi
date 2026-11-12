-- run once per chromosome (CHROMOSOMES in app/pipeline.py): the run for chromosome 1 creates the
-- table and the others insert into it
create table connect_vcf_dbsnp
SELECT a.*, b.rsID_ALT, b.rsID FROM vcf AS a
JOIN dbsnp37_chr{suffix} AS b
ON a.connect_key = b.connect_key
;
