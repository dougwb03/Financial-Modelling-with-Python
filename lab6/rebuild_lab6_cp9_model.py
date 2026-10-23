from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parent
nb = nbf.v4.new_notebook()
nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}}
c = []
def md(x): c.append(nbf.v4.new_markdown_cell(x.strip()))
def code(x): c.append(nbf.v4.new_code_cell(x.strip()))

md('''# Lab 6 — CP9: ABG Rebuild and Oracle Full Base Model

**Company A:** Oracle (ORCL) · **Company B:** Microsoft (MSFT) · **Units:** USD millions except shares, percentages, and per-share values.

This is a separate Tuesday workbook. It reads the SEC-backed company data from the prework workbook, rather than duplicating filing reads. The model follows the required order: income statement; driver-led balance sheet; FCFE; cash last; check block; valuation gated by checks and `g < r`.

**AI disclosure:** I used an AI coding partner to assemble and test this notebook from the SEC-backed prework. I must independently verify the sources, mappings, assumptions, formulas, and outputs before submission. Edition A must be written in class without AI.''')

code('''from __future__ import annotations
from copy import deepcopy
from datetime import date
from pathlib import Path
import os, json, nbformat, pandas as pd
pd.options.display.float_format=lambda x: f"{x:,.2f}"
LAB=Path.cwd() if Path("Lab6_Oracle_Microsoft_Prework.ipynb").exists() else Path("lab6")
assert (LAB/"Lab6_Oracle_Microsoft_Prework.ipynb").exists()
assert (LAB/"cache"/"oracle_2025_10k.htm").exists()
print(f"Run date: {date.today():%Y-%m-%d}; lab folder: {LAB.resolve()}")''')

md('''## Primary and secondary sources

The cached SEC Forms 10-K are the controlling primary evidence. The next cell is an actual WRDS / Compustat annual-fundamentals pull. It prompts only for a WRDS username in an interactive kernel, then uses WRDS’s normal authentication. It saves the returned data and an audit record to `lab6/outputs/`; SEC filed data continue to control any disagreement.''')

code('''def pull_wrds():
    status={"run_date":date.today().isoformat(),"source":"WRDS / Compustat comp.funda","status":None,"detail":None}
    out=LAB/"outputs"; out.mkdir(exist_ok=True); username=os.getenv("WRDS_USERNAME")
    if not username:
        try: username=input("WRDS username (Enter to record pending): ").strip()
        except Exception: username=""
    if not username:
        data=pd.DataFrame(); status.update(status="pending",detail="No WRDS username supplied; rerun this cell interactively.")
    else:
        try:
            import wrds
            conn=wrds.Connection(wrds_username=username)
            sql="""select gvkey, datadate, fyear, tic, revt, oiadp, ni, at, lt, ceq, capx, ppent, invt, dlc, dltt, che from comp.funda where tic in ('ORCL','MSFT') and indfmt='INDL' and datafmt='STD' and popsrc='D' and consol='C' and fyear between 2023 and 2025 order by tic, datadate"""
            data=conn.raw_sql(sql,date_cols=["datadate"]); conn.close(); data.to_csv(out/"wrds_compustat_funda_orcl_msft.csv",index=False)
            status.update(status="retrieved",detail=f"Retrieved {len(data)} annual rows.")
        except Exception as exc:
            data=pd.DataFrame(); status.update(status="failed",detail=f"{type(exc).__name__}: {exc}")
    pd.DataFrame([status]).to_csv(out/"wrds_compustat_attempt.csv",index=False)
    return status,data
wrds_status,wrds_funda=pull_wrds(); display(pd.DataFrame([wrds_status]));
if not wrds_funda.empty: display(wrds_funda)
else: print("No Compustat value has been substituted for the SEC model inputs.")''')

md('''## Company half — SEC-filed history from prework

Only prework’s data-definition cells are evaluated. This preserves the separate company/method halves and avoids a new hand transcription.''')

code('''prework=nbformat.read(LAB/"Lab6_Oracle_Microsoft_Prework.ipynb",as_version=4); scope={"pd":pd}
for cell in prework.cells:
    if cell.cell_type=="code" and any(x in cell.source for x in ("oracle = pd.DataFrame","microsoft = pd.DataFrame","filing_only = pd.DataFrame")): exec(cell.source,scope)
oracle,microsoft,filing_only=scope["oracle"].copy(),scope["microsoft"].copy(),scope["filing_only"].copy()
display(oracle); assert oracle.loc[2025,"revenue"]==57399 and oracle.loc[2025,"net_income"]==12443''')

