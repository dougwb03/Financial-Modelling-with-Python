from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Lab6_CP9_ABG_Oracle.ipynb"
TARGET = ROOT / "Lab6_CP10_Oracle_Microsoft.ipynb"
nb = nbf.read(SOURCE, as_version=4)

def md(s):
    nb.cells.append(nbf.v4.new_markdown_cell(s.strip()))

def code(s):
    nb.cells.append(nbf.v4.new_code_cell(s.strip()))

md(r'''
# Lab 6 — CP10: Microsoft Swap, Two-Company Exhibit, and Decision

This Thursday extension begins from the completed CP9 model above. It retains Oracle as Company A and runs the unchanged `project_company`, `checks`, and `valuation` method on Microsoft as Company B. Units are USD millions except per-share values, shares, and percentages.

**Required live action:** run the existing WRDS annual-fundamentals cell above and the WRDS market-price cell below with your own login. The notebook deliberately does not use Yahoo Finance or any consumer feed. If access is pending, it writes a dated attempt and leaves the price comparison visibly pending rather than inventing a price.

**AI disclosure:** I used an AI coding partner to extend my CP9 notebook into a rerunnable CP10 workflow. I must independently verify sources, company mappings, inputs, price dates, outputs, flip point, decision, triggers, and peer note before submitting. The handwritten Edition A was completed separately in class without AI.
''')

md(r'''
## Step 4 — Company B: Microsoft company half

Microsoft’s FY2025 is the known-answer year. The company half below uses only the Microsoft filed annual lines already loaded from the separate prework notebook: its 2025 10-K was filed 2025-07-30 (accession `0000950170-25-100235`). Unlike ABG, Microsoft has no floor-plan financing; unlike Oracle, it reports gross profit directly. Cash operating cost below gross profit is derived as `operating expenses − D&A`, so D&A is deducted exactly once in the method half.
''')

