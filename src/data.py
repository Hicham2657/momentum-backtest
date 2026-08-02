""" Load and clean monthly data from the Kenneth French data library (https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)"""

import numpy as np
import pandas as pd
import pandas_datareader.data as web

START = '1963-07'
MISSING_CODES = [-99.99, -999]

def fetch(name):
    """ Download a dataset, returns the monthly table as a decimal return (rather than %)"""
    table = web.DataReader(name, 'famafrench', START)[0]
    table.columns = [c.strip() for c in table.columns]
    return table.replace(MISSING_CODES, np.nan)/100


def build_dataset():
    """Merge the momentum strategy with the factor series"""
    factors = fetch('F-F_Research_Data_Factors')
    momentum =fetch('F-F_Momentum_Factor')
    deciles = fetch('10_Portfolios_Prior_12_2')

    strategy = (deciles['Hi PRIOR'] - deciles['Lo PRIOR']).rename('strategy')

    data = pd.concat([strategy, factors, momentum], axis=1).dropna()
    data.index = data.index.to_timestamp()
    return data


if __name__ == '__main__':
    data = build_dataset()
    print(data.shape)
    print(data.columns.tolist())
    print(data.head(3))
    print(data.tail(3))
    print("\nAnnualised mean:")
    print((data.mean() * 12).round(4))
