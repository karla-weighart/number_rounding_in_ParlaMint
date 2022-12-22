import numpy as np
import pandas as pd

import conllu

from typing import List, Tuple


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


def find_pattern_in_sentence(pattern: List[Tuple[str]], sentence: conllu.models.TokenList) -> List[pd.DataFrame]:
    """
    Parameters
    ----------
    pattern: [(column, value), ...] that should be matched. the tuples have to be consecutive.
    sentence: TokenList from the conllu parser

    Returns
    -------
    List of dataframes, each dataframe contains the concrete forms that matched the pattern
    """
    search_results = []
    sentence_df = pd.DataFrame(sentence)

    for i in range(sentence_df.shape[0] - len(pattern) + 1):
        if np.alltrue([sentence_df.iloc[i+p][pattern[p][0]] == pattern[p][1] for p in range(len(pattern))]):
            search_results.append(sentence_df.iloc[i:i+len(pattern)]['form'])
    return search_results