code(r'''
def company_history(a):
    h = pd.DataFrame(index=a.index)
    h["revenue growth"] = a.revenue.pct_change()
    h["gross margin"] = 1 - a.cost_of_revenue / a.revenue
    # The method starts at gross profit, so direct cost is already reflected there.
    h["cash operating costs / revenue"] = (a.operating_expenses - a.depreciation_and_amortization) / a.revenue
    h["D&A / revenue"] = a.depreciation_and_amortization / a.revenue
    h["tax / pretax"] = a.income_tax / a.pretax_income
    h["capex / revenue"] = a.capital_expenditure / a.revenue
    h["inventory / revenue"] = a.inventory / a.revenue
    return h

mh = company_history(microsoft)
display(mh.map(lambda x: "—" if pd.isna(x) else f"{x:.1%}"))

# FY2025 operating NWC, USD m: current assets less cash, minus current liabilities less current debt.
# Hand-entered filing reads are documented in prework: cash $30,242m and total debt $41,787m.
# Current assets $191,131m, current liabilities $141,218m and current debt $1,635m are SEC Company Facts
# values for the same Microsoft FY2025 10-K, cached in CIK0000789019_companyfacts.json.
msft_current_assets, msft_current_liabilities, msft_current_debt = 191131., 141218., 1635.
msft_cash, msft_total_debt = 30242., 41787.
msft_nwc = (msft_current_assets - msft_cash) - (msft_current_liabilities - msft_current_debt)

def hist_mean(frame, column):
    return float(frame.loc[2024:2025, column].mean())

mz = microsoft.loc[2025]
# Same CAPM components as Oracle, with beta as the only company-specific component in this FCFE setup.
# Replace the provisional betas with the documented professional-source values returned below before submission.
CAPM = {"risk_free_rate": .0425, "equity_risk_premium": .0500}
PROVISIONAL_BETAS = {"Oracle": .95, "Microsoft": .85}
MSFT = {
    "name": "Microsoft", "ticker": "MSFT", "opening_year": 2025,
    "opening": {"revenue": mz.revenue, "inventory": mz.inventory, "ppe": mz.ppe_net,
                "cash": msft_cash, "debt": msft_total_debt, "equity": mz.shareholders_equity,
                "assets": mz.total_assets, "liabilities": mz.total_liabilities},
    "drivers": {
        "growth": [hist_mean(mh, "revenue growth")] * 5,
        "gm": [hist_mean(mh, "gross margin")] * 5,
        "cash_cost": [hist_mean(mh, "cash operating costs / revenue")] * 5,
        "da": [hist_mean(mh, "D&A / revenue")] * 5,
        "tax": [hist_mean(mh, "tax / pretax")] * 5,
        "capex": [hist_mean(mh, "capex / revenue")] * 5,
        "inventory": [hist_mean(mh, "inventory / revenue")] * 5,
        "nwc": [msft_nwc / mz.revenue] * 5,
        "interest_rate": (mz.operating_income - mz.pretax_income) / msft_total_debt,
        "noncash": 0., "paydown": 0., "buyback": 0., "cash_floor": 10000., "revolver_cap": 25000.
    },
    "valuation": {"r": CAPM["risk_free_rate"] + PROVISIONAL_BETAS["Microsoft"] * CAPM["equity_risk_premium"],
                  "g": .025, "shares": 7425.545491, "shares_are_millions": True}
}

msft_labels = {
    "growth": "history: FY2024–25 mean", "gm": "history: FY2024–25 mean",
    "cash_cost": "history: FY2024–25 mean; D&A separated", "da": "history: FY2024–25 mean",
    "tax": "history: FY2024–25 mean", "capex": "history: FY2024–25 mean",
    "inventory": "history: FY2024–25 mean", "nwc": "fact: FY2025 operating NWC / revenue",
    "interest_rate": "history proxy: FY2025 EBIT-to-pretax bridge / opening debt",
    "paydown": "judgment: zero pending debt guidance", "buyback": "judgment: zero pending repurchase guidance",
    "cash_floor": "judgment: $10bn", "r": "CAPM: same Rf and ERP as Oracle; provisional MSFT beta pending WRDS", "g": "judgment: same terminal convention as Oracle"
}
msft_ledger = pd.DataFrame(
    [(k, v, msft_labels.get(k, "judgment")) for k, v in MSFT["drivers"].items() if k not in ("noncash", "revolver_cap")] +
    [("risk-free rate", CAPM["risk_free_rate"], "common CAPM component"),
     ("equity risk premium", CAPM["equity_risk_premium"], "common CAPM component"),
     ("provisional beta", PROVISIONAL_BETAS["Microsoft"], "replace with professional-source beta"),
     ("cost of equity", MSFT["valuation"]["r"], msft_labels["r"]),
     ("terminal growth", MSFT["valuation"]["g"], msft_labels["g"]),
     ("shares (millions)", MSFT["valuation"]["shares"], "fact: 2026 Form 10-K cover")],
    columns=["input", "value", "label / basis"])
display(msft_ledger)
print(f"FY2025 operating NWC: ${msft_nwc:,.0f}m ({msft_nwc / mz.revenue:.1%} of revenue)")
''')

md("""
### Microsoft FY2025 known-answer gate — run before forecasting

This uses the filed year itself, not a forecast. It must reproduce revenue, operating income, net income, latest filed cover shares, and net debt before the projected years can be trusted.
""")

code(r'''
def rebuild_microsoft_filed(a):
    gross_profit = a.revenue - a.cost_of_revenue
    cash_operating_costs = a.operating_expenses - a.depreciation_and_amortization
    operating_income = gross_profit - cash_operating_costs - a.depreciation_and_amortization
    interest_other = operating_income - a.pretax_income
    net_income = a.pretax_income - a.income_tax
    return pd.Series({"Revenue": a.revenue, "Operating income": operating_income, "Net income": net_income,
                      "Latest shares (millions)": 7425.545491, "Net debt": msft_total_debt - msft_cash,
                      "Interest / other income bridge": interest_other})

msft_filed = pd.Series({"Revenue": 281724., "Operating income": 128528., "Net income": 101832.,
                        "Latest shares (millions)": 7425.545491, "Net debt": 11545.,
                        "Interest / other income bridge": 4901.})
msft_gate = pd.DataFrame({"filed FY2025": msft_filed, "model FY2025": rebuild_microsoft_filed(microsoft.loc[2025])})
msft_gate["difference"] = msft_gate.iloc[:, 1] - msft_gate.iloc[:, 0]
msft_gate["pass"] = msft_gate.difference.abs() < .01
display(msft_gate)
assert msft_gate["pass"].all(), "Stop here: fix Microsoft’s filed-year mapping before projecting."
''')

