-- 여기서 Null값 뽑아야함
CREATE TABLE connect_vcf_dbsnp_gwas_1kgp_uniprot_temp
SELECT a.*, b.`GENENAME`, b.`VARIANT AA CHANGE`, b.`CONSEQUENCE TYPE`, b.`UNIPROT_REF`, b.`UNIPROT_ALT`
from connect_vcf_dbsnp_gwas_1kgp a
left outer JOIN `uniprot` b
ON a.SNPS = b.`SOURCE DB ID`
;

-- uniprot이 있는 값들만
CREATE TABLE connect_vcf_dbsnp_gwas_1kgp_uniprot
SELECT * FROM connect_vcf_dbsnp_gwas_1kgp_uniprot_temp a WHERE a.UNIPROT_ALT = a.allele_1 OR a.UNIPROT_ALT = a.allele_2
;

-- 최종 테이블
insert into connect_vcf_dbsnp_gwas_1kgp_uniprot
SELECT * FROM connect_vcf_dbsnp_gwas_1kgp_uniprot_temp a WHERE a.`VARIANT AA CHANGE` IS NULL 
;

-- 불필요한 테이블 제거하는 쿼리문
drop table connect_vcf_dbsnp_gwas_1kgp_uniprot_temp
;