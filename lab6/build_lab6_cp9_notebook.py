from pathlib import Path
import nbformat as nbf


ROOT = Path(__file__).resolve().parent
nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python"},
}
cells = []


def md(source):
    cells.append(nbf.v4.new_markdown_cell(source.strip()))


def code(source):
    cells.append(nbf.v4.new_code_cell(source.strip()))


md("""
# Lab 6 — CP9: ABG Rebuild and Oracle Company-A Swap

**Student:** Douglas Buckeridge  
**Companies:** Company A = Oracle (ORCL); Company B = Microsoft (MSFT)  
**Units:** USD millions except per-share values, shares, and percentages.

This is a new Tuesday workbook, separate from `Lab6_Oracle_Microsoft_Prework.ipynb`. It deliberately has two halves:

- **COMPANY:** SEC-filed history, company-specific mappings and labeled inputs.
- **METHOD:** the ABG pro-forma, check block, and FCFE valuation functions.

The prework notebook remains the immutable filed-line source. This workbook reads its validated Oracle/Microsoft tables instead of duplicating hand-entered figures. The cached 10-Ks in `cache/` remain controlling primary evidence; the WRDS / Compustat block is a secondary-source extraction attempt and comparison, never a substitute for a filing.

**Scope:** Steps 1–2 only. ABG is fully verified. Oracle is loaded and its FY2025 filed year is rebuilt before any forecast; Microsoft is loaded as the clean Thursday swap. No Edition A, valuation range, recommendation, flip point, trigger, or peer note is generated here.

**AI disclosure:** I used an AI coding partner to assemble and test this executable workbook from my prior SEC-backed prework and the course method. I independently need to review every source, mapping, input, formula, and output before submission. Edition A must be written in class with no AI open.
""")

md("""
## Sources and source hierarchy

1. **Primary / controlling:** Oracle and Microsoft Forms 10-K, SEC EDGAR, cached in `lab6/cache/`, with accession numbers retained in prework. The filed financial statements control disagreements.
2. **Structured primary aid:** SEC Company Facts JSON, cached with the filings and used in the prework’s annual-line construction.
3. **Secondary / professional:** WRDS Compustat North America Fundamentals Annual (`comp.funda`). The code below uses WRDS credentials only if they are configured. If unavailable, it records a dated, honest pending-access attempt—never fabricated Compustat values.

The supplied Week 6 deck requires: income statement first; driver-based balance-sheet items; FCFE; cash **last**; then balance identity, cash tie, cash floor, and terminal-growth checks. Valuation must refuse when any required condition fails.
""")

code("""
from __future__ import annotations

from copy import deepcopy
from datetime import date
from pathlib import Path
import os
import json
import nbformat
import pandas as pd

pd.options.display.float_format = lambda x: f"{x:,.2f}"

LAB = Path.cwd()
if not (LAB / "Lab6_Oracle_Microsoft_Prework.ipynb").exists():
    LAB = Path("lab6")
assert (LAB / "Lab6_Oracle_Microsoft_Prework.ipynb").exists(), "Run from repository root or lab6/."
assert (LAB / "cache" / "oracle_2025_10k.htm").exists(), "Missing cached Oracle 2025 10-K."
assert (LAB / "cache" / "microsoft_2025_10k.htm").exists(), "Missing cached Microsoft 2025 10-K."
print(f"Run date: {date.today().isoformat()} | Lab folder: {LAB.resolve()}")
""")

md("""
## COMPANY — filed history read from the separate prework workbook

Only the three data-definition cells from prework are evaluated here. This avoids a second manual transcription while retaining every figure’s statement/accession provenance in the source notebook and `source_log.md`.
""")

code("""
prework = nbformat.read(LAB / "Lab6_Oracle_Microsoft_Prework.ipynb", as_version=4)
prework_ns = {"pd": pd}
needed = ("oracle = pd.DataFrame", "microsoft = pd.DataFrame", "filing_only = pd.DataFrame")
for cell in prework.cells:
    if cell.cell_type == "code" and any(token in cell.source for token in needed):
        exec(cell.source, prework_ns)

oracle = prework_ns["oracle"].copy()
microsoft = prework_ns["microsoft"].copy()
filing_only = prework_ns["filing_only"].copy()
assert oracle.loc[2025, "revenue"] == 57399
assert microsoft.loc[2025, "revenue"] == 281724
display(oracle)
""")

