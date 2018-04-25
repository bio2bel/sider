# -*- coding: utf-8 -*-

import logging
from collections import defaultdict

import time
from tqdm import tqdm

from bio2bel import AbstractManager
from .constants import MODULE_NAME
from .models import Base, Compound, CompoundSideEffect, Indication, Umls
from .parser import get_meddra_df, get_side_effects_df

log = logging.getLogger(__name__)


def _convert_flat(stitch_flat_id):
    return "%s" % (abs(int(stitch_flat_id[3:])) - 100000000)


def _convert_stereo(stitch_stereo_id):
    return "%s" % abs(int(stitch_stereo_id[3:]))


class Manager(AbstractManager):
    """Manages the SIDER database."""

    module_name = MODULE_NAME
    flask_admin_models = [Compound, CompoundSideEffect, Umls, Indication]

    def __init__(self, *args, **kwargs):
        """
        :param Optional[str] connection: SQLAlchemy connection string
        """
        super().__init__(*args, **kwargs)

        self.species_cache = {}
        self.gene_cache = {}
        self.homologene_cache = {}
        self.gene_homologene = {}

    @property
    def _base(self):
        return Base

    def is_populated(self):
        """Check if the database is already populated.

        :rtype: bool
        """
        return 0 < self.count_compounds()

    def count_compounds(self):
        """Count the number of compounds in the database.

        :rtype: int
        """
        return self._count_model(Compound)

    def count_side_effects(self):
        """Count the number of side effects in the database.

        :rtype: int
        """
        return self._count_model(CompoundSideEffect)

    def count_indications(self):
        """Count the number of indications in the database.

        :rtype: int
        """
        return self._count_model(Indication)

    def count_umls(self):
        """Count the number of UMLS entries in the database.

        :rtype: int
        """
        return self._count_model(Umls)

    def summarize(self):
        """Summarize the contents of the database.

        :rtype: dict[str,int]
        """
        return dict(
            compounds=self.count_compounds(),
            side_effects=self.count_side_effects(),
            indications=self.count_indications(),
            umls=self.count_umls(),
        )

    def _populate_meddra(self, url=None):
        """Populates the MedDRA terms in the database

        From http://sideeffects.embl.de/media/download/README, this file should have the following columns:

        1. UMLS concept id
        2. MedDRA id
        3. kind of term (from MedDRA e.g. PT = preferred term)
        4. name of side effect

        :param Optional[str] url: The URL for the meddra.tsv file
        """
        log.info('getting MedDRA data')
        df = get_meddra_df(url=url)

        for row in tqdm(df.iterrows(), total=len(df.index)):
            pass

    def _populate_compounds(self):
        """Done in two steps, using both the indications and the side effects documents"""

        log.debug('getting loaded compounds')
        cid_model = {
            compound.stitch_id: compound
            for compound in self.session.query(Compound).all()
        }

        side_effect_df = get_side_effects_df()

        log.debug('iterating side effects data frame')
        it = tqdm(side_effect_df[['STITCH_FLAT_ID', 'STITCH_STEREO_ID']].itertuples(), total=len(side_effect_df.index))
        for _, stitch_flat_id, stitch_stereo_id in it:
            pubchem_flat_id = _convert_flat(stitch_flat_id)
            pubchem_stereo_id = _convert_stereo(stitch_stereo_id)

            flat_model = cid_model.get(stitch_flat_id)
            if flat_model is None:
                flat_model = cid_model[stitch_flat_id] = Compound(
                    stitch_id=stitch_flat_id,
                    pubchem_id=pubchem_flat_id
                )
                self.session.add(flat_model)

            stereo_model = cid_model.get(stitch_stereo_id)
            if stereo_model is None:
                stereo_model = cid_model[stitch_stereo_id] = Compound(
                    stitch_id=stitch_stereo_id,
                    pubchem_id=pubchem_stereo_id,
                    parent=flat_model
                )
                self.session.add(stereo_model)

        t = time.time()
        log.info('committing compound models')
        self.session.commit()
        log.info('committed compound models in %.2f seconds', time.time() - t)

    def _populate_side_effects(self, url=None):
        log.info('getting side effects')
        df = get_side_effects_df(url=url)

        pubchem_to_umls_cids = defaultdict(set)
        pubchem_to_side_effects = defaultdict(set)

        it = tqdm(df.iterrows(), total=len(df.index))
        for source, stitch_flat_id, stitch_stereo_id, umls_on_label, meddra_type, umls_meddra, name in it:
            pubchem_flat_id = _convert_flat(stitch_flat_id)
            pubchem_stereo_id = _convert_stereo(stitch_stereo_id)

            term_type, term_cid, term_name = meddra_type, umls_meddra, name

            if term_type != 'PT':
                continue

            pubchem_to_umls_cids[pubchem_flat_id].add(term_cid)
            pubchem_to_umls_cids[pubchem_stereo_id].add(term_cid)
            pubchem_to_side_effects[pubchem_flat_id].add(term_name)
            pubchem_to_side_effects[pubchem_stereo_id].add(term_name)

            e = CompoundSideEffect(
                pubchem_id=cid_flat,
                # FIXME
            )

            self.session.add(e)

        self.session.commit()

    def populate(self, meddra_url=None, side_effects_url=None, indications_url=None):
        """Populates the side effects and indications

        :param Optional[str] meddra_url:
        :param Optional[str] side_effects_url:
        :param Optional[str] indications_url:
        """
        self._populate_compounds()
