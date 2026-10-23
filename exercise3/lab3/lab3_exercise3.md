# Exercise 3 — Lab 3 record

## Step 1 — conventions

Return type: simple monthly returns from adjusted month-end close (`yfinance`, `auto_adjust=True`).  
Frequency: monthly; annualization ×12 for means and alphas, ×√12 for volatilities.  
Risk-free: RF column, Ken French Data Library, Fama/French 3 Factors monthly.  
Window: 2015-07 to 2025-06, 120 months.  
Market series: French Mkt-RF (regression); SPY (investable benchmark).  
Equal-weight: rebalanced monthly to 1/N.  
Standard deviation: sample (`ddof=1`).

## Step 3 — Sharpe comparison

| security | CAGR | ann vol | Sharpe (excess, arithmetic) | CAGR/vol, rf=0 |
|---|---|---|---|---|
| BAC | 13.17% | 29.75% | 0.502 | 0.443 |
| C | 7.39% | 32.59% | 0.326 | 0.227 |
| CFG | 8.91% | 36.45% | 0.372 | 0.245 |
| IBM | 11.29% | 23.97% | 0.489 | 0.471 |
| JPM | 18.86% | 24.50% | 0.755 | 0.770 |
| KEY | 5.63% | 34.50% | 0.281 | 0.163 |
| PNC | 10.33% | 27.02% | 0.430 | 0.382 |
| TFC | 4.66% | 28.38% | 0.241 | 0.164 |
| USB | 4.03% | 26.56% | 0.212 | 0.152 |
| WFC | 6.59% | 29.33% | 0.302 | 0.225 |
| ZION | 7.84% | 36.86% | 0.342 | 0.213 |
| EW panel | 10.00% | 26.80% | 0.423 | 0.373 |

Rank changes occur between BAC and IBM, among C, WFC, and ZION, and between KEY and TFC. I use the arithmetic-excess-return Sharpe ratio for the course because it matches the stated excess-return convention.

## Step 4 — Jensen regressions

| security | α/yr | t(α) | β | t(β) | R² | resid vol |
|---|---|---|---|---|---|---|
| BAC | -1.97% | -0.317 | 1.415 | 12.920 | 0.586 | 19.22% |
| C | -7.70% | -1.112 | 1.532 | 12.571 | 0.573 | 21.40% |
| CFG | -3.91% | -0.432 | 1.461 | 9.169 | 0.416 | 27.97% |
| IBM | 1.10% | 0.177 | 0.889 | 8.080 | 0.356 | 19.31% |
| JPM | 5.04% | 0.942 | 1.126 | 11.936 | 0.547 | 16.56% |
| KEY | -6.09% | -0.690 | 1.322 | 8.506 | 0.380 | 27.28% |
| PNC | -2.38% | -0.380 | 1.173 | 10.601 | 0.488 | 19.42% |
| TFC | -6.70% | -0.950 | 1.134 | 9.125 | 0.414 | 21.82% |
| USB | -7.02% | -1.062 | 1.060 | 9.098 | 0.412 | 20.45% |
| WFC | -4.97% | -0.674 | 1.156 | 8.909 | 0.402 | 22.77% |
| ZION | -3.04% | -0.309 | 1.310 | 7.568 | 0.327 | 30.37% |
| EW panel | -3.42% | -0.585 | 1.234 | 11.988 | 0.549 | 18.07% |

I would not stand behind any alpha as statistically reliable: none has an absolute alpha t-statistic near the usual 5% threshold of about 1.98. The equal-weight t-statistic reflects both shared market exposure and diversification of name-specific residual variation; it need not equal any member's t-statistic.

## Step 5 — risk decomposition

