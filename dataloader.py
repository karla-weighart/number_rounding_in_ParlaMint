from glob import glob

from environment_constants import PATH, YEARS


def make_tsv_files_dict():
    tsv_files_dict = {}
    for year in YEARS:
        tsv_files_dict[year] = [file_name for file_name in glob(PATH + "\\" + year + "\\*.tsv")]


def make_conllu_files_dict():
    conllu_files_dict = {}
    for year in YEARS:
        conllu_files_dict[year] = [file_name for file_name in glob(PATH+"\\"+year+"\\*.conllu")]
    return conllu_files_dict
