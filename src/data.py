""" Load and clean monthly data from the Kenneth French data library (https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) """

from functools import lru_cache

import numpy as np
import pandas as pd
import pandas_datareader.data as web

START = '1963-07'
MISSING_CODES = [-99.99, -999]
DECILES = '10_Portfolios_Prior_12_2'


@lru_cache(maxsize=None)
def _download(name):
    """Fetch dataset once and keep it in cahce."""
    return web.DataReader(name, 'famafrench', start=START)


def _clean(table):
    """Data cleaning"""
    table = table.copy()
    table.columns = [c.strip() for c in table.columns]
    return table.replace(MISSING_CODES, np.nan)


def fetch(name, table=0):
    """ return monthly table as decimal returns """
    return _clean(_download(name)[table]) / 100


def load_decile_returns():
    """Monthly value weighted returns of the ten momentum deciles"""
    return fetch(DECILES)


def load_average_firm_size():
    return _clean(_download(DECILES)[5])


def build_dataset():
    """concat the momentum strategy with the factors."""
    factors = fetch('F-F_Research_Data_Factors')
    momentum = fetch('F-F_Momentum_Factor')
    deciles = load_decile_returns()

    # Long-short (Self-financing,)
    strategy = (deciles['Hi PRIOR'] - deciles['Lo PRIOR']).rename('strategy')

    data = pd.concat([strategy, factors, momentum], axis=1).dropna()
    data.index = data.index.to_timestamp()
    return data


if __name__ == '__main__':
    data = build_dataset()
    print(data.shape)
    print(data.columns.tolist())
    print(data.head(5))
    print(data.tail(5))
    print("\nAnnualised mean:")
    print((data.mean() * 12).round(4))