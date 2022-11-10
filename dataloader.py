from glob import glob

from environment_constants import PATH, YEARS


def get_tsv_file_path(conllu_file_path):
    return conllu_file_path[:-len('.conllu')] + '-meta.tsv'


def make_conllu_files_dict():
    conllu_files_dict = {}
    for year in YEARS:
        conllu_files_dict[year] = [file_name for file_name in glob(PATH+"\\"+year+"\\*.conllu")]
    return conllu_files_dict
