# -*- coding: utf-8 -*-

"""SQLAlchemy models for Bio2BEL SIDER."""

from pybel.constants import DECREASES, INCREASES
from pybel.dsl import abundance, pathology
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

from .constants import MODULE_NAME

COMPOUND_TABLE_NAME = f'{MODULE_NAME}_compound'
UMLS_TABLE_NAME = f'{MODULE_NAME}_umls'
MEDDRA_TYPE_TABLE_NAME = f'{MODULE_NAME}_meddratype'
DETECTION_TABLE_NAME = f'{MODULE_NAME}_detection'
COMPOUND_SIDE_EFFECT_TABLE_NAME = f'{MODULE_NAME}_sideeffect'
COMPOUND_INDICATION_TABLE_NAME = f'{MODULE_NAME}_indication'

Base = declarative_base()


class Compound(Base):
    """Represents a compound."""

    __tablename__ = COMPOUND_TABLE_NAME

    id = Column(Integer, primary_key=True)

    pubchem_id = Column(String(255), nullable=False, index=True)
    stitch_id = Column(String(255), nullable=False, index=True)
    inchi_key = Column(Text, nullable=True, doc='InChI Key for this compound')

    #: Identifier of the flat parent, if this is a stereo entry
    parent_id = Column(Integer, ForeignKey(f'{COMPOUND_TABLE_NAME}.id'), nullable=True)
    children = relationship('Compound', backref=backref('parent', remote_side=[id]))

    def __repr__(self):
        return f'pubchem.compound:{self.pubchem_id}'

    def as_bel(self) -> abundance:
        """Return this compound as an abundance for PyBEL."""
        return abundance(namespace='PUBCHEM', identifier=str(self.pubchem_id))


class Umls(Base):
    """Represents a UMLS entry."""

    __tablename__ = UMLS_TABLE_NAME

    id = Column(Integer, primary_key=True)

    cui = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)

    def __repr__(self):
        return self.name

    def as_bel(self) -> pathology:
        """Return this UMLS as an pathology for PyBE.L"""
        return pathology(namespace='UMLS', name=str(self.name), identifier=str(self.cui))


class MeddraType(Base):
    """Represents a MedDRA type."""

    __tablename__ = MEDDRA_TYPE_TABLE_NAME

    id = Column(Integer, primary_key=True)

    name = Column(String(255), nullable=False, index=True)

    def __repr__(self):
        return self.name


class Detection(Base):
    """Represents the detection method."""

    __tablename__ = DETECTION_TABLE_NAME

    id = Column(Integer, primary_key=True)

    name = Column(String(255), nullable=False, index=True)

    def __repr__(self):
        return self.name


class SideEffect(Base):
    """Represents a side effect of a compound."""

    __tablename__ = COMPOUND_SIDE_EFFECT_TABLE_NAME

    id = Column(Integer, primary_key=True)

    compound_id = Column(Integer, ForeignKey(f'{COMPOUND_TABLE_NAME}.id'), nullable=False)
    compound = relationship(Compound, backref=backref('side_effects', lazy='dynamic'))

    umls_id = Column(Integer, ForeignKey(f'{UMLS_TABLE_NAME}.id'), nullable=False)
    umls = relationship(Umls, backref=backref('side_effects', lazy='dynamic'))

    meddra_type_id = Column(Integer, ForeignKey(f'{MEDDRA_TYPE_TABLE_NAME}.id'), nullable=False)
    meddra_type = relationship(MeddraType)

    def add_to_bel_graph(self, graph):
        """Add this relationship as an edge to the BEL graph.

        :param pybel.BELGraph graph:
        :return:
        :rtype: str
        """
        return graph.add_qualified_edge(
            self.compound.as_bel(),
            self.umls.as_bel(),
            relation=INCREASES,
            citation='26481350',
            evidence='Extracted from SIDER',
        )


class Indication(Base):
    """Represents an indication of a compound."""

    __tablename__ = COMPOUND_INDICATION_TABLE_NAME

    id = Column(Integer, primary_key=True)

    compound_id = Column(Integer, ForeignKey(f'{COMPOUND_TABLE_NAME}.id'), nullable=False)
    compound = relationship(Compound, backref=backref('indications', lazy='dynamic'))

    umls_id = Column(Integer, ForeignKey(f'{UMLS_TABLE_NAME}.id'), nullable=False)
    umls = relationship(Umls, backref=backref('indications', lazy='dynamic'))

    meddra_type_id = Column(Integer, ForeignKey(f'{MEDDRA_TYPE_TABLE_NAME}.id'), nullable=False)
    meddra_type = relationship(MeddraType)

    detection_id = Column(Integer, ForeignKey(f'{DETECTION_TABLE_NAME}.id'), nullable=False)
    detection = relationship(Detection)

    def add_to_bel_graph(self, graph):
        """Add this relationship as an edge to the BEL graph.

        :param pybel.BELGraph graph:
        :return:
        :rtype: str
        """
        return graph.add_qualified_edge(
            self.compound.as_bel(),
            self.umls.as_bel(),
            relation=DECREASES,
            citation='26481350',
            evidence='Extracted from SIDER',
        )
