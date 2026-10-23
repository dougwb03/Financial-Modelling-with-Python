"""MSF Financial Modeling — Week 2 Lab 2 (generated source; label: lab2).

Run in Colab after uploading this entire lab2 folder, or locally from its parent:
    python3 -m pip install yfinance pandas requests
    python3 lab2/lab2.py

The deliberate universe is a 12-name US bank-stress panel.  It is constructed using
the names known at the *end* of the sample, so that survivorship/look-ahead risk is
visible rather than silently designed away.  Change only the documented constants if
you choose a different defensible universe.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf

LABEL = "lab2"
SAMPLE_START, SAMPLE_END = "2022-03-01", "2023-08-31"
OUT = Path(__file__).resolve().parent / "output"
RAW = OUT / "raw"
UA = {"User-Agent": "MSF Financial Modeling student contact: replace-with-your-email@example.edu"}
# End-of-sample / retrospective list: include failed or acquired issuers deliberately.
REQUESTED = ["JPM", "BAC", "WFC", "C", "USB", "PNC", "TFC", "RF", "KEY", "WAL", "FRC", "SBNY"]


def sec_tickers() -> dict[str, dict]:
    r = requests.get("https://www.sec.gov/files/company_tickers.json", headers=UA, timeout=30)
    r.raise_for_status()
    data = r.json()
    (RAW / "sec_company_tickers.json").write_text(json.dumps(data, indent=2))
    return {x["ticker"].upper(): x for x in data.values()}


def yahoo_history(ticker: str) -> pd.DataFrame:
    # yfinance end is exclusive.  auto_adjust=False preserves Close and Adj Close.
    end = (pd.Timestamp(SAMPLE_END) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    frame = yf.Ticker(ticker).history(start=SAMPLE_START, end=end, auto_adjust=False, actions=True)
    if frame.empty:
        return frame
    frame.index = pd.to_datetime(frame.index).tz_localize(None).normalize()
    return frame


def current_resolution(ticker: str) -> dict:
    """Current Yahoo label check. It is evidence about today, not proof of past identity."""
    try:
        info = yf.Ticker(ticker).get_info()
        return {"requested": ticker, "resolved_name": info.get("longName") or info.get("shortName"),
                "exchange": info.get("fullExchangeName") or info.get("exchange"),
                "market_cap": info.get("marketCap"), "resolution_error": ""}
    except Exception as exc:  # A failed resolution must itself be documented.
        return {"requested": ticker, "resolved_name": None, "exchange": None,
                "market_cap": None, "resolution_error": str(exc)}


def panel_rows(ticker: str, frame: pd.DataFrame, sec: dict[str, dict]) -> pd.DataFrame:
    meta = sec.get(ticker, {})
    cik = f"CIK {int(meta['cik_str']):010d}" if meta else "UNRESOLVED"
    entity = meta.get("title", "UNRESOLVED")
    out = frame.reset_index().rename(columns={"Date": "date", "Adj Close": "adj_close",
                                               "Stock Splits": "stock_splits", "Dividends": "dividends"})
    out.insert(0, "ticker", ticker)
    out.insert(1, "permanent_identifier", cik)
    out.insert(2, "entity", entity)
    out["date"] = pd.to_datetime(out["date"]).dt.date.astype(str)
    return out


def panel_fundamental_knowability(sec: dict[str, dict]) -> pd.DataFrame:
    """One disclosed fundamental, dated by filing date instead of period end."""
    issuer = "JPM"  # In the requested panel; Assets is an SEC-reported fundamental.
    meta = sec.get(issuer)
    if not meta:
        return pd.DataFrame()
    cik = f"{int(meta['cik_str']):010d}"
    r = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json", headers=UA, timeout=30)
    r.raise_for_status()
    payload = r.json()
    (RAW / f"sec_companyfacts_{issuer}.json").write_text(json.dumps(payload, indent=2))
    facts = payload["facts"]["us-gaap"]
    tag = "Assets"
    units = facts[tag]["units"]
    unit = "USD" if "USD" in units else next(iter(units))
    observations = pd.DataFrame(units[unit])
    observations["end"] = pd.to_datetime(observations["end"])
    observations["filed"] = pd.to_datetime(observations["filed"])
    candidates = observations[(observations["form"].isin(["10-Q", "10-K"])) &
                              (observations["end"] <= pd.Timestamp(SAMPLE_END))].copy()
    if candidates.empty:
        return pd.DataFrame()
    # Choose the latest period in scope, then its earliest filed observation.  A later
    # comparative/restated reference cannot make an old number knowable earlier.
    latest_end = candidates["end"].max()
    selected = candidates[candidates["end"] == latest_end].sort_values("filed").iloc[0]
    return pd.DataFrame([{"company": issuer, "permanent_identifier": f"CIK {cik}",
        "metric": tag, "unit": unit, "value": selected["val"], "period_end": selected["end"].date().isoformat(),
        "filing_date": selected["filed"].date().isoformat(),
        "lag_days": int((selected["filed"] - selected["end"]).days),
        "first_usable_date": selected["filed"].date().isoformat(), "form": selected["form"],
        "accession": selected.get("accn", "")}])


def write_catalog(inventory: pd.DataFrame) -> None:
    requested, no_rows = len(inventory), int((inventory.rows_returned == 0).sum())
    partial = int(((inventory.rows_returned > 0) & ~inventory.spans_sample).sum())
    usable = int(inventory.spans_sample.sum())
    no_pct, attrition = 100 * no_rows / requested, 100 * (requested - usable) / requested
    issue_rows = []
    if no_rows:
        issue_rows.append(("Requested names absent from the price response", "Blocker", f"{no_rows} of {requested} requested names returned 0 rows ({no_pct:.1f}%).", "lab2.py: yahoo_history / inventory", "Open", "Do not impute, backfill, or drop silently. Retain requested-name inventory; obtain CRSP/WRDS delisting history or narrow the question."))
    if partial:
        issue_rows.append(("Returned series do not cover the requested window", "High", f"{partial} of {requested} requested names returned some rows but failed the coverage test ({100*partial/requested:.1f}%).", "lab2.py: inventory coverage calculation", "Open", "Exclude from full-window metrics; preserve separately and inspect current ticker resolution."))
    issue_rows.append(("End-of-sample universe construction", "High", f"Universe contains {requested} names selected retrospectively at the end of the sample; {usable} span the full window ({100*usable/requested:.1f}%). Severity is High because Week 3 return/risk estimates would otherwise describe survivors, not the ex-ante investable set.", "lab2.py: REQUESTED and module docstring", "Open", "Report attrition and bound results; use CRSP membership/delisting returns before claiming a survivorship-free bank-sector result."))
    issue_rows.append(("Fundamental availability dated at period end", "High", "SEC output records period_end, filing_date, and lag_days for one JPM Assets observation; period-end dating would introduce look-ahead bias.", "lab2.py: panel_fundamental_knowability", "Open pending policy adoption", "Use the filing date as the earliest usable date. Adopt a conservative 45-calendar-day policy for all panel fundamentals; compare with a 30-day policy and explain its less conservative exposure."))
    lines = ["# Data-quality issue catalog — lab2", "", "Generated by `lab2.py` on " + date.today().isoformat() + ". Keep the evidence produced here; replace only the proposed handling after your analysis, if warranted.", "", "| Issue | Severity | Evidence | Code reference | Current state | Proposed handling |", "|---|---|---|---|---|---|"]
    lines += ["| " + " | ".join(x) + " |" for x in issue_rows]
    lines += ["", "## What this panel cannot be used for", "", "Until the Blocker is resolved or downgraded with evidence, this panel cannot support a survivorship-free estimate of 2022–2023 US bank-sector return or risk, nor a claim about the performance of failed/delisted names.", "", "## Required two-sentence Blocker answer", "", "A Blocker is open if the catalog still shows a Blocker row after my review. In Week 3 that forbids me from presenting full-universe/bank-sector risk or return metrics as survivorship-free; I may compute clearly labeled survivor-only descriptive metrics."]
    (OUT.parent / "data_quality_issues.md").write_text("\n".join(lines) + "\n")


def markdown_table(frame: pd.DataFrame) -> str:
    """Small dependency-free renderer; Colab does not need an extra tabulate package."""
    columns = list(frame.columns)
    text = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for values in frame.fillna("").astype(str).itertuples(index=False, name=None):
        text.append("| " + " | ".join(value.replace("|", "\\|").replace("\n", " ") for value in values) + " |")
    return "\n".join(text)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True); RAW.mkdir(exist_ok=True)
    sec = sec_tickers()
    inventory, all_rows, resolutions = [], [], []
    for ticker in REQUESTED:
        error = ""
        try:
            frame = yahoo_history(ticker)
        except Exception as exc:
            frame, error = pd.DataFrame(), str(exc)
        if not frame.empty:
            all_rows.append(panel_rows(ticker, frame, sec))
            begin, end = frame.index.min().date().isoformat(), frame.index.max().date().isoformat()
            spans = begin <= SAMPLE_START and end >= SAMPLE_END
        else:
            begin, end, spans = "—", "—", False
        inventory.append({"requested": ticker, "rows_returned": len(frame), "coverage_window": f"{begin} to {end}" if len(frame) else "—", "spans_sample": spans, "pull_error": error})
        resolutions.append(current_resolution(ticker))
    inv = pd.DataFrame(inventory)
    inv.to_csv(OUT / "coverage_inventory.csv", index=False)
    pd.DataFrame(resolutions).to_csv(OUT / "current_ticker_resolution.csv", index=False)
    panel = pd.concat(all_rows, ignore_index=True) if all_rows else pd.DataFrame(columns=["ticker", "permanent_identifier", "entity", "date"])
    panel.to_csv(OUT / "panel_security_master.csv", index=False)
    fundamental = panel_fundamental_knowability(sec)
    fundamental.to_csv(OUT / "fundamental_knowability_JPM.csv", index=False)
    write_catalog(inv)
    usable = int(inv.spans_sample.sum())
    report = [f"# Lab 2 output summary — {LABEL}", "", f"Sample: {SAMPLE_START} through {SAMPLE_END}.", "", "## Step 2 — coverage inventory", "", markdown_table(inv.drop(columns="pull_error")), "", f"Usable full-window names: {usable} of {len(inv)}. Attrition: {len(inv)-usable} of {len(inv)} ({100*(len(inv)-usable)/len(inv):.1f}%).", "", "## Step 5 — knowability", "", markdown_table(fundamental) if not fundamental.empty else "SEC revenue fact could not be selected; inspect the saved SEC response/error before asserting a result.", "", "The first usable date is the SEC filing date, not the period end. Proposed panel policy: treat a fundamental as usable 45 calendar days after period end, which is more conservative than 30 days and protects against typical reporting lags; use the later of that policy date and the actual filing date.", "", "## Files to use in the written submission", "", "- `output/coverage_inventory.csv`: requested name, returned rows, coverage, span test.", "- `output/current_ticker_resolution.csv`: current-name/exchange/market-cap label check.", "- `output/panel_security_master.csv`: Week 3 input; every returned row has a permanent identifier or is visibly `UNRESOLVED`.", "- `data_quality_issues.md`: catalog and the exact limitation to carry into Week 3."]
    (OUT / "lab2_output_summary.md").write_text("\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()
