import pandas as pd

from ast import literal_eval
from environment_constants import LIT_EVAL_RESULT_COLUMNS


def load_saved_df(path: str):
    saved_df = pd.read_csv(path, index_col=0)
    for column in LIT_EVAL_RESULT_COLUMNS:
        try:
            saved_df[column] = saved_df[column].swifter.apply(literal_eval)
    return saved_df
