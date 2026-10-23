from pathlib import Path
import nbformat as nbf

root = Path(__file__).resolve().parent
nb = nbf.v4.new_notebook()
nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}}
cells = []

def md(text):
    cells.append(nbf.v4.new_markdown_cell(text.strip()))

def code(text):
    cells.append(nbf.v4.new_code_cell(text.strip()))

md("""
# Lab 6 — Oracle and Microsoft: Tuesday Prework and Studio Workbook

**Student:** Douglas Buckeridge  
**Units:** USD millions, except shares and percentages  
**Prepared:** 2026-09-28  
**Companies:** Oracle (ORCL, CIK 0001341439) and Microsoft (MSFT, CIK 0000789019)

## What is complete before Tuesday

- SEC Company Facts JSON has been retrieved with an identifying User-Agent and cached in `lab6/cache/`.
- Three annual fiscal years have been assembled using the figure first reported in that year's own 10-K, with accession number, filing date, fiscal start/end, and day count.
- The requested filing-only items (capex, cash, debt, and latest cover share count) are recorded below with their statement/cover source.
- Both balance identities reconcile in each year.

## What must wait for the room

1. Rebuild ABG live in Step 1 and confirm the $291.75 known answer and checks.
2. In Step 2, build the **Oracle** company half into the method you typed in class; run the 2025 known-answer reproduction before projecting.
3. Write Edition A in the room with no AI open. This notebook intentionally contains no Edition A prose or prediction.

**AI disclosure (prework):** I used an AI coding partner to retrieve and organize SEC-source data, cache the source files, and scaffold this workbook. I must independently review every figure, source, vintage choice, formula, assumption, and output before I submit it. Edition A will be written in the room without AI.
""")

md("""
## Sources, vintage, and basis

All historical results are GAAP, fiscal-year results, in USD millions. The annual table uses each fiscal year as first reported in that year's own 10-K—not a later comparative restatement. The current 2025 10-K is also retained locally for statement review. The Company Facts feed does not reliably carry every presentation line; the Oracle direct-cost and operating-expense subtotals are derived from the named expense rows in its filed statement, and this is explicitly flagged.

See `source_log.md` for access routes and retrieval dates. The cached data are inputs to reproduce, not a substitute for the filing.
""")

code("""
from pathlib import Path
from datetime import date
import json
import pandas as pd

pd.options.display.float_format = lambda x: f"{x:,.1f}"
CACHE = Path("cache") if Path("cache").exists() else Path("lab6/cache")
assert (CACHE / "CIK0001341439_companyfacts.json").exists(), "Run from lab6/ or repository root."

with open(CACHE / "CIK0001341439_companyfacts.json") as f:
    oracle_facts = json.load(f)
with open(CACHE / "CIK0000789019_companyfacts.json") as f:
    microsoft_facts = json.load(f)
print(f"Loaded cached SEC Company Facts for {oracle_facts['entityName']} and {microsoft_facts['entityName']}.")
""")

md("""
## Filed annual lines — Oracle

`cost_of_revenue` is the sum of Oracle's filed direct expense rows: Cloud services and license support, Hardware, and Services. `operating_expenses_below_gross_profit` is total operating expenses less that direct-cost subtotal. Oracle's statement does not print a gross-profit subtotal; it is therefore calculated as revenue less the named direct costs. This is a disclosed presentation mapping, not a fabricated SEC tag.
""")

