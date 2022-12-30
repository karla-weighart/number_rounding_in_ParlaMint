import pandas as pd

from ast import literal_eval

from helper_methods import inner_dataframe_from_row


def load_saved_df(path: str):
    saved_df = pd.read_csv(path, index_col=0)
    saved_df['sentence'] = saved_df['sentence'].map(literal_eval)
    return saved_df
