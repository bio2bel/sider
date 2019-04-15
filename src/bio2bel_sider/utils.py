# -*- coding: utf-8 -*-

"""Utilities for Bio2BEL SIDER."""

from typing import Optional


def convert_flat_stitch_id_to_pubchem_cid(stitch_flat_id: str) -> str:
    """Convert a flattened STITCH identifier (no stereochemistry) to PubChem compound identifier."""
    return str(abs(int(stitch_flat_id[3:])) - 100000000)


def _convert_stereo_stitch_id_to_pubchem_cid(stitch_stereo_id: str) -> str:
    """Convert a STITCH identifier to PubChem compound identifier."""
    return str(abs(int(stitch_stereo_id[3:])))


def enrich_pubchem_synonyms(pubchem_cid):
    """Enrich synonyms.tsv with information from PubChem."""
    import pubchempy as pcp
    compound = pcp.Compound.from_cid(int(pubchem_cid))
    return compound.synonyms


def get_chembl(pubchem_cid) -> Optional[str]:
    """Get the ChEMBL identifier from a PubChem compound identifier."""
    for synonym in enrich_pubchem_synonyms(pubchem_cid):
        if synonym.startswith('CHEMBL'):
            return synonym
