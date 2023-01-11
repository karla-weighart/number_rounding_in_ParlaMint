import pandas as pd

from word2number import w2n

from typing import Union


def concordance_descendants(cell: pd.DataFrame, start_index: int, depth: int = 1) -> pd.DataFrame:
    """

    Parameters
    ----------
    cell: inner dataframe
    start_index: index of the word whose modifiers will be returned
    depth: how often the function will be called recursively, i.e. how far down in the syntax tree we move

    Returns
    -------
    dataframe containing only the lines that have the word with the given index as their parent or higher-level ancestor
    """
    this_iteration_df = cell[cell['head'] == start_index]

    if depth == 1:
        return this_iteration_df
    else:
        return pd.concat(
            [this_iteration_df] +
            [concordance_descendants(cell, index, depth=depth - 1) for index in this_iteration_df.index]
        ).sort_index()
    # TODO: add column for depth_level


def concordance_ancestors(cell: pd.DataFrame, start_index: int, depth: int = 1):
    """

    Parameters
    ----------
    cell: inner dataframe
    start_index: index of the word that modifies the words that will be returned
    depth: how often the function will be called recursively, i.e. how far up in the syntax tree we move

    Returns
    -------
    dataframe containing only the lines that have the word with the given index as their child or higher-level descendant
    """
    this_iteration_df = pd.DataFrame(cell.iloc[cell.iloc[start_index]['head']]).T
    if depth == 1:
        return this_iteration_df
    else:
        return pd.concat(
            [this_iteration_df] +
            [concordance_ancestors(cell, index, depth=depth - 1) for index in this_iteration_df.index]
        ).sort_index()
    # TODO: add column for depth_level


def find_roundedness(num: Union[int, float]) -> tuple[int, int]:
    """

    Parameters
    ----------
    num: number to be investigated
    (example: 304000.0)

    Returns
    -------
    number of 'proper' digits, i.e. everything that is not a trailing zero
    (in example: 3, because '304' are proper digits)

    number of trailing zeroes
    (in example: 4, because '000.0' are trailing zeroes)
    """
    num_str = str(num).lstrip('0').replace('.', '')
    proper_digits = len(num_str.rstrip('0'))
    trailing_zeroes = len(num_str) - proper_digits
    return proper_digits, trailing_zeroes


def group_nums(cell: dict) -> Union[dict, str]:
    # TODO: test this more!
    # TODO: (maybe)
    #  instead of ['roughly', ['7', 'hundred', 'million']]
    #  return ['roughly', ('numgroup', ['7', 'hundred', 'million'])]
    #  and for cconj: ['between', ('cconj', ['7', 'and', '8'])]
    #  and for '-' or 'to': ['from', ('range', ['7', 'to', '8'])]
    """

    Parameters
    ----------
    cell: sentence df as dict

    Returns
    -------
    cell with consecutive numerals that modify each other merged into on list of strings
    (which can then be interpreted with parse_num_group())

    if non-consecutive numerals modify each other: "needs manual inspection"
    """
    sentence = pd.DataFrame(cell)
    sentence.loc[sentence['upos'] == 'NUM', 'form'] = sentence.loc[sentence['upos'] == 'NUM', 'form'].map(lambda x: [x])

    def _inner_group_nums(_sentence: pd.DataFrame) -> Union[pd.DataFrame, str]:
        numerals_df = _sentence.loc[_sentence['upos'] == 'NUM']

        # if no numbers modify each other, nothing needs to be done
        if (set(numerals_df.index) & set(numerals_df['head'])) == set():
            return _sentence

        # in all other cases, go into recursion:
        for numeral_index in numerals_df.index:
            if _sentence.iloc[numeral_index]['head'] in numerals_df.index:
                ancestor_row = concordance_ancestors(_sentence, numeral_index).iloc[0]

                # in most cases, two numerals referring to each other are actually part of the same number
                # e.g. "200 thousand" = 200 000
                # if this is the case, concatenate to one number and adjust the rest of the dataframe
                if ancestor_row.name == numeral_index + 1:
                    _sentence.iloc[numeral_index]['form'].extend(ancestor_row['form'])
                    _sentence.iloc[numeral_index] = pd.Series([_sentence.iloc[numeral_index]['form'],
                                                               'NUM',
                                                               ancestor_row['head']])
                    _sentence.drop(index=numeral_index + 1, inplace=True)
                    _sentence.loc[_sentence['head'] > numeral_index, 'head'] -= 1
                    _sentence.reset_index(drop=True, inplace=True)

                # sometimes, one number refers to another but there is an "and", "or", "to", "-" between the two
                # in this case, make both numbers refer to the conjunction instead
                elif ancestor_row.name == numeral_index + 2 \
                        and \
                        _sentence.iloc[numeral_index + 1]['upos'] in {'CCONJ', 'ADP', 'SYM'}:
                    return "needs manual inspection" # TODO: make NUMs refer to the conjunction to disentangle
                else:
                    return "needs manual inspection"

        _sentence = _inner_group_nums(_sentence)
        return _sentence

    try:
        return _inner_group_nums(sentence).to_dict('list')
    except AttributeError:
        return "needs manual inspection"


def parse_num_group(num_group: list[str, ...]) -> Union[float, int, str]:
    """

    Parameters
    ----------
    num_group: list of strings that represent numbers
        either as English words ('five') or as digits ('500', '3.14')

    Returns
    -------
    numerical value of what this string would be read as by a human
    """
    # we assume that subsequent numerals are meant in a multiplicative way, i.e. 500 million means 500 * 1000000
    # TODO: CAVEAT: for something like ['fifty' 'five'], this will yield 250 instead of 55. let's hope we don't have
    #  this in the dataset
    # therefore we initialize with the neutral element of multiplication
    value = 1

    for num in num_group:
        if '.' in num:
            try:
                num_value = float(num)
            except ValueError:
                return "needs manual inspection"
        else:
            try:
                num_value = int(num)
            except ValueError:
                try:
                    num_value = w2n.word_to_num(num)
                except ValueError:
                    return "needs manual inspection"
        value *= num_value
    return value
