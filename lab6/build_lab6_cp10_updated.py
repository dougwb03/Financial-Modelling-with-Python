from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Lab6_CP10_Oracle_Microsoft.ipynb"
TARGET = ROOT / "Lab6_CP10_Oracle_Microsoft_updated.ipynb"
nb = nbf.read(SOURCE, as_version=4)

def replace_cell(needle, source):
    for cell in nb.cells:
        if needle in cell.source:
            cell.source = source.strip()
            cell.outputs = []
            cell.execution_count = None
            return
    raise RuntimeError(f"Could not locate notebook cell containing: {needle}")

def insert_before(needle, cell):
    for n, old in enumerate(nb.cells):
        if needle in old.source:
            nb.cells.insert(n, cell)
            return
    raise RuntimeError(f"Could not locate insertion point: {needle}")

insert_before("## Step 4 — Company B", nbf.v4.new_markdown_cell("""
## Read this before editing or running

**You must make these inputs yourself.** Cells explicitly headed **MANUAL INPUT** are intentionally not completed by the notebook:

1. In the `MANUAL_MSFT_DRIVER_OVERRIDES` cell, decide whether the FY2025–26 historical averages are your forecast view. Leave a value as `None` to retain the history-based default, or replace it with your own five-year list. Your changes are judgments and must be defensible.
2. In the `EDITION_A` cell, type the exact Oracle and Microsoft price, date, and professional source you wrote by hand on Tuesday. Do not enter a consumer-source price.
3. After the WRDS price pull, read the computed result and write your own final recommendation, trigger thresholds, review dates, and real peer note. The notebook makes no claim that those opinions are automatic.

The newest Microsoft filed year is **FY2026 ended 2026-06-30**, filed on 2026-07-29. This updated notebook uses it as the opening/known-answer year. Oracle remains on the CP9 company-A basis; the different fiscal year ends are disclosed in the fairness check.
""".strip()))

