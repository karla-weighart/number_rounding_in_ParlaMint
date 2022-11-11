import pandas as pd
import numpy as np

from tqdm import tqdm

from dataloader import make_meta_files_dict


def files_where_column_not_empty(column_name):
    """returns a list of all -meta.tsv files where the specified column contains something else than NaNs"""
    files_where_column_not_empty_list = []
    for path_list in tqdm(make_meta_files_dict().values()):
        for path in path_list:
            df = pd.read_csv(path, sep='\t')
            if not np.all([pd.isna(s) for s in df[column_name]]):
                files_where_column_not_empty_list.append(path)
    return files_where_column_not_empty_list


def values_in_column(column_name):
    """returns a set of all values found in the specified column across all -meta.tsv files"""
    label_set = set()
    for path_list in tqdm(make_meta_files_dict().values()):
        for path in path_list:
            df = pd.read_csv(path, sep='\t')
            new_labels = set(df[column_name])
            label_set = label_set.union(new_labels)
    return label_set


def files_where_column_has_value(column_name, value):
    """returns a list of all -meta.tsv files where the specified column contains the specified value at least once"""
    files_where_column_has_value_list = []
    for path_list in tqdm(make_meta_files_dict().values()):
        for path in path_list:
            df = pd.read_csv(path, sep='\t')
            if value in set(df[column_name]):
                files_where_column_has_value_list.append(path)
    return files_where_column_has_value_list
