import config

import pymysql
import json
import math
import ast

class pymysql_class:
    def db_connect(self):
        self.connection = pymysql.connect(host=config.DATABASE_CONFIG['host'],
                                    user=config.DATABASE_CONFIG['user'],
                                    password=config.DATABASE_CONFIG['password'],
                                    database=config.DATABASE_CONFIG['dbname'],
                                    cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.connection.cursor()
        return self.cursor

    def db_close(self):
        self.connection.close()

def get_disease_trait(user):
    db_session = pymysql_class()
    cursor = db_session.db_connect()
    cursor.execute(f"select distinct DISEASE_TRAIT FROM connect_vcf_dbsnp_gwas_1kgp_uniprot_{user}")
    rows = cursor.fetchall()
    db_session.db_close()
    return rows

def get_summary(bio_input):
    db_session = pymysql_class()
    cursor = db_session.db_connect()
    cursor.execute(f'SELECT content FROM medlineplus WHERE topic_name ="{bio_input}" AND title = "summary";')
    rows = cursor.fetchall()
    db_session.db_close()
    return rows

def get_snps_riskscore_1kgp(bio_input,user):
    db_session = pymysql_class()
    cursor = db_session.db_connect()
    cursor.execute(f'SELECT DISEASE_TRAIT, SNPS, risk_score,risk_level,risk_type,CI,GBR,FIN,CHS,PUR,CDX,CLM,IBS,PEL,PJL,KHV,ACB,GWD,ESN,BEB,MSL,STU,ITU,CEU,YRI,CHB,JPT,LWK,ASW,MXL,TSI,GIH FROM connect_vcf_dbsnp_gwas_1kgp_uniprot_{user} WHERE DISEASE_TRAIT = "{bio_input}";')
    rows = cursor.fetchall()
    db_session.db_close()
    return rows

def get_count_snps(bio_input,user):
    db_session = pymysql_class()
    cursor = db_session.db_connect()
    cursor.execute(f'SELECT count(distinct SNPS) FROM connect_vcf_dbsnp_gwas_1kgp_uniprot_{user} WHERE DISEASE_TRAIT = "{bio_input}";')
    rows = cursor.fetchall()
    db_session.db_close()
    return rows

def get_medlineplus(bio_input):
    
    db_session = pymysql_class()
    cursor = db_session.db_connect()
    cursor.execute(f'SELECT title,link_title,link FROM medlineplus WHERE topic_name ="{bio_input}" AND (title = "Diagnosis and Tests" OR title = "Treatments and Therapies");')
    rows = cursor.fetchall()
    temp_list = list()
    for i in rows:
        link_title_list = ast.literal_eval(i['link_title'])
        link_list = ast.literal_eval(i['link'])
        for j in range(len(link_title_list)):
            temp_dict = dict()
            temp_dict['title'] = i['title']
            temp_dict['link_title'] = link_title_list[j]
            temp_dict['link'] = link_list[j]
            temp_list.append(temp_dict)
    db_session.db_close()
    return temp_list

def get_tkm(bio_input):
    try:
        db_session = pymysql_class()
        cursor = db_session.db_connect()
        cursor.execute(f'SELECT tkm_name FROM pharmdbk_tkm_relation WHERE kinds = "{bio_input}";')
        tkm_name = cursor.fetchall()

        tkm_list = list()
        for i in tkm_name:
            tkm_list.append(i['tkm_name'])
        
        cursor.execute(f'SELECT * FROM tkm_ref_tb WHERE tkm_eng IN {str(tuple(tkm_list))};')
        rows = cursor.fetchall()
        db_session.db_close()
        return rows
    except:
        return None

def get_medicine(tkm):
    try:
        db_session = pymysql_class()
        cursor = db_session.db_connect()
        tkm_key_list = list()
        for i in tkm:
            tkm_key_list.append(i['tkm_key'])
        cursor.execute(f'SELECT * FROM `medicine` WHERE TKM_KEY IN {str(tuple(tkm_key_list))};')
        medicine = cursor.fetchall()
        db_session.db_close()
        return medicine
    except:
        return None

def get_scientific_detail(bio_input,user):
    db_session = pymysql_class()
    cursor = db_session.db_connect()
    cursor.execute(f'SELECT DISEASE_TRAIT, SNPS, `VARIANT AA CHANGE`,GENENAME,var_type,EFFECT_ALLELE,ALLELE_1,ALLELE_2 FROM connect_vcf_dbsnp_gwas_1kgp_uniprot_{user} WHERE DISEASE_TRAIT = "{bio_input}";')
    rows = cursor.fetchall()
    db_session.db_close()
    return rows
    
def get_reference(bio_input,user):
    db_session = pymysql_class()
    cursor = db_session.db_connect()
    cursor.execute(f'SELECT distinct LINK,AUTHOR,JOURNAL,STUDY FROM connect_vcf_dbsnp_gwas_1kgp_uniprot_{user} WHERE DISEASE_TRAIT = "{bio_input}";')
    rows = cursor.fetchall()
    db_session.db_close()
    return rows

def get_oasis(tkm_key):
    try:
        db_session = pymysql_class()
        cursor = db_session.db_connect()
        cursor.execute(f'SELECT * FROM `oasis_clinical` WHERE tkm_key = "{tkm_key}";')
        oasis_clinical = cursor.fetchall()

        cursor.execute(f'SELECT * FROM `oasis_preclinical` WHERE tkm_key = "{tkm_key}";')
        oasis_preclinical = cursor.fetchall()

        cursor.execute(f'SELECT * FROM `oasis_reference` WHERE tkm_key = "{tkm_key}";')
        oasis_reference = cursor.fetchall()
        db_session.db_close()
        return oasis_clinical, oasis_preclinical, oasis_reference
    
    except:
        return None

def get_igsr(snps,user):
    db_session = pymysql_class()
    cursor = db_session.db_connect()
    cursor.execute(f'SELECT ACB,ASW,BEB,CDX,CEU,CHB,CHS,CLM,ESN,FIN,GBR,GIH,GWD,IBS,ITU,JPT,KHV,LWK,MSL,MXL,PEL,PJL,PUR,STU,TSI,YRI FROM connect_vcf_dbsnp_gwas_1kgp_uniprot_{user} WHERE SNPS = "{snps}";')
    rows = cursor.fetchall()
    
    igsr_key_list = list()
    igsr_value_list = list()
    for i in rows[0]:
        igsr_key_list.append(i)

    for i in rows[0].values():
        try:
            igsr_value_list.append(math.floor(json.loads(i.replace("'",'"'))['1']*100))
        except:
            igsr_value_list.append(0)

    igsr_list = list()
    for key,value in zip(igsr_key_list,igsr_value_list):
        igsr_dict = dict()
        igsr_dict['key'] = key
        igsr_dict['value'] = value
        igsr_list.append(igsr_dict)
    
    detail_list = [
        {'superpopulation' : 'AFR', 'pop_name' : 'African Caribbean'},
        {'superpopulation' : 'AFR', 'pop_name' : 'African Ancestry SW'},
        {'superpopulation' : 'SAS', 'pop_name' : 'Bengali'},
        {'superpopulation' : 'EAS', 'pop_name' : 'Dai Chinese'},
        {'superpopulation' : 'EUR', 'pop_name' : 'CEPH'},
        {'superpopulation' : 'EAS', 'pop_name' : 'Han Chinese'},
        {'superpopulation' : 'EAS', 'pop_name' : 'Southern Han Chinese'},
        {'superpopulation' : 'AMR', 'pop_name' : 'Colombian'},
        {'superpopulation' : 'AFR', 'pop_name' : 'Esan'},
        {'superpopulation' : 'EUR', 'pop_name' : 'Finnish'},
        {'superpopulation' : 'EUR', 'pop_name' : 'British'},
        {'superpopulation' : 'SAS', 'pop_name' : 'Gujarati'},
        {'superpopulation' : 'AFR', 'pop_name' : 'Gambian Mandinka'},
        {'superpopulation' : 'EUR', 'pop_name' : 'Iberian'},
        {'superpopulation' : 'SAS', 'pop_name' : 'Telugu'},
        {'superpopulation' : 'EAS', 'pop_name' : 'Japanese'},
        {'superpopulation' : 'EAS', 'pop_name' : 'Kinh Vietnamese'},
        {'superpopulation' : 'AFR', 'pop_name' : 'Luhya'},
        {'superpopulation' : 'AFR', 'pop_name' : 'Mende'},
        {'superpopulation' : 'AMR', 'pop_name' : 'Mexican Ancestry'},
        {'superpopulation' : 'AMR', 'pop_name' : 'Peruvian'},
        {'superpopulation' : 'SAS', 'pop_name' : 'Punjabi'},
        {'superpopulation' : 'AMR', 'pop_name' : 'Puerto Rican'},
        {'superpopulation' : 'EUR', 'pop_name' : 'Toscani'},
        {'superpopulation' : 'SAS', 'pop_name' : 'Tamil'},
        {'superpopulation' : 'AFR', 'pop_name' : 'Yoruba'}
    ]

    for i in range(26):
        igsr_list[i].update(detail_list[i])
    
    db_session.db_close()
    return igsr_list

def get_ncbi(genename):
    db_session = pymysql_class()
    cursor = db_session.db_connect()
    cursor.execute(f'SELECT geneid FROM `ncbi_ref` WHERE symbol = "{genename}";')
    geneid = cursor.fetchone()['geneid']
    
    cursor.execute(f'SELECT content FROM `ncbi` WHERE geneid = "{geneid}" and title = "Summary";')
    content = cursor.fetchone()['content']
    db_session.db_close()
    return content