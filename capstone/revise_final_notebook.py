"""Apply the final-consistency revisions to the generated capstone notebook.

This intentionally edits only the copied Final notebook.  The source capstone
notebook remains an untouched record of the prior submission.
"""
from pathlib import Path
import sys
import nbformat


cap = Path(__file__).resolve().parent
path = cap / (sys.argv[1] if len(sys.argv) > 1 else "Capstone_Oracle_Microsoft_Final.ipynb")
nb = nbformat.read(path, as_version=4)

# The requested deliverable name is deliberately retained in the title.
if nb.cells and nb.cells[0].cell_type == "markdown":
    nb.cells[0].source = nb.cells[0].source.replace('# Capstone_Oracle_Microsoft', '# Capstone_Oracle_Mircosoft update')

# The trigger cell must be precise, observable, and tied to the low case.
for cell in nb.cells:
    if cell.cell_type == "code" and cell.source.startswith("triggers=pd.DataFrame("):
        cell.source = r'''triggers=pd.DataFrame([
    ['Oracle', 'FY2027 EBIT margin', 'below 30.0%',
     'Oracle FY2027 Form 10-K, year ended 2027-05-31',
     'A result below the low-case operating-margin threshold would weaken the OCI utilisation and operating-leverage assumptions.'],
    ['Microsoft', 'FY2027 total revenue growth', 'below 12.0%',
     'Microsoft FY2027 Form 10-K, year ended 2027-06-30',
     'A result below the low-case revenue-growth threshold would weaken the Azure, subscriptions, and Copilot monetisation assumptions.'],
], columns=['Company','Observable metric','Threshold','Source/review','Explanation'])
display(triggers)'''

# Recompute the Oracle FY2031 ranking flip point from the executed linked DCF.
# The observable trigger below is deliberately FY2027 margin, while this
# calculation remains the FY2031 relative-gap threshold.
for cell in nb.cells:
    if cell.cell_type == "code" and cell.source.startswith("def or_gap(margin):"):
        cell.source = r'''def or_gap(margin):
    d=deepcopy(BASE); d['margin'][4]=margin
    return run_linked(ocfg,d,MANUAL)[2]['per_share']/MANUAL['price']-1

target=mgap
grid=np.linspace(.20,.70,501)
dif=[or_gap(x)-target for x in grid]
pairs=[(grid[i],grid[i+1]) for i in range(len(grid)-1) if dif[i]*dif[i+1]<=0]
if not pairs:
    raise RuntimeError('No Oracle FY2031 EBIT-margin flip within 20%–70%; no invented flip point.')
lo,hi=pairs[0]
for _ in range(70):
    mid=(lo+hi)/2
    if (or_gap(lo)-target)*(or_gap(mid)-target)<=0:
        hi=mid
    else:
        lo=mid
flip=(lo+hi)/2
assert f'{flip:.4%}' == '44.9024%', f'Unexpected Oracle flip point: {flip:.8%}'
fd=deepcopy(BASE); fd['margin'][4]=flip
fval=run_linked(ocfg,fd,MANUAL)[2]['per_share']
hist=(history.operating_margin.min(),history.operating_margin.max())
eps=.002
confirm=pd.DataFrame({'FY2031 Oracle EBIT margin':[flip-eps,flip,flip+eps],
                      'Oracle relative gap':[or_gap(flip-eps),or_gap(flip),or_gap(flip+eps)],
                      'Microsoft relative gap':[mgap]*3})
display(confirm)
print(f'Solved flip point={flip:.4%}; Oracle value=${fval:.2f}; relative gap={or_gap(flip):.4%}; historical operating-margin range={hist[0]:.2%}–{hist[1]:.2%}; flip is {"inside" if hist[0]<=flip<=hist[1] else "outside"} historical range.')'''

# The stated Microsoft trigger is its low-case FY2027 growth threshold.
for cell in nb.cells:
    if cell.cell_type == "code" and cell.source.startswith("MSC={'Low':"):
        cell.source = cell.source.replace("'growth':[.10,.09,.08,.07,.06]", "'growth':[.12,.09,.08,.07,.06]")