md("""
## Secondary source — WRDS / Compustat comparison attempt

This is intentionally executable rather than a claim that WRDS data were retrieved. Set `WRDS_USERNAME` and the normal WRDS password mechanism before running if access is available. The query selects annual industrial-format fields for ORCL and MSFT; it writes an audit CSV whether the pull succeeds or not. SEC values remain the model inputs and control any difference.
""")

code("""
wrds_fields = "gvkey, datadate, fyear, tic, revt, oiadp, ni, at, lt, ceq, capx, ppent, invt, dlc, dltt, che"
wrds_status = {"run_date": date.today().isoformat(), "status": None, "detail": None}
wrds_compare = pd.DataFrame()

if not os.getenv("WRDS_USERNAME"):
    wrds_status.update(status="pending", detail="WRDS_USERNAME is not configured in this kernel; no credential-free Compustat query is possible.")
else:
    try:
        import wrds
        conn = wrds.Connection(wrds_username=os.environ["WRDS_USERNAME"])
        query = ("select " + wrds_fields + " from comp.funda "
                 "where tic in ('ORCL', 'MSFT') "
                 "and indfmt = 'INDL' and datafmt = 'STD' and popsrc = 'D' and consol = 'C' "
                 "and fyear between 2023 and 2025 order by tic, datadate")
        wrds_compare = conn.raw_sql(query, date_cols=["datadate"])
        conn.close()
        wrds_status.update(status="retrieved", detail=f"{len(wrds_compare)} Compustat annual rows returned.")
    except Exception as exc:
        wrds_status.update(status="failed", detail=f"{type(exc).__name__}: {exc}")

audit_path = LAB / "outputs"
audit_path.mkdir(exist_ok=True)
pd.DataFrame([wrds_status]).to_csv(audit_path / "wrds_compustat_attempt.csv", index=False)
if not wrds_compare.empty:
    wrds_compare.to_csv(audit_path / "wrds_compustat_funda_orcl_msft.csv", index=False)
display(pd.DataFrame([wrds_status]))
if wrds_status["status"] != "retrieved":
    print("SEC 10-K values remain controlling. Supply WRDS credentials and rerun this one cell to produce the secondary comparison.")
else:
    display(wrds_compare)
""")

md("""
## Step 1 — ABG known-answer rebuild

This is the reusable **METHOD** built against the ABG classroom input half. The mechanics follow the deck exactly: interest is on opening debt; balance-sheet lines follow drivers; FCFE comes before cash; cash is calculated last; and the valuation cell refuses failed checks or `g ≥ r`.
""")

