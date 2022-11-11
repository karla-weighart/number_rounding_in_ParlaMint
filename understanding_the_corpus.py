import pandas as pd
import numpy as np

from tqdm import tqdm

from dataloader import make_meta_files_dict


def check_if_column_empty(column_name):
    files_where_column_empty = []
    for path_list in tqdm(make_meta_files_dict().values()):
        for path in path_list:
            df = pd.read_csv(path, sep='\t')
            if not np.all([pd.isna(s) for s in df['Agenda']]):
                files_where_column_empty.append(path)
    return files_where_column_empty
