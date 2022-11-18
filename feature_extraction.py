import numpy as np
import pandas as pd
from typing import List, Tuple


def find_pattern_in_sentence(pattern: List[Tuple[str]], sentence_df: pd.DataFrame) -> List[pd.DataFrame]:
    """
    Parameters
    ----------
    pattern: [(column, value), ...] that should be matched. the tuples have to be consecutive.
    sentence_df: DataFrame from the conllu files (single sentence, one row = one word)

    Returns
    -------
    dataframe with the concrete forms that matched the pattern
    """
    search_results = []
    for i in range(sentence_df.shape[0] - len(pattern) + 1):
        if np.alltrue([sentence_df.iloc[i+p][pattern[p][0]] == pattern[p][1] for p in range(len(pattern))]):
            search_results.append(sentence_df.iloc[i:i+len(pattern)]['form'])
    return search_results
