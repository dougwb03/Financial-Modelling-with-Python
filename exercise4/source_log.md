# Exercise 4 source log — Oracle

| Source | Purpose | Date / period | Local evidence | Notes |
|---|---|---|---|---|
| SEC Company Facts CIK0001341439 | FY2024–FY2026 structured history | Cache inspected 2026-10-01 | `lab6/cache/CIK0001341439_companyfacts.json` | Primary source. Visible notebook extraction and provenance table use revenue, EBIT, net income, capex, cash, AR, AP, PP&E, assets, equity, and debt tags. |
| Oracle 10-K 0001193125-26-277521 | Filing-only inventory and factual validation | FY ended 2026-05-31; filed 2026-06-22 | `lab6/cache/oracle_2026_10k.htm` | Inventory $303m; Company Facts inventory tag not available for FY2026. |
| Oracle 10-Q 0001193125-26-389274 | Latest shares | Filed 2026-09-11 | `lab6/cache/oracle_2026q1.htm` | 3,023,736,000 shares as of 2026-09-07. |
| WRDS Compustat Security Daily | ORCL/SPY daily closing-price beta and dated ORCL price | 24 months ended 2026-09-30; price 2026-09-29 | `exercise4/wrds_beta_audit.csv`; `exercise4/wrds_compustat_orcl_spy_daily_returns.csv` | `prccd` return beta is 1.6369 from 501 matched daily observations. The notebook fails loudly without the successful audit/series. |
| U.S. Treasury Daily Treasury Par Yield Curve | Risk-free rate | 2026-09-29 | Official source reference | 5-year nominal CMT: 5.06%. |
| Damodaran U.S. Historical Implied ERP table | Equity risk premium | 2025 | Official NYU data reference | 4.234% implied ERP input. |

The WRDS beta calculation is `cov(ORCL daily closing-price return, SPY daily closing-price return) / var(SPY daily return)`, where return is `prccd / lag(prccd) - 1`. The prior `trfd` approach was rejected after verification because `trfd` is an adjustment factor, not a daily-return series.

The current bridge uses FY2026 year-end net debt and latest filed shares. Updating cash and debt from the latest 10-Q is a separate, optional data-refresh step that would require recalculation.

## Submission package

Include the required SEC cache `lab6/cache/CIK0001341439_companyfacts.json` and the successful WRDS beta files `exercise4/wrds_beta_audit.csv` and `exercise4/wrds_compustat_orcl_spy_daily_returns.csv`. Do not submit or rely on `exercise4/beta_source_attempts.csv` as final-beta evidence; it conflicts with the successful saved WRDS `prccd` audit.