| security | β | total | systematic | idiosyncratic | share |
|---|---|---|---|---|---|
| BAC | 1.415 | 29.7% | 22.8% | 19.2% | 59% |
| C | 1.532 | 32.6% | 24.7% | 21.4% | 57% |
| CFG | 1.461 | 36.5% | 23.5% | 28.0% | 42% |
| IBM | 0.889 | 24.0% | 14.3% | 19.3% | 36% |
| JPM | 1.126 | 24.5% | 18.1% | 16.6% | 55% |
| KEY | 1.322 | 34.5% | 21.3% | 27.3% | 38% |
| PNC | 1.173 | 27.0% | 18.9% | 19.4% | 49% |
| TFC | 1.134 | 28.4% | 18.3% | 21.8% | 41% |
| USB | 1.060 | 26.6% | 17.1% | 20.4% | 41% |
| WFC | 1.156 | 29.3% | 18.6% | 22.8% | 40% |
| ZION | 1.310 | 36.9% | 21.1% | 30.4% | 33% |
| EW panel | 1.234 | 26.8% | 19.9% | 18.1% | 55% |

The equal-weight panel's idiosyncratic volatility is 18.07%, versus a median single-name idiosyncratic volatility of 21.40%. Equal-weighting 11 names reduced company-specific risk, but substantial residual risk remains because the panel is concentrated in related financial firms.

## Step 6 — independent JPM beta verification

Yahoo Finance's JPM quote page reported Beta (5Y Monthly) = 0.98, retrieved 2026-09-20.  

| security | beta | window | conventions |
|---|---|---|---|
| Yahoo Finance Beta (5Y Monthly) | 0.980 | Yahoo does not state; labelled 5Y Monthly | Not fully disclosed by Yahoo |
| Matched rerun (JPM on SPY) | 0.985 | 2021-09 through 2026-08 (60 complete months) | Simple returns from adjusted month-end closes; OLS with intercept on SPY |

I matched identity, frequency, 60 complete-month window, simple adjusted-close returns, SPY regressor, and an intercept OLS formula. Yahoo does not disclose all conventions, so I assume adjusted monthly total returns against an S&P 500 proxy; the 0.005 difference is provisional and consistent with rounding.

## Step 7 — benchmark defence

| benchmark | alpha_per_year | t_alpha | beta | R_squared |
|---|---|---|---|---|
| French Mkt-RF | -3.42% | -0.585 | 1.234 | 0.549 |
| SPY | -3.66% | -0.602 | 1.242 | 0.514 |
| RSP | -0.95% | -0.190 | 1.290 | 0.664 |

The strongest objection is that SPY's capitalization weighting is unlike the equal-weighted, bank-heavy panel; RSP is a plausible alternative and its alpha is materially different. I concede that benchmark sensitivity. Mkt-RF remains the stated factor benchmark and SPY the predeclared broad investable benchmark, but I report all three and make no benchmark-independent alpha claim.

## Step 8 — What these numbers can and cannot support

A **Blocker remains open**, so no headline alpha is reported for the full U.S. bank sector. These are survivor-subset descriptive results only.

| Open issue | Effect on alpha | Response |
|---|---|---|
| Requested names absent — **Blocker** | Missing failed/unavailable names leave a full-universe alpha unidentified. | **Restrict claim:** do not call this a survivorship-free bank-sector result. |
| End-of-sample universe — **High** | Survivor selection can bias alpha and historical performance. | **Bound damage:** report continuous-coverage subset only; obtain CRSP/WRDS membership and delisting returns for a sector claim. |
| Fundamental availability date — **High** | Period-end dating would create look-ahead bias if fundamentals drove a strategy. | **Fix input:** use filing date plus a 45-calendar-day availability policy before fundamental use. |

The panel can describe the realized surviving tickers under these conventions. It cannot support failed/delisted-name performance, an ex-ante bank-sector strategy, or a survivorship-free sector alpha.

## Step 9 — finding

The equal-weight alpha is negative under all three benchmarks, but RSP is materially less negative and has a higher R² than Mkt-RF or SPY. Since no alpha t-statistic is near conventional significance, this is evidence of benchmark sensitivity, not evidence that one benchmark establishes a reliable alpha.

## AI disclosure

Codex was used to help implement the calculations, assemble the requested markdown record, and explain the documented limitations. I reviewed the data, conventions, calculations, and written claims; the final submission retains the open Blocker rather than treating it as resolved.
