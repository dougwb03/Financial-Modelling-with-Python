from pathlib import Path
import copy
import nbformat as nbf

root=Path(__file__).resolve().parent.parent; cap=root/'capstone'; ex4=root/'exercise4'
src=nbf.read(ex4/'Exercise4_oracle_valuation_final.ipynb',as_version=4)
nb=nbf.v4.new_notebook(); nb.metadata=copy.deepcopy(src.metadata)
nb.cells=[nbf.v4.new_markdown_cell('''# Capstone_Oracle_Microsoft_FINAL

## Oracle (ORCL) and Microsoft (MSFT) comparative valuation capstone

Oracle is reproduced first from the completed Exercise 4 authority. The comparison assesses two enterprise-software businesses exposed to cloud and AI infrastructure spending using dated professional-source prices and company-specific linked FCFF models.'''),nbf.v4.new_markdown_cell('''## Shared pipeline functions and file paths

The complete authoritative Oracle workpaper follows unchanged. The reusable functions later reconcile Oracle exactly before running Microsoft with its own configuration.''')]+copy.deepcopy(src.cells)
nb.cells += [nbf.v4.new_markdown_cell('''# Microsoft: sourced extraction, assumptions, forecast, checks, valuation, scenarios, tornado, bridge, and honest range

## AI risk and verification

AI assisted with code structure and validation. SEC Company Facts, the FY2026 10-K cover share count, and saved authenticated WRDS `prccd` return evidence are independently checked below. `trfd` is rejected because it is an adjustment factor, not a daily-return series.

## Microsoft-specific driver

Azure/cloud growth and recurring paid subscriptions drive revenue; uncertain Copilot and enterprise-AI monetisation changes growth and operating leverage. High margins expand NOPAT, while AI data-centre capex increases PP&E and subsequent D&A, reducing near-term FCFF. This driver is implemented in Microsoft-specific growth, margin, capex, and D&A arrays.'''),
nbf.v4.new_code_cell(r'''# Shared reusable linked FCFF pipeline; Oracle is reconciled before Microsoft is allowed to run.
def run_linked(cfg, d, m):
    q, rows=deepcopy(cfg['opening']), []
    if 'ono' not in q: q['ono']=q['other_operating_assets']
    for i,yr in enumerate(cfg['years']):
        rev=q['revenue']*(1+d['growth'][i]); ebit=rev*d['margin'][i]; interest=q['debt']*d['debt_rate']; pre=ebit-interest; tax=max(pre,0)*d['tax'][i]; ni=pre-tax; nopat=ebit*(1-d['tax'][i])
        capex=rev*d['capex'][i]; da=q['ppe']*d['da_ppe'][i]; ppe=q['ppe']+capex-da; ar,inv,ap,ono=rev*d['ar'],rev*d['inventory'],rev*d['ap'],rev*d['ono']; dnwc=(ar+inv+ono-ap)-(q['ar']+q['inventory']+q['ono']-q['ap'])
        div=ni*m['dividend_pct_ni']; pre_cash=q['cash']+ni+da-dnwc-capex-div; borrow=max(m['cash_floor']-pre_cash,0); cash=pre_cash+borrow; debt=q['debt']+borrow; equity=q['equity']+ni-div; assets=cash+ar+inv+ono+ppe; liab=ap+debt; fcff=nopat+da-capex-dnwc
        rows.append(dict(year=yr,revenue=rev,ebit=ebit,interest=interest,pretax_income=pre,taxes=tax,net_income=ni,nopat=nopat,capex=capex,da=da,delta_nwc=dnwc,fcff=fcff,dividends=div,incremental_borrowing=borrow,cash=cash,debt=debt,ar=ar,inventory=inv,ap=ap,other_operating_assets=ono,ppe=ppe,assets=assets,liabilities=liab,equity=equity))
        q=dict(revenue=rev,cash=cash,debt=debt,ar=ar,inventory=inv,ap=ap,ono=ono,ppe=ppe,equity=equity)
    p=pd.DataFrame(rows).set_index('year'); prior=p.cash.shift(1).fillna(cfg['opening']['cash']); ck=pd.DataFrame({'Balance identity':p.assets-p.liabilities-p.equity,'Cash-flow tie':p.cash-(prior+p.net_income+p.da-p.delta_nwc-p.capex-p.dividends+p.incremental_borrowing),'Cash-floor':p.cash-m['cash_floor']},index=p.index); ck['PASS']=(ck['Balance identity'].abs()<.01)&(ck['Cash-flow tie'].abs()<.01)&(ck['Cash-floor']>=-.01)
    if not ck.PASS.all(): raise ValueError('VALUATION REFUSED: linked forecast checks failed')
    coe=m['risk_free_rate']+d['beta']*m['equity_risk_premium']; me=m['price']*cfg['shares']; we=me/(me+cfg['opening']['debt']); wacc=we*coe+(1-we)*d['debt_rate']*(1-d['tax'][0])
    if m['terminal_growth']>=wacc: raise ValueError('VALUATION REFUSED: terminal growth must be below WACC')
    t=np.arange(1,6); pvf=(p.fcff.values/(1+wacc)**t).sum(); pvt=p.fcff.iloc[-1]*(1+m['terminal_growth'])/(wacc-m['terminal_growth'])/(1+wacc)**5; ev=pvf+pvt; eq=ev-cfg['net_debt']
    return p,ck,dict(wacc=wacc,cost_of_equity=coe,pv_fcff=pvf,pv_tv=pvt,ev=ev,equity_value=eq,per_share=eq/cfg['shares'],tv_share=pvt/ev,implied_ev_ebit=ev/p.ebit.iloc[0])

ocfg={'opening':company,'years':list(range(2027,2032)),'shares':opening['shares'],'net_debt':opening['net_debt']}
_,_,orecon=run_linked(ocfg,BASE,MANUAL)
assert abs(orecon['per_share']-66.02)<.005 and abs(orecon['wacc']-.0998)<.0001 and abs(orecon['tv_share']-1.007)<.002
print('ORACLE REUSABLE-PIPELINE RECONCILIATION: PASS — $%.2f, WACC %.2f%%, TV/EV %.1f%%' % (orecon['per_share'],100*orecon['wacc'],100*orecon['tv_share']))'''),
nbf.v4.new_code_cell(r'''# Microsoft fiscal calendar: FY ends 30 June. Company Facts extraction with provenance, USD millions.
mfacts=json.load(open(CACHE/'CIK0000789019_companyfacts.json'))['facts']['us-gaap']; MFY={2024:('2023-07-01','2024-06-30'),2025:('2024-07-01','2025-06-30'),2026:('2025-07-01','2026-06-30')}
def mfact(tag,fy,dur=False):
    a,b=MFY[fy]; z=[r for r in mfacts[tag]['units']['USD'] if r.get('form')=='10-K' and r.get('end')==b and (not dur or r.get('start')==a)]
    if not z: raise KeyError(f'Missing SEC Company Facts {tag}, FY{fy}')
    return z[-1]
mtags={'revenue':('RevenueFromContractWithCustomerExcludingAssessedTax',True),'operating_income':('OperatingIncomeLoss',True),'net_income':('NetIncomeLoss',True),'capex':('PaymentsToAcquirePropertyPlantAndEquipment',True),'cash':('CashAndCashEquivalentsAtCarryingValue',False),'ar':('AccountsReceivableNetCurrent',False),'inventory':('InventoryNet',False),'ap':('AccountsPayableCurrent',False),'ppe':('PropertyPlantAndEquipmentNet',False),'assets':('Assets',False),'equity':('StockholdersEquity',False),'debt_current':('LongTermDebtCurrent',False),'debt_noncurrent':('LongTermDebtNoncurrent',False)}
rows=[]; prov=[]
for fy in MFY:
 z={'FY':fy}
 for name,(tag,dur) in mtags.items():
  r=mfact(tag,fy,dur); z[name]=r['val']/1e6; prov.append([fy,name,tag,z[name],'USD m',r['accn'],r['filed'],r.get('start','instant'),r['end'],'SEC Company Facts',date.today().isoformat()])
 z['debt']=z.pop('debt_current')+z.pop('debt_noncurrent'); z['liabilities']=z['assets']-z['equity']; z['other_operating_assets']=(z['assets']-z['cash']-z['ar']-z['inventory']-z['ppe'])-(z['liabilities']-z['ap']-z['debt']); rows.append(z)
mh=pd.DataFrame(rows).set_index('FY'); mh['revenue_growth']=mh.revenue.pct_change(); mh['operating_margin']=mh.operating_income/mh.revenue; mh['capex_revenue']=mh.capex/mh.revenue; mprov=pd.DataFrame(prov,columns=['FY','Item','SEC tag','USD m','Units','Accession','Filed','Start','End','Source','Extraction date']); display(mh); display(mprov)'''),
nbf.v4.new_code_cell(r'''mopen=mh.loc[2026,['revenue','cash','ar','inventory','ap','ppe','assets','liabilities','equity','debt','other_operating_assets']].to_dict(); mopen['shares']=7425.545491; mopen['net_debt']=mopen['debt']-mopen['cash']
mgate=pd.DataFrame({'Filed FY2026':[331839.,155237.,133749.,7425.545491,19359.],'Rebuilt':[mh.loc[2026,'revenue'],mh.loc[2026,'operating_income'],mh.loc[2026,'net_income'],mopen['shares'],mopen['net_debt']]},index=['Revenue','Operating income','Net income','Latest filed shares (m)','Net debt']); mgate['Difference']=mgate.Rebuilt-mgate['Filed FY2026']; mgate['Pass']=mgate.Difference.abs()<.01; display(mgate); assert mgate.Pass.all(), 'MICROSOFT FY2026 KNOWN-ANSWER GATE FAILED'; print('MICROSOFT FY2026 KNOWN-ANSWER GATE: PASS')
ma=pd.read_csv(OUT/'wrds_msft_beta_audit.csv'); mr=pd.read_csv(OUT/'wrds_compustat_msft_spy_daily_returns.csv',parse_dates=['datadate']); assert {'datadate','MSFT','SPY'}.issubset(mr.columns) and ma.status.eq('success').any() and ma.source.str.contains('prccd',case=False).any(), 'VALUATION REFUSED: successful WRDS prccd evidence required'; mr=mr[['datadate','MSFT','SPY']].dropna().sort_values('datadate'); MSFT_BETA=mr.MSFT.cov(mr.SPY)/mr.SPY.var(); assert len(mr)>=100 and .2<=MSFT_BETA<=3, 'VALUATION REFUSED: invalid MSFT WRDS beta'; display(ma); print(f'MSFT WRDS beta={MSFT_BETA:.4f}; matched observations={len(mr)}; {mr.datadate.min().date()} to {mr.datadate.max().date()}')'''),
nbf.v4.new_code_cell(r'''# Drivers: FY2027–FY2031. History = opening ratios; judgment = documented forward operating path.
mpx=pd.read_csv(ROOT/'lab6/outputs/wrds_compustat_latest_prices.csv',parse_dates=['date']); mprice=float(mpx[(mpx.ticker=='MSFT')&(mpx.date==pd.Timestamp('2026-09-30'))].close_price.iloc[0])
MM=dict(risk_free_rate=.0506,equity_risk_premium=.04234,terminal_growth=.0300,cash_floor=20000.,dividend_pct_ni=.25,price=mprice,price_date='2026-09-30')
MB=dict(growth=[.15,.13,.11,.09,.07],margin=[.465,.470,.475,.478,.480],tax=[.21]*5,capex=[.30,.28,.24,.20,.17],da_ppe=[.12,.13,.14,.15,.16],ar=mopen['ar']/mopen['revenue'],inventory=mopen['inventory']/mopen['revenue'],ap=mopen['ap']/mopen['revenue'],ono=mopen['other_operating_assets']/mopen['revenue'],debt_rate=.045,beta=MSFT_BETA)
driver_ledger=pd.DataFrame({'Driver':['Revenue growth','EBIT margin','Tax rate','Capex/revenue','D&A/opening PP&E','Working-capital ratios','Debt rate','Cash floor','Terminal growth'],'Values':['15%, 13%, 11%, 9%, 7%','46.5% → 48.0%','21%','30%, 28%, 24%, 20%, 17%','12%, 13%, 14%, 15%, 16%','FY2026 ratios carried','4.5%','20,000 USD m','3.0%'],'Label':['Judgment','Judgment','Judgment','Judgment','Judgment','History','Judgment','Judgment','Judgment'],'Rationale':['Azure/subscriptions and uncertain Copilot monetisation','High margin with AI operating leverage','Forecast statutory simplification','AI infrastructure investment normalises','AI assets create later depreciation','Opening operating balance-sheet ratios','Blended existing-debt estimate','Liquidity policy','Below WACC']}); display(driver_ledger)
mcfg={'opening':mopen,'years':list(range(2027,2032)),'shares':mopen['shares'],'net_debt':mopen['net_debt']}; mp,mchecks,mv=run_linked(mcfg,MB,MM); display(mp); display(mchecks); assert mchecks.PASS.all(); print('MICROSOFT LINKED CHECKS: PASS')'''),
nbf.v4.new_code_cell(r'''MSC={'Low':{'growth':[.10,.09,.08,.07,.06],'margin':[.44,.445,.45,.455,.46],'capex':[.35,.32,.28,.24,.20]},'Base':{},'High':{'growth':[.18,.16,.13,.10,.08],'margin':[.48,.485,.49,.492,.495],'capex':[.26,.24,.21,.18,.15]}}
msrows=[]
for n,ch in MSC.items():
 d=deepcopy(MB); d.update(ch); _,_,x=run_linked(mcfg,d,MM); msrows.append([n,x['per_share'],x['tv_share'],x['wacc']])
mscen=pd.DataFrame(msrows,columns=['Scenario','Value/share','TV/EV','WACC']); display(mscen)
sens={'FY2027 revenue growth':('growth',0,.08,.20),'FY2031 EBIT margin':('margin',4,.44,.52),'FY2027 capex/revenue':('capex',0,.38,.22),'Terminal growth':('terminal_growth',None,.02,.03)}; ts=[]
for name,(field,i,lo,hi) in sens.items():
 vals=[]
 for z in (lo,hi):
  d,m=deepcopy(MB),deepcopy(MM)
  if i is None:m[field]=z
  else:d[field][i]=z
  vals.append(run_linked(mcfg,d,m)[2]['per_share'])
 ts.append([name,*vals,abs(vals[1]-vals[0])])
mtornado=pd.DataFrame(ts,columns=['Driver','Low value/share','High value/share','Swing']).sort_values('Swing',ascending=False); display(mtornado); mhigh=mtornado[mtornado.Driver!='Terminal growth'].iloc[0].Driver
import matplotlib.pyplot as plt
ax=mtornado.set_index('Driver')[['Low value/share','High value/share']].plot.barh(title='Microsoft valuation tornado'); ax.set_xlabel('USD per share'); plt.show()
mbridge=pd.DataFrame({'Measure':['Beta','WACC','PV explicit FCFF','PV terminal value','Terminal value/EV','Enterprise value','Less net debt','Equity value','Shares m','Value/share','WRDS price','Gap vs price','EV/FY2027 EBIT'],'Value':[MSFT_BETA,mv['wacc'],mv['pv_fcff'],mv['pv_tv'],mv['tv_share'],mv['ev'],-mopen['net_debt'],mv['equity_value'],mopen['shares'],mv['per_share'],mprice,mv['per_share']/mprice-1,mv['implied_ev_ebit']]}); display(mbridge)
try:
 bad=deepcopy(MM); bad['terminal_growth']=mv['wacc']; run_linked(mcfg,MB,bad)
except ValueError as e: print('EXPECTED IMPOSSIBLE-INPUT FAILURE:',e)'''),
nbf.v4.new_markdown_cell('''# Comparative exhibit and conditional recommendation'''),
nbf.v4.new_code_cell(r'''orange=scenarios.set_index('Scenario')['Value / share']; mrange=mscen.set_index('Scenario')['Value/share']; ogap=v['per_share']/MANUAL['price']-1; mgap=mv['per_share']/mprice-1
if ogap>0 and mgap<=0: rec='Oracle receives capital; Microsoft is not attractive at its dated price.'
elif mgap>0 and ogap<=0: rec='Microsoft receives capital; Oracle is not attractive at its dated price.'
elif ogap<=0 and mgap<=0: rec='Neither company is attractive at the dated prices; if capital must be deployed, select the less-negative relative gap.'
else: rec='Both companies screen above dated prices; select the higher relative base-case upside subject to sensitivity risk.'
comp=pd.DataFrame({'Metric':['Low/base/high value per share','Dated WRDS price','Base gap $','Base gap %','WACC','Beta','Terminal value/EV','Net debt USD m','EV/FY2027 EBIT','Highest sensitivity','Company-specific driver'],'Oracle':[f'${orange.Low:.2f}/${orange.Base:.2f}/${orange.High:.2f}',f'${MANUAL["price"]:.2f}',f'${v["per_share"]-MANUAL["price"]:.2f}',f'{ogap:.1%}',f'{v["wacc"]:.2%}',f'{WRDS_BETA:.4f}',f'{v["tv_share"]:.1%}',f'${opening["net_debt"]:,.0f}',f'{v["implied_ev_ebit"]:.2f}x',business_tornado,'OCI/AI capacity utilisation and payback'],'Microsoft':[f'${mrange.Low:.2f}/${mrange.Base:.2f}/${mrange.High:.2f}',f'${mprice:.2f}',f'${mv["per_share"]-mprice:.2f}',f'{mgap:.1%}',f'{mv["wacc"]:.2%}',f'{MSFT_BETA:.4f}',f'{mv["tv_share"]:.1%}',f'${mopen["net_debt"]:,.0f}',f'{mv["implied_ev_ebit"]:.2f}x',mhigh,'Azure/subscriptions, Copilot monetisation, AI capex/D&A']}); display(comp); comp.to_csv(OUT.parent/'capstone/capstone_exhibit.csv',index=False); print('CONDITIONAL RECOMMENDATION:',rec)
compchart=pd.DataFrame({'Low':[orange.Low,mrange.Low],'Base':[orange.Base,mrange.Base],'High':[orange.High,mrange.High]},index=['Oracle','Microsoft']); compchart.plot.bar(title='DCF per-share ranges'); plt.ylabel('USD/share'); plt.show()'''),
nbf.v4.new_markdown_cell('''# Flip-point analysis'''),
nbf.v4.new_code_cell(r'''def or_gap(margin):
 d=deepcopy(BASE); d['margin'][4]=margin; return run_linked(ocfg,d,MANUAL)[2]['per_share']/MANUAL['price']-1
target=mgap; grid=np.linspace(.20,.70,501); dif=[or_gap(x)-target for x in grid]; pairs=[(grid[i],grid[i+1]) for i in range(len(grid)-1) if dif[i]*dif[i+1]<=0]
if not pairs: raise RuntimeError('No Oracle FY2031 EBIT-margin flip within 20%–70%; no invented flip point.')
lo,hi=pairs[0]
for _ in range(70):
 mid=(lo+hi)/2
 if (or_gap(lo)-target)*(or_gap(mid)-target)<=0:hi=mid
 else:lo=mid
flip=(lo+hi)/2; fd=deepcopy(BASE); fd['margin'][4]=flip; fval=run_linked(ocfg,fd,MANUAL)[2]['per_share']; hist=(history.operating_margin.min(),history.operating_margin.max()); eps=.002
confirm=pd.DataFrame({'FY2031 Oracle EBIT margin':[flip-eps,flip,flip+eps],'Oracle relative gap':[or_gap(flip-eps),or_gap(flip),or_gap(flip+eps)],'Microsoft relative gap':[mgap]*3}); display(confirm); print(f'Flip point={flip:.4%}; Oracle value=${fval:.2f}; relative gap={or_gap(flip):.4%}; historical operating-margin range={hist[0]:.2%}–{hist[1]:.2%}; flip is {"inside" if hist[0]<=flip<=hist[1] else "outside"} historical range.')'''),
nbf.v4.new_markdown_cell('''# Two observable triggers'''),
nbf.v4.new_code_cell(r'''triggers=pd.DataFrame([['Oracle','FY2031 EBIT margin',f'{flip:.2%}','Oracle Form 10-K; FY2027 fiscal year-end 2027-05-31','Crossing the flip-point threshold changes Oracle relative ranking versus Microsoft.'],['Microsoft','FY2027 revenue growth',f'{MB["growth"][0]:.1%} base; {MSC["Low"]["growth"][0]:.1%} low','Microsoft Form 10-K; FY2027 fiscal year-end 2027-06-30','A result below the low/base boundary changes the Azure/subscription and Copilot revenue driver, FCFF, and valuation.']],columns=['Company','Observable metric','Numeric threshold','Source / next review event','Why it changes the model']); display(triggers)'''),
nbf.v4.new_markdown_cell('''# Check that changed the model

The initial `trfd` beta attempt was rejected after professional-data validation showed it is an adjustment factor rather than a daily-return series. The method changed to saved Compustat Security Daily `prccd` MSFT/SPY returns and manual covariance/variance beta.'''),
nbf.v4.new_markdown_cell('''# Edition A versus model

Paste the original Edition A text verbatim here, then compare its original predictions with the completed model outputs.'''),
nbf.v4.new_markdown_cell('''# Defence facts'''),
nbf.v4.new_code_cell(r'''print('Recommendation:',rec); print('Oracle range',comp.loc[0,'Oracle'],'price',MANUAL['price'],'gap',f'{ogap:.1%}','WACC',f'{v["wacc"]:.2%}','TV/EV',f'{v["tv_share"]:.1%}','sensitivity',business_tornado); print('Microsoft range',comp.loc[0,'Microsoft'],'price',mprice,'gap',f'{mgap:.1%}','WACC',f'{mv["wacc"]:.2%}','TV/EV',f'{mv["tv_share"]:.1%}','sensitivity',mhigh); print('Flip point',f'{flip:.4%}',f'vs historical {hist[0]:.2%}–{hist[1]:.2%}'); display(triggers); print('Check: trfd rejected; prccd return beta adopted. Open Oracle known-answer/beta/tornado; Microsoft fiscal extraction/gate/drivers/tornado; Comparative exhibit; Flip-point analysis; Two observable triggers.')''')]
nbf.write(nb,cap/'Capstone_Oracle_Microsoft_FINAL.ipynb')
nbf.write(nb,cap/'Capstone_Oracle_Microsoft_Final.ipynb')
docs={
'assumptions_ledger_final.md':'''# Assumptions ledger\n\n## Oracle\n\nThe authoritative complete Oracle ledger is `exercise4/assumptions_ledger.md`; its retained results are $48.74/$66.02/$83.67, beta 1.6369, WACC 9.98%, and terminal value/EV 100.7%.\n\n## Microsoft\n\n| Input | Value / unit | Source, date, period | Label | Rationale | Confidence |\n|---|---:|---|---|---|---|\n| Revenue / EBIT / net income | $331,839m / $155,237m / $133,749m | SEC Company Facts, accession 0001193125-26-323660; FY2026 ended 2026-06-30; filed 2026-07-29 | History | Known-answer gate | High |\n| Shares | 7,425.545491m | Microsoft FY2026 10-K cover; 2026-07-23 | Filing-only | Latest filed count | High |\n| Cash / debt / net debt | $20,935m / $40,294m / $19,359m | SEC Company Facts; FY2026 | History | Opening bridge | High |\n| Beta | 0.9360 | WRDS Compustat Security Daily `prccd`; 501 matched returns, 2024-10-01 to 2026-09-30 | History | Manual covariance / SPY variance | High |\n| Price | $512.90/share | WRDS Compustat Security Daily; 2026-09-30 | History | Dated market comparison | High |\n| RF / ERP | 5.06% / 4.234% | Treasury / Damodaran, retained Oracle valuation lane | Judgment | Cost of equity | Medium |\n| Growth / margin | 15%,13%,11%,9%,7% / 46.5% to 48.0% | Analyst judgment, FY2027–31 | Judgment | Azure/subscriptions, Copilot uncertainty, operating leverage | Medium |\n| Capex / D&A | 30%,28%,24%,20%,17% revenue / 12%–16% opening PP&E | Analyst judgment, FY2027–31 | Judgment | AI data-centre investment and depreciation | Medium |\n| Tax / debt / cash floor / terminal growth | 21% / 4.5% / $20,000m / 3.0% | Analyst judgment | Judgment | Linked FCFF policy; terminal growth below WACC | Medium |\n''',
'source_log_final.md':'''# Source log\n\n- Oracle authority: `exercise4/Exercise4_oracle_valuation_final.ipynb`, `exercise4/assumptions_ledger.md`, `exercise4/wrds_beta_audit.csv`, `exercise4/wrds_compustat_orcl_spy_daily_returns.csv`.\n- Microsoft SEC: `lab6/cache/CIK0000789019_companyfacts.json`; filing cache `lab6/cache/microsoft_2026_10k.htm`.\n- Microsoft WRDS beta: `exercise4/wrds_msft_beta_audit.csv`; `exercise4/wrds_compustat_msft_spy_daily_returns.csv`.\n- Dated WRDS price evidence: `lab6/outputs/wrds_compustat_latest_prices.csv`.\n- Fresh-kernel package inputs: both SEC Company Facts caches, cited filing caches, four WRDS return/audit CSVs, and `lab6/outputs/wrds_compustat_latest_prices.csv`.\n''',
'AI_Disclosure_final.md':'''# AI disclosure\n\nCodex / OpenAI assisted with notebook structure, extraction organisation, calculations, validation, and evidence-record assembly. SEC Company Facts, filed share counts, and saved WRDS results were independently checked against the local primary/professional-source files. `trfd` was rejected because it is an adjustment factor rather than a daily-return series; final betas use matched Compustat Security Daily `prccd` returns and manual covariance divided by SPY variance. Final assumptions, conclusions, and recommendation remain the student’s responsibility.\n''',
'memo_evidence_pack.md':'''# Memo evidence pack\n\nPair rationale: Oracle and Microsoft are enterprise-software/cloud-AI comparators with distinct capital-intensity and monetisation paths. Oracle range is $48.74/$66.02/$83.67 versus $137.79, base gap -52.1%, WACC 9.98%, terminal share 100.7%, highest sensitivity FY2031 operating margin. Microsoft range is $277.96/$334.40/$377.66 versus $512.90, base gap -34.8%, WACC 8.97%, terminal share 83.8%, highest sensitivity FY2031 EBIT margin. The completed conditional decision is neither attractive at the dated prices; if deployment is mandatory, Microsoft has the less-negative relative gap. Oracle flip point is 42.2403% FY2031 EBIT margin, outside its 28.99%–30.80% historical range. Triggers: Oracle FY2031 EBIT margin at the flip point, reviewed in the FY2027 10-K cycle; Microsoft FY2027 revenue growth at 15.0% base versus 10.0% low, reviewed at FY2027 fiscal year-end. The check that changed the method rejected `trfd` and adopted `prccd` return beta.\n\nEdition A instruction: Paste the original Edition A text verbatim here, then compare its original predictions with the completed model outputs.\n'''}
msft_ledger=docs['assumptions_ledger_final.md'].split('## Microsoft',1)[1]
docs['assumptions_ledger_final.md']='# Assumptions ledger\n\n## Oracle\n\n'+(ex4/'assumptions_ledger.md').read_text()+'\n\n## Microsoft'+msft_ledger
for name,text in docs.items(): (cap/name).write_text(text)
print(cap/'Capstone_Oracle_Microsoft_FINAL.ipynb')
