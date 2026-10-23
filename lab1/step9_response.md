# Step 9 — own-security instruction-file run

Security selected: Microsoft Corporation (`MSFT`; CIK `0000789019`). I selected it because it is a liquid US-listed common stock with a stable current ticker, SEC filing coverage, and an easily auditable permanent identifier; it is a deliberately clean comparison against NVDA rather than an attempt to manufacture an edge case.

## Response produced under `standing_instructions.md`

Requested quantity: **daily unadjusted OHLCV reconciliation** for MSFT, 2024-06-05 through 2024-06-13.

Primitives: date; open; high; low; close; volume; permanent entity identifier. Unit: USD per share for OHLC and shares for volume. Frequency: daily US trading session. The permanent identifier is SEC CIK `0000789019`, retrieved 2026-08-27 from SEC EDGAR. A current ticker is only a lookup label; it is not the series key.

Source 1 was Yahoo Finance through `yfinance`, retrieved 2026-08-27, with `auto_adjust=False` and `actions=True`; raw rows are saved by `lab1.py`. Source 2 was Financial Datasets Prices API, intended via `https://api.financialdatasets.ai/prices/` with daily interval and the identical date window. On 2026-08-27 the access route was attempted by checking the required local `FINANCIAL_DATASETS_API_KEY`; no key was present, so no second value was invented. This would have been an independent source because it has a separate API and data-production chain from Yahoo.

The internal OHLC test is computed by `lab1.py`; its output is `output/internal_consistency_flags.csv`. The cross-source comparison and adjudication remain unresolved until the key is supplied. The correct conclusion is not “MSFT agreed with Yahoo”; it is “MSFT has one retrieved source and cannot yet meet the two-source reconciliation requirement.”

Concrete difference from the NVDA training case: the NVDA raw series includes a 10-for-1 stock split on 2024-06-10, whereas the selected MSFT slice has no split. That makes the unadjusted-versus-adjusted convention especially important for NVDA, even though the desired reconciliation window is otherwise very short.