replace_cell("def company_history", r'''
# FY2026 Microsoft filed values are read from the cached 2026 Form 10-K Company Facts record.
# Source: Microsoft FY2026 Form 10-K filed 2026-07-29, accession 0001193125-26-323660.
msft_facts = json.load(open(LAB / "cache" / "CIK0000789019_companyfacts.json"))["facts"]["us-gaap"]
def fy2026_usd(tag, duration=False):
    rows = msft_facts[tag]["units"]["USD"]
    matches = [x for x in rows if x.get("end") == "2026-06-30" and x.get("form") == "10-K"
               and (not duration or x.get("start") == "2025-07-01")]
    if not matches:
        raise KeyError(f"No FY2026 10-K fact found for {tag}")
    return matches[-1]["val"] / 1e6

msft_2026_revenue = fy2026_usd("RevenueFromContractWithCustomerExcludingAssessedTax", duration=True)
msft_2026_gp = fy2026_usd("GrossProfit", duration=True)
msft_2026_depreciation = fy2026_usd("Depreciation", duration=True)
msft_2026_amortization = fy2026_usd("AmortizationOfIntangibleAssets", duration=True)
microsoft.loc[2026] = {
    "start": "2025-07-01", "end": "2026-06-30", "days": 365,
    "accession": "0001193125-26-323660", "filed": "2026-07-29",
    "revenue": msft_2026_revenue, "cost_of_revenue": msft_2026_revenue - msft_2026_gp,
    "gross_profit": msft_2026_gp, "operating_expenses": fy2026_usd("OperatingExpenses", duration=True),
    "operating_income": fy2026_usd("OperatingIncomeLoss", duration=True),
    "pretax_income": fy2026_usd("IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest", duration=True),
    "income_tax": fy2026_usd("IncomeTaxExpenseBenefit", duration=True), "net_income": fy2026_usd("NetIncomeLoss", duration=True),
    "depreciation_and_amortization": msft_2026_depreciation + msft_2026_amortization,
    "operating_cash_flow": fy2026_usd("NetCashProvidedByUsedInOperatingActivities", duration=True),
    "capital_expenditure": fy2026_usd("PaymentsToAcquirePropertyPlantAndEquipment", duration=True),
    "inventory": fy2026_usd("InventoryNet"), "ppe_net": fy2026_usd("PropertyPlantAndEquipmentNet"),
    "total_assets": fy2026_usd("Assets"), "total_liabilities": fy2026_usd("Liabilities"),
    "shareholders_equity": fy2026_usd("StockholdersEquity"),
}
microsoft = microsoft.sort_index()

def company_history(a):
    h = pd.DataFrame(index=a.index)
    h["revenue growth"] = a.revenue.pct_change()
    h["gross margin"] = 1 - a.cost_of_revenue / a.revenue
    h["cash operating costs / revenue"] = (a.operating_expenses - a.depreciation_and_amortization) / a.revenue
    h["D&A / revenue"] = a.depreciation_and_amortization / a.revenue
    h["tax / pretax"] = a.income_tax / a.pretax_income
    h["capex / revenue"] = a.capital_expenditure / a.revenue
    h["inventory / revenue"] = a.inventory / a.revenue
    return h

mh = company_history(microsoft)
display(microsoft.loc[2024:2026])
display(mh.map(lambda x: "—" if pd.isna(x) else f"{x:.1%}"))

# FY2026 operating NWC from the same filed Company Facts data (USD m):
# current assets less cash, less current liabilities excluding current debt.
msft_current_assets = fy2026_usd("AssetsCurrent")
msft_current_liabilities = fy2026_usd("LiabilitiesCurrent")
msft_current_debt = fy2026_usd("LongTermDebtCurrent")
msft_cash = fy2026_usd("CashAndCashEquivalentsAtCarryingValue")
msft_total_debt = msft_current_debt + fy2026_usd("LongTermDebt")
msft_nwc = (msft_current_assets - msft_cash) - (msft_current_liabilities - msft_current_debt)

def hist_mean(frame, column):
    return float(frame.loc[2025:2026, column].mean())

mz = microsoft.loc[2026]
CAPM = {"risk_free_rate": .0425, "equity_risk_premium": .0500}
PROVISIONAL_BETAS = {"Oracle": .95, "Microsoft": .85}
MSFT = {
    "name": "Microsoft", "ticker": "MSFT", "opening_year": 2026,
    "opening": {"revenue": mz.revenue, "inventory": mz.inventory, "ppe": mz.ppe_net,
                "cash": msft_cash, "debt": msft_total_debt, "equity": mz.shareholders_equity,
                "assets": mz.total_assets, "liabilities": mz.total_liabilities},
    "drivers": {
        "growth": [hist_mean(mh, "revenue growth")] * 5, "gm": [hist_mean(mh, "gross margin")] * 5,
        "cash_cost": [hist_mean(mh, "cash operating costs / revenue")] * 5, "da": [hist_mean(mh, "D&A / revenue")] * 5,
        "tax": [hist_mean(mh, "tax / pretax")] * 5, "capex": [hist_mean(mh, "capex / revenue")] * 5,
        "inventory": [hist_mean(mh, "inventory / revenue")] * 5, "nwc": [msft_nwc / mz.revenue] * 5,
        "interest_rate": (mz.operating_income - mz.pretax_income) / msft_total_debt,
        "noncash": 0., "paydown": 0., "buyback": 0., "cash_floor": 10000., "revolver_cap": 25000.
    },
    "valuation": {"r": CAPM["risk_free_rate"] + PROVISIONAL_BETAS["Microsoft"] * CAPM["equity_risk_premium"],
                  "g": .025, "shares": 7425.545491, "shares_are_millions": True}
}

msft_labels = {"growth": "history: FY2025–26 mean", "gm": "history: FY2025–26 mean",
    "cash_cost": "history: FY2025–26 mean; D&A separated", "da": "history: FY2025–26 mean",
    "tax": "history: FY2025–26 mean", "capex": "history: FY2025–26 mean",
    "inventory": "history: FY2025–26 mean", "nwc": "fact: FY2026 operating NWC / revenue",
    "interest_rate": "history proxy: FY2026 EBIT-to-pretax bridge / opening debt",
    "paydown": "MANUAL JUDGMENT: zero pending debt guidance", "buyback": "MANUAL JUDGMENT: zero pending repurchase guidance",
    "cash_floor": "MANUAL JUDGMENT: $10bn", "r": "CAPM: common Rf/ERP; provisional MSFT beta pending WRDS", "g": "MANUAL JUDGMENT: common terminal convention"}
msft_ledger = pd.DataFrame([(k, v, msft_labels.get(k, "judgment")) for k, v in MSFT["drivers"].items() if k not in ("noncash", "revolver_cap")] +
    [("risk-free rate", CAPM["risk_free_rate"], "common CAPM component"), ("equity risk premium", CAPM["equity_risk_premium"], "common CAPM component"),
     ("provisional beta", PROVISIONAL_BETAS["Microsoft"], "MANUAL / replace with professional source"),
     ("cost of equity", MSFT["valuation"]["r"], msft_labels["r"]), ("terminal growth", MSFT["valuation"]["g"], msft_labels["g"]),
     ("shares (millions)", MSFT["valuation"]["shares"], "fact: FY2026 10-K cover")], columns=["input", "value", "label / basis"])
display(msft_ledger)
print(f"FY2026 operating NWC: ${msft_nwc:,.0f}m ({msft_nwc / mz.revenue:.1%} of revenue); total debt: ${msft_total_debt:,.0f}m.")
''')

