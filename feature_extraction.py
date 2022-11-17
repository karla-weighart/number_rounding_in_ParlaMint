import numpy as np
import pandas as pd


def find_pattern_in_sentence(pattern: str, sentence_df: pd.DataFrame):
    for i in range(sentence_df.shape[0] - len(pattern) + 1):
        if np.alltrue([sentence_df.iloc[i+p][pattern[p][0]] == pattern[p][1] for p in range(len(pattern))]):
            return sentence_df.iloc[i:i+len(pattern)]['form']
