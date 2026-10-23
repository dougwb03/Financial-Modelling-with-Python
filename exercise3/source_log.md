# Exercise 3 — Source log

This log covers the sources used in the completed Lab 3 and Lab 4 work. All calculations use the 2015-07 through 2025-06 monthly return window unless another window is stated.

| Source | Access route / date | Role | Independence / limitation |
|---|---|---|---|
| Ken French Data Library, Fama/French 3 Factors | Local copy `lab3/F-F_Research_Data_Factors.csv`, originally downloaded from the Fama/French 3 Factors CSV page; used 2026-09-20 | Monthly Mkt-RF and RF; the RF rate forms security excess returns and Mkt-RF is the primary regression factor | Public academic data; factor conventions differ from a tradable ETF benchmark. |
| Yahoo Finance price history via `yfinance` | `yf.download`, adjusted close, used 2026-09-20 | Month-end adjusted prices for the 11 tickers, SPY, and RSP; simple monthly returns and the Step 7 investable-benchmark regressions | Public vendor feed, not survivorship-free; does not restore missing/delisted requested panel names. |
| Yahoo Finance JPM quote page | <https://finance.yahoo.com/quote/JPM/>; retrieved 2026-09-20 | Step 6 independent reference: JPM `Beta (5Y Monthly)` = 0.98 | Vendor does not disclose every beta convention. The matched JPM-on-SPY rerun is therefore called provisional. |
| U.S. SEC EDGAR | `company_tickers.json` and `data.sec.gov/api/xbrl/companyfacts`; Lab 2 run recorded 2026-08-30 | Lab 2 issuer identity and fundamental-availability evidence, carried into the data-quality catalog | Primary regulatory source; it does not provide historical membership or delisting returns. |
| WRDS / CRSP | No WRDS table was accessed for this exercise; access was not established as of 2026-09-20 | Intended professional independent source for permanent identifiers, historical membership, and delisting returns | This is the unresolved route for the Blocker. No CRSP result is represented as having been obtained. Before a survivorship-free sector claim, document the exact WRDS access attempt and query/table used. |

## Source limitations carried into the claims

The French and Yahoo sources support reproducible calculations for the surviving continuous-coverage ticker subset. They do not resolve the two requested names absent from the price response or end-of-sample survivor selection. Consequently, the Exercise 3 reports do not make a survivorship-free bank-sector alpha claim.

## AI disclosure

Codex was used to inspect the existing work, add and execute the requested analysis cells, produce the markdown records, and write this source log. The user remains responsible for reviewing the calculations and for accurately representing the stated source-access limitation.