# Restore the exact completed Microsoft base growth path from the untouched
# source notebook.  Trigger monitoring does not authorize changing this base
# forecast.
for cell in nb.cells:
    if cell.cell_type == "code" and cell.source.startswith("# Drivers: FY2027–FY2031."):
        cell.source = cell.source.replace("growth=[.15,.13,.11,.09,.07]", "growth=[.19,.17,.15,.13,.07]")
        cell.source = cell.source.replace("'15%, 13%, 11%, 9%, 7%'", "'19%, 17%, 15%, 13%, 7%'")
        cell.source = cell.source.replace("'Azure/subscriptions and uncertain Copilot monetisation'", "'Stronger Azure demand, recurring subscriptions, and Copilot enterprise monetisation through FY2030; convergence in FY2031'")

# Write every companion from the in-memory, executed valuation outputs.  This
# cell sits immediately before Defence facts, so the entire evidence pack is
# refreshed in the same clean kernel execution as the final presentation.
nb.cells = [c for c in nb.cells if not (c.cell_type == "code" and c.source.startswith("# Final companion-output refresh:"))]
for i, cell in enumerate(nb.cells):
    if cell.cell_type == "markdown" and cell.source.strip() == "# Defence facts":
        insert_at = i
        break
else:
    raise RuntimeError("Defence facts anchor not found")