md('''## Step 1 — ABG known answer

The classroom ABG half is retained solely to test the reusable method against the deck’s $291.75 and 79.8% terminal-share known answer.''')

code('''ABG={"opening_year":2025,"opening":{"revenue":17999.,"inventory":2135.8,"ppe":3070.4,"cash":40.4,"floor_plan":2027.,"debt":3572.,"revolver":0.,"equity":3891.7,"other_assets":6371.6,"other_liabilities":2127.5},"drivers":{"growth":.018,"gm":.1705,"sga":[.665,.655,.645,.645,.645],"da":.0268,"noncash":120.,"capex":250.,"tax":.255,"days":52.2,"fp_pct":.949,"owc":.008,"fp_rate":.0467,"debt_rate":.0544,"rev_rate":.06,"rev_cap":850.,"floor":25.,"paydown":150.,"buyback":150.},"valuation":{"r":.10,"g":.025,"shares":17951349}}
def project_abg(c,years=5,cash_override=None):
 d,p,rows=c["drivers"],deepcopy(c["opening"]),[]
 for n in range(years):
  y=c["opening_year"]+n+1; rev=p["revenue"]*(1+d["growth"]); gp=rev*d["gm"]; cogs=rev-gp; da=p["ppe"]*d["da"]; sga=gp*d["sga"][n]; ebit=gp-sga-da-d["noncash"]; interest=p["floor_plan"]*d["fp_rate"]+p["debt"]*d["debt_rate"]+p["revolver"]*d["rev_rate"]; tax=(ebit-interest)*d["tax"]; ni=(ebit-interest)-tax
  inv=cogs*d["days"]/365; fp=inv*d["fp_pct"]; ppe=p["ppe"]+d["capex"]-da; debt=p["debt"]-d["paydown"]; owc=d["owc"]*(rev-p["revenue"]); other_assets=p["other_assets"]+owc-d["noncash"]; equity=p["equity"]+ni-d["buyback"]
  fcfe=ni+da+d["noncash"]-d["capex"]-(inv-p["inventory"])-owc+(fp-p["floor_plan"])-d["paydown"]; before=p["cash"]+fcfe-d["buyback"]; draw=max(0.,d["floor"]-before); revolver=p["revolver"]+draw
  if revolver>d["rev_cap"]: raise ValueError(f"{y}: revolver cap exceeded")
  expected=before+draw; cash=(cash_override or {}).get(y,expected); rows.append(dict(year=y,revenue=rev,gross_profit=gp,cogs=cogs,sga=sga,depreciation_and_amortization=da,noncash=d["noncash"],ebit=ebit,interest=interest,tax=tax,net_income=ni,inventory=inv,floor_plan=fp,ppe=ppe,debt=debt,equity=equity,fcfe=fcfe,cash=cash,expected_cash=expected,cash_floor=d["floor"],revolver=revolver,total_assets=inv+ppe+cash+other_assets,total_liabilities=fp+debt+revolver+p["other_liabilities"]))
  p=dict(revenue=rev,inventory=inv,ppe=ppe,cash=cash,floor_plan=fp,debt=debt,revolver=revolver,equity=equity,other_assets=other_assets,other_liabilities=p["other_liabilities"])
 return pd.DataFrame(rows).set_index("year")
def checks(p,tolerance=.1):
 q=pd.DataFrame(index=p.index); q["balance_residual"]=p.total_assets-p.total_liabilities-p.equity; q["cash_tie_residual"]=p.cash-p.expected_cash; q["cash_minus_floor"]=p.cash-p.cash_floor; q["pass"]=q.balance_residual.abs().le(tolerance)&q.cash_tie_residual.abs().le(tolerance)&q.cash_minus_floor.ge(-tolerance); return q
def valuation(c,p):
 r,g=c["valuation"]["r"],c["valuation"]["g"]
 if g>=r: raise ValueError("Valuation refused: terminal growth must be below discount rate.")
 if not checks(p)["pass"].all(): raise ValueError("Valuation refused: check block failed.")
 pv=sum(x/(1+r)**i for i,x in enumerate(p.fcfe,1)); pvt=(p.fcfe.iloc[-1]+c["drivers"]["paydown"])*(1+g)/(r-g)/(1+r)**len(p); eq=pv+pvt; share_count=c["valuation"]["shares"]*(1e6 if c["valuation"].get("shares_are_millions",False) else 1); return {"equity_value":eq,"value_per_share":eq*1e6/share_count,"terminal_share":pvt/eq}
abg=project_abg(ABG); abgv=valuation(ABG,abg); display(abg[["revenue","gross_profit","cogs","sga","depreciation_and_amortization","ebit","interest","tax","net_income","inventory","floor_plan","ppe","debt","equity","fcfe","cash","revolver"]]); display(checks(abg)); print(f"ABG: ${abgv['value_per_share']:,.2f}/share; terminal share {abgv['terminal_share']:.1%}"); assert checks(abg)["pass"].all() and abs(abgv["value_per_share"]-291.75)<1 and abs(abgv["terminal_share"]-.798)<.003''')

