import pandas as pd
import numpy as np

from typing import Union


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


def contains_num(cell: dict) -> bool:
    """

    Parameters
    ----------
    cell: sentence df as dict

    Returns
    -------
    whether the sentence contains any 'NUM'
    """

    # contains_digit = np.any([str(x) in '.'.join(cell['form']) for x in range(10)])
    # as later methods only work on 'NUM's, this yields too many false positives
    contains_numeral = 'NUM' in cell['upos']
    return contains_numeral  # or contains_digit


def num_list(cell: dict) -> Union[list, str]:
    """

    Parameters
    ----------
    cell: sentence df as dict

    Returns
    -------
    list of the forms of all 'NUM's in that sentence (which might already have been grouped + parsed before)
    """

    # some cells already are "needs manual inspection". propagate that
    if type(cell) == str:
        return "needs manual inspection"

    sentence = pd.DataFrame(cell)
    return list(zip(sentence[sentence['upos'] == 'NUM'].index, sentence[sentence['upos'] == 'NUM']['form']))