code("""
ABG = {
    "name": "Asbury Automotive Group", "ticker": "ABG", "opening_year": 2025,
    "opening": {"revenue": 17999.0, "inventory": 2135.8, "ppe": 3070.4, "cash": 40.4,
                "floor_plan": 2027.0, "debt": 3572.0, "revolver": 0.0, "equity": 3891.7,
                "other_assets": 6371.6, "other_liabilities": 2127.5},
    "drivers": {"organic_revenue_growth": .018, "gross_margin": .1705,
                "sga_pct_gross_profit": [.665, .655, .645, .645, .645],
                "depreciation_pct_opening_ppe": .0268, "asset_impairment": 120.0,
                "capital_spending": 250.0, "tax_rate": .255, "inventory_days_cogs": 52.2,
                "floor_plan_pct_inventory": .949, "other_working_capital_pct_change_revenue": .008,
                "floor_plan_interest_rate": .0467, "term_debt_interest_rate": .0544,
                "revolver_interest_rate": .060, "revolver_cap": 850.0, "minimum_cash": 25.0,
                "term_debt_repayment": 150.0, "buyback": 150.0},
    "valuation": {"cost_of_equity": .10, "terminal_growth": .025, "shares_outstanding": 17_951_349},
}

def project_abg(company, years=5, cash_override=None):
    # ABG method half. Cash is calculated only after FCFE and buyback.
    d, prior, rows = company["drivers"], deepcopy(company["opening"]), []
    for n in range(years):
        year = company["opening_year"] + n + 1
        revenue = prior["revenue"] * (1 + d["organic_revenue_growth"])
        gross_profit = revenue * d["gross_margin"]
        cogs = revenue - gross_profit
        sga = gross_profit * d["sga_pct_gross_profit"][n]
        depreciation = prior["ppe"] * d["depreciation_pct_opening_ppe"]
        ebit = gross_profit - sga - depreciation - d["asset_impairment"]
        interest = (prior["floor_plan"] * d["floor_plan_interest_rate"] + prior["debt"] * d["term_debt_interest_rate"] + prior["revolver"] * d["revolver_interest_rate"])
        pretax, tax = ebit - interest, (ebit - interest) * d["tax_rate"]
        net_income = pretax - tax
        inventory = cogs * d["inventory_days_cogs"] / 365
        floor_plan = inventory * d["floor_plan_pct_inventory"]
        other_wc_change = d["other_working_capital_pct_change_revenue"] * (revenue - prior["revenue"])
        ppe = prior["ppe"] + d["capital_spending"] - depreciation
        debt = prior["debt"] - d["term_debt_repayment"]
        equity = prior["equity"] + net_income - d["buyback"]
        other_assets = prior["other_assets"] + other_wc_change - d["asset_impairment"]
        fcfe = net_income + depreciation + d["asset_impairment"] - d["capital_spending"] - (inventory - prior["inventory"]) - other_wc_change + (floor_plan - prior["floor_plan"]) - d["term_debt_repayment"]
        cash_before_revolver = prior["cash"] + fcfe - d["buyback"]
        revolver_draw = max(0.0, d["minimum_cash"] - cash_before_revolver)
        revolver = prior["revolver"] + revolver_draw
        if revolver > d["revolver_cap"] + 1e-9:
            raise ValueError(f"{year}: revolver cap exceeded")
        expected_cash = cash_before_revolver + revolver_draw
        cash = (cash_override or {}).get(year, expected_cash)
        total_assets = inventory + ppe + cash + other_assets
        total_liabilities = floor_plan + debt + revolver + prior["other_liabilities"]
        rows.append(dict(year=year, revenue=revenue, gross_profit=gross_profit, sga=sga, depreciation=depreciation, ebit=ebit, interest=interest, net_income=net_income, inventory=inventory, ppe=ppe, debt=debt, revolver=revolver, equity=equity, fcfe=fcfe, cash=cash, expected_cash=expected_cash, minimum_cash=d["minimum_cash"], total_assets=total_assets, total_liabilities=total_liabilities))
        prior = dict(revenue=revenue, inventory=inventory, ppe=ppe, cash=cash, floor_plan=floor_plan, debt=debt, revolver=revolver, equity=equity, other_assets=other_assets, other_liabilities=prior["other_liabilities"])
    return pd.DataFrame(rows).set_index("year")

def check_block(projection, tolerance=.1):
    checks = pd.DataFrame(index=projection.index)
    checks["balance_residual"] = projection.total_assets - projection.total_liabilities - projection.equity
    checks["cash_tie_residual"] = projection.cash - projection.expected_cash
    checks["cash_minus_floor"] = projection.cash - projection.minimum_cash
    checks["pass"] = (checks.balance_residual.abs() <= tolerance) & (checks.cash_tie_residual.abs() <= tolerance) & (checks.cash_minus_floor >= -tolerance)
    return checks

def value_fcfe(company, projection):
    k, g = company["valuation"]["cost_of_equity"], company["valuation"]["terminal_growth"]
    if g >= k:
        raise ValueError("Valuation refused: terminal growth must be below the discount rate.")
    if not check_block(projection)["pass"].all():
        raise ValueError("Valuation refused: the projection check block does not pass.")
    pv_fcfe = sum(flow / (1 + k) ** period for period, flow in enumerate(projection.fcfe, 1))
    terminal_value = (projection.fcfe.iloc[-1] + company["drivers"]["term_debt_repayment"]) * (1 + g) / (k - g)
    pv_terminal = terminal_value / (1 + k) ** len(projection)
    equity_value = pv_fcfe + pv_terminal
    return {"pv_five_year_fcfe": pv_fcfe, "discounted_terminal_value": pv_terminal, "equity_value": equity_value, "value_per_share": equity_value * 1e6 / company["valuation"]["shares_outstanding"], "terminal_share": pv_terminal / equity_value}
""")

code("""
abg_projection = project_abg(ABG)
abg_checks = check_block(abg_projection)
abg_value = value_fcfe(ABG, abg_projection)
display(abg_projection.loc[:, ["revenue", "ebit", "net_income", "fcfe", "cash", "revolver"]])
display(abg_checks)
print(f"ABG value per share: ${abg_value['value_per_share']:,.2f}")
print(f"ABG terminal share: {abg_value['terminal_share']:.1%}")
assert abg_checks["pass"].all(), "ABG check block failed. Walk back to the first divergent line."
assert abs(abg_value["value_per_share"] - 291.75) < 1.00
assert abs(abg_value["terminal_share"] - .798) < .003
""")

