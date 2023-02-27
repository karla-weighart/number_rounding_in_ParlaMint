PATH = "C:\\Users\\karla\\Desktop\\Zula_Data"

# columns that contain valuable information (I used understanding_the_corpus to identify those columns)
# see dataset_info.md for more information about the content of these columns
META_COLUMNS = ['ID',
                'House',
                'Speaker_role',
                'Speaker_type',
                'Speaker_party',
                'Party_status',
                'Speaker_name',
                'Speaker_gender'
                ]
SENTENCE_COLUMNS = ['form',
                    'upos',
                    'head'
                    ]

# result columns that should be parsed if loading from csv
LIT_EVAL_RESULT_COLUMNS = ['sentence',
                           'is_mp', 'mp',
                           'is_female', 'female',
                           'is_upper_house', 'upper_house',
                           'is_chairperson', 'chairperson',
                           'sentence_grouped_nums',
                           'sentence_parsed_num_groups',
                           'NUMs',
                           'roundedness',
                           'num_ancestors',
                           'num_ancestor_set',
                           'num_descendants',
                           'num_descendant_set'
                           ]
