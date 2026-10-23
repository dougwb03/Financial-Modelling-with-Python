# Source-log addendum — lab2

Copy this section into the root `source_log.md` after the Colab run and replace bracketed items. It is intentionally labeled as Lab 2 and records both successful pulls and access barriers.

## Lab 2 — panel construction and quality checks

| Source | Access route / date | Role and fields | Independence / limitation | Result |
|---|---|---|---|---|
| Yahoo Finance via `yfinance` | `yf.Ticker(ticker).history`, run [date] | Daily unadjusted OHLC, adjusted close, volume, dividends, splits for the requested panel; coverage inventory | Public vendor feed; not survivorship-free and ticker labels can resolve to a current issuer | [working / rows absent / error] |
| SEC EDGAR | `company_tickers.json` and `data.sec.gov/api/xbrl/companyfacts`, run [date], identifying User-Agent | Current CIK/name lookup; JPM reported Assets period end, filing date, form, accession | Primary regulatory source for issuer metadata and filing availability; does not provide delisting returns or historical index membership | [working / barrier] |
| WRDS / CRSP | Route tried: [web / Python library / support request], [date] | Intended independent professional source: CRSP permanent security ID, delisting return (`DLRET`), and survivorship-aware membership | Independent of Yahoo; required to evaluate unavailable/delisted names fairly | [access result and exact barrier, if any] |
| Second free source: [name] | [URL/route], [date] | [What was checked: corporate event, historical pricing, or issuer identity] | Explain why it is independent of Yahoo | [result] |

### Required source note

For every missing or short series, cite a public account of the event and record the relevant date. Do not use a current ticker resolution as evidence that the historical ticker represented the same issuer.
