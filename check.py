import pandas_datareader.data as web

START = '1963-07'

def load(name):
    d = web.DataReader(name, 'famafrench', start=START)
    print(f"--- {name} ---")
    print("tables :", [k for k in d.keys() if k != 'DESCR'])
    print(d[0].head(3))
    print()
    return d

if __name__ == '__main__':
    ff3 = load('F-F_Research_Data_Factors')
    mom = load('F-F_Momentum_Factor')
    p10 = load('10_Portfolios_Prior_12_2')
    print(p10)