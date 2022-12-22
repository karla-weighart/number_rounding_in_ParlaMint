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
    # noinspection PyTypeChecker
    return pd.read_csv(StringIO(row['sentence']), sep='\t')
