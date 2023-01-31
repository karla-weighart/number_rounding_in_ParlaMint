from typing import Union

import pandas as pd


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
    sentence_df = pd.DataFrame(row['sentence_parsed_num_groups'])

    descendants_df = \
        concordance_descendants(sentence_df, row['NUMs'][0], depth=depth)

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


def concordance_ancestors_on_row(row: pd.Series, depth: int = 1) -> dict:
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
    sentence_df = pd.DataFrame(row['sentence_parsed_num_groups'])

    return concordance_ancestors(sentence_df, row['NUMs'][0], depth=depth).to_dict('list')


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
        if "no descendants" in cell:
            return "no descandants"

    return set(cell['form'])
