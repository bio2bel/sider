# -*- coding: utf-8 -*-

"""SQLAlchemy models for Bio2BEL SIDER."""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

import pybel.dsl
from pybel import BELGraph
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

    def __repr__(self):  # noqa: D105
        return f'pubchem:{self.pubchem_id}'

    def as_bel(self) -> pybel.dsl.Abundance:
        """Return this compound as an abundance for PyBEL."""
        return pybel.dsl.Abundance(
            namespace='pubchem',
            identifier=str(self.pubchem_id),
        )


class Umls(Base):
    """Represents a UMLS entry."""

    __tablename__ = UMLS_TABLE_NAME
    id = Column(Integer, primary_key=True)

    cui = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)

    def __repr__(self):  # noqa: D105
        return self.name

    def as_bel(self) -> pybel.dsl.Pathology:
        """Return this UMLS as an pathology for PyBEL."""
        return pybel.dsl.Pathology(
            namespace='umls',
            name=str(self.name),
            identifier=str(self.cui),
        )


class MeddraType(Base):
    """Represents a MedDRA type."""

    __tablename__ = MEDDRA_TYPE_TABLE_NAME
    id = Column(Integer, primary_key=True)

    name = Column(String(255), nullable=False, index=True)

    def __repr__(self):  # noqa: D105
        return self.name


class Detection(Base):
    """Represents the detection method."""

    __tablename__ = DETECTION_TABLE_NAME
    id = Column(Integer, primary_key=True)

    name = Column(String(255), nullable=False, index=True)

    def __repr__(self):  # noqa: D105
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

    def add_to_bel_graph(self, graph: BELGraph) -> str:
        """Add this relationship as an edge to the BEL graph."""
        return graph.add_increases(
            self.compound.as_bel(),
            self.umls.as_bel(),
            citation='26481350',
            evidence='Extracted from SIDER',
            annotations={
                'Database': 'SIDER',
                'SIDER_MEDDRA_TYPE': self.meddra_type.name,
            }
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

    def add_to_bel_graph(self, graph: BELGraph) -> str:
        """Add this relationship as an edge to the BEL graph."""
        return graph.add_decreases(
            self.compound.as_bel(),
            self.umls.as_bel(),
            citation='26481350',
            evidence='Extracted from SIDER',
            annotations={
                'Database': 'SIDER',
                'SIDER_MEDDRA_TYPE': self.meddra_type.name,
                'SIDER_DETECTION': self.detection.name,
            }
        )