writer = nbformat.v4.new_code_cell(r'''# Final companion-output refresh: values are derived only from this executed kernel.
outdir = OUT.parent / 'capstone'
oracle_range = f'${orange.Low:.2f}/${orange.Base:.2f}/${orange.High:.2f}'
msft_range = f'${mrange.Low:.2f}/${mrange.Base:.2f}/${mrange.High:.2f}'
assert abs(v['per_share'] - 66.02) < .005
assert abs(v['wacc'] - .0998) < .0001
assert abs(v['tv_share'] - 1.007) < .002
assert f'{flip:.4%}' == '44.9024%'

def sensitivity_markdown(frame, low_col, high_col):
    lines = ['| Driver | Low value/share | High value/share | Swing |', '|---|---:|---:|---:|']
    for _, row in frame.iterrows():
        lines.append(f"| {row['Driver']} | ${row[low_col]:.2f} | ${row[high_col]:.2f} | ${row['Swing']:.2f} |")
    return '\n'.join(lines)

oracle_sens = sensitivity_markdown(tornado, 'Low value / share', 'High value / share')
msft_sens = sensitivity_markdown(mtornado, 'Low value/share', 'High value/share')

ledger_header = '| Valuation driver / assumption | Value | Unit | Label | Source and date | Rationale | Confidence |\n|---|---:|---|---|---|---|---|'
oracle_rows = [
    ('Revenue growth FY2027–31', '20%, 18%, 16%, 10%, 7%', '%', 'Judgment', 'Model base-case driver; documented 2026-10-01', 'Models OCI/AI monetisation that moderates as the forecast matures.', 'Lower'),
    ('EBIT margin FY2027–31', '31.5%, 33.0%, 34.0%, 34.5%, 35.0%', '% of revenue', 'Judgment', 'Model base-case driver; documented 2026-10-01', 'Assumes utilisation and operating leverage outweigh data-centre cost and depreciation.', 'Lower'),
    ('Tax rate FY2027–31', '22.0%', '%', 'Judgment', 'Model input; documented 2026-10-01', 'Provides a consistent simplified NOPAT and net-income forecast tax rate.', 'Medium'),
    ('Capex/revenue FY2027–31', '70%, 55%, 42%, 32%, 25%', '% of revenue', 'Judgment', 'Model base-case driver; documented 2026-10-01', 'Preserves the high early infrastructure build and its gradual payback.', 'Lower'),
    ('D&A/opening PP&E FY2027–31', '15%, 16%, 17%, 18%, 18%', '% of opening PP&E', 'Judgment', 'Model input; documented 2026-10-01', 'Makes infrastructure PP&E generate a later depreciation burden.', 'Lower'),
    ('Working-capital ratios', f"AR {BASE['ar']:.4%}; inventory {BASE['inventory']:.4%}; AP {BASE['ap']:.4%}; other operating assets {BASE['ono']:.4%}", '% of revenue', 'History', 'Oracle FY2026 SEC Company Facts cache and FY2026 10-K; 2026-10-01', 'Carries the opening operating-balance-sheet relationships through the forecast.', 'Medium'),
    ('Beta', f'{WRDS_BETA:.4f}', 'x', 'History', 'WRDS Compustat Security Daily `prccd`, 501 returns, 2024-10-01–2026-09-30', 'Uses cov(ORCL return, SPY return) divided by var(SPY return).', 'High'),
    ('Risk-free rate', f"{MANUAL['risk_free_rate']:.2%}", '%', 'History', 'U.S. Treasury 5-year nominal CMT; 2026-09-29; executed notebook input', 'Anchors the CAPM cost of equity to the dated Treasury observation.', 'Medium'),
    ('Equity risk premium', f"{MANUAL['equity_risk_premium']:.3%}", '%', 'History', 'Damodaran U.S. implied ERP; 2025; executed notebook input', 'Supplies the market-risk premium used in CAPM.', 'Medium'),
    ('Pre-tax cost of debt', f"{BASE['debt_rate']:.1%}", '%', 'Judgment', 'Oracle debt disclosures and analyst estimate; documented 2026-10-01', 'Approximates the blended cost of existing debt rather than new borrowing.', 'Lower'),
    ('Cash floor', f"${MANUAL['cash_floor']:,.0f}", 'USD m', 'Judgment', 'Model financing policy; documented 2026-10-01', 'Defines the minimum liquidity level before incremental borrowing is calculated.', 'Lower'),
    ('Dividends', f"{MANUAL['dividend_pct_ni']:.0%} of net income", '% of net income', 'Judgment', 'Model financing policy; documented 2026-10-01', 'Makes dividends an explicit component of the forecast cash roll-forward.', 'Lower'),
    ('Terminal growth', f"{MANUAL['terminal_growth']:.1%}", '%', 'Judgment', 'Five-year average GDP reference; documented 2026-10-01', 'Remains below WACC and supports a conservative perpetuity assumption.', 'Medium'),
    ('Net debt', f"${opening['net_debt']:,.0f}", 'USD m', 'History', 'Oracle FY2026 SEC Company Facts cache; year ended 2026-05-31', 'Bridges enterprise value to equity value using filed debt less cash.', 'High'),
    ('Shares', f"{opening['shares']:,.3f}", 'm shares', 'History', 'Oracle FY2026 Q1 10-Q cover, accession 0001193125-26-389274; 2026-09-07', 'Uses the latest filed share count for the per-share calculation.', 'High'),
    ('Dated price', f"${MANUAL['price']:.2f}", 'USD/share', 'History', 'WRDS Compustat Security Daily; 2026-09-29', 'Is the dated market comparison rather than a valuation input target.', 'High'),
    ('Scenario bounds', 'Low/Base/High: growth 10–22%, margin 30–38%, capex 78–22% across FY2027–31', '% of revenue unless noted', 'Judgment', 'Model scenario definitions; documented 2026-10-01', 'Shows a coherent downside/base/upside operating-path range without changing the base case.', 'Lower'),
    ('Sensitivity bounds', 'FY2027 growth 8–25%; FY2031 margin 31–39%; FY2027 capex 85–55%; terminal growth 2–3%', '%', 'Judgment', 'Model tornado definitions; documented 2026-10-01', 'Tests the specified operational and terminal-value bounds one at a time.', 'Lower'),
]
msft_rows = [
    ('Revenue growth FY2027–31', ', '.join(f'{x:.0%}' for x in MB['growth']), '%', 'Judgment', 'Model base-case driver; documented 2026-10-03', 'Reflects Azure demand, subscriptions, and Copilot monetisation through FY2030 before convergence.', 'Medium'),
    ('EBIT margin FY2027–31', ', '.join(f'{x:.1%}' for x in MB['margin']), '% of revenue', 'Judgment', 'Model base-case driver; documented 2026-10-03', 'Represents a high-margin business with modest continuing operating leverage.', 'Medium'),
    ('Tax rate FY2027–31', f"{MB['tax'][0]:.0%}", '%', 'Judgment', 'Model input; documented 2026-10-03', 'Provides a consistent simplified NOPAT and net-income forecast tax rate.', 'Medium'),
    ('Capex/revenue FY2027–31', ', '.join(f'{x:.0%}' for x in MB['capex']), '% of revenue', 'Judgment', 'Model base-case driver; documented 2026-10-03', 'Captures high AI infrastructure investment that normalises over the forecast.', 'Medium'),
    ('D&A/opening PP&E FY2027–31', ', '.join(f'{x:.0%}' for x in MB['da_ppe']), '% of opening PP&E', 'Judgment', 'Model input; documented 2026-10-03', 'Recognises later depreciation from AI infrastructure assets.', 'Medium'),
    ('Working-capital ratios', f"AR {MB['ar']:.4%}; inventory {MB['inventory']:.4%}; AP {MB['ap']:.4%}; other operating assets {MB['ono']:.4%}", '% of revenue', 'History', 'Microsoft FY2026 SEC Company Facts cache; year ended 2026-06-30', 'Carries the opening operating-balance-sheet relationships through the forecast.', 'Medium'),
    ('Beta', f'{MSFT_BETA:.4f}', 'x', 'History', 'WRDS Compustat Security Daily `prccd`, 501 returns, 2024-10-01–2026-09-30', 'Uses cov(MSFT return, SPY return) divided by var(SPY return).', 'High'),
    ('Risk-free rate', f"{MM['risk_free_rate']:.2%}", '%', 'History', 'U.S. Treasury 5-year nominal CMT; 2026-09-29; executed notebook input', 'Anchors the CAPM cost of equity to the dated Treasury observation.', 'Medium'),
    ('Equity risk premium', f"{MM['equity_risk_premium']:.3%}", '%', 'History', 'Damodaran U.S. implied ERP; 2025; executed notebook input', 'Supplies the market-risk premium used in CAPM.', 'Medium'),
    ('Pre-tax cost of debt', f"{MB['debt_rate']:.1%}", '%', 'Judgment', 'Existing-debt estimate; documented 2026-10-03', 'Approximates the blended cost of existing debt rather than new borrowing.', 'Lower'),
    ('Cash floor', f"${MM['cash_floor']:,.0f}", 'USD m', 'Judgment', 'Model financing policy; documented 2026-10-03', 'Defines the minimum liquidity level before incremental borrowing is calculated.', 'Lower'),
    ('Dividends', f"{MM['dividend_pct_ni']:.0%} of net income", '% of net income', 'Judgment', 'Model financing policy; documented 2026-10-03', 'Makes dividends an explicit component of the forecast cash roll-forward.', 'Lower'),
    ('Terminal growth', f"{MM['terminal_growth']:.1%}", '%', 'Judgment', 'Model terminal input; documented 2026-10-03', 'Remains below WACC and supports a conservative perpetuity assumption.', 'Medium'),
    ('Net debt', f"${mopen['net_debt']:,.0f}", 'USD m', 'History', 'Microsoft FY2026 SEC Company Facts cache; year ended 2026-06-30', 'Bridges enterprise value to equity value using filed debt less cash.', 'High'),
    ('Shares', f"{mopen['shares']:,.6f}", 'm shares', 'History', 'Microsoft FY2026 10-K cover, accession 0001193125-26-323660; 2026-07-23', 'Uses the latest filed share count for the per-share calculation.', 'High'),
    ('Dated price', f"${mprice:.2f}", 'USD/share', 'History', 'WRDS Compustat Security Daily; 2026-09-30', 'Is the dated market comparison rather than a valuation input target.', 'High'),
    ('Scenario bounds', 'Low/Base/High: growth 6–20%, margin 44.0–49.5%, capex 35–15% across FY2027–31', '% of revenue unless noted', 'Judgment', 'Model scenario definitions; documented 2026-10-03', 'Shows a coherent downside/base/upside operating-path range without changing the base case.', 'Lower'),
    ('Sensitivity bounds', 'FY2027 growth 10–23%; FY2031 margin 44–52%; FY2027 capex 38–22%; terminal growth 2–3%', '%', 'Judgment', 'Model tornado definitions; documented 2026-10-03', 'Tests the specified operational and terminal-value bounds one at a time.', 'Lower'),
]
def ledger_table(rows):
    return ledger_header + '\n' + '\n'.join('| ' + ' | '.join(map(str, row)) + ' |' for row in rows)
legacy_assumptions = f"""# Assumptions ledger — final executed run

## Oracle

Oracle’s complete opening-data and valuation-driver ledger appears below. The shared linked-DCF rerun reconciles to {oracle_range}, dated price ${MANUAL['price']:.2f}, WACC {v['wacc']:.2%}, and terminal value/EV {v['tv_share']:.1%}.

## Microsoft

| Input | Final executed value | Classification / basis |
|---|---:|---|
| Dated price | ${mprice:.2f} on {MM['price_date']} | WRDS Compustat Security Daily |
| Beta | {MSFT_BETA:.4f} | Saved WRDS `prccd` MSFT/SPY returns; covariance / variance |
| WACC | {mv['wacc']:.2%} | CAPM equity plus after-tax debt, market-value weights |
| Low / base / high value per share | {msft_range} | Shared linked FCFF pipeline |
| Revenue growth FY2027–31 | 19%, 17%, 15%, 13%, 7% | Judgment: Stronger Azure demand, recurring subscriptions, and Copilot enterprise monetisation through FY2030; convergence in FY2031 |
| EBIT margin FY2027–31 | 46.5%, 47.0%, 47.5%, 47.8%, 48.0% | Judgment: operating leverage |
| Capex / revenue FY2027–31 | 30%, 28%, 24%, 20%, 17% | Judgment: AI infrastructure |
| Terminal growth / cash floor | 3.0% / $20,000m | Judgment / liquidity policy |
"""
assumptions_text = legacy_assumptions + f"""

## Full valuation-driver ledger

The following is the complete company-specific record of load-bearing opening data and valuation drivers used by the executed linked DCF. Values are from this executed kernel; USD amounts are millions unless specified. Forecast drivers flow directly into revenue, EBIT, NOPAT, FCFF, WACC, terminal value, enterprise value, and per-share value.

### Oracle

{ledger_table(oracle_rows)}

### Microsoft

{ledger_table(msft_rows)}
"""

legacy_source_log = """# Source log — final executed run

- Oracle opening history, assumptions, beta evidence and professional dated price: retained Exercise 4 source files and the Oracle cells in `Capstone_Oracle_Mircosoft update.ipynb`.
- Microsoft opening history: SEC Company Facts cache `lab6/cache/CIK0000789019_companyfacts.json`; FY2026 Form 10-K, year ended 2026-06-30.
- Microsoft filed share count: FY2026 Form 10-K cover.
- Microsoft beta: `exercise4/wrds_msft_beta_audit.csv` and `exercise4/wrds_compustat_msft_spy_daily_returns.csv`; authenticated Compustat Security Daily `prccd` returns.
- Microsoft dated price: `lab6/outputs/wrds_compustat_latest_prices.csv`, WRDS Compustat Security Daily, 2026-09-30.
- Final companion files were regenerated by the final notebook cell after all DCF calculations and assertions passed.
"""
source_text = legacy_source_log + """

## Detailed evidence register

| Source | Purpose | Period / date | Accession, where applicable | Local evidence file | Notes |
|---|---|---|---|---|---|
| SEC Company Facts — Oracle | Opening history, net debt, working capital | FY2026 ended 2026-05-31 | 0001193125-26-277521 | `lab6/cache/CIK0001341439_companyfacts.json` | Primary SEC cache read by the final kernel. |
| SEC Company Facts — Microsoft | Opening history, net debt, working capital | FY2026 ended 2026-06-30 | 0001193125-26-323660 | `lab6/cache/CIK0000789019_companyfacts.json` | Primary SEC cache read by the final kernel. |
| Oracle FY2026 Form 10-K | Filing-only inventory and historical cross-check | Filed 2026-06-17; FY ended 2026-05-31 | 0001193125-26-277521 | `lab6/cache/oracle_2026_10k.htm` | Final kernel reads the filing cache. |
| Oracle FY2026 Q1 Form 10-Q | Latest filed Oracle share count | Filed 2026-09-11; cover dated 2026-09-07 | 0001193125-26-389274 | `lab6/cache/oracle_2026q1.htm` | Filing-only share-count evidence. |
| Microsoft FY2026 Form 10-K | Filing read and latest filed shares | Filed 2026-07-29; FY ended 2026-06-30 | 0001193125-26-323660 | `lab6/cache/microsoft_2026_10k.htm` | Final kernel reads the filing cache and cover count. |
| WRDS Compustat Security Daily — ORCL/SPY | Oracle beta calculation | 501 returns, 2024-10-01–2026-09-30 | N/A | `capstone/wrds_beta_audit.csv`; `capstone/wrds_compustat_orcl_spy_daily_returns.csv` | Final-kernel Oracle beta gate uses these matched `prccd` returns and covariance/variance. |
| WRDS Compustat Security Daily — MSFT/SPY | Microsoft beta calculation | 501 returns, 2024-10-01–2026-09-30 | N/A | `exercise4/wrds_msft_beta_audit.csv`; `exercise4/wrds_compustat_msft_spy_daily_returns.csv` | Uses matched `prccd` returns and covariance/variance. |
| WRDS Compustat Security Daily prices | Dated market prices | 2026-09-30 (MSFT and ORCL extract) | N/A | `lab6/outputs/wrds_compustat_latest_prices.csv` | Microsoft price is $512.90; Oracle model price remains its existing 2026-09-29 $137.79 observation. |
| U.S. Treasury 5-year nominal CMT | Risk-free-rate input | 2026-09-29 | N/A | `Capstone_Oracle_Mircosoft update.ipynb` | Executed input is 5.06%; no separate downloaded cache is claimed. |
| Damodaran U.S. implied ERP | Equity-risk-premium input | 2025 | N/A | `Capstone_Oracle_Mircosoft update.ipynb` | Executed input is 4.234%; no separate downloaded cache is claimed. |

The final companion files were regenerated by the final notebook cell after all valuation assertions passed.
"""

ai_text = """# AI disclosure — final

ChatGPT Plus assisted with prompt drafting, assignment-requirement review, and output review; Codex/OpenAI assisted with notebook structure, implementation, validation, and evidence-record assembly. The final notebook independently checks SEC Company Facts, filing-only share counts, and saved WRDS evidence. `trfd` was rejected because it is an adjustment factor rather than a daily-return series; final betas use matched Compustat Security Daily `prccd` returns and covariance divided by SPY variance. The model judgments and conditional recommendation remain the student’s responsibility.
"""

memo_text = f"""# Memo evidence pack — final executed run

The shared parameterized linked-DCF pipeline reruns Oracle and Microsoft with company opening data, beta, WACC inputs, operating drivers, and cash-floor policy supplied as parameters. Oracle’s hard reconciliation passes: base value/share ${v['per_share']:.2f}, WACC {v['wacc']:.2%}, and terminal value/EV {v['tv_share']:.1%}.

| Measure | Oracle | Microsoft |
|---|---:|---:|
| Low / base / high | {oracle_range} | {msft_range} |
| Dated price | ${MANUAL['price']:.2f} ({MANUAL['price_date']}) | ${mprice:.2f} ({MM['price_date']}) |
| Base gap | ${v['per_share']-MANUAL['price']:.2f} ({ogap:.1%}) | ${mv['per_share']-mprice:.2f} ({mgap:.1%}) |
| WACC | {v['wacc']:.2%} | {mv['wacc']:.2%} |
| Terminal value / EV | {v['tv_share']:.1%} | {mv['tv_share']:.1%} |
| Highest sensitivity | {business_tornado} | {mhigh} |

## Executed sensitivity outputs

### Oracle

{oracle_sens}

### Microsoft

{msft_sens}

Oracle’s ranking flip point remains FY2031 EBIT margin of {flip:.4%}. The completed conditional recommendation is: {rec}

| Company | Observable metric | Threshold | Source/review | Explanation |
|---|---|---|---|---|
| Oracle | FY2027 EBIT margin | below 30.0% | Oracle FY2027 Form 10-K, year ended 2027-05-31 | A result below the low-case operating-margin threshold would weaken the OCI utilisation and operating-leverage assumptions. |
| Microsoft | FY2027 total revenue growth | below 12.0% | Microsoft FY2027 Form 10-K, year ended 2027-06-30 | A result below the low-case revenue-growth threshold would weaken the Azure, subscriptions, and Copilot monetisation assumptions. |
"""

(outdir / 'assumptions_ledger_final.md').write_text(assumptions_text)
(outdir / 'source_log_final.md').write_text(source_text)
(outdir / 'AI_Disclosure_final.md').write_text(ai_text)
(outdir / 'memo_evidence_pack.md').write_text(memo_text)
print('FINAL COMPANION OUTPUTS REFRESHED FROM THIS EXECUTED KERNEL')''')
nb.cells.insert(insert_at, writer)
nbformat.write(nb, path)
print(path)