md("""
### Required refusal probes

The next cell proves both guards are live, then restores the clean ABG state. A green tick without these controls would not be evidence that the valuation is protected.
""")

code("""
broken = project_abg(ABG, cash_override={2027: abg_projection.loc[2027, "cash"] + 10})
assert not check_block(broken)["pass"].all()
try:
    value_fcfe(ABG, broken)
except ValueError as exc:
    print(exc)
bad_terminal = deepcopy(ABG)
bad_terminal["valuation"]["terminal_growth"] = bad_terminal["valuation"]["cost_of_equity"]
try:
    value_fcfe(bad_terminal, abg_projection)
except ValueError as exc:
    print(exc)
""")

md("""
## Step 2 — Company A swap: Oracle

Oracle does not inherit ABG’s floor-plan or franchise-right mechanics. Its distinguishing valuation driver is cloud-infrastructure capacity: 2025 capex rose sharply while revenue, margin, and cash generation need to be read together. Oracle’s filed income statement does not print gross profit: prework maps `cost_of_revenue` from the named Cloud services/license support, Hardware, and Services direct-cost rows. D&A is embedded in the reported operating-cost presentation and therefore is **not subtracted again** in this filed-year income-statement rebuild.
""")

code("""
def company_half(name, ticker, annual, shares_millions, debt, cash, accessions):
    latest = annual.loc[2025]
    history = pd.DataFrame(index=annual.index)
    history["revenue_growth"] = annual.revenue.pct_change()
    history["operating_margin"] = annual.operating_income / annual.revenue
    history["cash_tax_rate"] = annual.income_tax / annual.pretax_income
    history["capex_pct_revenue"] = annual.capital_expenditure / annual.revenue
    history["d_and_a_pct_revenue"] = annual.depreciation_and_amortization / annual.revenue
    history["inventory_pct_revenue"] = annual.inventory / annual.revenue
    return {
        "name": name, "ticker": ticker, "annual": annual.copy(), "history": history,
        "opening_year": 2025, "opening": {"revenue": latest.revenue, "cash": cash, "debt": debt, "ppe": latest.ppe_net, "inventory": latest.inventory, "equity": latest.shareholders_equity, "assets": latest.total_assets, "liabilities": latest.total_liabilities},
        "valuation": {"shares_outstanding_millions": shares_millions}, "accessions": accessions,
    }

ORACLE = company_half("Oracle", "ORCL", oracle, 3023.736, 92568, 10786,
                      {2025: "0000950170-25-087926", "latest_shares": "0001193125-26-389274"})
MICROSOFT = company_half("Microsoft", "MSFT", microsoft, 7425.545491, 41787, 30242,
                         {2025: "0000950170-25-100235", "latest_shares": "0001193125-26-323660"})

oracle_ledger = pd.DataFrame([
    ["Revenue growth", None, "history / guidance / judgment", "Choose after reviewing the history and Oracle guidance; do not retain ABG growth."],
    ["Direct-cost ratio / operating margin", None, "history / guidance / judgment", "Oracle direct-cost presentation is filing-specific; no ABG gross-margin carryover."],
    ["Cash tax rate", None, "history / guidance / judgment", "Normalize explicitly; FY2025 filed tax rate is shown in history."],
    ["Capex / revenue", None, "history / guidance / judgment", "Cloud infrastructure capacity is the company-specific driver."],
    ["D&A method", None, "history / judgment", "Do not subtract it twice in the filed-income-statement rebuild."],
    ["Working capital / revenue", None, "history / judgment", "No dealer inventory / floor-plan mechanic."],
    ["Debt repayment and buyback", None, "guidance / judgment", "Must be modeled with a dated filing or management source."],
    ["Cost of equity", None, "judgment", "Use the same components as Microsoft; beta and leverage may differ."],
    ["Terminal growth", None, "judgment", "Must remain below cost of equity."],
    ["Latest shares outstanding (millions)", 3023.736, "fact", "Oracle 2026 Q1 10-Q cover; accession 0001193125-26-389274."],
], columns=["input", "value", "label", "basis / source note"])
display(ORACLE["history"].style.format("{:.1%}"))
display(oracle_ledger)
""")

