# Lab 4 — Thursday checkpoint record (Steps 0–5)

## Step 0 — parameter count and input checks

The Lab 3 covariance matrix is square (11 × 11), has the same names and order as the excess-return panel, is symmetric, and its diagonal matches the annualized monthly volatilities squared. The detailed diagonal evidence is saved in `outputs/step0_covariance_diagonal_check.csv`.

|  | names | months_per_estimation_window | distinct_covariance_entries | mean_estimates | total_parameters | months_per_parameter |
|---|---|---|---|---|---|---|
| 0 | 11 | 60 | 66 | 11 | 77 | 0.78 |

This is a complexity count, not degrees of freedom: each 60-month estimation window informs all estimates, but 60 observations for 77 estimated quantities is a reason to expect noise.

## Step 2 — unconstrained two-window weight swing

Gross leverage: A = 373.49; B = 5.82.

|  | weight_A | weight_B | swing_percentage_points |
|---|---|---|---|
| JPM | 9491.43% | 133.68% | -9357.7 |
| WFC | -8669.33% | 84.53% | 8753.9 |
| BAC | 6049.86% | -86.49% | -6136.4 |
| C | -4313.58% | -63.05% | 4250.5 |
| PNC | -4242.50% | 4.46% | 4247.0 |
| TFC | 1724.71% | -10.16% | -1734.9 |
| USB | 1255.52% | -46.61% | -1302.1 |
| IBM | -1141.92% | 68.76% | 1210.7 |
| CFG | -257.25% | 21.03% | 278.3 |
| ZION | 188.42% | 28.55% | -159.9 |
| KEY | 14.65% | -34.70% | -49.3 |

JPM moved most, by 9357.7 percentage points. A company-level change alone is unlikely to justify a shift of that size over adjacent five-year windows; noisy estimated means and covariances are the more plausible explanation.

## Step 3 — out of sample: window-A weights held through B

Window B is 2020-07 through 2025-06. Target weights were reset monthly but never re-estimated.

|  | annualized_excess_return | annualized_volatility | sharpe_ratio | gross_leverage |
|---|---|---|---|---|
| tangency_from_A | -258.52% | 1905.17% | -0.136 | 373.49 |
| 1/N | 18.19% | 27.42% | 0.663 | 1.00 |

**Prediction written before running:** Before running the optimizer, I predict that 1/N will have the higher out-of-sample Sharpe ratio by roughly 0.30 because each 60-month fit estimates 77 parameters from only 60 monthly observations.

**Result:** 1/N won by 0.799 Sharpe points. This agrees with the prediction.

## Step 4 — long-only portfolio with a 15% cap

The cap is feasible because 11 × 15% = 165%. It requires at least 7 names. The A fit holds 7 of 11 names and has gross leverage 1.00.

Constrained weights estimated on A:

|  | weight |
|---|---|
| JPM | 15.00% |
| PNC | 15.00% |
| TFC | 15.00% |
| ZION | 15.00% |
| BAC | 15.00% |
| CFG | 15.00% |
| C | 10.00% |
| IBM | 0.00% |
| USB | 0.00% |
| KEY | 0.00% |
| WFC | 0.00% |

In-sample Sharpe: constrained 0.279; unconstrained 1.642. The remedy gave up 1.363 of in-sample Sharpe.

|  | annualized_excess_return | annualized_volatility | sharpe_ratio | gross_leverage |
|---|---|---|---|---|
| constrained_from_A | 17.62% | 29.03% | 0.607 | 1.00 |
| 1/N | 18.19% | 27.42% | 0.663 | 1.00 |

Largest constrained A→B swing: 15.0 percentage points, compared with 9357.7 percentage points unconstrained. The cost beyond Sharpe is expressive: the remedy rules out shorts, a position over 15%, and therefore a concentrated single-name or relative-value view.

## Step 5 — cap defence and saved Week 5 portfolio

**Choice and timing:** I chose the 15% cap before running Lab 4 weight calculations, after reviewing the Lab 3 panel. Chosen before running Lab 4 weight calculations, after reviewing the Lab 3 panel.

**Strongest objection:** the cap is a judgment rather than a fact in the data. A 15% cap forces at least 7 names, but a 20% cap would force only five, so a different number can generate a different portfolio.

**Response:** I concede that the number is a choice. It is a documented risk-control preference for this small, bank-heavy panel: each five-year fit has only 0.78 months per estimated parameter. The cap prevents an estimated edge from becoming a position above 15%, while avoiding the equal-weight outcome that a 9.09% cap would force.

The saved Week 5 portfolio is `outputs/step5_week5_portfolio_weights.csv`; its constraints are beside it in `outputs/step5_week5_portfolio_constraints.json`. It is long-only, capped at 15%, fully invested, holds 8 names, and has gross leverage **1.00**. I intend to reset it to these target weights monthly; the resulting turnover and cost are reserved for Week 5.

## Checkpoint status and AI disclosure

**Stopping point:** Completed Steps 0–5. Step 6 is intentionally not started because it belongs to the after-Thursday Exercise 3 work.

**AI disclosure:** AI was used to help structure and document the notebook, implement the optimization code, and explain the cap logic. I reviewed the calculations, the declared cap, the prediction, and the interpretations against the course instructions.
