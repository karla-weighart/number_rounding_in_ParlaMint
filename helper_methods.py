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


def is_enum(cell: pd.DataFrame) -> bool:
    return cell.shape[0] == 2 and (cell['upos'].iloc[0], cell['upos'].iloc[1]) == ('X', 'PUNCT')

