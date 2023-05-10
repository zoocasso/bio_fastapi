import config

from sqlalchemy import create_engine
import pymysql

import re
import pandas as pd
from tqdm import tqdm
import time


def array_annotation(array_file):
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
    """
        vcf
    """
    vcf_start = time.time()
    print('vcf_parsing')
    
    with open(array_file, "r") as file:
        content = file.read()

    new_content = re.sub(r'^#.*\n', '', content, flags=re.MULTILINE)

    with open(array_file, "w") as file:
        file.write(new_content)

    vcf_df = pd.read_csv(array_file, sep='\t', names=['rsID','CHR','POS','genotype'])

    geno = vcf_df.loc[:,['genotype']]
    allele_list = list()
    for i in tqdm(geno.values):
        allele_list.append(list(i[0]))

    allele_df = pd.DataFrame(allele_list, columns=['allele_1','allele_2'])

    final_df = pd.concat([vcf_df,allele_df],axis=1)
    final_df = final_df.loc[:,['CHR','POS','rsID','allele_1','allele_2']]
    final_df.to_sql(name='vcf_petra',con=db_connection, if_exists='append', index=False)
    cursor.execute('ALTER TABLE `vcf_petra` ADD INDEX `rsID` (`rsID`);')
    mydb.commit()
    vcf_end = time.time()
    print(f"vcf_parsing : {vcf_end - vcf_start:.5f} sec")

    """
        dbsnp
    """
    dbsnp_start = time.time()
    print('connect_dbsnp')
    connect_dbsnp_sql = open('./app/array_annotation/connect_dbsnp.sql', 'r', encoding='utf-8').read()
    connect_dbsnp_sql_list = connect_dbsnp_sql.split(';\n')
    for i in tqdm(connect_dbsnp_sql_list):
        cursor.execute(i)
        mydb.commit()
    cursor.execute('ALTER TABLE `connect_vcf_dbsnp_petra` ADD INDEX `rsID_ALT` (`rsID_ALT`);')
    mydb.commit()
    dbsnp_end = time.time()
    print(f"connect_dbsnp : {dbsnp_end - dbsnp_start:.5f} sec")

    """
        gwas
    """
    gwas_start = time.time()
    print('connect_gwas')
    connect_gwas_sql = open('./app/array_annotation/connect_gwas.sql', 'r', encoding='utf-8').read()
    connect_gwas_sql_list = connect_gwas_sql.split(';\n')
    for i in tqdm(connect_gwas_sql_list):
        cursor.execute(i)
        mydb.commit()
    cursor.execute('ALTER TABLE `connect_vcf_dbsnp_gwas_petra` ADD INDEX `connect_key` (`connect_key`);')
    mydb.commit()
    gwas_end = time.time()
    print(f"connect_gwas : {gwas_end - gwas_start:.5f} sec")

    """
        akgp = 1kgp
    """
    akgp_start = time.time()
    print('connect_1kgp')
    connect_1kgp_sql = open('./app/array_annotation/connect_1kgp.sql', 'r', encoding='utf-8').read()
    connect_1kgp_sql_list = connect_1kgp_sql.split(';\n')
    for i in tqdm(connect_1kgp_sql_list):
        cursor.execute(i)
        mydb.commit()
    cursor.execute('ALTER TABLE `connect_vcf_dbsnp_gwas_1kgp_petra` ADD INDEX `SNPS` (`SNPS`);')
    mydb.commit()
    akgp_end = time.time()
    print(f"connect_1kgp : {akgp_end - akgp_start:.5f} sec")

    """
        uniprot
    """
    uniprot_start = time.time()
    print('connect_uniprot')
    connect_uniprot_sql = open('./app/array_annotation/connect_uniprot.sql', 'r', encoding='utf-8').read()
    connect_uniprot_sql_list = connect_uniprot_sql.split(';\n')
    for i in tqdm(connect_uniprot_sql_list):
        cursor.execute(i)
        mydb.commit()
    uniprot_end = time.time()
    print(f"connect_uniprot : {uniprot_end - uniprot_start:.5f} sec")

    cursor.execute(f'rename table connect_vcf_dbsnp_gwas_1kgp_uniprot to {array_file}')
    end = time.time()
    print(f"total time : {end - start:.5f} sec")