md("""
### Microsoft projection — unchanged method half

The cell below is intentionally only a company swap. It calls the CP9 method unchanged: income statement; driver-led balance sheet; FCFE; cash last; then the independent check block and gated valuation.
""")

code(r'''
mp = project_company(MSFT)
mv = valuation(MSFT, mp)
display(mp[["revenue", "gross_profit", "cash_operating_costs", "depreciation_and_amortization", "ebit", "interest", "tax", "net_income", "inventory", "ppe", "debt", "equity", "fcfe", "cash", "revolver"]])
display(checks(mp))
assert checks(mp)["pass"].all(), "Microsoft check block failed; identify the first failing line."
display(pd.DataFrame({"value": [mv["equity_value"], mv["value_per_share"], mv["terminal_share"]],
                      "units": ["USD millions", "USD/share", "%"]},
                     index=["equity value", "value per share", "terminal share"]))
print(f"Microsoft valuation share denominator: {MSFT['valuation']['shares']:,.6f} million shares (2026 Form 10-K cover).")
''')

md(r'''
## Step 5 — Dated professional market prices, fairness check, and the one exhibit

This WRDS cell queries **Compustat Security Daily** (`comp.secd`) for dated closing prices, an approved professional source. It also attempts the current Compustat Security beta separately; beta failure cannot discard a successful price pull. It prompts for a WRDS username if `WRDS_USERNAME` is not configured; WRDS then handles its normal password prompt. It saves the retrieved price/date and a dated audit record under `outputs/`. `EDITION_A` is intentionally a two-item manual entry: enter exactly the two prices and dates you wrote by hand in Tuesday’s Edition A so the notebook can print the code pull beside that known answer. Do not substitute a Yahoo or yfinance value.
''')

code(r'''
# These are the values READ BY HAND in Edition A, not new model inputs. Fill them exactly as written.
EDITION_A = {"ORCL": {"price": None, "date": None, "source": "enter your Edition A professional source"},
             "MSFT": {"price": None, "date": None, "source": "enter your Edition A professional source"}}
PRICE_AS_OF = date.today().isoformat()  # latest available Compustat Security Daily close on or before this date

def pull_wrds_prices(as_of=PRICE_AS_OF):
    status = {"run_date": date.today().isoformat(), "source": "WRDS / Compustat Security Daily (comp.secd)", "status": None, "detail": None}
    username = os.getenv("WRDS_USERNAME")
    if not username:
        try:
            username = input("WRDS username (Enter to record pending): ").strip()
        except Exception:
            username = ""
    if not username:
        status.update(status="pending", detail="No WRDS username supplied; rerun interactively for Compustat market prices.")
        prices, beta_data = pd.DataFrame(columns=["ticker", "date", "close_price"]), pd.DataFrame()
    else:
        try:
            import wrds
            conn = wrds.Connection(wrds_username=username)
            price_sql = f"""
                with ranked as (
                    select s.tic as ticker, d.datadate as date, d.prccd as close_price,
                           row_number() over (partition by s.tic order by d.datadate desc) as rn
                    from comp.secd d join comp.security s on d.gvkey=s.gvkey and d.iid=s.iid
                    where s.tic in ('ORCL','MSFT') and d.datadate <= '{as_of}'::date
                      and d.prccd is not null and d.prccd > 0
                ) select ticker, date, close_price from ranked where rn=1 order by ticker
            """
            prices = conn.raw_sql(price_sql, date_cols=["date"])
            if set(prices.ticker) != {"ORCL", "MSFT"}:
                raise ValueError("Compustat Security Daily did not return one latest price for both ORCL and MSFT.")
            try:
                beta_data = conn.raw_sql("select tic as ticker, beta from comp.security where tic in ('ORCL','MSFT') and beta is not null")
                beta_data = beta_data.drop_duplicates("ticker", keep="last")
                prices = prices.merge(beta_data, on="ticker", how="left")
            except Exception as beta_exc:
                beta_data = pd.DataFrame()
                status["beta_note"] = f"Compustat beta query did not run: {type(beta_exc).__name__}: {beta_exc}"
            conn.close()
            status.update(status="retrieved", detail=f"Retrieved {len(prices)} Compustat dated closes through {as_of}.")
        except Exception as exc:
            prices, beta_data = pd.DataFrame(columns=["ticker", "date", "close_price"]), pd.DataFrame()
            status.update(status="failed", detail=f"{type(exc).__name__}: {exc}")
    (LAB / "outputs").mkdir(exist_ok=True)
    pd.DataFrame([status]).to_csv(LAB / "outputs" / "wrds_compustat_price_attempt.csv", index=False)
    if not prices.empty:
        prices.to_csv(LAB / "outputs" / "wrds_compustat_latest_prices.csv", index=False)
    return status, prices

price_status, crsp_prices = pull_wrds_prices()
display(pd.DataFrame([price_status]))
if crsp_prices.empty:
    print("Price comparison is PENDING. Run this cell with WRDS access before submitting CP10.")
else:
    edition_rows = pd.DataFrame([{"ticker": t, "Edition A price": d["price"], "Edition A date": d["date"], "Edition A source": d["source"]}
                                for t, d in EDITION_A.items()])
    display(crsp_prices.merge(edition_rows, on="ticker", how="left"))
''')

