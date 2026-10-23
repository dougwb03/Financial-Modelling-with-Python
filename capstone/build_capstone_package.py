from pathlib import Path
import copy, csv
import nbformat as nbf

ROOT=Path(__file__).resolve().parent.parent; CAP=ROOT/'capstone'; EX4=ROOT/'exercise4'
src=nbf.read(EX4/'Exercise4_oracle_valuation_final.ipynb',as_version=4)
nb=nbf.v4.new_notebook(); nb.metadata=copy.deepcopy(src.metadata)
nb.cells=[nbf.v4.new_markdown_cell('''# Oracle (ORCL) and Microsoft (MSFT) comparative valuation capstone

Oracle is executed first from the complete completed Exercise 4 authority. Microsoft valuation is evidence-gated: no beta, market-data substitute, scenario, comparison, flip point, trigger, or recommendation is generated unless its successful authenticated WRDS Compustat Security Daily `prccd` evidence is available.'''),nbf.v4.new_markdown_cell('''## Shared pipeline functions and file paths

The authoritative Oracle cells follow unchanged and refer to `exercise4` and `lab6/cache`. The Microsoft gate below is deliberately strict.''')]+copy.deepcopy(src.cells)
nb.cells += [nbf.v4.new_markdown_cell('''## Reusable linked pipeline reconciliation

Oracle’s already-executed linked DCF is the reusable pipeline control: `project`, `checks`, and `value` are parameterised by company opening data, drivers, and manual assumptions. The exact Oracle reconciliation below must pass before comparison work.'''),nbf.v4.new_code_cell("""assert abs(v['per_share']-66.02)<.005 and abs(v['wacc']-.0998)<.0001
assert abs(WRDS_BETA-1.6369)<.0001 and abs(v['tv_share']-1.007)<.002
print('ORACLE SHARED-PIPELINE RECONCILIATION: PASS — $%.2f/share, WACC %.2f%%, terminal share %.1f%%' % (v['per_share'],100*v['wacc'],100*v['tv_share']))"""),nbf.v4.new_markdown_cell('''# Microsoft: sourced extraction, known-answer gate, and required professional beta gate

## Microsoft-specific driver

Azure/cloud growth and recurring paid subscriptions drive revenue. Copilot and enterprise-AI monetisation uncertainty affects growth and operating leverage. High operating margins support FCFF, while AI capex expands PP&E and later D&A, suppressing near-term FCFF. This is not Oracle’s OCI/capacity narrative.

## AI risk and verification

`trfd` is rejected because it is an adjustment factor, not a daily-return series. The sole valid beta is manual `cov(MSFT return, SPY return) / var(SPY return)`, where each return is `prccd / lag(prccd) - 1`.'''),nbf.v4.new_code_cell("""MSFT_FACTS=CACHE/'CIK0000789019_companyfacts.json'; assert MSFT_FACTS.exists(), 'Microsoft SEC Company Facts cache required'
mf=json.load(open(MSFT_FACTS))['facts']['us-gaap']; FY=('2025-07-01','2026-06-30')
def get(tag,duration=False):
 r=[x for x in mf[tag]['units']['USD'] if x.get('form')=='10-K' and x.get('end')==FY[1] and (not duration or x.get('start')==FY[0])]
 if not r: raise KeyError('Missing Microsoft SEC Company Facts: '+tag)
 return r[-1]
tags={'Revenue':'RevenueFromContractWithCustomerExcludingAssessedTax','Operating income':'OperatingIncomeLoss','Net income':'NetIncomeLoss'}
rebuilt={k:get(t,True)['val']/1e6 for k,t in tags.items()}; rebuilt['Shares (m)']=7425.545491
debt=(get('LongTermDebtCurrent')['val']+get('LongTermDebtNoncurrent')['val'])/1e6; cash=get('CashAndCashEquivalentsAtCarryingValue')['val']/1e6; rebuilt['Net debt']=debt-cash
filed=pd.Series({'Revenue':331839.,'Operating income':155237.,'Net income':133749.,'Shares (m)':7425.545491,'Net debt':19359.}); gate=pd.DataFrame({'Filed FY2026':filed,'Rebuilt':pd.Series(rebuilt)}); gate['Difference']=gate.Rebuilt-gate['Filed FY2026']; gate['Pass']=gate.Difference.abs()<0.01; display(gate); assert gate.Pass.all(), 'MICROSOFT FY2026 KNOWN-ANSWER GATE FAILED'; print('MICROSOFT FY2026 KNOWN-ANSWER GATE: PASS')"""),nbf.v4.new_code_cell("""MSFT_AUDIT=OUT/'wrds_msft_beta_audit.csv'; MSFT_RETURNS=OUT/'wrds_compustat_msft_spy_daily_returns.csv'
if not MSFT_AUDIT.exists() or not MSFT_RETURNS.exists(): raise RuntimeError('MICROSOFT VALUATION REFUSED: missing wrds_msft_beta_audit.csv and/or wrds_compustat_msft_spy_daily_returns.csv; require successful authenticated WRDS Compustat Security Daily prccd MSFT/SPY 24-month export.')
ma=pd.read_csv(MSFT_AUDIT); mr=pd.read_csv(MSFT_RETURNS,parse_dates=['datadate'])
if not {'datadate','MSFT','SPY'}.issubset(mr) or not (ma.status.eq('success').any() and ma.source.str.contains('prccd',case=False,na=False).any()): raise RuntimeError('MICROSOFT VALUATION REFUSED: malformed/non-successful prccd evidence')
mr=mr[['datadate','MSFT','SPY']].dropna().sort_values('datadate'); assert len(mr)>=100, 'MICROSOFT VALUATION REFUSED: <100 matched observations'; MSFT_BETA=mr.MSFT.cov(mr.SPY)/mr.SPY.var(); assert .2<=MSFT_BETA<=3, 'MICROSOFT VALUATION REFUSED: implausible beta'; print(MSFT_BETA,len(mr),mr.datadate.min(),mr.datadate.max())"""),nbf.v4.new_markdown_cell('''# Comparative exhibit and conditional recommendation

No comparative conclusion is generated until both company valuation gates pass.

# Flip-point analysis

No flip point is generated until Microsoft’s completed base case exists.

# Two observable triggers

No thresholds are generated until low/base-case or flip-point logic exists.

# Check that changed the model

The initially attempted `trfd` beta method was rejected when validation established that `trfd` is an adjustment factor rather than a daily-return series. The method changed to matched Compustat Security Daily `prccd` returns and manual covariance/variance beta.

# Edition A versus model

Paste the original Edition A text verbatim here, then compare its original predictions with the completed model outputs.

# Defence facts

Oracle: $48.74/$66.02/$83.67 range, $137.79 dated price, -52.1% base gap, 9.98% WACC, 100.7% terminal share, FY2031 operating-margin sensitivity. Microsoft comparison, recommendation, flip point, and triggers are refused pending the named WRDS evidence. Open: Oracle known-answer gate; WRDS beta; reusable reconciliation; Microsoft known-answer gate; Microsoft professional beta gate; Check that changed the model.''')]
for i,c in enumerate(nb.cells):
 if c.cell_type=='markdown' and '# Edition A versus model' in c.source:
  edition='''# Edition A versus model

Paste the original Edition A text verbatim here, then compare its original predictions with the completed model outputs.'''
  before,after=c.source.split('# Edition A versus model',1)
  defence='# Defence facts'+after.split('# Defence facts',1)[1]
  c.source=before
  nb.cells.insert(i+1,nbf.v4.new_markdown_cell(edition))
  nb.cells.insert(i+2,nbf.v4.new_markdown_cell(defence))
  break