md("""
### Oracle FY2025 known-answer gate — before forecasting

This rebuild uses Oracle’s own FY2025 statement relationships: revenue less filed direct costs less filed below-gross-profit operating costs equals operating income; the filed non-operating bridge takes operating income to pretax income; filed tax takes pretax income to net income. It is a test of the source mapping, not a projection or a valuation.
""")

code("""
def rebuild_filed_year(company, fiscal_year):
    a = company["annual"].loc[fiscal_year]
    direct_cost_ratio = a.cost_of_revenue / a.revenue
    opex_ratio = a.operating_expenses_below_gross_profit / a.revenue
    revenue = a.revenue
    direct_cost = revenue * direct_cost_ratio
    operating_expenses = revenue * opex_ratio
    operating_income = revenue - direct_cost - operating_expenses
    non_operating_bridge = a.pretax_income - operating_income
    pretax_income = operating_income + non_operating_bridge
    income_tax = pretax_income * (a.income_tax / a.pretax_income)
    net_income = pretax_income - income_tax
    return pd.Series({"Revenue": revenue, "Operating income": operating_income, "Net income": net_income, "Latest shares (millions)": company["valuation"]["shares_outstanding_millions"], "Net debt": company["opening"]["debt"] - company["opening"]["cash"]})

oracle_model_2025 = rebuild_filed_year(ORACLE, 2025)
oracle_filed_2025 = pd.Series({"Revenue": 57399.0, "Operating income": 17678.0, "Net income": 12443.0, "Latest shares (millions)": 3023.736, "Net debt": 81782.0})
oracle_gate = pd.DataFrame({"filed_2025": oracle_filed_2025, "model_2025": oracle_model_2025})
oracle_gate["difference"] = oracle_gate.model_2025 - oracle_gate.filed_2025
oracle_gate["pass"] = oracle_gate.difference.abs() < .01
display(oracle_gate)
assert oracle_gate["pass"].all(), "Oracle known-answer gate failed. Fix the filed mapping before forecasting."
print("Oracle FY2025 known-answer gate passes. Forecasting remains intentionally unstarted until assumptions are selected and labeled.")
""")

md("""
## Company B ready to swap on Thursday — Microsoft

Microsoft is loaded through the identical company-half constructor; nothing in the METHOD is changed. Its FY2025 known-answer check is shown as a staged, independently runnable gate, but no Thursday valuation/decision task is completed early.
""")

code("""
def rebuild_microsoft_filed_year(company, fiscal_year):
    a = company["annual"].loc[fiscal_year]
    revenue = a.revenue
    operating_income = revenue - a.cost_of_revenue - a.operating_expenses
    pretax_income = operating_income + (a.pretax_income - operating_income)
    net_income = pretax_income - a.income_tax
    return pd.Series({"Revenue": revenue, "Operating income": operating_income, "Net income": net_income, "Latest shares (millions)": company["valuation"]["shares_outstanding_millions"], "Net debt": company["opening"]["debt"] - company["opening"]["cash"]})

microsoft_model_2025 = rebuild_microsoft_filed_year(MICROSOFT, 2025)
microsoft_filed_2025 = pd.Series({"Revenue": 281724.0, "Operating income": 128528.0, "Net income": 101832.0, "Latest shares (millions)": 7425.545491, "Net debt": 11545.0})
microsoft_gate = pd.DataFrame({"filed_2025": microsoft_filed_2025, "model_2025": microsoft_model_2025})
microsoft_gate["difference"] = microsoft_gate.model_2025 - microsoft_gate.filed_2025
microsoft_gate["pass"] = microsoft_gate.difference.abs() < .01
display(microsoft_gate)
assert microsoft_gate["pass"].all()
""")

md("""
## CP9 status

**Status:** ABG reproduces the deck’s $291.75/share and 79.8% terminal share; its balance, cash-tie, cash-floor, and valuation guards pass. Oracle’s filed lines are loaded from the separate SEC prework and its FY2025 revenue, operating income, net income, latest shares, and net debt reproduce. Oracle forecasting is intentionally pending the student’s labeled history/guidance/judgment assumptions in the Tuesday studio. WRDS is coded as a credential-gated secondary-source extraction and writes a dated attempt record on every run.

Before CP9 submission: write Edition A by hand with no AI, update this status only if the classroom work changes it, and retain the generated `outputs/wrds_compustat_attempt.csv` with the notebook.
""")

nb["cells"] = cells
output = ROOT / "Lab6_CP9_ABG_Oracle.ipynb"
nbf.write(nb, output)
print(output)
