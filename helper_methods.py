import ast
import pandas as pd


def read_inner_dataframe(cell: str) -> pd.DataFrame:
    """

    Parameters
    ----------
    cell: single cell of the 'sentence' column of the DataFrame that contains one line per sentence (= outer DataFrame)

    Returns
    -------
    sentence DataFrame (= inner DataFrame)
    """
    return pd.DataFrame(ast.literal_eval(cell))  # TODO doesnt work


# TODO
# def apply_to_all_rows(dataframe: pd.DataFrame, func: callable, apply_to_column: str, result_to_column: str) \
#         -> pd.DataFrame:
#    dataframe[result_to_column] = dataframe.apply(func, axis=1)
