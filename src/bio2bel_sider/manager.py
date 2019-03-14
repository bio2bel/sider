# -*- coding: utf-8 -*-

"""Manager for Bio2BEL SIDER."""

import logging
import time
from typing import Dict, Mapping, Optional, Type

from tqdm import tqdm

from bio2bel import AbstractManager
from bio2bel.manager.bel_manager import BELManagerMixin
from bio2bel.manager.flask_manager import FlaskMixin
from pybel import BELGraph
from .constants import MODULE_NAME
from .models import Base, Compound, Detection, Indication, MeddraType, SideEffect, Umls
from .parser import get_indications_df, get_meddra_df, get_side_effects_df
from .utils import convert_flat_stitch_id_to_pubchem_cid

log = logging.getLogger(__name__)

INDICATIONS_COLUMNS = [
    'STITCH_FLAT_ID',
    'Method of Detection',
    'MedDRA Concept Type',
    'UMLS CUI from MedDRA',
    'MedDRA Concept name',
]

SIDE_EFFECTS_COLUMNS = [
    'STITCH_FLAT_ID',
    'MedDRA Concept Type',
    'UMLS CUI from MedDRA',
    'MedDRA Concept name',
]


class Manager(AbstractManager, BELManagerMixin, FlaskMixin):
    """Drugs' side effects and indications."""

    _base = Base
    module_name = MODULE_NAME
    edge_model = [Indication, SideEffect]
    flask_admin_models = [Compound, Umls, Indication, SideEffect]

    def __init__(self, *args, **kwargs):  # noqa: D107
        super().__init__(*args, **kwargs)

        self.stitch_id_to_compound = {}
        self.cui_to_umls = {}
        self.meddra_types = {}
        self.detections = {}

    def is_populated(self) -> bool:
        """Check if the database is already populated."""
        return 0 < self.count_compounds()

    def count_compounds(self) -> int:
        """Count the number of compounds in the database."""
        return self._count_model(Compound)

    def count_side_effects(self) -> int:
        """Count the number of side effects in the database."""
        return self._count_model(SideEffect)

    def count_indications(self) -> int:
        """Count the number of indications in the database."""
        return self._count_model(Indication)

    def count_umls(self) -> int:
        """Count the number of UMLS entries in the database."""
        return self._count_model(Umls)

    def summarize(self) -> Mapping[str, int]:
        """Summarize the contents of the database."""
        return dict(
            compounds=self.count_compounds(),
            side_effects=self.count_side_effects(),
            indications=self.count_indications(),
            umls=self.count_umls(),
        )

    def get_compound_by_stitch_id(self, stitch_id: str) -> Optional[Compound]:
        """Get a compound by its STITCH identifier, if it exists."""
        return self.session.query(Compound).filter(Compound.stitch_id == stitch_id).one_or_none()

    def get_or_create_compound(self, stitch_id: str, **kwargs) -> Compound:
        """Get a compound by its STITCH identifier, or create one if it doesn't exist."""
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
        """Get a UMLS by its CUI, if it exists."""
        return self.session.query(Umls).filter(Umls.cui == cui).one_or_none()

    def get_or_create_umls(self, cui: str, **kwargs) -> Umls:
        """Get a UMLS by its CUI, or create one if it does not exist."""
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

    def _get_or_create_model(self, d: Dict[str, Type[Base]], m: Type[Base], n, i: str, **kwargs) -> Type[Base]:
        model = d.get(i)
        if model is not None:
            return model

        model = self.session.query(m).filter_by(**{n: i}).one_or_none()
        if model is not None:
            d[i] = model
            return model

        model = d[i] = m(**{n: i}, **kwargs)
        self.session.add(model)
        return model

    def get_or_create_detection(self, name: str) -> Detection:
        """Get a detection by its name, or create one if it doesn't exist."""
        return self._get_or_create_model(self.detections, Detection, 'name', name)

    def get_or_create_meddra_type(self, name: str) -> MeddraType:
        """Get a MedDRA type by its name, or create one if it doesn't exit."""
        return self._get_or_create_model(self.meddra_types, MeddraType, 'name', name)

    def _populate_indications(self, url: Optional[str] = None):
        """Populate compound indications.

        :param url: A custom URL for the indications data source
        """
        indications_df = get_indications_df(url=url)
        indications_df = indications_df.loc[indications_df['UMLS CUI from MedDRA'].notna(), INDICATIONS_COLUMNS]
        log.info('populating indications effects')

        it = tqdm(indications_df.itertuples(), total=len(indications_df.index), desc='Indications')
        for _, stitch_id, detection, meddra_type, cui, concept_name in it:
            pubchem_id = convert_flat_stitch_id_to_pubchem_cid(stitch_id)
            se_flat = Indication(
                compound=self.get_or_create_compound(stitch_id=stitch_id, pubchem_id=pubchem_id),
                umls=self.get_or_create_umls(cui=cui, name=concept_name),
                meddra_type=self.get_or_create_meddra_type(meddra_type),
                detection=self.get_or_create_detection(detection)
            )
            self.session.add(se_flat)

        t = time.time()
        log.info('committing indications')
        self.session.commit()
        log.info('committed indications in %.2f seconds', time.time() - t)

    def _populate_side_effects(self, url: Optional[str] = None):
        """Populate compound side effects.

        Done in two steps, using both the indications and the side effects documents.

        :param url: A custom URL for the side effects data source
        """
        side_effects_df = get_side_effects_df(url=url)
        side_effects_df = side_effects_df.loc[side_effects_df['UMLS CUI from MedDRA'].notna(), SIDE_EFFECTS_COLUMNS]

        log.info('populating side effects')
        it = tqdm(side_effects_df.itertuples(), total=len(side_effects_df.index), desc='Side Effects')
        for _, stitch_id, meddra_type, cui, side_effect_name in it:
            pubchem_id = convert_flat_stitch_id_to_pubchem_cid(stitch_id)

            se_flat = SideEffect(
                compound=self.get_or_create_compound(stitch_id=stitch_id, pubchem_id=pubchem_id),
                umls=self.get_or_create_umls(cui=cui, name=side_effect_name),
                meddra_type=self.get_or_create_meddra_type(meddra_type),
            )

            self.session.add(se_flat)

            # Maybe use stereochemistry later?
            # pubchem_stereo_id = _convert_stereo(stitch_stereo_id)
            # stereo_model = self.get_or_create_compound(stitch_id=stitch_stereo_id,
            #                                            pubchem_id=pubchem_stereo_id,parent=flat_model)
            # se_stereo = CompoundSideEffect(compound=stereo_model, side_effect=umls)

        t = time.time()
        log.info('committing side effects')
        self.session.commit()
        log.info('committed side effects in %.2f seconds', time.time() - t)

    def _populate_meddra(self, url: Optional[str] = None):
        """Populate the MedDRA terms in the database.

        From http://sideeffects.embl.de/media/download/README, this file should have the following columns:

        1. UMLS concept id
        2. MedDRA id
        3. kind of term (from MedDRA e.g. PT = preferred term)
        4. name of side effect

        :param url: The URL for the meddra.tsv file
        """
        log.info('getting MedDRA data')
        df = get_meddra_df(url=url)

        for row in tqdm(df.iterrows(), total=len(df.index)):
            pass

    def populate(self, side_effects_url: Optional[str] = None, indications_url: Optional[str] = None):
        """Populate the side effects and indications from SIDER.

        :param side_effects_url:
        :param indications_url:
        """
        self._populate_indications(url=indications_url)
        self._populate_side_effects(url=side_effects_url)

    def to_bel(self) -> BELGraph:
        """Serialize SIDER to BEL."""
        graph = BELGraph(
            name='Side Effect Resource (SIDER)',
            version='1.0.0',
        )

        for side_effect in tqdm(self._get_query(SideEffect), total=self.count_side_effects(), desc='side effects'):
            side_effect.add_to_bel_graph(graph)

        for indication in tqdm(self._get_query(Indication), total=self.count_indications(), desc='indications'):
            indication.add_to_bel_graph(graph)

        return graph
