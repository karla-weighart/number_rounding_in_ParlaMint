import pandas as pd

from ast import literal_eval
from environment_constants import LIT_EVAL_RESULT_COLUMNS


def load_saved_df(path: str):
    saved_df = pd.read_csv(path, index_col=0)
    for i, column in enumerate(LIT_EVAL_RESULT_COLUMNS, start=1):
        print(f"attempting to load column {i}/{len(LIT_EVAL_RESULT_COLUMNS)}: '{column}'")
        try:
            saved_df[column] = saved_df[column].swifter.apply(literal_eval)
        except Exception as e:
            print(f"During parsing column {column}, an error occured: {e}")
    return saved_df