code("""
oracle = pd.DataFrame([
    {"fiscal_year": 2023, "start": "2022-06-01", "end": "2023-05-31", "days": 365,
     "accession": "0000950170-23-028914", "filed": "2023-06-20", "revenue": 49954, "cost_of_revenue": 13564,
     "gross_profit_derived": 36390, "operating_expenses_below_gross_profit": 23297, "operating_income": 13093,
     "pretax_income": 9126, "income_tax": 623, "net_income": 8503, "depreciation_and_amortization": 6108,
     "operating_cash_flow": 17165, "capital_expenditure": 8695, "inventory": 298, "ppe_net": 17069,
     "total_assets": 134384, "total_liabilities": 133311, "shareholders_equity": 1073},
    {"fiscal_year": 2024, "start": "2023-06-01", "end": "2024-05-31", "days": 366,
     "accession": "0000950170-24-075605", "filed": "2024-06-20", "revenue": 52961, "cost_of_revenue": 15143,
     "gross_profit_derived": 37818, "operating_expenses_below_gross_profit": 22465, "operating_income": 15353,
     "pretax_income": 11741, "income_tax": 1274, "net_income": 10467, "depreciation_and_amortization": 6139,
     "operating_cash_flow": 18673, "capital_expenditure": 6866, "inventory": 334, "ppe_net": 21536,
     "total_assets": 140976, "total_liabilities": 132272, "shareholders_equity": 8704},
    {"fiscal_year": 2025, "start": "2024-06-01", "end": "2025-05-31", "days": 365,
     "accession": "0000950170-25-087926", "filed": "2025-06-18", "revenue": 57399, "cost_of_revenue": 16927,
     "gross_profit_derived": 40472, "operating_expenses_below_gross_profit": 22794, "operating_income": 17678,
     "pretax_income": 14160, "income_tax": 1717, "net_income": 12443, "depreciation_and_amortization": 6174,
     "operating_cash_flow": 20821, "capital_expenditure": 21215, "inventory": 303, "ppe_net": 43522,
     "total_assets": 168361, "total_liabilities": 147910, "shareholders_equity": 20451},
]).set_index("fiscal_year")
display(oracle)
""")

md("""
## Filed annual lines — Microsoft

Microsoft reports gross margin and total operating expenses directly in its consolidated income statement. Its reported cash-flow line is used for depreciation and amortization as presented in the filing.
""")

code("""
microsoft = pd.DataFrame([
    {"fiscal_year": 2023, "start": "2022-07-01", "end": "2023-06-30", "days": 365,
     "accession": "0000950170-23-035122", "filed": "2023-07-27", "revenue": 211915, "cost_of_revenue": 65863,
     "gross_profit": 146052, "operating_expenses": 57529, "operating_income": 88523, "pretax_income": 89311,
     "income_tax": 16950, "net_income": 72361, "depreciation_and_amortization": 11000, "operating_cash_flow": 87582,
     "capital_expenditure": 28107, "inventory": 2500, "ppe_net": 95641, "total_assets": 411976,
     "total_liabilities": 205753, "shareholders_equity": 206223},
    {"fiscal_year": 2024, "start": "2023-07-01", "end": "2024-06-30", "days": 366,
     "accession": "0000950170-24-087843", "filed": "2024-07-30", "revenue": 245122, "cost_of_revenue": 74114,
     "gross_profit": 171008, "operating_expenses": 61575, "operating_income": 109433, "pretax_income": 107787,
     "income_tax": 19651, "net_income": 88136, "depreciation_and_amortization": 15200, "operating_cash_flow": 118548,
     "capital_expenditure": 44477, "inventory": 1246, "ppe_net": 135591, "total_assets": 512163,
     "total_liabilities": 243686, "shareholders_equity": 268477},
    {"fiscal_year": 2025, "start": "2024-07-01", "end": "2025-06-30", "days": 365,
     "accession": "0000950170-25-100235", "filed": "2025-07-30", "revenue": 281724, "cost_of_revenue": 87831,
     "gross_profit": 193893, "operating_expenses": 65365, "operating_income": 128528, "pretax_income": 123627,
     "income_tax": 21795, "net_income": 101832, "depreciation_and_amortization": 22000, "operating_cash_flow": 136162,
     "capital_expenditure": 64551, "inventory": 938, "ppe_net": 204966, "total_assets": 619003,
     "total_liabilities": 275524, "shareholders_equity": 343479},
]).set_index("fiscal_year")
display(microsoft)
""")

