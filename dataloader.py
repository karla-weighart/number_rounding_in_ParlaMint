from glob import glob
from pathlib import Path
from typing import List, Tuple

from tqdm.notebook import tqdm

import conllu
import pandas as pd

from environment_constants import PATH, META_COLUMNS, SENTENCE_COLUMNS


def make_conllu_files_list() -> List[str]:
    """
    Returns
    -------
    a list of paths to all .conllu files
    """
    conllu_files_list = [file_name for file_name in glob(PATH + "\\*.conllu")]
    return conllu_files_list


def make_meta_files_list() -> List[str]:
    """
    Returns
    -------
    a list of paths to all -meta.tsv files
    """
    meta_files_list = [file_name for file_name in glob(PATH + "\\*-meta.tsv")]
    return meta_files_list


def get_meta_file_path(conllu_file_path: str) -> str:
    """

    Parameters
    ----------
    conllu_file_path: path of a conllu file

    Returns
    -------
    path of the corresponding -meta.tsv file
    """
    return conllu_file_path[:-len('.conllu')] + '-meta.tsv'


def sentences_and_meta_df(file_path: str) -> pd.DataFrame:
    """

    Parameters
    ----------
    file_path: path to a .conllu file

    Returns
    -------
    pandas DataFrame containing one line per sentence
    columns as defined in environment constant META_COLUMNS
    """

    def sentence_to_df_row(sentence: conllu.models.TokenList) -> pd.Series:
        """

        Parameters
        ----------
        sentence: single sentence from the conllu parser

        Returns
        -------
        pandas Series with columns:
            'sent_id' : e.g. '2015-01-05-commons.seg1.1'
            'sentence' : pd.DataFrame
            'utterance_id' :
                if the sentence is the first of utterance: utterance ID (e.g. ParlaMint-GB_2015-01-05-commons.u1)
                else: None (will be filled in later in outer function)
        """
        sentence_row = pd.Series({'sent_id': sentence.metadata['sent_id'][len('ParlaMint-GB_'):],
                                  'sentence': pd.DataFrame(sentence)[SENTENCE_COLUMNS],
                                  'utterance_id': sentence.metadata.get('newdoc id')
                                  })
        return sentence_row

    file = open(file_path, 'r', encoding='utf-8').read()
    sentences = conllu.parse(file)
    sentences_df = pd.concat((sentence_to_df_row(s) for s in sentences), axis=1).T

    # some sentences from sentence_to_df_row() do not come with utterance_ids
    # make them inherit the utterance_id of their predecessor with ffill
    sentences_df['utterance_id'] = sentences_df['utterance_id'].ffill()

    # only load columns that contain valuable information (I used understanding_the_corpus to identify those columns)
    meta_df = pd.read_csv(get_meta_file_path(file_path), sep='\t')[META_COLUMNS]

    # rename utterance_ID column to match sentences_df so the two dfs can be merged
    meta_df = meta_df.rename(columns={'ID': 'utterance_id'})

    sentences_df = sentences_df.merge(meta_df)

    # === data efficiency ===

    # get rid of utterances by ghost speakers
    sentences_df = sentences_df[sentences_df['Speaker_type'] != '-']

    # clip off unnecessary letters
    sentences_df['utterance_id'] = \
        [utterance_id[len('ParlaMint-GB_'):] for utterance_id in sentences_df['utterance_id']]

    # compress data: binary datatypes for binary categories
    sentences_df['upper_house'] = (sentences_df['House'] == 'Upper house')
    sentences_df['chairperson'] = (sentences_df['Speaker_role'] == 'Chairperson')
    sentences_df['mp'] = (sentences_df['Speaker_type'] == 'MP')
    sentences_df['female'] = (sentences_df['Speaker_gender'] == 'F')
    sentences_df.drop(columns=['House', 'Speaker_role', 'Speaker_type', 'Speaker_gender'], inplace=True)

    return sentences_df


def complete_sentences_and_meta_df() -> pd.DataFrame:
    """

    Returns
    -------
    DataFrame containing the entire corpus minus everything said by ghost speakers
    one line per sentence
    columns as defined in environment constant META_COLUMNS
    """

    path_list = make_conllu_files_list()
    complete_df = pd.concat(tqdm((sentences_and_meta_df(path) for path in path_list), total=len(path_list)))
    return complete_df


def save_complete_sentences_and_meta_df(path: str = "C:/Users/karla/Desktop/Zula_Data_all_in_one/data.csv"):
    filepath = Path(path)
    complete_df = complete_sentences_and_meta_df()
    complete_df.to_csv(filepath)
