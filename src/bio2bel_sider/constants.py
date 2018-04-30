# -*- coding: utf-8 -*-

import os

from bio2bel.utils import get_connection, get_data_dir

MODULE_NAME = 'sider'

DATA_DIR = get_data_dir(MODULE_NAME)
DEFAULT_CACHE_CONNECTION = get_connection(MODULE_NAME)

# For more information on the contents of these files, see: http://sideeffects.embl.de/media/download/README

MEDDRA_URL = 'http://sideeffects.embl.de/media/download/meddra.tsv.gz'
MEDDRA_PATH = os.path.join(DATA_DIR, 'meddra.tsv.gz')
MEDDRA_HEADER = [
    'UMLS_ID',
    'MedDRA_ID',
    'Kind',  # (from MedDRA e.g. PT = preferred term)
    'Name',
]

SIDE_EFFECTS_URL = 'http://sideeffects.embl.de/media/download/meddra_all_label_se.tsv.gz'
SIDE_EFFECTS_PATH = os.path.join(DATA_DIR, 'meddra_all_label_se.tsv.gz')
SIDE_EFFECTS_HEADER = [
    'Source Label',
    'STITCH_FLAT_ID',
    'STITCH_STEREO_ID',
    'UMLS from Label',
    'MedDRA Concept Type',
    'UMLS from MedDRA',
    'Side Effect Name',
]

INDICATIONS_URL = 'http://sideeffects.embl.de/media/download/meddra_all_label_indications.tsv.gz'
INDICATIONS_PATH = os.path.join(DATA_DIR, 'meddra_all_label_indications.tsv.gz')
INDICATIONS_HEADER = [
    'STITCH_ID',
    'UMLS',
    'Method of Detection',  # NLP_indication / NLP_precondition / text_mention
    'Concept Name',
    'MedDR Concept Type',  # (LLT=lowest level term, PT=preferred term; in a few cases the term is neither LLT nor PT)
    'UMLS for MedDRA Term',
    'MedDRA concept name',
]

FREQUENCY_URL = 'http://sideeffects.embl.de/media/download/meddra_freq.tsv.gz'
FREQUENCY_PATH = os.path.join(DATA_DIR, 'meddra_freq.tsv.gz')
FREQUENCY_HEADER = [
    'STITCH_FLAT_ID',
    'STITCH_STEREO_ID',
    ...
]
