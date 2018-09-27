# -*- coding: utf-8 -*-

"""Test cases for Bio2BEL SIDER."""

import os

from bio2bel.testing import AbstractTemporaryCacheClassMixin
from bio2bel_sider import Manager

HERE = os.path.abspath(os.path.dirname(__file__))
TEST_SIDE_EFFECTS_PATH = os.path.join(HERE, 'test_meddra_all_indications.tsv')
TEST_INDICATIONS_PATH = os.path.join(HERE, 'test_meddra_all_se.tsv')


class TemporaryCacheClassMixin(AbstractTemporaryCacheClassMixin):
    """A test case with the SIDER database populated."""

    Manager = Manager

    @classmethod
    def populate(cls):
        """Populate the SIDER database."""
        cls.manager.populate(
            side_effects_url=TEST_SIDE_EFFECTS_PATH,
            indications_url=TEST_INDICATIONS_PATH,
        )
