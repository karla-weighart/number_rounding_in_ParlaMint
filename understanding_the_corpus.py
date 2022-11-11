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


def check_subcorpora():
    """checks if any meta file contains anything but 'Reference' or 'COVID' in the 'Subcorpus' column
    spoiler alert: NOPE."""
    files_where_other_subcorpus = []
    for path_list in tqdm(make_meta_files_dict().values()):
        for path in tqdm(path_list):
            df = pd.read_csv(path, sep='\t')
            mask1 = df['Subcorpus'] != 'Reference'
            if not df[mask1]['ID'].shape == (0,):
                mask2 = df[mask1]['Subcorpus'] != 'COVID'
                if not df[mask1][mask2]['ID'].shape == (0,):
                    files_where_other_subcorpus.append(path)
    return files_where_other_subcorpus
