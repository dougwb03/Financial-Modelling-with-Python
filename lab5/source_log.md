# Lab 5 source log

| Source | Access route | Coverage / use | Retrieved | Notes |
|---|---|---|---|---|
| Lab 5 handout and rules | Course page supplied by instructor | ABG balances, drivers, known-answer checks | 2026-09-23 | Classroom `guidance`; used exactly as supplied. |
| SEC EDGAR Company Facts | `data.sec.gov/api/xbrl/companyfacts/CIK0001341439.json` and `CIK0000789019.json`, with identifying User-Agent | Target-lock annual revenue, operating income, assets, fiscal dates/accessions | 2026-09-23 | Filed data; cross-check the cited 10-K statements. |
| SEC EDGAR filing archive | Accession-specific 10-K documents | Controlling source and merger-screen review | 2026-09-23 | Filing wins over provider field if values disagree. |
| WRDS / Compustat | Previously used institutional WRDS connection; Compustat North America Fundamentals Annual query planned for Week 6 | Professional secondary source for Oracle and Microsoft historical fundamentals | 2026-09-23 | Access is expected to be available next week. Export and compare the relevant annual fields then; do not represent Compustat values as retrieved until the query is run. |
| Yahoo Finance via `yfinance` | Notebook run-time history call | Dated ABG market close beside DCF | At run time | Preserve printed date and close in notebook. |

All target-lock amounts are USD millions. The notebook labels supplied opening data and drivers as guidance, the discount rate and terminal growth as judgments, and shares as fact.
