-- run once per chromosome (CHROMOSOMES in app/pipeline.py): the run for chromosome 1 creates the
-- table and the others insert into it
CREATE TABLE connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '{chrom}'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr{suffix}` b
ON tb.connect_key = b.connect_key
;
