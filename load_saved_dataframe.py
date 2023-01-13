import pandas as pd

from ast import literal_eval


def load_saved_df(path: str):
    saved_df = pd.read_csv(path, index_col=0)
    saved_df['sentence'] = saved_df['sentence'].swifter.apply(literal_eval)
    return saved_df
