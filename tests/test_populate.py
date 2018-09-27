# -*- coding: utf-8 -*-

"""Tests for Bio2BEL SIDER."""

from bio2bel_sider import Manager
from tests.cases import TemporaryCacheClassMixin


class TestPopulate(TemporaryCacheClassMixin):
    """Test that the SIDER database was populated."""

    manager: Manager

    def test_counts(self):
        """Test the right number of entities were added."""
        self.assertEqual(4, self.manager.count_indications())
        self.assertEqual(4, self.manager.count_side_effects())
