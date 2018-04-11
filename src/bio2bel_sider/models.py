# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

from pybel.dsl import abundance, pathology

TABLE_PREFIX = 'sider'
COMPOUND_TABLE_NAME = f'{TABLE_PREFIX}_compound'
COMPOUND_SIDE_EFFECT_TABLE_NAME = f'{TABLE_PREFIX}_compound_sideEffect'
UMLS_TABLE_NAME = f'{TABLE_PREFIX}_umls'
INDICATION_TABLE_NAME = f'{TABLE_PREFIX}_indication'
SPECIES_TABLE_NAME = f'{TABLE_PREFIX}_species'
XREF_TABLE_NAME = f'{TABLE_PREFIX}_xref'

Base = declarative_base()


class Compound(Base):
    """Represents a compound"""
    __tablename__ = COMPOUND_TABLE_NAME

    id = Column(Integer, primary_key=True)

    pubchem_id = Column(String(255), nullable=False, index=True)
    stitch_id = Column(String(255), nullable=False, index=True)

    #: Identifier of the flat parent, if this is a stereo entry
    parent_id = Column(Integer, ForeignKey('{}.id'.format(COMPOUND_TABLE_NAME)), nullable=True)
    children = relationship('Compound', backref=backref('parent', remote_side=[id]))

    def __repr__(self):
        return f'<Compound pubchem_id={self.pubchem_id}>'

    def as_bel(self) -> abundance:
        """Returns this compound as an abundance for PyBEL"""
        return abundance()


class CompoundSideEffect(Base):
    __tablename__ = COMPOUND_SIDE_EFFECT_TABLE_NAME

    id = Column(Integer, primary_key=True)


class Umls(Base):
    """Represents a UMLS entry"""
    __tablename__ = UMLS_TABLE_NAME

    id = Column(Integer, primary_key=True)

    umls_id = Column(String(255), nullable=False, index=True)


class Indication(Base):
    """Represents a disease/phenotype/condition"""
    __tablename__ = INDICATION_TABLE_NAME

    id = Column(Integer, primary_key=True)

    umls_id = Column(String(255), nullable=False, index=True)

    meddra_name = Column(String(255), nullable=False, index=True)

    def as_bel(self) -> pathology:
        """Returns this compound as a pathology for PyBEL"""
        return pathology()
