import pandas as pd

from ast import literal_eval


def inner_dataframe_from_row(row: pd.Series) -> pd.DataFrame:
    """

    Parameters
    ----------
    row: single row of the outer DataFrame, corresponds to one sentence

    Returns
    -------
    sentence DataFrame (= inner DataFrame)
    """
    cell = row['sentence']
    return pd.DataFrame(cell)


def is_enum(cell: pd.DataFrame) -> bool:
    return cell.shape[0] == 2 and (cell['upos'].iloc[0], cell['upos'].iloc[1]) in {('X', 'PUNCT'), ('NUM', 'PUNCT')}

