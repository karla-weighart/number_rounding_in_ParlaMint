import conllu
import pandas as pd
import random
import spacy

from glob import glob
from tqdm.notebook import tqdm

from helper_methods import is_enum, count_words, contains_num
from environment_constants import PATH, META_COLUMNS, SENTENCE_COLUMNS

if __name__ == '__main__':
    nlp = spacy.load("en_core_web_trf")