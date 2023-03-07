from typing import Union

import numpy as np
import pandas as pd
from word2number import w2n

from concordance import concordance_ancestors


def group_nums(cell: dict) -> dict:
    """

    Parameters
    ----------
    cell: sentence df as dict

    Returns
    -------
    cell with
    - consecutive numerals that modify each other merged into on list of strings
      (which can then be interpreted with parse_num_group())
    - 'three' 'to' 'four' and similar get restructured so the numerals both have the connector as their new heads
      and the connector has whatever the head of one of the number was as its new head

    in other cases: error message AS STRING (so it doesn't stop the running program)
    """

    sentence = pd.DataFrame(cell)
    sentence.loc[sentence['upos'] == 'NUM', 'form'] = \
        sentence.loc[sentence['upos'] == 'NUM', 'form'].map(lambda x: [x])

    def _inner_group_nums(_sentence: pd.DataFrame) -> Union[pd.DataFrame, str]:

        numerals_df = _sentence.loc[_sentence['upos'] == 'NUM']

        # if no numbers refer to each other, nothing needs to be done anymore
        if (set(numerals_df.index) & set(numerals_df['head'])) == set():
            return _sentence

        # else (implicit else via return statement): resolve all cases where one numeral refers to another
        # start with the first numeral that is not the head of another numeral but has a numeral as its head (=ancestor)
        # in other words: one that is a leaf of a tree of numerals
        numeral_index = [index for index in numerals_df.index
                         if index not in set(numerals_df['head'])
                         and _sentence.loc[index, 'head'] in numerals_df.index
                         ][0]

        ancestor_row = concordance_ancestors(_sentence, numeral_index).iloc[0]
        ancestor_index = ancestor_row.name

        # in most cases, two numerals referring to each other are actually part of the same number
        # e.g. "200 thousand" = 200 000
        # if this is the case, concatenate to one number and adjust the rest of the dataframe
        if ancestor_index == numeral_index + 1:
            _sentence.loc[numeral_index, 'form'].extend(ancestor_row['form'])
            _sentence.loc[numeral_index, 'head'] = ancestor_row['head']
            _sentence.drop(index=(numeral_index + 1), inplace=True)
            _sentence.loc[_sentence['head'] > numeral_index, 'head'] -= 1
            _sentence.reset_index(drop=True, inplace=True)

        # sometimes, one number refers to another but there is an "and", "or", "to", "-" between the two
        # this might happen either with the other number 2 ahead or 2 behind
        # in these cases, make the conjunction the parent of both numbers
        # the conjunction then gets the parent that one of the numbers initially had
        elif abs(ancestor_index - numeral_index) == 2:
            connector_index = (numeral_index + ancestor_index) // 2

            if _sentence.loc[connector_index, 'form'] in {'to', '-'} \
                    or _sentence.loc[connector_index, 'upos'] == 'CCONJ':

                indexes = {numeral_index, ancestor_index, connector_index}
                parent_indexes = {_sentence.loc[index, 'head'] for index in indexes}
                super_parent_index = list(parent_indexes - indexes)[0]
                _sentence.loc[connector_index, 'head'] = super_parent_index

                for num_index in {numeral_index, ancestor_index}:
                    _sentence.loc[num_index, 'head'] = connector_index
            else:
                raise AttributeError(f"needs manual inspection (group nums failed at line {numeral_index})")

        else:
            raise AttributeError(f"needs manual inspection (group nums failed at line {numeral_index})")

        return _inner_group_nums(_sentence)

    return _inner_group_nums(sentence).to_dict('list')


def parse_num_group(num_group: list[str, ...]) -> tuple[str, Union[int, float]]:
    """

    Parameters
    ----------
    num_group: list of strings that represent numbers
        either as English words ('five') or as digits ('500', '3.14')

    Returns
    -------
    numerical value of what this string would be read as by a human as str
    float representation (which would not suffice on its own because float(4.000) = float(4)) #TODO
    """

    num_0 = num_group[0]

    # we assume that a '.' is a decimal point and therefore needs to be handled as a float
    if '.' in num_0:
        try:
            # simplify '50,000' or '50 000' to '50000' with replace()
            value = float(num_0.replace(',', '').replace(' ', ''))
            num_0_value = num_0
        except ValueError:
            raise AttributeError(f"needs manual inspection (parse_num_groups failed with num_0 float-like: {num_0})")
    else:
        try:
            # simplify '50,000' or '50 000' to '50000' with replace()
            value = int(num_0.replace(',', '').replace(' ', ''))
            num_0_value = str(value)
        except ValueError:
            try:
                value = w2n.word_to_num(num_0)
                num_0_value = str(value)
            except ValueError:
                raise AttributeError(f"needs manual inspection (parse_num_groups failed with num_0 int-like: {num_0})")

    if len(num_group) == 1:
        return num_0_value, value

    # implicit else: only reached if len(num_group) > 1
    # we assume that subsequent numerals are meant in a multiplicative way, i.e. 500 million means 500 * 1000000
    for num in num_group[1:]:
        try:
            num_value = w2n.word_to_num(num)
        except ValueError as e:
            raise AttributeError(f"needs manual inspection (parse_num_groups failed with w2n: ({num}, {e}))")

        if num_value <= 0:
            raise AttributeError(f"needs manual inspection (parse_num_group failed with negative number: {num_value})")

        elif np.log10(num_value) != int(np.log10(num_value)):
            raise AttributeError(f"needs manual inspection (parse_num_group failed, not power of ten: {num_value})")

        value *= num_value

    # convert to int in case num_0 was float and multiplication therefore made everything a float
    if value != int(value):
        raise AttributeError(f"needs manual inspection (parse_num_group float/int problem: {value})")

    return str(int(value)), value


