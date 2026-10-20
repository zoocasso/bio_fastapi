-- a UniProt variant is joined only when the person carries its allele; a variant without one
-- (no UniProt entry, or none for these alleles) stays, with empty UniProt columns
CREATE TABLE connect_vcf_dbsnp_gwas_1kgp_uniprot_array
SELECT a.*, b.`GENENAME`, b.`VARIANT AA CHANGE`, b.`CONSEQUENCE TYPE`, b.`UNIPROT_REF`, b.`UNIPROT_ALT`
from connect_vcf_dbsnp_gwas_1kgp_array a
left outer JOIN `uniprot` b
ON a.SNPS = b.`SOURCE DB ID` AND (b.UNIPROT_ALT = a.allele_1 OR b.UNIPROT_ALT = a.allele_2)
;
