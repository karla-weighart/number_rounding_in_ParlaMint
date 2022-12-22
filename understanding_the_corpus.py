import conllu

import pandas as pd


def count_words_in_sentence(sentence: conllu.models.TokenList) -> int:
    """

    Parameters
    ----------
    sentence: TokenList from the conllu parser

    Returns
    -------
    number of words in that sentence
    Does not count punctuation or genitive markers as words even though they have their own lines in the .conllu files.
    """
    sentence_df = pd.DataFrame(sentence)

    filtered_df = sentence_df[(sentence_df['upos'] != 'PUNCT')
                              & (sentence_df['lemma'] != '’s')
                              & (sentence_df['lemma'] != '’')]
    return filtered_df.shape[0]


