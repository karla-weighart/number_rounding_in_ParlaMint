from io import StringIO
import pandas as pd


def read_inner_dataframe(row: pd.Series) -> pd.DataFrame:
    """

    Parameters
    ----------
    row: row from a pd.DataFrame that has been created by reading a saved .csv file (= outer DataFrame)

    Returns
    -------
    sentence DataFrame (= inner DataFrame)
    """
    return pd.DataFrame(row['sentence'])

# TODO
def apply_to_all_rows(dataframe: pd.DataFrame, func: callable, apply_to_column: str, result_to_column: str) \
        -> pd.DataFrame:
    dataframe[result_to_column] = dataframe.apply(func, axis=1)
