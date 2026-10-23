# Oracle assumptions ledger

Extraction date: 2026-10-01. USD millions unless stated.

| Input | Value / method | Source | Period / units | Label and rationale | Confidence |
|---|---|---|---|---|---|
| Revenue, EBIT, net income | 67,357 / 20,606 / 17,087 | SEC Company Facts; FY2026 10-K 0001193125-26-277521 | FY2026; USD m | History; visible notebook extraction and known-answer gate. | High |
| Capex, cash, AR, AP, PP&E, assets, equity, debt | 55,663 / 31,289 / 10,385 / 10,977 / 99,957 / 261,759 / 42,508 / 129,541 | SEC Company Facts | FY2026; USD m | History; visible Python extraction and provenance table. | High |
| Inventory | 303 | Oracle FY2026 10-K, Consolidated Balance Sheets; extracted 2026-10-01 | 2026-05-31; USD m | Filing-only; Company Facts `InventoryNet` is unavailable for FY2026 in the local cache. | High |
| Latest shares | 3,023.736 | Oracle 2026 Q1 10-Q cover, 0001193125-26-389274, filed 2026-09-11 | 2026-09-07; m shares | Filing-only market-value equity input. | High |
| Dated share price | 137.79 | WRDS Compustat Security Daily | 2026-09-29; USD/share | History; comparison price, not a target. | High |
| **Beta** | **1.6369 = cov(ORCL return, SPY return) / var(SPY return)** | WRDS Compustat Security Daily `comp.secd.prccd`; saved local audit and return series | 501 daily returns, 2024-10-01 to 2026-09-30 | History. Sole beta used everywhere. `trfd` was rejected because it is an adjustment factor, not a daily-return series. | High |
| Risk-free rate / ERP | 5.06% / 4.234% | U.S. Treasury 5-year nominal CMT / Damodaran U.S. implied ERP | 2026-09-29 / 2025 | Valuation inputs. | Medium |
| Tax rate | 22.0% | Judgment; model input; documented 2026-10-01 | FY2027–31 | Simplified forecast tax rate used in NOPAT and net-income calculations. | Medium |
| Working-capital ratios | AR/revenue 15.4178%; inventory/revenue 0.4498%; AP/revenue 16.2967%; net other operating assets/revenue 61.0063% | FY2026 SEC Company Facts and FY2026 10-K filing-only inventory; calculated in notebook; extracted 2026-10-01 | FY2026 opening ratios; forecast FY2027–31 | Forecast operating-balance-sheet ratios carried from the opening year. | Medium |
| Pre-tax cost of debt | 4.5% | Oracle debt disclosures; analyst estimate | Forecast | Judgment. Estimated blended cost of existing debt, not new borrowing cost; may be below 5.06% Treasury because debt was issued earlier. | Judgment / lower confidence |
| Terminal growth | 3.0% | 5year average GDP | Terminal | Must remain below WACC; sensitivity range is 2.0%–3.0%. | Medium |
| Cash floor / dividends | $10,000 / 32% of net income | Judgment | FY2027–31 | Explicit financing policy. Cash is calculated last; borrowing funds the shortfall. | Judgment / lower confidence |
| D&A / opening PP&E | 15.0% / 16.0% / 17.0% / 18.0% / 18.0% | Judgment; model input; documented 2026-10-01 | FY2027–FY2031 | Makes data-centre PP&E create a later depreciation burden. | Judgment / lower confidence |
| Scenario / sensitivity bounds | Low/Base/High scenarios; tornado bounds: FY2027 revenue growth 8.0%–25.0%, FY2031 operating margin 31.0%–39.0%, FY2027 capex/revenue 85.0%–55.0%, terminal growth 2.0%–3.0% | Judgment; model input; documented 2026-10-01 | Valuation scenarios and tornado | Judgment ranges used to show valuation sensitivity; they do not change the base case. | Judgment / lower confidence |

## OCI/AI monetisation base-case drivers

| Driver | FY2027 | FY2028 | FY2029 | FY2030 | FY2031 | Basis | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| Revenue growth | 20.0% | 18.0% | 16.0% | 10.0% | 7.0% | Optimistic OCI/AI monetisation base case, not a conservative assumption. | Judgment / lower confidence |
| EBIT margin | 31.5% | 33.0% | 34.0% | 34.5% | 35.0% | Assumes utilisation and operating leverage outweigh data-centre cost and depreciation. | Judgment / lower confidence |
| Capex / revenue | 70.0% | 55.0% | 42.0% | 32.0% | 25.0% | Deliberately high early; gradual payback of the FY2026 infrastructure build, not smoothing the spike away. | Judgment / lower confidence |
| D&A / opening PP&E | 15.0% | 16.0% | 17.0% | 18.0% | 18.0% | Makes data-centre PP&E create a later depreciation burden. | Judgment / lower confidence |

Early negative FCFF and additional borrowing are intended outcomes of this capacity-investment path. The simplified operating balance sheet defines other operating assets as net other operating assets (filing other assets less filing other liabilities), so forecast total assets are cash + AR + inventory + other operating assets + PP&E and total liabilities are AP + debt.
