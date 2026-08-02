# Specification

I wrote this before running any regression, so that the results cannot be the product of parameter tuning.

## Question

How much of the gross return of a decile momentum strategy survives once standard risk factors and transaction costs are taken into account?

My work consists of a decomposition, not a search for alpha. A result of "no remaining alpha" is a valid outcome and is reported.

## Data

- Source: Kenneth French Data Library.
- Datasets: `F-F_Research_Data_Factors`, `F-F_Momentum_Factor`,
  `10_Portfolios_Prior_12_2`.
- Sample: 1963-07 to 2026-05, 755 monthly observations.
- Missing values: -99.99 and -999 -> NaN, before rescaling
- Returns are converted from percent to decimal once at loading time.

## Strategy

- Definition: `Hi PRIOR` minus `Lo PRIOR`.
- Weighting: value-weighted, not equal-weighted. Equal weighting gives a very small company the same weight as a very large one, which produces higher returns that could not be captured in reality.
- The strategy is self-financing: the short funds the long, so the net capital outlay is zero. It is therefore already an excess return and `RF` is not subtracted.

## Models

Three regressions, the dependent variable is the strategy return in every case.

1. Market: `Mkt-RF`
2. FF3: `Mkt-RF`, `SMB`, `HML`
3. FF4: `Mkt-RF`, `SMB`, `HML`, `Mom`

The intercept is the alpha, reported annualised as `alpha * 12`.

Note on interpretation (stated in advance): the strategy is decile 10 minus decile 1, whereas Mom is a 2x3 sort averaged across size groups. The strategy is therefore a more extreme, less diversified version of the same effect, and its momentum loading (FF4 regression) is expected to exceed one. Any alpha that survives FF4 measures what that extra concentration adds and is likely to be eroded by transaction costs because the short leg is concentrated in the smallest and least liquid stocks.

## Inference

- Estimator: OLS.
- Standard errors: Newey-West HAC, lag 6.
- OLS standard errors assume i.i.d. residuals. Monthly equity returns are heteroskedastic and autocorrelated, so those standard errors are too small and t-statistics are inflated.
- Significance threshold: |t| > 1.96.

## Descriptive statistics

I will report on the full sample, for the strategy return series: annualised mean and volatility, Sharpe ratio, skewness, excess kurtosis, first order autocorrelation, maximum drawdown, and the best and worst single months.

Average firm size per decile is also reported, to establish which leg of the strategy holds the least liquid stocks (added after regressions).

## Robustness

Fixed here and run once.

- Transaction costs: a constant monthly cost shifts the regression intercept without affecting the loadings, so net alpha equals gross alpha minus turnover times cost. Turnover is not observable from these data. A grid of monthly turnover assumptions is therefore applied (from 20% up to 100% turnover), and the break-even cost (the level at which net alpha reaches zero) is reported for each. A single cost is applied to both legs, which is optimistic because costs are naturally higher on the short leg.
- Comparison with `Mom`: correlation and difference in annualised means, to quantify how much of the strategy is the published factor in a more extreme form.
- Sub-periods: three non overlapping blocks of roughly equal length (1963-1984, 1985-2005, 2006-2026), so that each estimate rests on a  comparable number of observations. FF4 is rerun on each. Each block holds about a third of the sample, so t-statistics are expected to fall by a factor of about sqrt(3).

## Limitations
- My project does not build signal from raw prices. The portfolios are supplied pre-built
- The short leg is concentrated in small companies, since a stock that has fallen sharply has a smaller market capitalisation. Shorting costs are not modelled.
- (This was added after the regressions to see if the Alpha survives on different periods) Sub-period estimates are too imprecise to separate a stable alpha from an   eroding one. Resolving that would need a longer sample.

## Out of scope

Non-US markets, volatility models, machine learning, portfolio optimisation.