code(r'''
# Same five-year horizon and terminal convention for both. Only beta / resulting cost of equity differs.
# When the optional Compustat beta field is returned, it replaces the provisional beta for both companies.
if not crsp_prices.empty and "beta" in crsp_prices and crsp_prices.beta.notna().all():
    PROVISIONAL_BETAS["Oracle"] = float(crsp_prices.set_index("ticker").loc["ORCL", "beta"])
    PROVISIONAL_BETAS["Microsoft"] = float(crsp_prices.set_index("ticker").loc["MSFT", "beta"])
ORACLE["valuation"]["r"] = CAPM["risk_free_rate"] + PROVISIONAL_BETAS["Oracle"] * CAPM["equity_risk_premium"]
MSFT["valuation"]["r"] = CAPM["risk_free_rate"] + PROVISIONAL_BETAS["Microsoft"] * CAPM["equity_risk_premium"]
op, ov = project_company(ORACLE), valuation(ORACLE, project_company(ORACLE))
mp, mv = project_company(MSFT), valuation(MSFT, project_company(MSFT))
assert ORACLE["valuation"]["g"] == MSFT["valuation"]["g"] and len(op) == len(mp) == 5
fairness = pd.DataFrame({
    "Oracle": [len(op), ORACLE["valuation"]["g"], CAPM["risk_free_rate"], CAPM["equity_risk_premium"], PROVISIONAL_BETAS["Oracle"], ORACLE["valuation"]["r"]],
    "Microsoft": [len(mp), MSFT["valuation"]["g"], CAPM["risk_free_rate"], CAPM["equity_risk_premium"], PROVISIONAL_BETAS["Microsoft"], MSFT["valuation"]["r"]],
}, index=["forecast horizon (years)", "terminal growth", "risk-free rate", "equity risk premium", "beta (replace with WRDS value)", "cost of equity"])
display(fairness)
''')