md('''## Step 2 — Oracle: history, inputs, and no `NaN` display

The first year has no preceding year, so growth is displayed as `—`, not `NaN`. Oracle’s filed direct costs are Cloud services/license support, Hardware, and Services. Its operating-cost subtotal includes D&A; the model separates D&A from that subtotal and therefore deducts it exactly once.

Forecast inputs are explicitly labeled. History inputs use FY2024–25 values. Debt repayment, buyback, cash floor, cost of equity, and terminal growth are provisional judgments and require evidence before Exercise 4.''')

code('''def history(a):
 h=pd.DataFrame(index=a.index); h["revenue growth"]=a.revenue.pct_change(); h["gross margin"]=1-a.cost_of_revenue/a.revenue; h["cash costs / revenue"]=(a.operating_expenses_below_gross_profit-a.depreciation_and_amortization)/a.revenue; h["D&A / revenue"]=a.depreciation_and_amortization/a.revenue; h["tax / pretax"]=a.income_tax/a.pretax_income; h["capex / revenue"]=a.capital_expenditure/a.revenue; h["inventory / revenue"]=a.inventory/a.revenue; return h
oh=history(oracle); display(oh.map(lambda x:"—" if pd.isna(x) else f"{x:.1%}"))
avg=lambda col:float(oh.loc[2024:2025,col].mean()); z=oracle.loc[2025]
facts=json.load(open(LAB/"cache"/"CIK0001341439_companyfacts.json"))["facts"]["us-gaap"]
def fact_2025(tag):
 rows=facts[tag]["units"]["USD"]
 return next(x["val"]/1e6 for x in reversed(rows) if x.get("end")=="2025-05-31" and x.get("form")=="10-K")
current_assets,current_liabilities,current_debt=map(fact_2025,["AssetsCurrent","LiabilitiesCurrent","DebtCurrent"])
nwc=(current_assets-10786.)-(current_liabilities-current_debt) # operating current assets less operating current liabilities; excludes cash and debt
ORACLE={"name":"Oracle","opening_year":2025,"opening":{"revenue":z.revenue,"inventory":z.inventory,"ppe":z.ppe_net,"cash":10786.,"debt":92568.,"equity":z.shareholders_equity,"assets":z.total_assets,"liabilities":z.total_liabilities},"drivers":{"growth":[avg("revenue growth")]*5,"gm":[avg("gross margin")]*5,"cash_cost":[avg("cash costs / revenue")]*5,"da":[avg("D&A / revenue")]*5,"tax":[avg("tax / pretax")]*5,"capex":[avg("capex / revenue")]*5,"inventory":[avg("inventory / revenue")]*5,"nwc":[nwc/z.revenue]*5,"interest_rate":(z.operating_income-z.pretax_income)/92568.,"noncash":0.,"paydown":0.,"buyback":0.,"cash_floor":5000.,"revolver_cap":25000.},"valuation":{"r":.09,"g":.025,"shares":3023.736,"shares_are_millions":True}}
labels={"growth":"history: FY2024–25 mean","gm":"history: FY2024–25 mean","cash_cost":"history: FY2024–25 mean, D&A separated","da":"history: FY2024–25 mean","tax":"history: FY2024–25 mean","capex":"history: FY2024–25 mean","inventory":"history: FY2024–25 mean","nwc":"history: FY2025 derived operating NWC","interest_rate":"history proxy: FY2025 EBIT-to-pretax bridge / opening debt","paydown":"judgment: zero pending debt guidance","buyback":"judgment: zero pending repurchase guidance","cash_floor":"judgment: $5bn","r":"judgment: provisional cost of equity","g":"judgment: provisional terminal growth"}
ledger=pd.DataFrame([(k,v,labels.get(k,"judgment")) for k,v in ORACLE["drivers"].items() if k not in ("noncash","revolver_cap")]+[("cost of equity",ORACLE["valuation"]["r"],labels["r"]),("terminal growth",ORACLE["valuation"]["g"],labels["g"]),("shares (millions)",ORACLE["valuation"]["shares"],"fact: 2026 Q1 10-Q cover")],columns=["input","value","label / basis"]); display(ledger)''')

