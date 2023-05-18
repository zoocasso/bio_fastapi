import app.vcf_annotation.pyvcf_221017 as pyvcf
from app import config

from sqlalchemy import create_engine
import pymysql

import pandas as pd
from tqdm import tqdm
import time

def gt_bases_sep(gt_bases):
    alt_list = list()
    a_list = gt_bases.split("/")
    for i in a_list:
        alt_list.append(i.split("|"))
    return sum(alt_list,[])

def vcf_counter(object):
    count=0
    for i in object:
        if i:
            count=count+1
    return count

def vcf_annotation(vcf_file):
    start = time.time()
    
    db_connection_str = f"mysql+pymysql://{config.DATABASE_CONFIG['user']}:{config.DATABASE_CONFIG['password']}@{config.DATABASE_CONFIG['host']}/{config.DATABASE_CONFIG['dbname']}"
    db_connection = create_engine(db_connection_str)
    conn = db_connection.connect()

    mydb = pymysql.connect(host=config.DATABASE_CONFIG['host'],
                                user=config.DATABASE_CONFIG['user'],
                                password=config.DATABASE_CONFIG['password'],
                                database=config.DATABASE_CONFIG['dbname'],
                                cursorclass=pymysql.cursors.DictCursor)
    cursor = mydb.cursor()
    vcf_start = time.time()

    vcf_reader = pyvcf.Reader(open(vcf_file, 'r'))
    genom_length = vcf_counter(vcf_reader.reader)
    vcf_reader = pyvcf.Reader(open(vcf_file, 'r'))
    vcf_list = list()

    for i in tqdm(range(genom_length)):
        row_vcf_reader = vcf_reader.next()
        vcf_dict = {'chrom' : str(row_vcf_reader.CHROM),
                            'pos' : int(row_vcf_reader.POS),
                            'id' : str(row_vcf_reader.ID),
                            'ref' : str(row_vcf_reader.REF),
                            'alt' : row_vcf_reader.ALT[0],
                            'qual' : str(row_vcf_reader.QUAL),
                            'filter' : str(row_vcf_reader.FILTER) if str(row_vcf_reader.FILTER) != "[]" else 'PASS', 
                            'info' : str(row_vcf_reader.INFO), 
                            'format': str(row_vcf_reader.FORMAT)}
        sample=row_vcf_reader.genotype("SRR062634")
        sample_data_txt = ''
        try:
            sample_data_txt += str(row_vcf_reader.samples[0].data.GT)
        except:
            pass
        try:
            sample_data_txt += ";" + str(row_vcf_reader.samples[0].data.AD)
        except:
            pass
        try:
            sample_data_txt += ";" + str(row_vcf_reader.samples[0].data.DP)
        except:
            pass
        try:
            sample_data_txt += ";" + str(row_vcf_reader.samples[0].data.GQ)
        except:
            pass
        try:
            sample_data_txt += ";" + str(row_vcf_reader.samples[0].data.PL)
        except:
            pass
        vcf_dict['sample_data'] = str(sample_data_txt)
        vcf_dict['allele_1'] = gt_bases_sep(str(sample.gt_bases))[0]
        vcf_dict['allele_2'] = gt_bases_sep(str(sample.gt_bases))[1]
        vcf_dict['connect_key'] = f"{str(vcf_dict['chrom'])}-{str(vcf_dict['pos'])}-{str(vcf_dict['ref'])}-{str(vcf_dict['alt'])}" 
        vcf_list.append(vcf_dict)

    vcf_df = pd.DataFrame(vcf_list)
    vcf_df.to_sql(name='vcf',con=db_connection, if_exists='append', index=False)
    
    cursor.execute('ALTER TABLE `vcf` ADD INDEX `connect_key` (`connect_key`);')
    mydb.commit()

    vcf_end = time.time()
    print(f"vcf : {vcf_end - vcf_start:.5f} sec")


    dbsnp_start = time.time()
    print('connect_dbsnp')
    connect_dbsnp_sql = open('./app/vcf_annotation/connect_dbsnp.sql', 'r', encoding='utf-8').read()
    connect_dbsnp_sql_list = connect_dbsnp_sql.split(';\n')
    for i in tqdm(connect_dbsnp_sql_list):
        cursor.execute(i)
        mydb.commit()
    cursor.execute('ALTER TABLE `connect_vcf_dbsnp` ADD INDEX `rsID_ALT` (`rsID_ALT`);')
    mydb.commit()
    dbsnp_end = time.time()
    print(f"connect_dbsnp : {dbsnp_end - dbsnp_start:.5f} sec")

    gwas_start = time.time()
    print('connect_gwas')
    connect_gwas_sql = open('./app/vcf_annotation/connect_gwas.sql', 'r', encoding='utf-8').read()
    connect_gwas_sql_list = connect_gwas_sql.split(';\n')
    for i in tqdm(connect_gwas_sql_list):
        cursor.execute(i)
        mydb.commit()
    cursor.execute('ALTER TABLE `connect_vcf_dbsnp_gwas` ADD INDEX `connect_key` (`connect_key`);')
    mydb.commit()
    gwas_end = time.time()
    print(f"connect_gwas : {gwas_end - gwas_start:.5f} sec")


    akgp_start = time.time()
    print('connect_1kgp')
    connect_1kgp_sql = open('./app/vcf_annotation/connect_1kgp.sql', 'r', encoding='utf-8').read()
    connect_1kgp_sql_list = connect_1kgp_sql.split(';\n')
    for i in tqdm(connect_1kgp_sql_list):
        cursor.execute(i)
        mydb.commit()
    cursor.execute('ALTER TABLE `connect_vcf_dbsnp_gwas_1kgp` ADD INDEX `SNPS` (`SNPS`);')
    mydb.commit()
    akgp_end = time.time()
    print(f"connect_1kgp : {akgp_end - akgp_start:.5f} sec")


    uniprot_start = time.time()
    print('connect_uniprot')
    connect_uniprot_sql = open('./app/vcf_annotation/connect_uniprot.sql', 'r', encoding='utf-8').read()
    connect_uniprot_sql_list = connect_uniprot_sql.split(';\n')
    for i in tqdm(connect_uniprot_sql_list):
        cursor.execute(i)
        mydb.commit()
    uniprot_end = time.time()
    print(f"connect_uniprot : {uniprot_end - uniprot_start:.5f} sec")

    cursor.execute(f'rename table connect_vcf_dbsnp_gwas_1kgp_uniprot to {vcf_file}')
    end = time.time()
    print(f"total time : {end - start:.5f} sec")