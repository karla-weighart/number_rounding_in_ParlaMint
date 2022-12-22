import numpy as np
import pandas as pd

import conllu

from typing import List, Tuple

from helper_methods import read_inner_dataframe


def count_words_in_sentence(row: pd.Series) -> int:
    """

    Parameters
    ----------
    row: row of outer dataframe containing info for 1 sentence

    Returns
    -------
    number of words in that sentence
    Does not count punctuation or genitive markers as words even though they have their own lines in the .conllu files.
    """
    sentence_df = read_inner_dataframe(row)

    filtered_df = sentence_df[(sentence_df['upos'] != 'PUNCT')
                              & (sentence_df['form'] != '’s')
                              & (sentence_df['form'] != '’')]
    return filtered_df.shape[0]


def find_pattern_in_sentence(pattern: List[Tuple[str]], row: pd.Series) -> List[pd.DataFrame]:
    """

    Parameters
    ----------
    pattern: [(column, value), ...] that should be matched. the tuples have to be consecutive.
    row: row of outer dataframe containing info for 1 sentence

    Returns
    -------
    List of dataframes, each dataframe contains the concrete forms that matched the pattern
    """
    search_results = []
    sentence_df = read_inner_dataframe(row)

    for i in range(sentence_df.shape[0] - len(pattern) + 1):
        if np.alltrue([sentence_df.iloc[i+p][pattern[p][0]] == pattern[p][1] for p in range(len(pattern))]):
            search_results.append(sentence_df.iloc[i:i+len(pattern)]['form'])
    return search_results
