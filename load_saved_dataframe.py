import pandas as pd

from helper_methods import read_inner_dataframe


def load_saved_df(path: str):
    saved_df = pd.read_csv(path, index_col=0)
    saved_df['sentence'] = saved_df['sentence'].map(read_inner_dataframe)
    return saved_df