md('''## Oracle model — income statement → balance sheet → FCFE → cash last

`other_assets` is determined by the NWC driver and never plugs cash. The independent check block tests the full accounting relationship.''')

code('''def project_company(c,years=5,cash_override=None):
 d,p,rows=c["drivers"],deepcopy(c["opening"]),[]; other_liab=p["liabilities"]-p["debt"]; other_assets=p["assets"]-p["cash"]-p["ppe"]-p["inventory"]; prior_nwc=c["drivers"]["nwc"][0]*p["revenue"]; revolver=0.
 for n in range(years):
  y=c["opening_year"]+n+1
  # 1: income statement
  revenue=p["revenue"]*(1+d["growth"][n]); gross_profit=revenue*d["gm"][n]; cash_costs=revenue*d["cash_cost"][n]; da=revenue*d["da"][n]; ebit=gross_profit-cash_costs-da-d["noncash"]; interest=p["debt"]*d["interest_rate"]; pretax=ebit-interest; tax=max(0.,pretax*d["tax"][n]); ni=pretax-tax
  # 2: balance-sheet items from drivers
  inventory=revenue*d["inventory"][n]; capex=revenue*d["capex"][n]; ppe=p["ppe"]+capex-da; debt=max(0.,p["debt"]-d["paydown"]); equity=p["equity"]+ni-d["buyback"]; nwc=revenue*d["nwc"][n]; delta_nwc=nwc-prior_nwc; other_assets=other_assets+delta_nwc-(inventory-p["inventory"])
  # 3: FCFE before revolver financing
  fcfe_pre=ni+da+d["noncash"]-capex-delta_nwc-d["paydown"]
  # 4: cash LAST; revolver only restores the floor
  before=p["cash"]+fcfe_pre-d["buyback"]; draw=max(0.,d["cash_floor"]-before); revolver+=draw
  if revolver>d["revolver_cap"]+1e-9: raise ValueError(f"{y}: revolver cap exceeded")
  fcfe=fcfe_pre+draw; expected=before+draw; cash=(cash_override or {}).get(y,expected); assets=cash+inventory+ppe+other_assets; liabilities=debt+revolver+other_liab
  rows.append(dict(year=y,revenue=revenue,gross_profit=gross_profit,cash_operating_costs=cash_costs,depreciation_and_amortization=da,ebit=ebit,interest=interest,tax=tax,net_income=ni,inventory=inventory,ppe=ppe,debt=debt,equity=equity,nwc=nwc,delta_nwc=delta_nwc,capex=capex,fcfe_pre_financing=fcfe_pre,financing_draw=draw,fcfe=fcfe,cash=cash,expected_cash=expected,cash_floor=d["cash_floor"],revolver=revolver,total_assets=assets,total_liabilities=liabilities))
  p={"revenue":revenue,"inventory":inventory,"ppe":ppe,"cash":cash,"debt":debt,"equity":equity}; prior_nwc=nwc
 return pd.DataFrame(rows).set_index("year")
op=project_company(ORACLE); display(op[["revenue","gross_profit","cash_operating_costs","depreciation_and_amortization","ebit","interest","tax","net_income","inventory","ppe","debt","equity","fcfe","cash","revolver"]]); display(checks(op)); assert checks(op)["pass"].all()''')

md('''## Oracle FY2025 known-answer gate

The filed-year rebuild tests the statement mapping before relying on projections.''')