code(r'''
from IPython.display import SVG, display
from html import escape

def scenario_company(company, margin_shift=0., growth_shift=0.):
    x = deepcopy(company)
    x["drivers"]["gm"] = [v + margin_shift for v in x["drivers"]["gm"]]
    x["drivers"]["growth"] = [v + growth_shift for v in x["drivers"]["growth"]]
    return x

def scenario_values(company):
    # An explicit, rerunnable range: downside / base / upside. Same conventions are used for both firms.
    specs = {"Downside": {"margin_shift": -.02, "growth_shift": -.03},
             "Base": {"margin_shift": 0., "growth_shift": 0.},
             "Upside": {"margin_shift": .02, "growth_shift": .03}}
    out = []
    for case, changes in specs.items():
        c = scenario_company(company, **changes); p = project_company(c); v = valuation(c, p)
        out.append({"case": case, "value_per_share": v["value_per_share"], **changes})
    return pd.DataFrame(out).set_index("case")

orcl_range, msft_range = scenario_values(ORACLE), scenario_values(MSFT)
range_table = pd.DataFrame({"Oracle": orcl_range.value_per_share, "Microsoft": msft_range.value_per_share})
display(range_table.style.format("${:,.2f}"))

if crsp_prices.empty:
    print("Exhibit values were produced, but the dated-price lines and percentage gaps await the WRDS Compustat pull.")
else:
    price_map = crsp_prices.set_index("ticker").close_price.to_dict()
    comparison = pd.DataFrame({
        "company": ["Oracle", "Microsoft"], "ticker": ["ORCL", "MSFT"],
        "market_price": [price_map["ORCL"], price_map["MSFT"]],
        "price_date": [crsp_prices.set_index("ticker").loc["ORCL", "date"], crsp_prices.set_index("ticker").loc["MSFT", "date"]],
        "low": [orcl_range.loc["Downside", "value_per_share"], msft_range.loc["Downside", "value_per_share"]],
        "base": [orcl_range.loc["Base", "value_per_share"], msft_range.loc["Base", "value_per_share"]],
        "high": [orcl_range.loc["Upside", "value_per_share"], msft_range.loc["Upside", "value_per_share"]],
    })
    for c in ["low", "base", "high"]:
        comparison[f"{c}_gap_pct"] = comparison[c] / comparison.market_price - 1
    display(comparison.style.format({"market_price": "${:,.2f}", "low": "${:,.2f}", "base": "${:,.2f}", "high": "${:,.2f}",
                                     "low_gap_pct": "{:.1%}", "base_gap_pct": "{:.1%}", "high_gap_pct": "{:.1%}"}))
    # Standard-library SVG keeps the exhibit rerunnable even where matplotlib is not installed.
    width, height, left, right = 980, 330, 180, 940
    lo = min(comparison[["low", "market_price"]].min()) * .92
    hi = max(comparison[["high", "market_price"]].max()) * 1.08
    x = lambda value: left + (value - lo) / (hi - lo) * (right - left)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="white"/>',
           '<text x="20" y="28" font-family="Arial" font-size="18" font-weight="bold">CP10 — DCF range against dated Compustat market price</text>']
    for tick in range(6):
        value, xx = lo + (hi - lo) * tick / 5, left + (right - left) * tick / 5
        svg += [f'<line x1="{xx:.1f}" y1="55" x2="{xx:.1f}" y2="275" stroke="#dddddd"/>',
                f'<text x="{xx:.1f}" y="302" text-anchor="middle" font-family="Arial" font-size="12">${value:,.0f}</text>']
    for pos, row in comparison.reset_index(drop=True).iterrows():
        y, color = 115 + pos * 105, ("#2c7fb8" if pos == 0 else "#d95f0e")
        svg += [f'<text x="20" y="{y+5}" font-family="Arial" font-size="16">{escape(row.company)} ({row.ticker})</text>',
                f'<line x1="{x(row.low):.1f}" y1="{y}" x2="{x(row.high):.1f}" y2="{y}" stroke="{color}" stroke-width="14" stroke-linecap="round"/>',
                f'<circle cx="{x(row.base):.1f}" cy="{y}" r="7" fill="white" stroke="black" stroke-width="2"/>',
                f'<line x1="{x(row.market_price):.1f}" y1="{y-33}" x2="{x(row.market_price):.1f}" y2="{y+33}" stroke="#222" stroke-width="2" stroke-dasharray="6,4"/>',
                f'<text x="{x(row.market_price):.1f}" y="{y+53}" text-anchor="middle" font-family="Arial" font-size="12">Market ${row.market_price:,.2f} · {pd.Timestamp(row.price_date):%Y-%m-%d}</text>']
    svg += ['<text x="20" y="322" font-family="Arial" font-size="11">Thick bar: downside-to-upside DCF range · circle: base value · dashed line: dated Compustat price</text>', '</svg>']
    exhibit_path = LAB / "outputs" / "CP10_two_company_range_exhibit.svg"
    exhibit_path.write_text("\n".join(svg), encoding="utf-8")
    display(SVG(filename=str(exhibit_path))); print(f"Saved exhibit: {exhibit_path}")
''')

