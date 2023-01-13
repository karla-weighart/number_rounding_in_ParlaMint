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
        # start with the first numeral that is not the head of another numeral but has a numeral as its head
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
                    or _sentence.loc[connector_index, 'upos'] is 'CCONJ':

                indexes = {numeral_index, ancestor_index, connector_index}
                parent_indexes = {_sentence.loc[index, 'head'] for index in indexes}
                super_parent_index = list(parent_indexes - indexes)[0]
                _sentence.loc[connector_index, 'head'] = super_parent_index

                for num_index in {numeral_index, ancestor_index}:
                    _sentence.loc[num_index, 'head'] = connector_index
            else:
                raise AttributeError(f"needs manual inspection at line {numeral_index}")

        else:
            raise AttributeError(f"needs manual inspection at line {numeral_index}")

        return _inner_group_nums(_sentence)

    try:
        return _inner_group_nums(sentence).to_dict('list')
    except AttributeError as e:
        return str(e)


def parse_num_group(num_group: list[str, ...]) -> str:
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

        # simplify '50,000' to '50000'
        num = num.replace(',', '')

        # we assume that a '.' is a decimal point and therefore needs to be handled as a float
        if '.' in num:
            try:
                num_value = float(num)
            except ValueError:
                return "needs manual inspection"
        else:

            # try to naturally convert the string to an integer (maybe need to remove spaces first)
            try:
                num_value = int(num.replace(' ', ''))
            except ValueError:
                try:
                    num_value = w2n.word_to_num(num)
                except ValueError:
                    return "needs manual inspection"
        value *= num_value

    # if the for loop terminated normally, use the last num that was evaluated (which persists from the for-loop)
    # to determine whether the result should be represented as float or int
    else:
        if type(num_value) == int and int(value) == value:
            value = int(value)

    return str(value)


def parse_num_groups(cell_with_grouped_nums: Union[dict, str]) -> Union[dict, str]:

    # some cells cannot be parsed by group_nums and therefore contain a string with an error message
    if type(cell_with_grouped_nums) == str:
        return "needs manual inspection"

    # implicit else by return
    sentence = pd.DataFrame(cell_with_grouped_nums)

    sentence.loc[sentence['upos'] == 'NUM', 'form'] = sentence[sentence['upos'] == 'NUM']['form'].map(parse_num_group)

    return sentence.to_dict('list')