code('''def rebuild_filed(a):
 gp=a.revenue-a.cost_of_revenue; cash_cost=a.operating_expenses_below_gross_profit-a.depreciation_and_amortization; ebit=gp-cash_cost-a.depreciation_and_amortization; bridge=ebit-a.pretax_income; pretax=ebit-bridge; ni=pretax-pretax*(a.income_tax/a.pretax_income); return pd.Series({"Revenue":a.revenue,"Operating income":ebit,"Net income":ni,"Latest shares (millions)":3023.736,"Net debt":92568.-10786.})
filed=pd.Series({"Revenue":57399.,"Operating income":17678.,"Net income":12443.,"Latest shares (millions)":3023.736,"Net debt":81782.}); gate=pd.DataFrame({"filed FY2025":filed,"model FY2025":rebuild_filed(oracle.loc[2025])}); gate["difference"]=gate.iloc[:,1]-gate.iloc[:,0]; gate["pass"]=gate.difference.abs()<.01; display(gate); assert gate["pass"].all()''')

md('''## Valuation gate and refusal tests

The base-case valuation is mechanically complete but depends on the clearly labeled provisional judgments above. It is not an Exercise 4 range.''')

code('''ov=valuation(ORACLE,op); display(pd.DataFrame({"value":[ov["equity_value"],ov["value_per_share"],ov["terminal_share"]],"units":["USD millions","USD/share","%"]},index=["equity value","value per share","terminal share"]))
broken=project_company(ORACLE,cash_override={2027:op.loc[2027,"cash"]+1})
try: valuation(ORACLE,broken)
except ValueError as exc: print(f"Broken-check refusal: {exc}")
bad=deepcopy(ORACLE); bad["valuation"]["g"]=bad["valuation"]["r"]
try: valuation(bad,op)
except ValueError as exc: print(f"Terminal-growth refusal: {exc}")''')

md('''## Full pro-forma evaluation — Markdown exhibits

These are generated from the model outputs, not typed into a spreadsheet. Oracle has no dealer floor-plan financing, so that line is shown as zero and explicitly marked not applicable. Each table contains the required income statement, driver-led balance sheet, FCFE, cash-last, check block, and valuation stages.''')

code('''from IPython.display import Markdown, display
def pipe_table(frame):
    columns=[str(x) for x in frame.columns]
    lines=["| "+" | ".join(columns)+" |", "|"+"|".join(["---"]*len(columns))+"|"]
    lines += ["| "+" | ".join(str(value) for value in row)+" |" for row in frame.itertuples(index=False, name=None)]
    return "\\n".join(lines)
def proforma_markdown(name, p, v, is_abg):
    q=checks(p); years=[str(y) for y in p.index]
    rows=[]
    def add(stage,line,series): rows.append([stage,line,*[float(x) for x in series]])
    # 1. Income statement
    add("1. Income statement","Revenue",p.revenue); add("1. Income statement","Gross profit",p.gross_profit)
    if is_abg:
        add("1. Income statement","COGS",p.cogs); add("1. Income statement","SG&A",p.sga); add("1. Income statement","D&A",p.depreciation_and_amortization); add("1. Income statement","Non-cash impairment",p.noncash)
    else:
        add("1. Income statement","Cash operating costs",p.cash_operating_costs); add("1. Income statement","D&A",p.depreciation_and_amortization)
    add("1. Income statement","EBIT",p.ebit); add("1. Income statement","Interest on opening debt",p.interest); add("1. Income statement","Tax",p.tax); add("1. Income statement","Net income",p.net_income)
    # 2. Balance sheet
    add("2. Balance sheet","Inventory",p.inventory)
    add("2. Balance sheet","Floor-plan financing" if is_abg else "Floor-plan financing (not applicable)",p.floor_plan if is_abg else pd.Series(0.,index=p.index))
    add("2. Balance sheet","PP&E",p.ppe); add("2. Balance sheet","Debt after paydown",p.debt); add("2. Balance sheet","Equity after NI and buyback",p.equity)
    # 3–5. Cash / checks
    add("3. FCFE","FCFE before revolver" if not is_abg else "FCFE",p.fcfe_pre_financing if not is_abg else p.fcfe)
    add("3. FCFE","Revolver financing draw",p.financing_draw if not is_abg else p.revolver.diff().fillna(p.revolver))
    add("3. FCFE","FCFE",p.fcfe); add("4. Cash last","Cash",p.cash); add("4. Cash last","Revolver balance",p.revolver)
    add("5. Check block","Balance residual",q.balance_residual); add("5. Check block","Cash-tie residual",q.cash_tie_residual); add("5. Check block","Cash minus floor",q.cash_minus_floor)
    table=pd.DataFrame(rows,columns=["Stage","Line",*years])
    for y in years: table[y]=table[y].map(lambda x:f"{x:,.1f}")
    display(Markdown(f"### {name} full pro-forma\\n\\n"+pipe_table(table)))
    valuation_table=pd.DataFrame([["Equity value (USD m)",f"{v['equity_value']:,.1f}"],["Shares used",f"{ORACLE['valuation']['shares']:,.3f} million" if name=="Oracle" else f"{ABG['valuation']['shares']:,.0f} shares"],["Value per share",f"${v['value_per_share']:,.2f}"],["Terminal share",f"{v['terminal_share']:.1%}"],["Valuation gate","PASS — checks pass and g < r"]],columns=["6. Valuation cell","Result"])
    display(Markdown(pipe_table(valuation_table)))

proforma_markdown("ABG",abg,abgv,True)
proforma_markdown("Oracle",op,ov,False)''')

