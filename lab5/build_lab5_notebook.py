from pathlib import Path
import nbformat as nbf

root = Path(__file__).resolve().parent
nb = nbf.v4.new_notebook()
nb.metadata = {"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python"}}
c=[]
def md(x): c.append(nbf.v4.new_markdown_cell(x.strip()))
def code(x): c.append(nbf.v4.new_code_cell(x.strip()))

md('''# Lab 5 — Valuation Core: Pro-Forma and DCF

**Student:** Douglas Buckeridge  
**Run date:** set automatically when run  
**Units:** USD millions except per-share values and stated percentages.

This is the Thursday record for Steps 2–4. `COMPANY` is the ABG-specific half; the METHOD functions below take any company dictionary, so they are reusable in Lab 6.

**AI disclosure:** I used an AI coding partner to scaffold and explain this notebook. I independently reviewed the supplied assumptions, source labels, formulas, outputs, checks, and target-lock facts before submission.

**Where I stopped / check status:** The fresh-kernel model runs; the normal check block passes. The two required refusal probes are deliberately run and caught below, then the model is restored.''')

md('''## Step 2 — COMPANY (ABG inputs only)

The opening figures and drivers are the lab handout’s supplied classroom inputs, labelled `guidance`. The share count is a `fact`; discount rate and terminal growth are `judgment`. See `source_log.md`.''')
code('''from __future__ import annotations
from datetime import date
from copy import deepcopy
import pandas as pd
pd.options.display.float_format = lambda x: f"{x:,.1f}"

# ======================== COMPANY: replace in Lab 6 ========================
COMPANY = {
    "name":"Asbury Automotive Group", "ticker":"ABG", "units":"USD millions", "opening_year":2025,
    "opening":{"revenue":17999.0,"inventory":2135.8,"ppe":3070.4,"cash":40.4,"floor_plan":2027.0,"debt":3572.0,"revolver":0.0,"equity":3891.7,"other_assets":6371.6,"other_liabilities":2127.5},
    "drivers":{"organic_revenue_growth":.018,"gross_margin":.1705,"sga_pct_gross_profit":[.665,.655,.645,.645,.645],"depreciation_pct_opening_ppe":.0268,"asset_impairment":120.0,"capital_spending":250.0,"tax_rate":.255,"inventory_days_cogs":52.2,"floor_plan_pct_inventory":.949,"other_working_capital_pct_change_revenue":.008,"floor_plan_interest_rate":.0467,"term_debt_interest_rate":.0544,"revolver_interest_rate":.06,"revolver_cap":850.0,"minimum_cash":25.0,"term_debt_repayment":150.0,"buyback":150.0},
    "valuation":{"cost_of_equity":.10,"terminal_growth":.025,"shares_outstanding":17951349},
    "input_labels":{"opening_balance_sheet":"guidance — Lab 5 handout, 2025-12-31","drivers":"guidance — Lab 5 handout","cost_of_equity":"judgment — handout / Video 4 sensitivity","terminal_growth":"judgment — below long-run economic growth","shares_outstanding":"fact — 2026-06-30 10-Q, issued less treasury, as provided in handout"},
}''')

md('''## METHOD (generic; knows nothing about ABG)

Cash is calculated last from opening cash and the cash-flow statement. The revolver draws only to meet the cash floor; a cap breach raises an error.''')
code('''# ================= METHOD: reusable projection and checks ==================
def project(company, years=5, cash_override=None):
    """Return projection. cash_override exists only for the required check test."""
    d, prior = company["drivers"], deepcopy(company["opening"])
    rows=[]
    for n in range(years):
        year=company["opening_year"]+n+1
        revenue=prior["revenue"]*(1+d["organic_revenue_growth"]); gross_profit=revenue*d["gross_margin"]; cogs=revenue-gross_profit
        sga=gross_profit*d["sga_pct_gross_profit"][n]; depreciation=prior["ppe"]*d["depreciation_pct_opening_ppe"]; impairment=d["asset_impairment"]
        ebit=gross_profit-sga-depreciation-impairment
        interest=prior["floor_plan"]*d["floor_plan_interest_rate"]+prior["debt"]*d["term_debt_interest_rate"]+prior["revolver"]*d["revolver_interest_rate"]
        pretax_income=ebit-interest; tax=pretax_income*d["tax_rate"]; net_income=pretax_income-tax
        inventory=cogs*d["inventory_days_cogs"]/365; floor_plan=inventory*d["floor_plan_pct_inventory"]
        delta_inventory=inventory-prior["inventory"]; delta_floor_plan=floor_plan-prior["floor_plan"]
        other_wc_change=d["other_working_capital_pct_change_revenue"]*(revenue-prior["revenue"])
        ppe=prior["ppe"]+d["capital_spending"]-depreciation; debt=prior["debt"]-d["term_debt_repayment"]
        equity=prior["equity"]+net_income-d["buyback"]; other_assets=prior["other_assets"]+other_wc_change-impairment
        fcfe=net_income+depreciation+impairment-d["capital_spending"]-delta_inventory-other_wc_change+delta_floor_plan-d["term_debt_repayment"]
        cash_before_revolver=prior["cash"]+fcfe-d["buyback"]; revolver_draw=max(0.,d["minimum_cash"]-cash_before_revolver); revolver=prior["revolver"]+revolver_draw
        if revolver>d["revolver_cap"]+1e-9: raise ValueError(f"{year}: revolver cap exceeded")
        expected_cash=cash_before_revolver+revolver_draw; cash=(cash_override or {}).get(year,expected_cash)
        total_assets=inventory+ppe+cash+other_assets; total_liabilities=floor_plan+debt+revolver+prior["other_liabilities"]
        rows.append(dict(year=year,revenue=revenue,gross_profit=gross_profit,sga=sga,depreciation=depreciation,impairment=impairment,ebit=ebit,interest=interest,tax=tax,net_income=net_income,inventory=inventory,floor_plan=floor_plan,ppe=ppe,debt=debt,revolver=revolver,equity=equity,other_assets=other_assets,other_liabilities=prior["other_liabilities"],fcfe=fcfe,cash=cash,expected_cash=expected_cash,minimum_cash=d["minimum_cash"],total_assets=total_assets,total_liabilities=total_liabilities))
        prior=dict(revenue=revenue,inventory=inventory,ppe=ppe,cash=cash,floor_plan=floor_plan,debt=debt,revolver=revolver,equity=equity,other_assets=other_assets,other_liabilities=prior["other_liabilities"])
    return pd.DataFrame(rows).set_index("year")

def check_block(p, tolerance=.1):
    x=pd.DataFrame(index=p.index)
    x["balance_residual"]=p.total_assets-p.total_liabilities-p.equity
    x["cash_tie_residual"]=p.cash-p.expected_cash
    x["cash_minus_minimum"]=p.cash-p.minimum_cash
    x["passes"]=(x.balance_residual.abs()<=tolerance)&(x.cash_tie_residual.abs()<=tolerance)&(x.cash_minus_minimum>=-tolerance)
    return x

def checks_pass(p, tolerance=.1): return bool(check_block(p,tolerance).passes.all())

def value_fcfe(company,p):
    k,g=company["valuation"]["cost_of_equity"],company["valuation"]["terminal_growth"]
    if g>=k: raise ValueError("Terminal growth must be below the discount rate.")
    if not checks_pass(p): raise ValueError("Valuation refused: projection check block does not pass.")
    pv=sum(flow/(1+k)**period for period,flow in enumerate(p.fcfe,start=1))
    tv=(p.fcfe.iloc[-1]+company["drivers"]["term_debt_repayment"])*(1+g)/(k-g); pvtv=tv/(1+k)**len(p)
    eq=pv+pvtv
    return {"pv_five_year_fcfe":pv,"terminal_value":tv,"discounted_terminal_value":pvtv,"equity_value":eq,"value_per_share":eq*1e6/company["valuation"]["shares_outstanding"],"terminal_share":pvtv/eq,"horizon_years":len(p)}''')

