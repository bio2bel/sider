# -*- coding: utf-8 -*-

import logging

import pandas as pd

from bio2bel import make_downloader
from bio2bel_sider.constants import SIDE_EFFECTS_HEADER, SIDE_EFFECTS_PATH, SIDE_EFFECTS_URL

__all__ = [
    'download_side_effects',
    'get_side_effects_df',
]

log = logging.getLogger(__name__)

download_side_effects = make_downloader(SIDE_EFFECTS_URL, SIDE_EFFECTS_PATH)


def get_side_effects_df(url=None, cache=True, force_download=False):
    """Loads the indications into a data frame

    :param Optional[str] url: A custom path to use for data
    :param bool cache: If true, the data is downloaded to the file system, else it is loaded from the internet
    :param bool force_download: If true, overwrites a previously cached file
    :rtype: pandas.DataFrame
    """
    if url is None and cache:
        url = download_side_effects(force_download=force_download)

    df = pd.read_csv(
        url or SIDE_EFFECTS_URL,
        sep='\t',
        names=SIDE_EFFECTS_HEADER,
    )

    return df
