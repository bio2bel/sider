# -*- coding: utf-8 -*-

import logging

import pandas as pd

from bio2bel import make_downloader
from bio2bel_sider.constants import INDICATIONS_HEADER, INDICATIONS_PATH, INDICATIONS_URL

__all__ = [
    'download_indications',
    'get_indications_df',
]

log = logging.getLogger(__name__)

download_indications = make_downloader(INDICATIONS_URL, INDICATIONS_PATH)


def get_indications_df(url=None, cache=True, force_download=False):
    """Loads the indications into a data frame

    :param Optional[str] url: A custom path to use for data
    :param bool cache: If true, the data is downloaded to the file system, else it is loaded from the internet
    :param bool force_download: If true, overwrites a previously cached file
    :rtype: pandas.DataFrame
    """
    if url is None and cache:
        url = download_indications(force_download=force_download)

    df = pd.read_csv(
        url or INDICATIONS_URL,
        sep='\t',
        names=INDICATIONS_HEADER,
    )

    return df
