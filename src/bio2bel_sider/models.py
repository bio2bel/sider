# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, Integer, String, Text
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
    inchi_key = Column(Text, nullable=True, doc='InChI Key for this compound')

    #: Identifier of the flat parent, if this is a stereo entry
    parent_id = Column(Integer, ForeignKey(f'{COMPOUND_TABLE_NAME}.id'), nullable=True)
    children = relationship('Compound', backref=backref('parent', remote_side=[id]))

    def __repr__(self):
        return f'pubchem.compound:{self.pubchem_id}'

    def as_bel(self) -> abundance:
        """Returns this compound as an abundance for PyBEL"""
        return abundance(namespace='PUBCHEM', identifier=str(self.pubchem_id))


class Umls(Base):
    """Represents a UMLS entry."""
    __tablename__ = UMLS_TABLE_NAME

    id = Column(Integer, primary_key=True)

    cui = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)

    def __repr__(self):
        return self.name


class CompoundSideEffect(Base):
    __tablename__ = COMPOUND_SIDE_EFFECT_TABLE_NAME

    id = Column(Integer, primary_key=True)

    compound_id = Column(Integer, ForeignKey(f'{COMPOUND_TABLE_NAME}.id'), nullable=False)
    compound = relationship(Compound, backref=backref('side_effects', lazy='dynamic'))

    side_effect_id = Column(Integer, ForeignKey(f'{UMLS_TABLE_NAME}.id'), nullable=False)
    side_effect = relationship(Umls, backref=backref('side_effects', lazy='dynamic'))

    meddra_type = Column(String(32))


class Indication(Base):
    """Represents a disease/phenotype/condition."""
    __tablename__ = INDICATION_TABLE_NAME

    id = Column(Integer, primary_key=True)

    umls_id = Column(String(255), nullable=False, index=True)

    meddra_name = Column(String(255), nullable=False, index=True)

    def as_bel(self) -> pathology:
        """Returns this compound as a pathology for PyBEL"""
        return pathology()
