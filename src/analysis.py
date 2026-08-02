"""Factor regressions and risk statistics for the momentum strategy"""

import pandas as pd
import statsmodels.api as sm

from data import build_dataset, load_average_firm_size

MODELS = {
    'Market': ['Mkt-RF'],
    'FF3': ['Mkt-RF', 'SMB', 'HML'],
    'FF4': ['Mkt-RF', 'SMB', 'HML', 'Mom'],
}

HAC_LAGS = 6
MONTHS = 12
TURNOVER_GRID = [0.2, 0.4, 0.6, 0.8, 1.0]

SUB_PERIODS = {
    '1963-1984': ('1963-07', '1984-12'),
    '1985-2005': ('1985-01', '2005-12'),
    '2006-2026': ('2006-01', '2026-05'),
}


def run_regression(data, regressors, lags=HAC_LAGS):
    """regress on given factors with HAC errors"""
    X = sm.add_constant(data[regressors])
    return sm.OLS(data['strategy'], X).fit(
        cov_type='HAC', cov_kwds={'maxlags': lags}
    )



def summarise(data, lags=HAC_LAGS):
    """Alpha, confidence interval and loadings for each model"""
    rows = {}
    for name, regressors in MODELS.items():
        fit = run_regression(data, regressors, lags)
        low, high = fit.conf_int().loc['const']
        row = {
            'alpha (ann. %)': fit.params['const'] * MONTHS * 100,
            'CI low': low * MONTHS * 100,
            'CI high': high * MONTHS * 100,
            't-stat': fit.tvalues['const'],
            'R2': fit.rsquared_adj,
        }
        row.update({f: fit.params[f] for f in regressors})
        rows[name] = row
    return pd.DataFrame(rows).T


def describe(returns):
    """Risk and distribution statistics for a monthly return series"""
    cumulative = (1 + returns).cumprod()
    drawdown = cumulative / cumulative.cummax() - 1
    return pd.Series({
        'mean (ann. %)': returns.mean() * MONTHS * 100,
        'volatility (ann. %)': returns.std() * MONTHS ** 0.5 * 100,
        'Sharpe (ann.)': returns.mean() / returns.std() * MONTHS ** 0.5,
        'skewness': returns.skew(),
        'excess kurtosis': returns.kurt(),
        'autocorr (lag 1)': returns.autocorr(1),
        'max drawdown (%)': drawdown.min() * 100,
        'worst month (%)': returns.min() * 100,
        'best month (%)': returns.max() * 100,
    })


def break_even_costs(data, turnovers=TURNOVER_GRID):
    """ constant monthly cost shifts the intercept without affecting the loadings, so net_alpha = gross_alpha - turnover*cost"""
    alpha_monthly = run_regression(data, MODELS['FF4']).params['const']
    return pd.DataFrame({
        'monthly turnover': turnovers,
        'break-even cost (bp)': [alpha_monthly / t * 10_000 for t in turnovers],
    }).set_index('monthly turnover')



def sub_period_alphas(data, periods=SUB_PERIODS):
    """alpha estimated on the 3 blocks """
    rows = {}
    for label, (start, end) in periods.items():
        block = data.loc[start:end]
        fit = run_regression(block, MODELS['FF4'])
        low, high = fit.conf_int().loc['const']
        rows[label] = {
            'months': len(block),
            'alpha (ann. %)': fit.params['const'] * MONTHS * 100,
            'CI low': low * MONTHS * 100,
            'CI high': high * MONTHS * 100,
            't-stat': fit.tvalues['const'],
            'Mom': fit.params['Mom'],
        }
    return pd.DataFrame(rows).T

def main():
    data = build_dataset()

    print(f"Sample: {data.index.min():%Y-%m} to {data.index.max():%Y-%m}, "f"{len(data)} monthly observations\n")
    print("-----------------------------------------")
    print("Factor regressions:")
    print(summarise(data).round(3), "\n")
    print("-----------------------------------------")
    print("Risk statistics:")
    print(describe(data['strategy']).round(3), "\n")
    print("-----------------------------------------")

    strategy = data['strategy']
    worst, best = strategy.idxmin(), strategy.idxmax()
    print(f"Worst month: {worst:%Y-%m} at {strategy.min() * 100:.2f}%")
    print(f"Best month:  {best:%Y-%m} at {strategy.max() * 100:.2f}%\n")

    print("-----------------------------------------")

    print("Average firm size by decile ($m):")
    print(load_average_firm_size().mean().round(0), "\n")
    print("-----------------------------------------")
    print("Correlation with the published momentum factor (Mom):")
    print(data[['strategy', 'Mom']].corr().round(3), "\n")
    print("-----------------------------------------")
    print("Break-even transaction costs (FF4 alpha):")
    print(break_even_costs(data).round(1), "\n")
    print("-----------------------------------------")
    print("FF4 alpha by sub-period:")
    print(sub_period_alphas(data).round(3), "\n")


if __name__ == '__main__':
    main()