md("""
## Required checks: balance identity and period comparability

The fiscal year-end dates differ across the two companies, which is acceptable if each company is modeled on its own fiscal calendar. Within each company, the 2024 leap-year period is 366 days, not a 53-week year. The row is flagged rather than silently treating every year as 365 days.
""")

code("""
def prework_checks(name, data):
    check = pd.DataFrame(index=data.index)
    check["assets_minus_liabilities_minus_equity"] = data.total_assets - data.total_liabilities - data.shareholders_equity
    check["fiscal_days"] = data.days
    check["balance_pass"] = check["assets_minus_liabilities_minus_equity"].eq(0)
    check["period_note"] = check.fiscal_days.map(lambda d: "leap-year 366 days; not 53 weeks" if d == 366 else "365 days")
    print(name)
    display(check)
    assert check.balance_pass.all(), f"{name}: balance identity failed"

prework_checks("Oracle", oracle)
prework_checks("Microsoft", microsoft)
""")

md("""
## Filing-only inputs: recorded from the filing itself

These are deliberately not accepted from a generic data feed. Amounts are USD millions except share counts. The share count is the latest filed cover count available on 2026-09-28, not weighted-average diluted shares.
""")

code("""
filing_only = pd.DataFrame([
    {"company": "Oracle", "item": "Capital expenditure", "value": "21,215", "as_of_or_period": "FY ended 2025-05-31", "statement_or_cover": "2025 Form 10-K, Consolidated Statements of Cash Flows / MD&A cash-flow table", "accession": "0000950170-25-087926", "filed": "2025-06-18"},
    {"company": "Oracle", "item": "Cash and cash equivalents", "value": "10,786", "as_of_or_period": "2025-05-31", "statement_or_cover": "2025 Form 10-K, Consolidated Balance Sheets", "accession": "0000950170-25-087926", "filed": "2025-06-18"},
    {"company": "Oracle", "item": "Total debt (current + non-current)", "value": "92,568 = 7,271 + 85,297", "as_of_or_period": "2025-05-31", "statement_or_cover": "2025 Form 10-K, Consolidated Balance Sheets: Notes payable and other borrowings", "accession": "0000950170-25-087926", "filed": "2025-06-18"},
    {"company": "Oracle", "item": "Latest cover share count", "value": "3,023,736,000 shares", "as_of_or_period": "2026-09-07", "statement_or_cover": "2026 Q1 Form 10-Q cover", "accession": "0001193125-26-389274", "filed": "2026-09-11"},
    {"company": "Microsoft", "item": "Capital expenditure", "value": "64,551", "as_of_or_period": "FY ended 2025-06-30", "statement_or_cover": "2025 Form 10-K, Consolidated Statements of Cash Flows", "accession": "0000950170-25-100235", "filed": "2025-07-30"},
    {"company": "Microsoft", "item": "Cash and cash equivalents", "value": "30,242", "as_of_or_period": "2025-06-30", "statement_or_cover": "2025 Form 10-K, Consolidated Balance Sheets", "accession": "0000950170-25-100235", "filed": "2025-07-30"},
    {"company": "Microsoft", "item": "Total debt (current + non-current)", "value": "41,787 = 1,635 + 40,152", "as_of_or_period": "2025-06-30", "statement_or_cover": "2025 Form 10-K, Consolidated Balance Sheets", "accession": "0000950170-25-100235", "filed": "2025-07-30"},
    {"company": "Microsoft", "item": "Latest cover share count", "value": "7,425,545,491 shares", "as_of_or_period": "2026-07-23", "statement_or_cover": "2026 Form 10-K cover", "accession": "0001193125-26-323660", "filed": "2026-07-29"},
])
display(filing_only)
""")

md("""
## Tuesday Step 2 — Company A is Oracle

Do **not** copy ABG's nineteen inputs. Oracle's company-specific driver is cloud-infrastructure capacity and capex intensity, not dealership inventory/floor-plan financing. The compact workbench below calculates history; the forecast rows are intentionally blank for your own history/guidance/judgment decisions in class.
""")

