# -*- coding: utf-8 -*-

import logging
import time
from typing import Optional

import pandas as pd
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

        self.stitch_id_to_compound = {
            compound.stitch_id: compound
            for compound in self.session.query(Compound).all()
        }

        self.cui_to_umls = {
            umls.cui: umls
            for umls in self.session.query(Umls).all()
        }

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

    def get_compound_by_stitch_id(self, stitch_id: str) -> Optional[Compound]:
        return self.session.query(Compound).filter(Compound.stitch_id == stitch_id).one_or_none()

    def get_or_create_compound(self, stitch_id: str, **kwargs) -> Compound:
        model = self.stitch_id_to_compound.get(stitch_id)
        if model is not None:
            return model

        model = self.get_compound_by_stitch_id(stitch_id)
        if model is not None:
            self.stitch_id_to_compound[stitch_id] = model
            return model

        model = self.stitch_id_to_compound[stitch_id] = Compound(stitch_id=stitch_id, **kwargs)
        self.session.add(model)
        return model

    def get_umls_by_cui(self, cui: str) -> Optional[Umls]:
        return self.session.query(Umls).filter(Umls.cui == cui).one_or_none()

    def get_or_create_umls(self, cui: str, **kwargs) -> Umls:
        model = self.cui_to_umls.get(cui)
        if model is not None:
            return model

        model = self.get_umls_by_cui(cui)
        if model is not None:
            self.cui_to_umls[cui] = model
            return model

        model = self.cui_to_umls[cui] = Umls(cui=cui, **kwargs)
        self.session.add(model)
        return model

    def _populate_side_effects(self, url=None):
        """Done in two steps, using both the indications and the side effects documents

        :param Optional[str] url: A custom URL for the side effects data source
        """
        df = get_side_effects_df(url=url)

        log.info('populating side effects')

        _columns = ['STITCH_FLAT_ID', 'MedDRA Concept Type', 'UMLS from MedDRA', 'Side Effect Name', ]
        it = tqdm(df[pd.notna('UMLS from MedDRA'), _columns].itertuples(), total=len(df.index), desc='Side effects')
        for _, stitch_id, meddra_type, cui, side_effect_name in it:
            pubchem_id = _convert_flat(stitch_id)
            flat_model = self.get_or_create_compound(stitch_id=stitch_id, pubchem_id=pubchem_id)
            umls = self.get_or_create_umls(cui=cui, name=side_effect_name)
            se_flat = CompoundSideEffect(compound=flat_model, side_effect=umls, meddra_type=meddra_type)

            self.session.add(se_flat)

            # Maybe use stereochemistry later?
            # pubchem_stereo_id = _convert_stereo(stitch_stereo_id)
            # stereo_model = self.get_or_create_compound(stitch_id=stitch_stereo_id, pubchem_id=pubchem_stereo_id,parent=flat_model)
            # se_stereo = CompoundSideEffect(compound=stereo_model, side_effect=umls)

        t = time.time()
        log.info('committing side effects')
        self.session.commit()
        log.info('committed side effects in %.2f seconds', time.time() - t)

    def populate(self, meddra_url=None, side_effects_url=None, indications_url=None):
        """Populates the side effects and indications

        :param Optional[str] meddra_url:
        :param Optional[str] side_effects_url:
        :param Optional[str] indications_url:
        """
        self._populate_side_effects()
