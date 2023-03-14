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

# forms that will be searched for by is_about_money
MONEY_WORDS = {'£', 'pound', 'pounds', 'penny', 'pence', 'p',
               '€', 'euro', 'euros', 'cent', 'cents',
               '$', 'dollar', 'dollars', 'USD', 'US-dollar', 'US-dollars'}

# approximators that will be searched for by has_approximators
APPROXIMATORS = {('before', 'neighborhood'): (('around',),
                                              ('about',),
                                              ('appr',), ('appr.',), ('approx',), ('approx.',), ('approximately',),
                                              ('ca',), ('ca.',), ('circa',),
                                              ('on', 'the', 'order', 'of'),
                                              ('roughly',),
                                              ('round',),
                                              ('roundabout',),
                                              ('something', 'like')
                                              ),
                 ('after', 'plain'): (('or', 'so'),
                                      ),
                 ('before', 'upper_limit'): (('almost',),
                                             ('at', 'most'),
                                             ('below',),
                                             ('close', 'to'),
                                             ('nearly',),
                                             ('less', 'than'),
                                             ('lower', 'than'),
                                             ('under',),
                                             ('up', 'to'),
                                             ),
                 ('after', 'upper_limit'): (('and', 'below'),
                                            ('and', 'less'),
                                            ('or', 'below'),
                                            ('or', 'less')
                                            ),
                 ('before', 'lower_limit'): (('above',),
                                             ('at', 'least'),
                                             ('higher', 'than'),
                                             ('more', 'than'),
                                             ('over',)
                                             ),
                 ('after', 'lower_limit'): (('and', 'above'),
                                            ('and', 'higher'),
                                            ('and', 'more'),
                                            ('or', 'above'),
                                            ('or', 'higher'),
                                            ('or', 'more')
                                            )
                 }
