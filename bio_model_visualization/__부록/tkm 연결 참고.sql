SELECT a.Disease_Trait, a.topic_id, a.topic_weight, a.keyword_list, a.keyword_weight, b.tkm_list FROM lda_model_edit_table a
LEFT JOIN (SELECT kinds, group_concat(tkm_name SEPARATOR ' | ') AS tkm_list FROM pharmdbk_tkm_relation GROUP BY kinds) b
ON a.Disease_Trait = b.kinds
WHERE a.topic_rank = 1
;