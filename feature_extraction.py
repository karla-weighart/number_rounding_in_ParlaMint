import pandas as pd
import numpy as np

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

    return pd.concat(
        [this_iteration_df] +
        [concordance_descendants(cell, index, depth=depth - 1) for index in this_iteration_df.index]
    ).sort_index()
    # TODO: add column for depth_level


def concordance_descendants_on_row(row: pd.Series, depth: int = 1) -> Union[dict, str]:
    # TODO: test for depth>1
    """

    Parameters
    ----------
    row: row of the outer DataFrame
        where 'sentence_parsed_num_groups' already exist and 'NUMs' has already been exploded
    depth: how far down the ancestry tree will be searched

    Returns
    -------
    propagates "needs manual inspection"
    else: returns ancestry of the NUM of this row

    """
    sentence = row['sentence_parsed_num_groups']

    if type(sentence) == str:
        return "needs manual inspection (propagated)"

    descendants_df = \
        concordance_descendants(pd.DataFrame(row['sentence_parsed_num_groups']), row['NUMs'][0], depth=depth)

    if descendants_df.shape[0] == 0:
        return "no descendants"

    return descendants_df.to_dict('list')


def concordance_ancestors(cell: pd.DataFrame, start_index: int, depth: int = 1) -> pd.DataFrame:
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

    return pd.concat(
        [this_iteration_df] +
        [concordance_ancestors(cell, index, depth=depth - 1) for index in this_iteration_df.index]
    ).sort_index()
    # TODO: add column for depth_level


def concordance_ancestors_on_row(row: pd.Series, depth: int = 1) -> Union[dict, str]:
    # TODO: test for depth>1
    """

    Parameters
    ----------
    row: row of the outer DataFrame
        where 'sentence_parsed_num_groups' already exist and 'NUMs' has already been exploded
    depth: how far up the ancestry tree will be searched

    Returns
    -------
    propagates "needs manual inspection"
    else: returns ancestry of the NUM of this row
    """
    sentence = row['sentence_parsed_num_groups']

    if type(sentence) == str:
        return "needs manual inspection (propagated)"

    return concordance_ancestors(pd.DataFrame(row['sentence_parsed_num_groups']), row['NUMs'][0], depth=depth)\
        .to_dict('list')


def ancestry_set(cell: Union[dict, str]) -> Union[set, str]:
    """

    Parameters
    ----------
    cell: cell containing result from concordance_descendants_on_row or concordance_ancestors_on_row

    Returns
    -------
    propagates "needs manual inspection" / "no descendants"
    yields set of all descendants/ancestors
    """

    if type(cell) == str:
        if "manual inspection" in cell:
            return "needs manual inspection (propagated)"
        if "no descendants" in cell:
            return "no descandants"

    return set(cell['form'])


def group_nums(cell: dict) -> Union[dict, str]:
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
    sentence.loc[sentence['upos'] == 'NUM', 'form'] =\
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

    try:
        return _inner_group_nums(sentence).to_dict('list')
    except AttributeError as e:
        return str(e)


def parse_num_group(num_group: list[str, ...]) -> Union[tuple[str, float], str]:
    """

    Parameters
    ----------
    num_group: list of strings that represent numbers
        either as English words ('five') or as digits ('500', '3.14')

    Returns
    -------
    numerical value of what this string would be read as by a human as str
    float representation (which would not suffice on its own because float(4.000) = float(4))
    """

    num_0 = num_group[0]

    # we assume that a '.' is a decimal point and therefore needs to be handled as a float
    if '.' in num_0:
        try:
            # simplify '50,000' or '50 000' to '50000' with replace()
            value = float(num_0.replace(',', '').replace(' ', ''))
            num_0_value = num_0
        except ValueError:
            return f"needs manual inspection (parse_num_groups failed with num_0 float-like: {num_0})"
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
                return f"needs manual inspection (parse_num_groups failed with num_0 int-like: {num_0})"

    if len(num_group) == 1:
        return num_0_value, value

    # implicit else: only reached if len(num_group) > 1
    # we assume that subsequent numerals are meant in a multiplicative way, i.e. 500 million means 500 * 1000000
    # (for exceptions see the else-clause of for-loop)
    for num in num_group[1:]:
        try:
            num_value = w2n.word_to_num(num)
        except ValueError as e:
            return f"needs manual inspection (parse_num_groups failed with w2n: ({num_value}, {e}))"

        if num_value <= 0:
            return f"needs manual inspection (parse_num_group failed with negative number: {num_value})"

        elif np.log10(num_value) != int(np.log10(num_value)):
            return f"needs manual inspection (parse_num_group failed, not power of ten: {num_value})"

        value *= num_value

    # convert to int in case num_0 was float and multiplication therefore made everything a float
    if value != int(value):
        return f"needs manual inspection (parse_num_group float/int problem: {value})"
    return str(int(value)), value


def parse_num_groups(cell_with_grouped_nums: Union[dict, str]) -> Union[dict, str]:
    """

    Parameters
    ----------
    cell_with_grouped_nums: output of group_nums() (sentence df as dict)

    Returns
    -------
    applies parse_num_group to each NUM in cell, returns sentence df as dict
    """

    # some cells already are "needs manual inspection". propagate that
    if type(cell_with_grouped_nums) == str:
        return "needs manual inspection (propagated)"

    # implicit else by return
    sentence = pd.DataFrame(cell_with_grouped_nums)

    sentence.loc[sentence['upos'] == 'NUM', 'form'] = sentence[sentence['upos'] == 'NUM']['form'].map(parse_num_group)

    return sentence.to_dict('list')


def num_list(cell: dict) -> Union[list[tuple[int, tuple[str, int]]], str]:
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
        return "needs manual inspection (propagated)"

    sentence = pd.DataFrame(cell)
    return list(zip(sentence[sentence['upos'] == 'NUM'].index, sentence[sentence['upos'] == 'NUM']['form']))


def find_roundedness(num: Union[tuple[str, float], str]) -> Union[tuple[str, int, int], str]:
    """

    Parameters
    ----------
    num: tuple(index of number to be investigated, tuple(number as string, number as float))
    (example: (7, (304000.00, 304000.0))

    Returns
    -------
    tuple containing:
    str: 'float-like' or 'int-like': whether the given number contains a decimal point and is therefore float-like or not
    for float-likes:
        number of leading zeroes
        number of proper digits
    for int-likes:
        number of proper digits
        number of trailing zeroes
    number of 'proper' digits, i.e. everything that is not a trailing zero
    (in example: 3, because '304' are proper digits)

    number of trailing zeroes
    (in example: 4, because '000.0' are trailing zeroes)
    """
    # some cells already are "needs manual inspection". propagate that
    if type(num) == str and "manual inspection" in num:
        return "needs manual inspection (propagated)"

    num_as_str = num[1][0]

    if '.' in num_as_str:
        # remove decimal point
        num_as_str = num_as_str.replace('.', '')

        proper_digits = len(num_as_str.lstrip('0'))
        leading_zeroes = len(num_as_str) - proper_digits
        return 'float-like', leading_zeroes, proper_digits

    if num_as_str[0] == '0':
        return f"needs manual inspection (find_roundedness found leading zero: {num})"

    proper_digits = len(num_as_str.rstrip('0'))
    trailing_zeroes = len(num_as_str) - proper_digits
    return 'int-like', proper_digits, trailing_zeroes