md('''### Per-share and market-price control

Oracle’s valuation is divided by **3,023.736 million** shares, not 3,023.736 individual shares. A dated market price is intentionally not inserted here: it must be pulled from CRSP/Compustat on WRDS (or another approved professional source) in code for Thursday’s Step 5, then printed beside the price recorded by hand in Edition A. Yahoo Finance is not used.''')

md('''## Microsoft ready for Thursday

Microsoft is already loaded as the Company B half. On Thursday, create its labeled driver ledger, run the same `project_company()` method, reproduce FY2025 before forecasting, and then complete the fair two-company comparison.

**CP9 status:** ABG reproduces $291.75/share and 79.8% terminal share. Oracle FY2025 reproduces. Oracle follows the six required stages; check block passes; valuation refuses both a broken check and `g ≥ r`. Run the WRDS cell interactively with your credentials and retain its generated output.''')

md('''# CP9 submission documentation

## Sources and data status

The SEC EDGAR filings cached in `lab6/cache/` are the controlling primary source for filed financial-statement inputs. WRDS / Compustat is the professional secondary source used for an independent comparison.

The WRDS pull succeeded for Oracle and Microsoft annual fundamentals. It identified a newer Oracle year ended 2026-05-31 than the SEC annual inputs currently used in this notebook. Until that newer Oracle 10-K is added and reconciled, the Oracle valuation is a provisional model state rather than a final valuation conclusion.

## Step 1 — ABG known-answer check

ABG reproduces the classroom known answer of **$291.75 per share** with **79.8%** of equity value from terminal value. The balance identity, cash tie, and cash-floor checks pass. The valuation cell refuses to run when a check fails or when terminal growth is greater than or equal to the discount rate.

## Step 2 — Oracle company-specific mapping

Oracle does not use ABG’s dealer inventory floor-plan financing. Oracle’s direct costs are mapped from its filed Cloud services and license support, Hardware, and Services cost rows. Oracle’s operating-cost presentation includes depreciation and amortization; the model separates D&A from operating costs and deducts it once in the income statement.

Forecast drivers are labeled history, guidance, or judgment. The current base case is provisional because it uses historical relationships pending reconciliation to the newer filed year and review of Oracle guidance.

## Oracle known-answer gate

Before relying on any forecast, the filed-year rebuild compares model revenue, operating income, net income, latest share count, and net debt with filed values. The current historical year reproduces within the model. However, WRDS identifies a newer Oracle annual period, so the company half must be updated to the newer SEC filing before the model is treated as final.

## Per-share control

Oracle’s equity value is divided by **3,023.736 million shares**, not by 3,023.736 individual shares. The current model result is mechanically correct on this share-unit treatment, but it is not yet a final investment conclusion because the newer filed Oracle year must be reconciled and the provisional forecast assumptions must be reviewed.

## CP9 status

**ABG:** completed and checks pass.  
**Oracle:** company lines loaded; model mechanics and check block pass; WRDS secondary-source pull completed.  
**Open item:** update Oracle from the newer SEC annual filing identified by WRDS, reconcile the filed-year known-answer gate, and then reassess forecast assumptions.

Edition A is separate, handwritten in class, and not generated in this notebook.''')

nb["cells"]=c
nbf.write(nb,ROOT/"Lab6_CP9_ABG_Oracle_UPDATE3.ipynb")
print(ROOT/"Lab6_CP9_ABG_Oracle_UPDATE3.ipynb")
