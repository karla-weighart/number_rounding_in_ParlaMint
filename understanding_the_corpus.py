from typing import List, Set, Any

import pandas as pd
import numpy as np

from tqdm import tqdm

from dataloader import make_meta_files_list


def files_where_column_not_empty(column_name: str) -> List[str]:
    """returns a list of all -meta.tsv files where the specified column contains something else than NaNs"""
    files_where_column_not_empty_list = []
    for path_list in tqdm(make_meta_files_list()):
        for path in path_list:
            df = pd.read_csv(path, sep='\t')
            if not np.all([pd.isna(s) for s in df[column_name]]):
                files_where_column_not_empty_list.append(path)
    return files_where_column_not_empty_list


def values_in_column(column_name: str) -> Set[str]:
    """

    Parameters
    ----------
    column_name: name of a meta column (choose from COLUMN_NAMES)

    Returns
    -------
    set of all values found in the specified column across all -meta.tsv files
    """
    label_set = set()
    for path_list in tqdm(make_meta_files_list()):
        for path in path_list:
            df = pd.read_csv(path, sep='\t')
            new_labels = set(df[column_name])
            label_set = label_set.union(new_labels)
    return label_set


def files_where_column_has_value(column_name: str, value: Any) -> List[str]:
    """

    Parameters
    ----------
    column_name: name of a meta column (choose from COLUMN_NAMES)
    value: value that might appear in that column

    Returns
    -------
    a list of all -meta.tsv files where the specified column contains the specified value at least once
    """
    files_where_column_has_value_list = []
    for path_list in tqdm(make_meta_files_list()):
        for path in path_list:
            df = pd.read_csv(path, sep='\t')
            if value in set(df[column_name]):
                files_where_column_has_value_list.append(path)
    return files_where_column_has_value_list


def count_words_in_sentence(sentence_df: pd.DataFrame) -> int:
    """

    Parameters
    ----------
    sentence_df: single sentence DataFrame ("inner DataFrame")

    Returns
    -------
    number of words in that sentence
    Does not count punctuation or genitive markers as words even though they have their own lines in the .conllu files.
    """
    filtered_df = sentence_df[(sentence_df['upos'] != 'PUNCT')
                              & (sentence_df['lemma'] != '’s')
                              & (sentence_df['lemma'] != '’')]
    return filtered_df.shape[0]