code("""
oracle_drivers_history = pd.DataFrame(index=oracle.index)
oracle_drivers_history["revenue_growth"] = oracle.revenue.pct_change()
oracle_drivers_history["direct_cost_pct_revenue"] = oracle.cost_of_revenue / oracle.revenue
oracle_drivers_history["operating_margin"] = oracle.operating_income / oracle.revenue
oracle_drivers_history["cash_tax_rate"] = oracle.income_tax / oracle.pretax_income
oracle_drivers_history["capex_pct_revenue"] = oracle.capital_expenditure / oracle.revenue
oracle_drivers_history["d_and_a_pct_revenue"] = oracle.depreciation_and_amortization / oracle.revenue
display(oracle_drivers_history.style.format("{:.1%}"))

assumption_ledger = pd.DataFrame([
    ["Revenue growth", None, "history / guidance / judgment", "Enter after reviewing history and guidance", None],
    ["Direct-cost ratio or gross margin", None, "history / guidance / judgment", "Oracle direct costs mapped from filed expense rows", None],
    ["Operating expenses ratio", None, "history / guidance / judgment", "Do not retain ABG SG&A mechanic by default", None],
    ["Cash tax rate", None, "history / guidance / judgment", "Use a stated normalized choice", None],
    ["Capex / revenue", None, "history / guidance / judgment", "Company-specific cloud-infrastructure driver", None],
    ["D&A / PPE or revenue", None, "history / guidance / judgment", "State method", None],
    ["Working capital / revenue", None, "history / guidance / judgment", "State method", None],
    ["Cost of equity", None, "judgment", "Build from same components as Microsoft; beta/leverage may differ", None],
    ["Terminal growth", None, "judgment", "Must be below discount rate", None],
    ["Cash floor", None, "judgment", "Cash computed last; no plug", None],
    ["Latest shares outstanding", 3023.736, "fact", "2026 Q1 10-Q cover; millions of shares", "0001193125-26-389274"],
], columns=["input", "value", "label", "basis / note", "source"])
display(assumption_ledger)
""")

md("""
## Known-answer gate for Tuesday

Before forecasting Oracle, run your class-built pipeline on FY2025 and populate the first three model columns. The model cannot proceed to a valuation until this gate and the four check rows pass. This worksheet does not falsely mark a pipeline as reproduced before you build it live.
""")

code("""
known_answer_gate = pd.DataFrame({
    "filed_2025": [57399, 17678, 12443, 3023.736, 81782],
    "model_2025": [None, None, None, None, None],
    "difference": [None, None, None, None, None],
    "status": ["TO DO in Tuesday studio"] * 5,
}, index=["Revenue", "Operating income", "Net income", "Latest shares (millions)", "Net debt: 92,568 - 10,786"])
display(known_answer_gate)

check_block_template = pd.DataFrame({"result": [None, None, None, None], "pass?": [None, None, None, None]}, index=[
    "Assets - liabilities - equity", "Cash - (opening cash + net cash change)", "Cash - floor", "Terminal growth < discount rate"
])
display(check_block_template)
""")

md("""
## Tuesday submission packet — Checkpoint 9

Before leaving Tuesday, submit to Brightspace:

1. This notebook **after** you rebuilt ABG and swapped Oracle into the company half. It should show ABG's $291.75 check, Oracle's loaded lines, Oracle FY2025 known-answer comparison, and the check block.
2. One honest status line, e.g., `Stopped after [step]: [specific failed check or remaining task].` Never report a green check you did not test.
3. Your separate, timestamped, one-page Edition A written in class without AI: a paragraph on Oracle, a paragraph on Microsoft, then the three-line prediction.
4. Your AI disclosure (the prework disclosure above, updated for any additional help used).

**Do not submit Edition A generated by an agent.**
""")

nb["cells"] = cells
nbf.write(nb, root / "Lab6_Oracle_Microsoft_Prework.ipynb")
print(root / "Lab6_Oracle_Microsoft_Prework.ipynb")
