# Lab 2 output summary — lab2

Sample: 2022-03-01 through 2023-08-31.

## Step 2 — coverage inventory

| requested | rows_returned | coverage_window | spans_sample |
|---|---|---|---|
| JPM | 379 | 2022-03-01 to 2023-08-31 | True |
| BAC | 379 | 2022-03-01 to 2023-08-31 | True |
| WFC | 379 | 2022-03-01 to 2023-08-31 | True |
| C | 379 | 2022-03-01 to 2023-08-31 | True |
| USB | 379 | 2022-03-01 to 2023-08-31 | True |
| PNC | 379 | 2022-03-01 to 2023-08-31 | True |
| TFC | 379 | 2022-03-01 to 2023-08-31 | True |
| RF | 379 | 2022-03-01 to 2023-08-31 | True |
| KEY | 379 | 2022-03-01 to 2023-08-31 | True |
| WAL | 379 | 2022-03-01 to 2023-08-31 | True |
| FRC | 0 | — | False |
| SBNY | 0 | — | False |

Usable full-window names: 10 of 12. Attrition: 2 of 12 (16.7%).

## Step 5 — knowability

| company | permanent_identifier | metric | unit | value | period_end | filing_date | lag_days | first_usable_date | form | accession |
|---|---|---|---|---|---|---|---|---|---|---|
| JPM | CIK 0000019617 | Assets | USD | 3868240000000 | 2023-06-30 | 2023-08-03 | 34 | 2023-08-03 | 10-Q | 0000019617-23-000432 |

The first usable date is the SEC filing date, not the period end. Proposed panel policy: treat a fundamental as usable 45 calendar days after period end, which is more conservative than 30 days and protects against typical reporting lags; use the later of that policy date and the actual filing date.

## Files to use in the written submission

- `output/coverage_inventory.csv`: requested name, returned rows, coverage, span test.
- `output/current_ticker_resolution.csv`: current-name/exchange/market-cap label check.
- `output/panel_security_master.csv`: Week 3 input; every returned row has a permanent identifier or is visibly `UNRESOLVED`.
- `data_quality_issues.md`: catalog and the exact limitation to carry into Week 3.