nbf.write(nb,CAP/'Capstone_Oracle_Microsoft_Final.ipynb')
docs={'assumptions_ledger_final.md':'''# Assumptions ledger\n\n## Oracle\n\nThe complete authoritative ledger, including value, unit, source, date, period, history/guidance/judgment label, rationale, and confidence for each load-bearing input, is [exercise4/assumptions_ledger.md](../exercise4/assumptions_ledger.md). Oracle’s retained outputs are $48.74/$66.02/$83.67, $137.79 dated WRDS price, 1.6369 beta, 9.98% WACC, and 100.7% terminal-value share.\n\n## Microsoft\n\n| Input | Value | Source / period | Label | Rationale | Confidence |\n|---|---:|---|---|---|---|\n| Revenue | $331,839m | SEC Company Facts, FY2026 ended 2026-06-30, 0001193125-26-323660 | History | Known-answer gate | High |\n| Operating income | $155,237m | Same | History | Known-answer gate | High |\n| Net income | $133,749m | Same | History | Known-answer gate | High |\n| Latest shares | 7,425.545491m | FY2026 10-K cover, 2026-07-23 | Filing-only | Current share count | High |\n| Net debt | $19,359m | SEC Company Facts, FY2026 | History | $40,294m debt less $20,935m cash | High |\n| Beta/WACC/price/drivers/valuation | Unavailable | Missing authenticated WRDS MSFT/SPY `prccd` files | Unavailable | No substitute permitted | Not assessable |\n''','source_log_final.md':'''# Source log\n\n- Oracle authority: `exercise4/Exercise4_oracle_valuation_final.ipynb`, `exercise4/assumptions_ledger.md`, `exercise4/wrds_beta_audit.csv`, and `exercise4/wrds_compustat_orcl_spy_daily_returns.csv`.\n- SEC caches: `lab6/cache/CIK0001341439_companyfacts.json`, `lab6/cache/CIK0000789019_companyfacts.json`, `lab6/cache/oracle_2026_10k.htm`, `lab6/cache/oracle_2026q1.htm`, and `lab6/cache/microsoft_2026_10k.htm`.\n- Professional dated-close evidence: `lab6/outputs/wrds_compustat_latest_prices.csv`; it is insufficient for Microsoft beta.\n- Required but absent fresh-kernel evidence: `capstone/wrds_msft_beta_audit.csv` and `capstone/wrds_compustat_msft_spy_daily_returns.csv`, both from successful authenticated WRDS Compustat Security Daily `prccd` MSFT/SPY export.\n''','AI_Disclosure_final.md':'''# AI disclosure\n\nCodex / OpenAI assisted with package assembly, source-path organisation, and validation logic. SEC Company Facts, the Microsoft FY2026 10-K cover share count, Oracle Exercise 4 results, and saved Oracle WRDS evidence were independently checked against local primary/professional evidence. The earlier `trfd` approach was corrected because it is an adjustment factor, not a daily-return series; the valid method is matched `prccd` returns and manual covariance divided by SPY return variance. Final assumptions, conclusions, and recommendation remain the student’s responsibility. Microsoft valuation was not generated because its required authenticated `prccd` evidence is absent.\n''','memo_evidence_pack.md':'''# Comparative memo evidence pack\n\nOracle and Microsoft are enterprise software/cloud-AI comparators. Oracle’s completed evidence: range $48.74/$66.02/$83.67; WRDS price $137.79 on 2026-09-29; base gap -52.1%; beta 1.6369; WACC 9.98%; terminal share 100.7%; highest sensitivity FY2031 operating margin. Microsoft FY2026 gate: revenue $331,839m, operating income $155,237m, net income $133,749m, shares 7,425.545491m, net debt $19,359m. The MSFT/SPY authenticated WRDS `prccd` audit and returns are absent, so no Microsoft range, recommendation, flip point, or trigger is asserted. The genuine check that changed the method rejected `trfd` as an adjustment factor.\n\nEdition A instruction: Paste the original Edition A text verbatim here, then compare its original predictions with the completed model outputs.\n'''}
for name,text in docs.items(): (CAP/name).write_text(text)
with open(CAP/'capstone_exhibit.csv','w',newline='') as f:
 w=csv.writer(f); w.writerow(['metric','Oracle','Microsoft','evidence_status']); [w.writerow(x) for x in [('low/base/high per share','48.74/66.02/83.67','NOT GENERATED','MSFT prccd audit/returns absent'),('dated professional price','137.79 on 2026-09-29','NOT GENERATED','MSFT beta lane incomplete'),('base gap','-52.1%','NOT GENERATED','comparison gate not passed'),('WACC','9.98%','NOT GENERATED','MSFT beta absent'),('beta','1.6369','NOT GENERATED','MSFT prccd evidence absent'),('terminal value share','100.7%','NOT GENERATED','comparison gate not passed'),('net debt','$98,252m','$19,359m','Oracle Exercise 4; Microsoft SEC FY2026'),('highest sensitivity','FY2031 operating margin','NOT GENERATED','comparison gate not passed')]]
print('Built',CAP/'Capstone_Oracle_Microsoft_Final.ipynb')
