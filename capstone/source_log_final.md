# Source log — final audited run

The revised notebook was executed after all scenario changes. It retains the saved authenticated WRDS `prccd` beta evidence and uses dated WRDS prices only as valuation comparisons. SEC and company-reported information supports the revised operating cases; the FY2028–31 arrays remain analyst scenario judgments, not company guidance.

| Source | Purpose in revised model | Period / date | Primary link or accession | Local evidence |
|---|---|---|---|---|
| Oracle FY2026 Form 10-K | FY2026 revenue, capex, RPO schedule, historical cross-check | Year ended 2026-05-31 | [0001193125-26-277521](https://www.sec.gov/Archives/edgar/data/1341439/000119312526277521/orcl-20260531.htm) | `lab6/cache/oracle_2026_10k.htm` |
| Oracle Q1 FY2027 earnings release / 8-K exhibit | Revenue/cloud/OCI growth, RPO, FY2027 revenue guide, Q1 capex and FCF | Quarter ended 2026-08-31 | [Oracle release](https://investor.oracle.com/investor-news/news-details/2026/Oracle-Announces-Q1-Results-Driven-by-Triple-Digit-Growth-in-Cloud-Infrastructure-Revenues/default.aspx); [SEC exhibit](https://www.sec.gov/Archives/edgar/data/1341439/000119312526387905/orcl-ex99_1.htm) | `lab6/cache/oracle_2026q1.htm` |
| Oracle Q1 FY2027 Form 10-Q | Latest filed shares and Q1 balance-sheet bridge | Filed 2026-09-11 | 0001193125-26-389274 | `lab6/cache/oracle_2026q1.htm` |
| Microsoft FY2026 Form 10-K | FY2026 results, finance-lease liability, finance-lease PP&E, capex, RPO, shares and opening balances | Year ended 2026-06-30 | [0001193125-26-323660](https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm) | `lab6/cache/microsoft_2026_10k.htm`; `lab6/cache/CIK0000789019_companyfacts.json` |
| Microsoft FY2026 Q4 earnings / FY2027 guidance | FY2027 revenue and operating-income outlook, Azure 45% constant-currency guide, sub-one-point margin decline, AI capex outlook | FY2026 Q4 / FY2027 outlook | [Microsoft event materials](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4) | Reviewed and cited in revised notebook/ledger |
| Microsoft Evercore Global TMT Conference | Capacity, custom silicon, utilisation and efficiency context | FY2026 | [Microsoft event materials](https://www.microsoft.com/en-us/investor/events/fy-2026/evercore-global-tmt-conference) | Reviewed as supporting context only |
| SEC Company Facts — Oracle | Opening history and balance-sheet data | FY2026 / Q1 FY2027 | SEC company facts cache | `lab6/cache/CIK0001341439_companyfacts.json` |
| SEC Company Facts — Microsoft | Opening history and balance-sheet data | FY2026 | SEC company facts cache | `lab6/cache/CIK0000789019_companyfacts.json` |
| WRDS Compustat Security Daily — ORCL/SPY | Oracle beta: matched daily `prccd` returns, covariance divided by SPY variance | 501 returns, 2024-10-01–2026-09-30 | Authenticated WRDS query | `capstone/wrds_beta_audit.csv`; `capstone/wrds_compustat_orcl_spy_daily_returns.csv` |
| WRDS Compustat Security Daily — MSFT/SPY | Microsoft beta: matched daily `prccd` returns, covariance divided by SPY variance | 501 returns, 2024-10-01–2026-09-30 | Authenticated WRDS query | `exercise4/wrds_msft_beta_audit.csv`; `exercise4/wrds_compustat_msft_spy_daily_returns.csv` |
| WRDS Compustat Security Daily prices | Dated market-price comparisons | ORCL 2026-09-29; MSFT 2026-09-30 | Authenticated WRDS query | `lab6/outputs/wrds_compustat_latest_prices.csv` |
| U.S. Treasury 5-year nominal CMT | Risk-free-rate input retained from prior audited model | 2026-09-29 | Existing audited notebook input | 5.06% executed input |
| Damodaran U.S. implied ERP | Equity-risk-premium input retained from prior audited model | 2025 | Existing audited notebook input | 4.234% executed input |

## Evidence-to-assumption mapping

- Oracle FY2027 base revenue growth begins at 35% because management guided to at least $90bn from FY2026 revenue of $67.4bn, while Q1 FY2027 revenue grew 30%, cloud 62%, and OCI 121%. Growth fades to 8% by FY2031 rather than extrapolating hypergrowth indefinitely.
- Oracle capex intensity is retained at 70%, 55%, 42%, 32%, and 25% of revenue because the company reported FY2026 capex of $55.7bn and Q1 FY2027 capex of $28.5bn. The model does not close a valuation gap by cutting reinvestment.
- Microsoft base growth is extended at 19%, 20%, 19%, 17%, and 14%, reflecting Azure, commercial subscriptions, Copilot/agent monetisation and RPO conversion; this remains an analyst judgment beyond management's near-term guidance.
- Microsoft base capex is 45%, 38%, 30%, 23%, and 17% of revenue, preserving elevated early AI investment while allowing later moderation for GPU/CPU-heavy capacity aging and utilisation. The upside uses 45%, 37%, 28%, 22%, and 17%. The $66.594bn finance-lease liability is included in debt, WACC, and net debt; the corresponding lease PP&E is already in reported PP&E.

The final notebook cell regenerates the companion valuation exhibit. The detailed assumptions ledger is a reviewed companion Markdown file kept in sync with the same executed assumptions.
