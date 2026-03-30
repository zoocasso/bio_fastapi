"""
    medlineplus의 Summary들을 데이터로 삼아 LDA로 토픽 모델링하는 코드
"""
import config

import pymysql
from sqlalchemy import create_engine
import pandas as pd
import nltk
from nltk.corpus import stopwords
import gensim
import pyLDAvis
import pyLDAvis.gensim

#초기 세팅시에만 주석 풀 것
#nltk.download('stopwords')


"""
    DB Load
"""
db_connection_str = f"mysql+pymysql://{config.DATABASE_CONFIG['user']}:{config.DATABASE_CONFIG['password']}@{config.DATABASE_CONFIG['host']}/{config.DATABASE_CONFIG['dbname']}"
db_connection = create_engine(db_connection_str)
conn = db_connection.connect()

connection = pymysql.connect(host=config.DATABASE_CONFIG['host'],
                            user=config.DATABASE_CONFIG['user'],
                            password=config.DATABASE_CONFIG['password'],
                            database=config.DATABASE_CONFIG['dbname'])
cursor = connection.cursor()

cursor.execute("SELECT topic_name, content FROM medlineplus WHERE title = 'Summary';")
rows = cursor.fetchall()
rows_df = pd.DataFrame(rows)
# print(rows_df)


"""
    텍스트 전처리
"""
# 특수 문자 제거
rows_df['clean_content'] = rows_df['content'].str.replace("[^\uAC00-\uD7A30-9a-zA-Z\s]", " ", regex=True).replace("[0-9]"," ",regex=True)

#길이가 2이하인 단어는 제거 (길이가 짧은 단어 제거)
rows_df['clean_content'] = rows_df['clean_content'].apply(lambda x: ' '.join([w for w in x.split() if len(w)>2]))

# 전체 단어에 대한 소문자 변환
rows_df['clean_content'] = rows_df['clean_content'].apply(lambda x: x.lower())

# print(rows_df)


"""
    토큰화 & 불용어 처리 & 명사만 추출
"""
# NLTK로부터 불용어를 받아온다.
stop_words = stopwords.words('english')

# my_stop_words = ['months','factor','levels','day','percentage','doctors','goal','people','plan','test','type','result','see','retests','least','year','level','tests','help','care','combination','diseases','institute','measures','problem','area','ways','procedure','diagnosis','collect','medicines','forms','talk','sharpyou','touch','end','process','cause','others','objects','living','pocket','benefits','anyone','tissue','procedures','tries','provider','clog','system','creams','stool','week','changes','disease','dirt','chocolate','evidence','treatments','medication','dirty','myth']
# stop_words = stop_words + my_stop_words

# tokenized_doc = rows_df['clean_content'].apply(lambda x: x.split()) # 토큰화
tokenized_NN_list = list()
for i in rows_df['clean_content']:
    word_tokens = nltk.word_tokenize(i)
    tokens_pos = nltk.pos_tag(word_tokens)
    NN_words = list()
    for word, pos in tokens_pos:
        if 'NN' in pos:
            NN_words.append(word)

    # 불용어를 제거한다.
    filter_NN_words = [item for item in NN_words if item not in stop_words]
    
    tokenized_NN_list.append(filter_NN_words)


"""
    LDA 모델
"""
# 정수 인코딩과 단어집합 만들기
dictionary = gensim.corpora.Dictionary(tokenized_NN_list)
corpus = [dictionary.doc2bow(text) for text in tokenized_NN_list]
# print(corpus[1]) # 수행된 결과에서 두번째 뉴스 출력. 첫번째 문서의 인덱스는 0

# LDA 모델 training
NUM_TOPICS = config.LDA_PARAM_CONFIG['NUM_TOPICS'] # 토픽의 개수
ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics = NUM_TOPICS, id2word=dictionary, passes=15)


"""
    LDA 시각화
"""
vis = pyLDAvis.gensim.prepare(ldamodel, corpus, dictionary)
# html로 저장
# pyLDAvis.save_html(vis, "pyLDAvis.html")


"""
    LDA 모델 확인
"""
## 1번 방법(print_topics)
# topics = ldamodel.print_topics(num_words=100)
# for topic in topics:
#     print(topic)


## 2번 방법(show_topic)
topic_keyword_list = list()
for topic_id in range(NUM_TOPICS):
    topic_word_probs = ldamodel.show_topic(topic_id, config.LDA_PARAM_CONFIG['NUM_KEYWORD']) # 토픽당 키워드 개수
    # print(topic_word_probs)
    for topic_word in topic_word_probs:
        temp_dict = dict()
        temp_dict['topic_id'] = topic_id
        temp_dict['keyword'] = topic_word[0]
        temp_dict['keyword_weight'] = topic_word[1]
        topic_keyword_list.append(temp_dict)
lda_topic_keyword_list_table = pd.DataFrame(topic_keyword_list)
# print(lda_topic_keyword_list_table)

# # LDA keyword list DB 적재
# lda_topic_keyword_list_table.to_sql(name='lda_model_keyword_list',con=db_connection, if_exists='append', index=False)


"""
    결과
"""
temp_list = list()
for index_1, lda_topic_list in enumerate(ldamodel[corpus]):
    # doc = lda_topic_list[0] if ldamodel.per_word_topics else lda_topic_list
    doc = sorted(lda_topic_list, key=lambda x: (x[1]), reverse=True)           
    for index_2, (lda_topic_index, lda_topic_weight) in enumerate(doc):
        temp_dict=dict()
        temp_dict['Disease_Trait'] = rows_df['topic_name'][index_1]
        temp_dict['topic_rank'] = int(index_2) + 1
        temp_dict['topic_id'] = lda_topic_index
        temp_dict['topic_weight'] = lda_topic_weight
        temp_list.append(temp_dict)
lda_topic_table = pd.DataFrame(temp_list)
# print(lda_topic_table)


# # DB 적재
# lda_topic_table.to_sql(name='lda_model',con=db_connection, if_exists='append', index=False)


# # edit table 생성 sql 파일 불러오고 실행
# make_edit_table_sql = open('make_edit_table.sql','r',encoding='utf-8').read()
# cursor.execute(make_edit_table_sql)
# connection.commit()