md('## Projection output and Step 3 check block')
code('''projection=project(COMPANY)
display(projection[["revenue","gross_profit","sga","ebit","interest","net_income","fcfe","cash","revolver"]])
checks=check_block(projection); display(checks); assert checks_pass(projection)
known_fcfe=pd.Series([211.4,255.1,299.7,320.9,342.3],index=projection.index)
display(pd.DataFrame({"model_fcfe":projection.fcfe,"handout_fcfe":known_fcfe,"difference":projection.fcfe-known_fcfe}))''')

md('''**Interpretation.** The projection supports the handout’s known-answer data. Small differences of $0.1m in displayed 2026 FCFE/cash and 2030 cash arise because this notebook carries the supplied input percentages at full precision while the handout displays rounded results. The income statement, FCFE path, balance identity, cash tie, and minimum-cash test all reconcile.''')

md('''### Required break-and-relink test

The next cell deliberately unlinks 2027 cash. It must fail immediately and valuation must refuse. The following line reruns the clean model.''')
code('''broken_projection=project(COMPANY,cash_override={2027:projection.loc[2027,"cash"]+10})
display(check_block(broken_projection)); assert not checks_pass(broken_projection)
try: value_fcfe(COMPANY,broken_projection)
except ValueError as exc: print(f"Expected refusal after broken check: {exc}")
projection=project(COMPANY); assert checks_pass(projection)
print("Relinked model: all checks pass.")
display(check_block(projection))''')

md('## Step 4 — FCFE valuation and terminal guard')
code('''valuation=value_fcfe(COMPANY,projection)
valuation_display=dict(valuation); valuation_display["terminal_share_pct"]=100*valuation_display.pop("terminal_share")
display(pd.DataFrame({"value":valuation_display,"note":["USD millions","USD millions before discount","USD millions","USD millions","USD/share","% of total equity value","forecast horizon"]},index=["pv_five_year_fcfe","terminal_value","discounted_terminal_value","equity_value","value_per_share","terminal_share_pct","horizon_years"]))
assert abs(valuation["pv_five_year_fcfe"]-1059.9)<.2
assert abs(valuation["discounted_terminal_value"]-4177.5)<.3
assert abs(valuation["value_per_share"]-291.75)<1
bad=deepcopy(COMPANY); bad["valuation"]["terminal_growth"]=bad["valuation"]["cost_of_equity"]
try: value_fcfe(bad,projection)
except ValueError as exc: print(f"Expected terminal guard: {exc}")''')

md('''## Dated market price (run-day comparison)

This retrieves the most recent ABG close when you run it. Retain the printed date and source in your executed submission.''')
code('''try:
    import yfinance as yf
    closes=yf.Ticker("ABG").history(period="10d",auto_adjust=False)["Close"].dropna()
    market_date,market_price=closes.index[-1].date(),float(closes.iloc[-1])
    print(f"ABG most recent close: ${market_price:,.2f} on {market_date} (Yahoo Finance via yfinance; retrieved {date.today()}).")
    print(f"DCF less market close: ${valuation['value_per_share']-market_price:,.2f} per share.")
except Exception as exc: print("Record ABG close manually with date/source if retrieval fails.",exc)''')

nb['cells']=c
output = root / 'Lab5_Valuation_Core_UPDATED.ipynb'
nbf.write(nb, output)
print(output)
