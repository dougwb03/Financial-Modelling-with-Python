"""MSF Financial Modeling — Week 1 Lab 1 reproducible pull and reconciliation.

Run: python3 -m pip install -r requirements.txt && python3 lab1.py
Optional independent second Gen-2 pull:
  export FINANCIAL_DATASETS_API_KEY='...'
The program never writes an invented second source: without that key it records the
qualifying access attempt and leaves the cross-source comparison unresolved.
"""
from __future__ import annotations

import json
import os
import time
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf

OUT = Path("output")
RAW = OUT / "raw"
OUT.mkdir(exist_ok=True)
RAW.mkdir(exist_ok=True)
TODAY = date.today().isoformat()
UA = {"User-Agent": "MSF Financial Modeling Lab contact: replace-with-your-email@example.edu"}
FIELDS = ["Open", "High", "Low", "Close", "Volume"]


def timed(label, action):
    started = time.perf_counter()
    result = action()
    return result, time.perf_counter() - started


def yahoo(symbol: str, start: str, end_inclusive: str) -> pd.DataFrame:
    # yfinance end is exclusive. Keep the vendor's adjusted close and cash actions.
    end = (pd.Timestamp(end_inclusive) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    df = yf.Ticker(symbol).history(start=start, end=end, auto_adjust=False, actions=True)
    if df.empty:
        raise RuntimeError(f"Yahoo returned no rows for {symbol}.")
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    return df


def financial_datasets(symbol: str, start: str, end: str) -> pd.DataFrame | None:
    key = os.getenv("FINANCIAL_DATASETS_API_KEY")
    if not key:
        return None
    response = requests.get(
        "https://api.financialdatasets.ai/prices/",
        params={"ticker": symbol, "interval": "day", "start_date": start, "end_date": end},
        headers={"X-API-KEY": key}, timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    (RAW / f"financial_datasets_{symbol}_{start}_{end}.json").write_text(json.dumps(payload, indent=2))
    rows = payload.get("prices", [])
    if not rows:
        raise RuntimeError(f"Financial Datasets returned no prices: {payload}")
    df = pd.DataFrame(rows).rename(columns=str.title).rename(columns={"Time": "Date"})
    df["Date"] = pd.to_datetime(df["Date"]).dt.normalize()
    return df.set_index("Date")[["Open", "High", "Low", "Close", "Volume"]].sort_index()


def sec_cik(symbol: str) -> tuple[str, str]:
    response = requests.get("https://www.sec.gov/files/company_tickers.json", headers=UA, timeout=30)
    response.raise_for_status()
    payload = response.json()
    for row in payload.values():
        if row["ticker"].upper() == symbol.upper():
            return f"{int(row['cik_str']):010d}", row["title"]
    raise LookupError(f"{symbol} is absent from SEC company_tickers.json")


def consistency(df: pd.DataFrame, source: str) -> pd.DataFrame:
    out = []
    for dt, row in df.iterrows():
        issues = []
        if row.High < max(row.Open, row.Close): issues.append("high below max(open, close)")
        if row.Low > min(row.Open, row.Close): issues.append("low above min(open, close)")
        move = abs(row.Close - row.Open) / row.Open
        spread = (row.High - row.Low) / row.Open
        # A 10x range-to-body ratio is a review flag, not a proof of error.
        if move > 0 and spread / move > 10: issues.append("range >10x open-close move (review)")
        if issues: out.append({"date": dt.date().isoformat(), "source": source, "issue": "; ".join(issues)})
    return pd.DataFrame(out, columns=["date", "source", "issue"])


def comparison(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    joined = a[FIELDS].join(b[FIELDS], lsuffix="_yahoo", rsuffix="_fd", how="inner")
    rows = []
    for dt, row in joined.iterrows():
        for field in FIELDS:
            left, right = row[f"{field}_yahoo"], row[f"{field}_fd"]
            # $0.005 and one share are conventional rounding tolerances for this lab.
            tol = 1 if field == "Volume" else 0.005
            if abs(left - right) > tol:
                rows.append({"date": dt.date().isoformat(), "field": field.lower(),
                             "yahoo": left, "financial_datasets": right,
                             "difference_pct": (right / left - 1) * 100})
    return pd.DataFrame(rows, columns=["date", "field", "yahoo", "financial_datasets", "difference_pct"])


def security_master(symbol: str, cik: str, company: str, prices: pd.DataFrame) -> pd.DataFrame:
    out = prices.reset_index().rename(columns={"Date": "date", "Stock Splits": "stock_splits", "Adj Close": "adj_close", "Dividends": "dividends"})
    out.insert(0, "ticker", symbol)
    out.insert(1, "permanent_identifier", f"CIK {cik}")
    out.insert(2, "entity", company)
    out["date"] = pd.to_datetime(out["date"]).dt.date.astype(str)
    return out


def main() -> None:
    training, own = "NVDA", "MSFT"  # Own-security choice is documented in source_log.md.
    nvda, yahoo_seconds = timed("Yahoo NVDA", lambda: yahoo(training, "2024-06-05", "2025-06-10"))
    msft, own_seconds = timed("Yahoo MSFT", lambda: yahoo(own, "2024-06-05", "2025-06-10"))
    nvda.to_csv(RAW / "yahoo_NVDA_2024-06-05_2025-06-10.csv")
    msft.to_csv(RAW / "yahoo_MSFT_2024-06-05_2025-06-10.csv")
    (nvda_cik, nvda_name), sec_seconds = timed("SEC CIK lookup", lambda: sec_cik(training))
    msft_cik, msft_name = sec_cik(own)
    pd.concat([security_master(training, nvda_cik, nvda_name, nvda), security_master(own, msft_cik, msft_name, msft)]).to_csv(OUT / "security_master.csv", index=False)

    p = nvda.loc[pd.Timestamp("2024-06-10"):pd.Timestamp("2025-06-10")]
    p0, pt = p.iloc[0]["Close"], p.iloc[-1]["Close"]
    a0, at = p.iloc[0]["Adj Close"], p.iloc[-1]["Adj Close"]
    dividends = p["Dividends"].sum()
    price_return, income_return = pt / p0 - 1, dividends / p0
    total_cash, total_adjusted = (pt + dividends) / p0 - 1, at / a0 - 1
    returns = pd.DataFrame([{"P0": p0, "Pt": pt, "sum_dividends": dividends,
        "price_return_pct": 100 * price_return, "income_return_pct": 100 * income_return,
        "total_return_cash_pct": 100 * total_cash, "total_return_adjusted_pct": 100 * total_adjusted,
        "gap_bp_adjusted_minus_cash": 10000 * (total_adjusted - total_cash)}])
    returns.to_csv(OUT / "nvda_returns.csv", index=False)

    window = nvda.loc["2024-06-05":"2024-06-13"]
    fd, fd_seconds = timed("Financial Datasets NVDA", lambda: financial_datasets(training, "2024-06-05", "2024-06-13"))
    own_window = msft.loc["2024-06-05":"2024-06-13"]
    own_fd = financial_datasets(own, "2024-06-05", "2024-06-13") if fd is not None else None
    checks = [consistency(window, "Yahoo"), consistency(own_window, "Yahoo")]
    if fd is not None:
        checks.append(consistency(fd, "Financial Datasets"))
        comparison(window, fd).to_csv(OUT / "nvda_disagreements.csv", index=False)
        checks.append(consistency(own_fd, "Financial Datasets"))
        comparison(own_window, own_fd).to_csv(OUT / "own_security_disagreements.csv", index=False)
    else:
        pd.DataFrame(columns=["date", "field", "yahoo", "financial_datasets", "difference_pct"]).to_csv(OUT / "nvda_disagreements.csv", index=False)
        pd.DataFrame(columns=["date", "field", "yahoo", "financial_datasets", "difference_pct"]).to_csv(OUT / "own_security_disagreements.csv", index=False)
    pd.concat(checks).to_csv(OUT / "internal_consistency_flags.csv", index=False)

    report = f"""# Lab 1 run record\n\nRetrieved: {TODAY} UTC; this file is regenerated by `python3 lab1.py`.\n\n## Step 1 — generation pulls\n\n| Source | Generation | Pull | Authentication | Nothing-to-data | Result |\n|---|---:|---|---|---:|---|\n| SEC EDGAR | 2 | `company_tickers.json`; NVDA and MSFT CIKs | None; SEC User-Agent supplied | {sec_seconds:.2f}s for Yahoo pricing pull; SEC request is made in same run | working |\n| Yahoo Finance via yfinance | 2 / unofficial public interface | daily OHLCV, adjusted close, dividends, splits | No account | {sec_seconds:.2f}s (NVDA) | working |\n| Financial Datasets Prices API | 2 | NVDA daily OHLCV | `X-API-KEY` from `FINANCIAL_DATASETS_API_KEY` | {fd_seconds:.2f}s | {'working' if fd is not None else 'not attempted: key absent'} |\n| WRDS / CRSP | 1 | not pulled | account route: WRDS web/API | — | pending account evidence from student |\n| LSEG Workspace / CodeBook | 1 | not pulled | Workspace entitlement / APPKEY | — | pending account evidence from student |\n\n## Step 4 — NVDA return, 2024-06-10 through 2025-06-10\n\n```text\nP0 = {p0:.2f}   Pt = {pt:.2f}   sum D = {dividends:.2f}\nprice return   = {price_return:7.2%}\nincome return  = {income_return:7.2%}\ntotal return   = {total_cash:7.2%}   (price + dividends)\ntotal return   = {total_adjusted:7.2%}   (adjusted close)\ngap            = {10000*(total_adjusted-total_cash):7.1f} bp\n```\n\nAdjusted close compounds dividends at their ex-date; the simple price-plus-dividends method treats every cash dividend as if it were received at the end, so with positive interim dividends the adjusted-close return is weakly higher.\n\n## Step 5 — reconciliation status\n\nThe comparison table is `output/nvda_disagreements.csv`. {'It contains the cells beyond tolerance.' if fd is not None else 'It is intentionally empty because no Financial Datasets key was supplied; this is unresolved, not evidence of agreement.'} Internal-rule flags are in `output/internal_consistency_flags.csv`. The high/low tests catch malformed OHLC bars; the range-to-body flag catches suspicious spikes or scale errors, but neither catches a uniform vendor convention difference such as consolidated volume.\n\n## Step 7 — identifiers\n\nNVDA: CIK {nvda_cik}, {nvda_name}. MSFT: CIK {msft_cik}, {msft_name}. CIK comes from SEC `company_tickers.json`; it is copied to every row in `security_master.csv`. Name/ticker-history confirmation requires SEC submissions/companyfacts review and is left as an explicit student verification item rather than asserted from this endpoint alone.\n"""
    report = report.replace(
        f"| SEC EDGAR | 2 | `company_tickers.json`; NVDA and MSFT CIKs | None; SEC User-Agent supplied | {sec_seconds:.2f}s for Yahoo pricing pull; SEC request is made in same run | working |",
        f"| SEC EDGAR | 2 | `company_tickers.json`; NVDA and MSFT CIKs | None; SEC User-Agent supplied | {sec_seconds:.2f}s | working |",
    ).replace(
        f"| Yahoo Finance via yfinance | 2 / unofficial public interface | daily OHLCV, adjusted close, dividends, splits | No account | {sec_seconds:.2f}s (NVDA) | working |",
        f"| Yahoo Finance via yfinance | 2 / unofficial public interface | daily OHLCV, adjusted close, dividends, splits | No account | {yahoo_seconds:.2f}s (NVDA) | working |",
    )
    (OUT / "run_record.md").write_text(report)
    print(report)


if __name__ == "__main__":
    main()
