import pandas as pd

from ast import literal_eval

def read_inner_dataframe(cell: str) -> pd.DataFrame:
    """

    Parameters
    ----------
    cell: single cell of the 'sentence' column of the DataFrame that contains one line per sentence (= outer DataFrame)

    Returns
    -------
    sentence DataFrame (= inner DataFrame)
    """
    return pd.DataFrame(literal_eval(cell))


def load_saved_df(path: str):
    saved_df = pd.read_csv(path, index_col=0)
    saved_df['sentence'] = saved_df['sentence'].map(read_inner_dataframe)
    return saved_df
