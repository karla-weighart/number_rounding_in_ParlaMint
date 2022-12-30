import numpy as np
import pandas as pd

from word2number import w2n

from typing import List, Tuple

from helper_methods import inner_dataframe_from_row


def concordance_modified_by(cell: pd.DataFrame, start_index: int, depth: int = 1) -> pd.DataFrame:
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
                [concordance_modified_by(cell, index, depth=depth-1) for index in this_iteration_df.index]
            ).sort_index()
    # TODO: add column for depth_level


def concordance_modifies(cell: pd.DataFrame, start_index: int, depth: int = 1):
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
            [concordance_modifies(cell, index, depth=depth-1) for index in this_iteration_df.index]
        ).sort_index()
    # TODO: add column for depth_level
