# Step 2 — source-fact verification

Verification date: 2026-08-27. The tested pull is Yahoo Finance through the `yfinance` Python package; the raw result is retained in `output/raw/` after running `python3 lab1.py`.

| Check | What I verified | Source checked against | Verdict |
|---|---|---|---|
| Package name | The installed import is `yfinance`, version 1.5.1; it is not the similarly named `yahoo_fin` package. | `python3` import/version output, captured in the run terminal | Checked out |
| Endpoint / method | The code calls `yf.Ticker(symbol).history(start=…, end=…, auto_adjust=False, actions=True)`, which returns historical bars and corporate actions. | The executable call in `lab1.py` and the saved raw CSV | Checked out |
| Field names | The returned frame includes `Open`, `High`, `Low`, `Close`, `Adj Close`, `Volume`, `Dividends`, and `Stock Splits`; `Adj Close` is not substituted for `Close`. | CSV header in `output/raw/yahoo_NVDA_2024-06-05_2025-06-10.csv` | Checked out |
| Coverage window | NVDA starts 2024-06-05 and includes 2025-06-10; the reconciliation slice has all seven trading dates from 2024-06-05 through 2024-06-13. | First/last dates and row dates in the saved CSV | Checked out |
| Licence / permitted use | The interface is an unofficial public-data wrapper, not a professional licensed feed. It must not be represented as CRSP/Refinitiv data, and any redistribution/commercial-use condition must be checked against the provider terms before use beyond this coursework. | Provider/package documentation and terms review to be attached by student if the course rules require a specific licence citation | Provisionally checked; no professional-use claim made |

Nothing in the four machine-verifiable checks contradicted the code. The licence item is deliberately qualified: “the code ran” is not proof of redistribution rights.