def parse_num_groups(cell_with_grouped_nums: Union[dict, str]) -> dict:
    """

    Parameters
    ----------
    cell_with_grouped_nums: output of group_nums() (sentence df as dict)

    Returns
    -------
    applies parse_num_group to each NUM in cell, returns sentence df as dict
    """

    sentence = pd.DataFrame(cell_with_grouped_nums)

    sentence.loc[sentence['upos'] == 'NUM', 'form'] = sentence[sentence['upos'] == 'NUM']['form'].map(parse_num_group)

    return sentence.to_dict('list')


def num_list(cell: dict) -> list[tuple[int, tuple[str, Union[float, int]]]]:
    """

    Parameters
    ----------
    cell: sentence df as dict

    Returns
    -------
    list containing
        one tuple per 'NUM' containing
            int: index of 'NUM'
            tuple:
                str: number as string (with all 0s etc)
                Union[float, int]: number in canonical float/int representation
    """

    sentence = pd.DataFrame(cell)
    return list(zip(sentence[sentence['upos'] == 'NUM'].index, sentence[sentence['upos'] == 'NUM']['form']))


def find_roundedness(num_as_str: str) -> tuple[bool, int, int, Union[int, str]]:
    """

    Parameters
    ----------
    num_as_str: string representation of a number

    Returns
    -------
    tuple containing:
    bool: whether the number is a 'float-like' (i.e. whether the given number contains a decimal point)
    int: n_proper_digits (number of 'proper' digits, i.e. everything that is not a leading/trailing zero)
    int: n_zeroes (for float-likes: n_leading_zeroes (before AND after decimal point), for int-likes: n_trailing_zeroes)
    int: n_decimals (for floats only, ints: "n/a" instead)
    """

    if '.' in num_as_str:

        n_pre_decimals = num_as_str.lstrip('0').index('.')
        n_decimals = len(num_as_str.lstrip('0')) - n_pre_decimals - 1

        # remove decimal point
        num_as_str = num_as_str.replace('.', '')

        n_proper_digits = len(num_as_str.lstrip('0'))
        n_leading_zeroes = len(num_as_str) - n_proper_digits

        return True, n_proper_digits, n_leading_zeroes, n_decimals

    # get rid of numbers that start with 0 but are not float-like (will be dropped by drop_na later on)
    elif num_as_str[0] == '0':
        return np.nan, np.nan, np.nan, np.nan

    n_proper_digits = len(num_as_str.rstrip('0'))
    n_trailing_zeroes = len(num_as_str) - n_proper_digits
    return False, n_proper_digits, n_trailing_zeroes, "n/a"


def find_uncertainty(row: pd.Series) -> tuple[float, float]:
    """

    Parameters
    ----------
    row: single number row from the df. find_roundedness() has to be applied before this!

    Returns
    -------
    tuple containing:
        float: absolute uncertainty of number
        float: relative uncertainty of number

    """
    if row['is_float-like']:
        absolute_uncertainty = 10 ** (-row['n_decimals'])
    else:
        absolute_uncertainty = 10 ** row['n_zeroes']

    if row['num_value'] == 0:
        relative_uncertainty = np.nan
    else:
        relative_uncertainty = abs(absolute_uncertainty / row['num_value'])

    return absolute_uncertainty, relative_uncertainty


def is_about_money(row: pd.Series, before_length: int = 1, after_length: int = 1) -> bool:
    # TODO: possible extension: def what_is_counted( ... ) -> str:
    #  which predefined category the counted noun comes from (if any of them)
    """

    Parameters
    ----------
    row: row corresponding to a single number from the large dataframe.
        df.explode('NUMs') etc. has to be applied before this!
    before_length: how many words before the number should be tested
    after_length: how many words after the number should be tested

    Returns
    -------
    bool: whether the number specifies an amount of money
    """
    sentence_df = pd.DataFrame(row['sentence_parsed_num_groups'])
    number_index = row['num_index']

    money_words = {'£', 'pound', 'pounds', '€', 'euro', 'euros', 'penny', 'pence', 'p'}

    start_index = max(0, number_index - before_length)
    stop_index = min(number_index + after_length + 1, sentence_df.shape[0])

    test_indices = range(start_index, stop_index)
    for index in test_indices:
        if sentence_df['form'][index] in money_words:
            return True
    return False
