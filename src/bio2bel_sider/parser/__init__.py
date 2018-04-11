# -*- coding: utf-8 -*-

from . import indications, meddra, side_effects
from .indications import *
from .meddra import *
from .side_effects import *

__all__ = (
        indications.__all__ +
        meddra.__all__ +
        side_effects.__all__
)
