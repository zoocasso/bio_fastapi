CREATE TABLE connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '1'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr1` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '2'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr2` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '3'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr3` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '4'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr4` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '5'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr5` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '6'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr6` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '7'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr7` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '8'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr8` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '9'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr9` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '10'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr10` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '11'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr11` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '12'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr12` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '13'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr13` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '14'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr14` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '15'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr15` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '16'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr16` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '17'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr17` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '18'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr18` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '19'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr19` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '20'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr20` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '21'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr21` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = '22'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr22` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp
with tb as(
    select * from connect_vcf_dbsnp_gwas
    where chrom = 'x' or chrom = 'y' or chrom = 'mt'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr22` b
ON tb.connect_key = b.connect_key
;