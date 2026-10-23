# Source log and adjudication record

Run date: 2026-08-27. Re-run `python3 lab1.py` to refresh the raw extracts and numerical outputs. All price dates below are US trading dates and all prices are USD per share.

| Source | Access route and authentication | Pull / coverage window | Fields and conventions | Status |
|---|---|---|---|---|
| SEC EDGAR | `https://www.sec.gov/files/company_tickers.json`, public request with identifying User-Agent | NVDA and MSFT identifier lookup, retrieved 2026-08-27 | CIK is an SEC permanent entity identifier; the ticker table supplies current display tickers and names, not a price history | Working Generation 2 pull |
| Yahoo Finance via `yfinance` | `yf.Ticker(...).history`; no account | NVDA and MSFT daily data, 2024-06-05–2025-06-10; NVDA reconciliation slice 2024-06-05–2024-06-13 | Unadjusted OHLC, vendor adjusted close, volume, cash dividends, stock splits. `auto_adjust=False` prevents accidental replacement of Close by adjusted values. | Working public pull; not a professional source |
| Financial Datasets Prices API | `https://api.financialdatasets.ai/prices/`; header `X-API-KEY: $FINANCIAL_DATASETS_API_KEY` | Intended: NVDA and MSFT daily OHLCV, 2024-06-05–2024-06-13 | API documentation specifies `ticker`, `interval=day`, `start_date`, `end_date` and returns OHLCV. It does not supply adjusted close/dividend fields in the documented bar response. | Qualifying attempt not yet made: key absent from this workspace on 2026-08-27. Independent because it is a separate vendor/API from Yahoo. |
| WRDS / CRSP | WRDS account / web or Python access | Intended: permanent identifier and survivorship-aware price history | CRSP conventions must be recorded from the table/data guide once access clears. | Pending student account clearance; no result asserted. |
| LSEG Workspace / CodeBook | Workspace APPKEY/CodeBook entitlement route | Intended: entitlement diagnostic and, if entitled, independent professional price extract | Workspace field and exchange permissions are account-specific. | Pending personal account evidence; no result asserted. |

## Reconciliation and adjudications

The executable produces `output/nvda_disagreements.csv` (training case) and `output/own_security_disagreements.csv` (MSFT) only after the Financial Datasets key is provided. Without it, empty tables mean **unresolved because the independent pull is absent**, not agreement. Do not submit them as a completed Step 5/6 result.

For each generated difference, add one entry in this form before submission:

> Field/date: _._ Difference: _._ Verdict: defect / convention difference / unresolved. Evidence: name the cell comparison plus the relevant internal consistency result, corporate action, vendor documentation, or exchange fact. Resolution: select _source/value_ for the reconciled series because _reason_.

Internal checks are automated in `output/internal_consistency_flags.csv`: high below max(open, close); low above min(open, close); and a review flag where intraday range exceeds ten times a nonzero open-close move. The first two catch impossible OHLC bars. The range check can reveal a decimal/split/outlier issue but cannot establish a volume-consolidation convention difference; a cross-source, persistent-volume pattern would be the relevant evidence for that.

## Permanent-identifier permanence check

NVDA — CIK `0001045810`, entity `NVIDIA CORP`. SEC submissions endpoint `https://data.sec.gov/submissions/CIK0001045810.json`, retrieved 2026-08-27, reports former name `NVIDIA CORP/CA` from 1998-05-07 through 2002-06-04 and current ticker `NVDA`. No NVDA ticker change is reported in the lab window (2024-06-05–2025-06-10); the CIK did not change.

MSFT — CIK `0000789019`, entity `MICROSOFT CORP`. SEC submissions endpoint `https://data.sec.gov/submissions/CIK0000789019.json`, retrieved 2026-08-27, reports no former names and current ticker `MSFT`. No name or ticker change is reported in the lab window.

Ticker-keyed long-window analysis can split a single issuer into apparent separate histories when a ticker changes, dropping the pre-change or post-change observations. Event studies or ten-year return calculations would then use a truncated series and can silently misstate returns; the CIK key preserves the entity through the label change.

## Lab 2 — panel-source addendum (generated source label: lab2)

Complete the run-specific rows in [`lab2/source_log_lab2.md`](lab2/source_log_lab2.md) after running `Lab2_Colab_Submission.ipynb`. It provides explicit records for the Yahoo panel pull, SEC CIK/filing-date evidence, the WRDS/CRSP attempt, and an independent second free source. Do not represent this template as a completed access attempt until the route, date, and observed barrier/result are entered.
