from glob import glob
import conllu
import pandas as pd

from environment_constants import PATH, YEARS


def make_conllu_files_dict():
    """makes a dict.
    keys: years (from environment constant YEARS)
    value for each year: list of paths to .conllu files from that year"""
    conllu_files_dict = {}
    for year in YEARS:
        conllu_files_dict[year] = [file_name for file_name in glob(PATH + "\\" + year + "\\*.conllu")]
    return conllu_files_dict


def make_meta_files_dict():
    """makes a dict.
    keys: years (from environment constant YEARS)
    value for each year: list of paths to -meta.tsv files from that year"""
    meta_files_dict = {}
    for year in YEARS:
        meta_files_dict[year] = [file_name for file_name in glob(PATH + "\\" + year + "\\*-meta.tsv")]
    return meta_files_dict


def get_tsv_file_path(conllu_file_path):
    """takes a path of a conllu file and returns the path of the corresponding meta file"""
    return conllu_file_path[:-len('.conllu')] + '-meta.tsv'


def sentence_to_df_row(sentence):
    """takes a sentence from the conllu parser and returns a single-row pandas DataFrame with columns:
    'sent_id' : e.g. '2015-01-05-commons.seg1.1'
    'sentence_df' : pandas DataFrame (yes, we are using a DataFrame within a DataFrame) containing the linguistic data
    'newdoc id' :
        if the sentence is the first of utterance: utterance ID (e.g. ParlaMint-GB_2015-01-05-commons.u1)
        else: None
    """
    sentence_row = pd.DataFrame({'sent_id': [sentence.metadata['sent_id'][len('ParlaMint-GB_'):]],
                                 'sentence_df': [pd.DataFrame(list(sentence))]})
    sentence_row['newdoc id'] = sentence.metadata.get('newdoc id')
    return sentence_row


def sentences_and_meta_df(file_path):
    file = open(file_path, 'r', encoding='utf-8').read()
    sentences = conllu.parse(file)
    sentences_df = pd.concat([sentence_to_df_row(s) for s in sentences])

    # some sentences from sentence_to_df_row() do not come with utterance IDs
    # make them inherit the utterance ID of their predecessor with ffill
    sentences_df['newdoc id'] = sentences_df['newdoc id'].ffill()
    meta_df = pd.read_csv(get_tsv_file_path(file_path), sep='\t').rename(columns={'ID': 'newdoc id'})
    sentences_df = sentences_df.merge(meta_df)
    return sentences_df
