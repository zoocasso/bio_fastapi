import pymysql

connection = pymysql.connect(host='211.34.105.108',
                             user='root',
                             password='vision9551',
                             database='__bio_db',
                             cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()

def get_summary(bio_input):
    cursor.execute(f"SELECT content FROM medlineplus WHERE topic_name ='{bio_input}' AND title = 'summary';")
    rows = cursor.fetchall()
    return rows

def get_snps_riskscore_1kgp(bio_input):
    cursor.execute(f"SELECT DISEASE_TRAIT, SNPS, risk_score,GBR,FIN,CHS,PUR,CDX,CLM,IBS,PEL,PJL,KHV,ACB,GWD,ESN,BEB,MSL,STU,ITU,CEU,YRI,CHB,JPT,LWK,ASW,MXL,TSI,GIH FROM connect_vcf_dbsnp_gwas_1kgp_uniprot WHERE DISEASE_TRAIT = '{bio_input}';")
    rows = cursor.fetchall()
    return rows

def get_count_snps(bio_input):
    cursor.execute(f"SELECT count(distinct SNPS) FROM connect_vcf_dbsnp_gwas_1kgp_uniprot WHERE DISEASE_TRAIT = '{bio_input}';")
    rows = cursor.fetchall()
    return rows

def get_medlineplus(bio_input):
    cursor.execute(f"SELECT title,content FROM medlineplus WHERE topic_name ='{bio_input}' AND (title = 'Diagnosis and Tests' OR title = 'Treatments and Therapies');")
    rows = cursor.fetchall()
    return rows

def get_tkm(bio_input):
    cursor.execute(f"SELECT tkm_name FROM pharmdbk_tkm_relation WHERE kinds = '{bio_input}';")
    tkm_name = cursor.fetchall()

    tkm_list = list()
    for i in tkm_name:
        tkm_list.append(i['tkm_name'])
    
    cursor.execute(f"SELECT * FROM tkm_ref_tb WHERE tkm_eng IN {str(tuple(tkm_list))};")
    rows = cursor.fetchall()
    return rows

def get_medicine(tkm):
    try:
        tkm_key_list = list()
        for i in tkm:
            tkm_key_list.append(i['tkm_key'])
        cursor.execute(f"SELECT * FROM `medicine` WHERE TKM_KEY IN {str(tuple(tkm_key_list))};")
        medicine = cursor.fetchall()
        return medicine
    except:
        return None

def get_scientific_detail(bio_input):
    cursor.execute(f"SELECT DISEASE_TRAIT, SNPS, `VARIANT AA CHANGE`,GENENAME,CONTEXT,EFFECT_ALLELE,ALLELE_1,ALLELE_2 FROM connect_vcf_dbsnp_gwas_1kgp_uniprot WHERE DISEASE_TRAIT = '{bio_input}';")
    rows = cursor.fetchall()
    return rows
    
def get_reference(bio_input):
    cursor.execute(f"SELECT distinct LINK,AUTHOR,JOURNAL,STUDY FROM connect_vcf_dbsnp_gwas_1kgp_uniprot WHERE DISEASE_TRAIT = '{bio_input}';")
    rows = cursor.fetchall()
    return rows

def get_oasis(tkm_key):
    try:
        cursor.execute(f"SELECT * FROM `oasis_clinical` WHERE tkm_key = '{tkm_key}';")
        oasis_clinical = cursor.fetchall()

        cursor.execute(f"SELECT * FROM `oasis_preclinical` WHERE tkm_key = '{tkm_key}';")
        oasis_preclinical = cursor.fetchall()

        cursor.execute(f"SELECT * FROM `oasis_reference` WHERE tkm_key = '{tkm_key}';")
        oasis_reference = cursor.fetchall()
        return oasis_clinical, oasis_preclinical, oasis_reference
    
    except:
        return None