insert_before("### Microsoft FY2025 known-answer", nbf.v4.new_markdown_cell("""
### MANUAL INPUT — Microsoft forecast judgments

The default forecast uses FY2025–26 historical averages. That is a starting point, not a forecast opinion. Replace any `None` below with a five-value list for FY2027–31 if your evidence or judgment differs. Do not change a value without updating the basis label in the ledger and being able to defend it.
""".strip()))
insert_before("### Microsoft FY2025 known-answer", nbf.v4.new_code_cell(r'''
# MANUAL INPUT: edit only the values on the right. None retains the history-based default.
MANUAL_MSFT_DRIVER_OVERRIDES = {
    "growth": None, "gm": None, "cash_cost": None, "da": None, "tax": None,
    "capex": None, "inventory": None, "nwc": None,
    "paydown": None, "buyback": None, "cash_floor": None, "terminal_growth": None,
}
for driver in ("growth", "gm", "cash_cost", "da", "tax", "capex", "inventory", "nwc"):
    if MANUAL_MSFT_DRIVER_OVERRIDES[driver] is not None:
        values = MANUAL_MSFT_DRIVER_OVERRIDES[driver]
        assert len(values) == 5, f"{driver} must contain five FY2027–31 values."
        MSFT["drivers"][driver] = values
        msft_labels[driver] = "MANUAL JUDGMENT: student-entered FY2027–31 values"
for driver in ("paydown", "buyback", "cash_floor"):
    if MANUAL_MSFT_DRIVER_OVERRIDES[driver] is not None:
        MSFT["drivers"][driver] = float(MANUAL_MSFT_DRIVER_OVERRIDES[driver])
        msft_labels[driver] = "MANUAL JUDGMENT: student-entered value"
if MANUAL_MSFT_DRIVER_OVERRIDES["terminal_growth"] is not None:
    MSFT["valuation"]["g"] = float(MANUAL_MSFT_DRIVER_OVERRIDES["terminal_growth"])
print("Manual override status:", {k: ("history default" if v is None else "STUDENT EDITED") for k, v in MANUAL_MSFT_DRIVER_OVERRIDES.items()})
'''.strip()))

