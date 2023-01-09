import pandas as pd
import numpy as np


def is_enum(cell: dict) -> bool:
    sentence_df = pd.DataFrame(cell)
    return sentence_df.shape[0] == 2 and\
        (sentence_df['upos'].iloc[0], sentence_df['upos'].iloc[1]) in {('X', 'PUNCT'), ('NUM', 'PUNCT')}


def count_words(cell: dict) -> int:
    """

    Parameters
    ----------
    cell: single sentence cell of outer DataFrame in dict format

    Returns
    -------
    number of words in that sentence
    Does not count punctuation or genitive markers as words even though they have their own lines in the .conllu files.
    """
    sentence_df = pd.DataFrame(cell)

    filtered_df = sentence_df[(sentence_df['upos'] != 'PUNCT')
                              & (sentence_df['form'] != '’s')
                              & (sentence_df['form'] != '’')]
    return filtered_df.shape[0]


def contains_num(cell: dict):
    contains_digit = np.any([str(x) in '.'.join(cell['form']) for x in range(10)])
    contains_numeral = 'NUM' in cell['upos']  # or 'X' in cell['upos']
    return contains_digit or contains_numeral
