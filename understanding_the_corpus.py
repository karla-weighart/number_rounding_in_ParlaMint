import pandas as pd
import numpy as np

from tqdm import tqdm

from dataloader import make_meta_files_dict


def check_if_column_empty(column_name):
    """returns a list of all -meta.tsv files where the specified column contains something else than NaNs"""
    files_where_column_empty = []
    for path_list in tqdm(make_meta_files_dict().values()):
        for path in path_list:
            df = pd.read_csv(path, sep='\t')
            if not np.all([pd.isna(s) for s in df['Agenda']]):
                files_where_column_empty.append(path)
    return files_where_column_empty


def values_in_column(column_name):
    """returns a list of all values found in the specified column across all -meta.tsv files"""
    label_list = []

    for path_list in tqdm(make_meta_files_dict().values()):
        for path in path_list:
            df = pd.read_csv(path, sep='\t')
            for label in label_list:
                df = df[df[column_name] != label]
                if df.shape[0] == 0:
                    break
            else:  # the following will only be executed if the for-loop did not break
                new_labels = set(df[column_name])
                label_list.extend(new_labels)
    return label_list
