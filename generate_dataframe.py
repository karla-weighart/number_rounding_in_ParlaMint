import conllu
import pandas as pd
import random

from glob import glob
from tqdm.notebook import tqdm

from helper_methods import is_enum, count_words, contains_num
from environment_constants import PATH, META_COLUMNS, SENTENCE_COLUMNS


def make_conllu_files_list() -> list[str]:
    """
    Returns
    -------
    a list of paths to all .conllu files
    """
    conllu_files_list = [file_name for file_name in glob(PATH + "\\*.conllu")]
    return conllu_files_list


def make_meta_files_list() -> list[str]:
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


def sentences_and_meta_df(file_path: str,
                          remove_ghosts: bool = True,
                          min_sentence_length: int = 3,
                          remove_enum: bool = True,
                          only_with_nums: bool = True) \
        -> pd.DataFrame:
    """

    Parameters
    ----------
    file_path: path to a .conllu file

    remove_ghosts: whether utterances by ghost speakers will be removed
    min_sentence_length: sentences below the specified length will be removed
    remove_enum: whether utterances that only contain "1." and the like will be removed
    only_with_nums: whether utterances that do not contain any numbers will be removed

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
        inner_dataframe = pd.DataFrame(sentence)[SENTENCE_COLUMNS]
        inner_dataframe['head'] = inner_dataframe['head'] - 1
        sentence_row = pd.Series({'sent_id': sentence.metadata['sent_id'][len('ParlaMint-GB_'):],
                                  'sentence': inner_dataframe.to_dict('list'),
                                  'utterance_id': sentence.metadata.get('newdoc id')
                                  })
        return sentence_row

    file = open(file_path, 'r', encoding='utf-8').read()
    sentences = conllu.parse(file)
    sentences_df = pd.concat((sentence_to_df_row(s) for s in sentences), axis=1).T

    # some sentences from sentence_to_df_row() do not come with utterance_ids
    # make them inherit the utterance_id of their predecessor with ffill
    sentences_df['utterance_id'] = sentences_df['utterance_id'].ffill()

    # === data cleaning ===

    # remove short sentences
    sentences_df = sentences_df[sentences_df['sentence']. \
                                    swifter.progress_bar(False).apply(count_words) >= min_sentence_length]

    # remove sentences of the form "2."
    if remove_enum and min_sentence_length < 3:
        sentences_df = sentences_df[sentences_df['sentence']. \
            swifter.progress_bar(False).apply(lambda cell: not is_enum(cell))]

    # remove sentences that do not contain any numbers
    if only_with_nums:
        sentences_df = sentences_df[sentences_df['sentence'].swifter.progress_bar(False).apply(contains_num)]

    # === combining sentence data and meta data ===

    # only load columns that contain valuable information
    meta_df = pd.read_csv(get_meta_file_path(file_path), sep='\t')[META_COLUMNS]

    # rename utterance_ID column to match sentences_df so the two dfs can be merged
    meta_df = meta_df.rename(columns={'ID': 'utterance_id'})

    sentences_df = sentences_df.merge(meta_df)

    # === data efficiency ===

    # clip off unnecessary letters
    sentences_df['utterance_id'] = \
        [utterance_id[len('ParlaMint-GB_'):] for utterance_id in sentences_df['utterance_id']]

    if remove_ghosts:
        # get rid of utterances by ghost speakers
        sentences_df = sentences_df[sentences_df['Speaker_type'] != '-']

        # compress data: binary datatype if removing ghosts makes category binary
        sentences_df['is_mp'] = (sentences_df['Speaker_type'] == 'MP')
        sentences_df['is_female'] = (sentences_df['Speaker_gender'] == 'F')
        sentences_df.drop(columns=['Speaker_type', 'Speaker_gender'], inplace=True)

    # compress data: binary datatype for binary categories
    sentences_df['is_upper_house'] = (sentences_df['House'] == 'Upper house')
    sentences_df['is_chairperson'] = (sentences_df['Speaker_role'] == 'Chairperson')
    sentences_df.drop(columns=['House', 'Speaker_role'], inplace=True)

    return sentences_df


def generate_sentences_and_meta_df_from_multiple_files(number_of_files: int = None,
                                                       random_seed: int=0,
                                                       remove_ghosts: bool = True,
                                                       min_sentence_length: int = 3,
                                                       remove_enum: bool = True,
                                                       only_with_nums: bool = True) \
        -> pd.DataFrame:
    """
    number_of_files: how many .conllu files are used to generate the dataframe
    random_seed: seed used to pick the number_of_files files randomly.
        if random_seed==0, the first number_of_files files will be used
    remove_ghosts, min_sentence_length, remove_enum, only_with_nums: passed to sentences_and_meta_df

    Returns
    -------
    DataFrame containing info from the first n conllu files
    one line per sentence
    columns as defined in environment constant META_COLUMNS
    """
    path_list = make_conllu_files_list()
    if number_of_files is not None:
        if random_seed != 0:
            random.Random(random_seed).shuffle(path_list)
        path_list = path_list[:number_of_files]

    multiple_file_df = pd.concat(tqdm((sentences_and_meta_df(
        path,
        remove_ghosts=remove_ghosts,
        min_sentence_length=min_sentence_length,
        remove_enum=remove_enum,
        only_with_nums=only_with_nums
    ) for path in path_list), total=len(path_list), desc="Generating Dataframe"))

    # reset index so we can use swifter
    multiple_file_df = multiple_file_df.reset_index(drop=True)

    return multiple_file_df
