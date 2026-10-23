# Source log — Lab 4

This log extends, but does not overwrite, the Lab 2 source log at `lab2/source_log_lab2.md`. Lab 4 performs no new market-data download: it uses the saved Lab 3 inputs below.

| Source | Access route / record | Role in Lab 4 | Independence / limitation |
|---|---|---|---|
| Lab 3 saved excess-return panel | `lab3/week4_monthly_excess_returns.csv`; loaded 2026-09-20 | 120 monthly excess returns for the 11-name panel; split into two 60-month windows | Derived Lab 3 analytical input; not an independent raw-data source |
| Lab 3 saved covariance matrix | `lab3/week4_annualized_excess_covariance.csv`; loaded 2026-09-20 | Annual covariance sanity check in Step 0 | Derived Lab 3 analytical input; recalculated within each window for optimization |
| Fama/French Research Data Factors | Lab 3 file `lab3/F-F_Research_Data_Factors.csv` | Risk-free rate used upstream to form the saved excess returns | Public academic data source; retained as documented in Lab 3 |
| Yahoo Finance via `yfinance` | Lab 3 data acquisition, documented in `lab3/lab3_notebook.ipynb` | Adjusted prices used upstream to form monthly total returns | Public vendor feed; not survivorship-free; limitation carried forward from Lab 3 |
| Week 4 prework page | https://cinderzhang.github.io/PythonFinance2026-site/week4/prework.html; consulted 2026-09-20 | Defines the cap feasibility floor and pre-optimization timing requirement | Course instruction, not a market-data source |

## Lab 4 convention carried forward

Returns are simple monthly **excess** returns. The saved Lab 3 covariance matrix is annualized; the optimizers in this notebook recompute covariance on monthly returns in the applicable estimation window. Performance annualizes arithmetic mean excess return by 12 and volatility by √12.
