CREATE TABLE lda_model_edit_table
SELECT a.*, b.keyword_list, b.keyword_weight
FROM lda_model a
LEFT JOIN (SELECT topic_id, group_concat(keyword SEPARATOR ' | ') AS keyword_list, GROUP_CONCAT(keyword_weight SEPARATOR ' | ') AS keyword_weight 
				FROM lda_model_keyword_list a 
				GROUP BY topic_id) b
ON a.topic_id = b.topic_id
;