import pandas as pd
import numpy as np

from typing import Any, Tuple


def is_enum(cell: dict) -> bool:
    sentence_df = pd.DataFrame(cell)
    return sentence_df.shape[0] == 2 and \
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


def try_apply(function: callable, arg: Any, error_message: bool = False):
    """

    Parameters
    ----------
    function: callable
    arg: arguments to pass to function
    error_message:
        True -> AttributeError will be returned as string
        False -> AttributeError will be caught, np.nan will be returned

    Returns
    -------
    tries to apply function to arg and return the result
    if this fails, returns either an error message as a string or np.nan depending on parameter error_message
    """
    try:
        return function(arg)
    except Exception as e:
        if error_message:
            return str(e)
        return np.nan


def drop_na_with_count(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """

    Parameters
    ----------
    df: DataFrame

    Returns
    -------
    drops all rows containing nans from the dataframe
    prints the number of rows that were dropped
    returns the cleaned dataframe
    """
    new_df = df.dropna().copy()
    n_rows_dropped = df.shape[0] - new_df.shape[0]
    return new_df, n_rows_dropped
