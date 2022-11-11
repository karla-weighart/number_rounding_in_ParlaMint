from glob import glob
import conllu
import pandas as pd

from environment_constants import PATH, YEARS


def get_tsv_file_path(conllu_file_path):
    return conllu_file_path[:-len('.conllu')] + '-meta.tsv'


def make_conllu_files_dict():
    conllu_files_dict = {}
    for year in YEARS:
        conllu_files_dict[year] = [file_name for file_name in glob(PATH + "\\" + year + "\\*.conllu")]
    return conllu_files_dict


def sentence_to_df_row(sentence):
    sentence_row = pd.DataFrame({'sent_id': [sentence.metadata['sent_id'][len('ParlaMint-GB_'):]],
                                 'sentence_df': [pd.DataFrame(list(sentence))]})
    sentence_row['newdoc id'] = sentence.metadata.get('newdoc id')
    return sentence_row


def sentences_and_meta_df(file_path):
    file = open(file_path, 'r', encoding='utf-8').read()
    sentences = conllu.parse(file)
    sentences_df = pd.concat([sentence_to_df_row(s) for s in sentences])
    sentences_df['newdoc id'] = sentences_df['newdoc id'].ffill()
    meta_df = pd.read_csv(get_tsv_file_path(file_path), sep='\t').rename(columns={'ID': 'newdoc id'})
    sentences_df = sentences_df.merge(meta_df)
    return sentences_df
