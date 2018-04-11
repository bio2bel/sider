# -*- coding: utf-8 -*-

import logging

import pandas as pd

from bio2bel import make_downloader
from bio2bel_sider.constants import MEDDRA_HEADER, MEDDRA_PATH, MEDDRA_URL

__all__ = [
    'download_meddra',
    'get_meddra_df',
]

log = logging.getLogger(__name__)

download_meddra = make_downloader(MEDDRA_URL, MEDDRA_PATH)


def get_meddra_df(url=None, cache=True, force_download=False):
    """Loads the indications into a data frame

    :param Optional[str] url: A custom path to use for data
    :param bool cache: If true, the data is downloaded to the file system, else it is loaded from the internet
    :param bool force_download: If true, overwrites a previously cached file
    :rtype: pandas.DataFrame
    """
    if url is None and cache:
        url = download_meddra(force_download=force_download)

    df = pd.read_csv(
        url or MEDDRA_URL,
        sep='\t',
        names=MEDDRA_HEADER,
    )

    return df
