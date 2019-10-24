# -*- coding: utf-8 -*-

"""Getters for MedDRA data."""

from bio2bel import make_df_getter
from bio2bel_sider.constants import (
    DRUG_NAMES_HEADER, DRUG_NAMES_PATH, DRUG_NAMES_URL, FREQUENCY_HEADER, FREQUENCY_PATH, FREQUENCY_URL, INDICATIONS_HEADER, INDICATIONS_PATH, INDICATIONS_URL,
    MEDDRA_HEADER, MEDDRA_PATH, MEDDRA_URL, SIDE_EFFECTS_HEADER, SIDE_EFFECTS_PATH, SIDE_EFFECTS_URL,
)

__all__ = [
    'get_indications_df',
    'get_drug_names_df',
    'get_meddra_df',
    'get_side_effects_df',
]

get_indications_df = make_df_getter(
    INDICATIONS_URL,
    INDICATIONS_PATH,
    sep='\t',
    names=INDICATIONS_HEADER,
)

get_drug_names_df = make_df_getter(
    DRUG_NAMES_URL,
    DRUG_NAMES_PATH,
    sep='\t',
    names=DRUG_NAMES_HEADER,
)

get_meddra_df = make_df_getter(
    MEDDRA_URL,
    MEDDRA_PATH,
    sep='\t',
    names=MEDDRA_HEADER,
)

get_side_effects_df = make_df_getter(
    SIDE_EFFECTS_URL,
    SIDE_EFFECTS_PATH,
    sep='\t',
    names=SIDE_EFFECTS_HEADER,
)

get_se_frequency_df = make_df_getter(
    FREQUENCY_URL,
    FREQUENCY_PATH,
    sep='\t',
    names=FREQUENCY_HEADER,
)
