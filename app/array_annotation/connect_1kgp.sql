CREATE TABLE connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '1'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr1` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '2'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr2` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '3'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr3` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '4'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr4` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '5'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr5` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '6'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr6` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '7'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr7` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '8'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr8` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '9'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr9` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '10'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr10` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '11'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr11` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '12'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr12` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '13'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr13` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '14'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr14` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '15'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr15` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '16'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr16` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '17'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr17` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '18'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr18` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '19'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr19` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '20'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr20` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '21'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr21` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = '22'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr22` b
ON tb.connect_key = b.connect_key
;

insert into connect_vcf_dbsnp_gwas_1kgp_petra
with tb as(
    select * from connect_vcf_dbsnp_gwas_petra
    where CHR = 'x' or CHR = 'y' or CHR = 'mt'
)
select tb.*, b.ACB, b.ASW, b.BEB, b.CDX, b.CEU, b.CHB, b.CHS, b.CLM, b.ESN, b.FIN, b.GBR, b.GIH, b.GWD, b.IBS, b.ITU, b.JPT, b.KHV, b.LWK, b.MSL, b.MXL, b.PEL, b.PJL, b.PUR, b.STU, b.TSI, b.YRI
from tb
left outer JOIN `1000genome_chr22` b
ON tb.connect_key = b.connect_key
;