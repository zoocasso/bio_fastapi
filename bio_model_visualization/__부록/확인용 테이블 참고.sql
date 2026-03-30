SELECT topic_id,GROUP_CONCAT(keyword SEPARATOR '|') AS keyword FROM lda_model_keyword_list GROUP BY topic_id
union
SELECT topic_id,GROUP_CONCAT(keyword_weight SEPARATOR '|') AS keyword_weight FROM lda_model_keyword_list GROUP BY topic_id
ORDER BY topic_id;