md(r'''
## Step 6 — Decision, rerun flip point, and triggers

The next cell calculates a flip point by repeatedly rerunning the model, not by reading a sensitivity-table intersection. It varies only Oracle’s gross-margin driver while holding all other assumptions fixed, and identifies where the two **base-value gaps to their own dated prices** meet. This is the decision metric, so dollar values are never ranked directly. It runs only after CRSP returns both prices.
''')

code(r'''
def value_gap(company, price):
    p = project_company(company)
    return valuation(company, p)["value_per_share"] / price - 1

if crsp_prices.empty:
    print("Flip point and decision are PENDING dated WRDS prices.")
else:
    price_map = crsp_prices.set_index("ticker").close_price.to_dict()
    base_orcl_gap, base_msft_gap = value_gap(ORACLE, price_map["ORCL"]), value_gap(MSFT, price_map["MSFT"])
    def ranking_difference(orcl_gm):
        c = deepcopy(ORACLE); c["drivers"]["gm"] = [orcl_gm] * 5
        return value_gap(c, price_map["ORCL"]) - base_msft_gap
    import numpy as np
    grid = np.linspace(.40, .95, 111)
    pairs = list(zip(grid[:-1], grid[1:]))
    bracket = next(((a, b) for a, b in pairs if ranking_difference(a) * ranking_difference(b) <= 0), None)
    if bracket is None:
        print("No Oracle gross-margin flip was bracketed between 40% and 95%; choose another single model assumption and rerun.")
    else:
        lo, hi = bracket
        for _ in range(60):
            mid = (lo + hi) / 2
            if ranking_difference(lo) * ranking_difference(mid) <= 0: hi = mid
            else: lo = mid
        flip_gm = (lo + hi) / 2
        oracle_history_min, oracle_history_max = oh["gross margin"].min(), oh["gross margin"].max()
        recommended = "Oracle" if base_orcl_gap > base_msft_gap else "Microsoft"
        other = "Microsoft" if recommended == "Oracle" else "Oracle"
        print(f"Recommendation (model output): allocate capital to {recommended}, conditional on the common-horizon CAPM/FCFE assumptions and dated Compustat closes.")
        print(f"Base gaps: Oracle {base_orcl_gap:.1%}; Microsoft {base_msft_gap:.1%}.")
        print(f"Flip point: Oracle gross margin = {flip_gm:.2%}; at that rerun the two percentage gaps meet and {other} ranks higher below it.")
        print(f"Oracle FY2023–25 gross-margin history: {oracle_history_min:.2%} to {oracle_history_max:.2%}; flip point is {'inside' if oracle_history_min <= flip_gm <= oracle_history_max else 'outside'} this history.")
''')

md(r'''
### Decision lines to submit — complete after running the cells above

Copy the *computed* recommendation and flip-point output here after checking it. Then make the trigger thresholds specific to your submitted result; neither a peer note nor a decision is fabricated by the notebook.

1. **Recommendation:** `We recommend [model winner] over [other]. This holds while [the selected driver] remains [above/below the computed flip point] under the common five-year FCFE / terminal-growth convention.`
2. **Flip point:** `The ranking turns on [single driver]. At [computed value] the rerun cases meet; [other] ranks higher on the other side. This value is [inside/outside] the company’s FY2023–25 history of [range].`
3. **Triggers:** `Oracle — Observable: filed gross margin (revenue less filed cost of revenue); threshold: below [your checked threshold, direction included]; review date: next Oracle 10-Q filing [enter date from SEC filing calendar]. Microsoft — Observable: filed gross margin; threshold: below [your checked threshold, direction included]; review date: next Microsoft 10-Q filing [enter date from SEC filing calendar].`

The two bracketed review dates are deliberately not guessed: confirm them from the SEC filing calendar / issuer reporting calendar before you hand in the three lines.
''')

md(r'''
## Step 7 — Peer read and CP10 submission record

Attach or paste the actual note **received** from a peer. It must name three defects (missing, unsupported, or the committee’s first question), not compliments or proposed fixes. This notebook cannot generate that note.

**CP10 submission contents:** the saved two-company exhibit (`outputs/CP10_two_company_range_exhibit.svg`) after its Compustat price lines appear; the three finalized decision lines; the actual peer note received; and the AI disclosure above. If a required check or price pull remains unavailable, submit the working state plus one honest line naming the failure and why.
''')

nbf.write(nb, TARGET)
print(TARGET)