replace_cell("def rebuild_microsoft_filed", r'''
def rebuild_microsoft_filed(a):
    gross_profit = a.revenue - a.cost_of_revenue
    cash_operating_costs = a.operating_expenses - a.depreciation_and_amortization
    operating_income = gross_profit - cash_operating_costs - a.depreciation_and_amortization
    interest_other = operating_income - a.pretax_income
    net_income = a.pretax_income - a.income_tax
    return pd.Series({"Revenue": a.revenue, "Operating income": operating_income, "Net income": net_income,
                      "Latest shares (millions)": 7425.545491, "Net debt": msft_total_debt - msft_cash,
                      "Interest / other income bridge": interest_other})

msft_filed = pd.Series({"Revenue": 331839., "Operating income": 155237., "Net income": 133749.,
                        "Latest shares (millions)": 7425.545491, "Net debt": 28586.,
                        "Interest / other income bridge": -10697.})
msft_gate = pd.DataFrame({"filed FY2026": msft_filed, "model FY2026": rebuild_microsoft_filed(microsoft.loc[2026])})
msft_gate["difference"] = msft_gate.iloc[:, 1] - msft_gate.iloc[:, 0]
msft_gate["pass"] = msft_gate.difference.abs() < .01
display(msft_gate)
assert msft_gate["pass"].all(), "Stop here: fix Microsoft’s FY2026 filed-year mapping before projecting."
''')

for cell in nb.cells:
    cell.source = cell.source.replace("Microsoft FY2025 known-answer gate", "Microsoft FY2026 known-answer gate")
    cell.source = cell.source.replace("Microsoft’s FY2025", "Microsoft’s FY2026")
    cell.source = cell.source.replace("Microsoft FY2025", "Microsoft FY2026")

insert_before("from IPython.display import SVG", nbf.v4.new_markdown_cell("""
### Microsoft full pro-forma — generated from the FY2026 company half

This is the same required order as CP9: income statement; driver-led balance sheet; FCFE; cash last; check block; valuation. It is generated from `mp`, never typed into a spreadsheet. Review every output after you make a manual override.
""".strip()))
insert_before("from IPython.display import SVG", nbf.v4.new_code_cell(r'''
def microsoft_full_proforma(projection, value, company):
    q, years = checks(projection), [str(y) for y in projection.index]
    rows = []
    def add(stage, line, series): rows.append([stage, line, *[float(v) for v in series]])
    add("1. Income statement", "Revenue", projection.revenue); add("1. Income statement", "Gross profit", projection.gross_profit)
    add("1. Income statement", "Cash operating costs", projection.cash_operating_costs); add("1. Income statement", "D&A", projection.depreciation_and_amortization)
    add("1. Income statement", "EBIT", projection.ebit); add("1. Income statement", "Interest / other income", projection.interest)
    add("1. Income statement", "Tax", projection.tax); add("1. Income statement", "Net income", projection.net_income)
    add("2. Balance sheet", "Inventory", projection.inventory); add("2. Balance sheet", "Floor-plan financing (not applicable)", pd.Series(0., index=projection.index))
    add("2. Balance sheet", "PP&E", projection.ppe); add("2. Balance sheet", "Debt after paydown", projection.debt); add("2. Balance sheet", "Equity after NI and buyback", projection.equity)
    add("3. FCFE", "FCFE before revolver", projection.fcfe_pre_financing); add("3. FCFE", "Revolver financing draw", projection.financing_draw); add("3. FCFE", "FCFE", projection.fcfe)
    add("4. Cash last", "Cash", projection.cash); add("4. Cash last", "Revolver balance", projection.revolver)
    add("5. Check block", "Balance residual", q.balance_residual); add("5. Check block", "Cash-tie residual", q.cash_tie_residual); add("5. Check block", "Cash minus floor", q.cash_minus_floor)
    table = pd.DataFrame(rows, columns=["Stage", "Line", *years])
    for year in years: table[year] = table[year].map(lambda x: f"{x:,.1f}")
    display(Markdown("### Microsoft FY2027–31 full pro-forma\n\n" + pipe_table(table)))
    valuation_table = pd.DataFrame([["Equity value (USD m)", f"{value['equity_value']:,.1f}"], ["Shares used", f"{company['valuation']['shares']:,.3f} million"], ["Value per share", f"${value['value_per_share']:,.2f}"], ["Terminal share", f"{value['terminal_share']:.1%}"], ["Valuation gate", "PASS — checks pass and g < r"]], columns=["6. Valuation", "Result"])
    display(Markdown(pipe_table(valuation_table)))

microsoft_full_proforma(mp, mv, MSFT)
'''.strip()))

nbf.write(nb, TARGET)
print(TARGET)
