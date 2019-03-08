# -*- coding: utf-8 -*-

"""Constants for Bio2BEL SIDER."""

import os

from bio2bel import get_data_dir

MODULE_NAME = 'sider'
DATA_DIR = get_data_dir(MODULE_NAME)

# For more information on the contents of these files, see: http://sideeffects.embl.de/media/download/README

MEDDRA_URL = 'http://sideeffects.embl.de/media/download/meddra.tsv.gz'
MEDDRA_PATH = os.path.join(DATA_DIR, 'meddra.tsv.gz')
MEDDRA_HEADER = [
    'UMLS_ID',
    'MedDRA_ID',
    'Kind',  # (from MedDRA e.g. PT = preferred term)
    'Name',
]

SIDE_EFFECTS_URL = 'http://sideeffects.embl.de/media/download/meddra_all_se.tsv.gz'
SIDE_EFFECTS_PATH = os.path.join(DATA_DIR, 'meddra_all_se.tsv.gz')
SIDE_EFFECTS_HEADER = [
    'STITCH_FLAT_ID',
    'STITCH_STEREO_ID',
    'UMLS CUI from Label',
    'MedDRA Concept Type',
    'UMLS CUI from MedDRA',
    'MedDRA Concept name',
]

INDICATIONS_URL = 'http://sideeffects.embl.de/media/download/meddra_all_indications.tsv.gz'
INDICATIONS_PATH = os.path.join(DATA_DIR, 'meddra_all_indications.tsv.gz')
INDICATIONS_HEADER = [
    'STITCH_FLAT_ID',
    'UMLS CUI from Label',
    'Method of Detection',  # NLP_indication / NLP_precondition / text_mention
    'Concept Name',
    'MedDRA Concept Type',  # (LLT=lowest level term, PT=preferred term; in a few cases the term is neither LLT nor PT)
    'UMLS CUI from MedDRA',
    'MedDRA Concept name',
]

DRUG_NAMES_URL = 'http://sideeffects.embl.de/media/download/drug_names.tsv'
DRUG_NAMES_PATH = os.path.join(DATA_DIR, 'drug_names.tsv')
DRUG_NAMES_HEADER = [
    'STITCH_FLAT_ID',
    'Drug Name',
]

FREQUENCY_URL = 'http://sideeffects.embl.de/media/download/meddra_freq.tsv.gz'
FREQUENCY_PATH = os.path.join(DATA_DIR, 'meddra_freq.tsv.gz')
FREQUENCY_HEADER = [
    'STITCH_FLAT_ID',
    'STITCH_STEREO_ID',
    # TODO finish
]
