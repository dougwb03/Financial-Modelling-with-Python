from pathlib import Path
import nbformat as nbf

root = Path(__file__).resolve().parent
source = root / "Lab6_CP10_Oracle_Microsoft_updated.ipynb"
target = root / "Lab6_CP10_Oracle_Microsoft_final.ipynb"
nb = nbf.read(source, as_version=4)

# Make the source-neutral variable name clear without disturbing the original pipeline.
for cell in nb.cells:
    cell.source = cell.source.replace("crsp_prices", "market_prices")

# Preserve only feasible scenarios in the gross-margin flip scan.
for cell in nb.cells:
    if "def value_gap(company, price):" in cell.source:
        cell.source = r'''
import numpy as np
def value_gap(company, price):
    return valuation(company, project_company(company))["value_per_share"] / price - 1
if market_prices.empty:
    print("Flip point and decision are PENDING dated professional prices.")
else:
    price_map=market_prices.set_index("ticker").close_price.to_dict()
    base_orcl_gap=value_gap(ORACLE,price_map["ORCL"]); base_msft_gap=value_gap(MSFT,price_map["MSFT"])
    def ranking_difference(gm):
        trial=deepcopy(ORACLE); trial["drivers"]["gm"]=[gm]*5
        try: return value_gap(trial,price_map["ORCL"])-base_msft_gap
        except ValueError as exc:
            if "revolver cap exceeded" in str(exc): return np.nan
            raise
    grid=np.linspace(.40,.95,111)
    results=pd.DataFrame({"oracle_gross_margin":grid,"ranking_difference":[ranking_difference(x) for x in grid]})
    results["feasible"]=results.ranking_difference.notna(); display(results)
    feasible=results[results.feasible].reset_index(drop=True)
    bracket=next(((feasible.loc[i,"oracle_gross_margin"],feasible.loc[i+1,"oracle_gross_margin"]) for i in range(len(feasible)-1) if feasible.loc[i,"ranking_difference"]*feasible.loc[i+1,"ranking_difference"]<=0),None)
    if bracket is None: print("No feasible Oracle gross-margin flip was bracketed; document this or select another single assumption.")
    else:
        lo,hi=bracket; flo=ranking_difference(lo)
        for _ in range(60):
            mid=(lo+hi)/2; fmid=ranking_difference(mid)
            if np.isnan(fmid): lo=mid; continue
            if flo*fmid<=0: hi=mid
            else: lo=mid; flo=fmid
        flip_gm=(lo+hi)/2; winner="Oracle" if base_orcl_gap>base_msft_gap else "Microsoft"; other="Microsoft" if winner=="Oracle" else "Oracle"
        print(f"Recommendation (model output): {winner}; base gaps Oracle {base_orcl_gap:.1%}, Microsoft {base_msft_gap:.1%}.")
        print(f"Flip point: Oracle gross margin {flip_gm:.2%}; below it {other} ranks higher.")
        print(f"Oracle FY2023–25 gross-margin history: {oh['gross margin'].min():.2%} to {oh['gross margin'].max():.2%}; flip is {'inside' if oh['gross margin'].min()<=flip_gm<=oh['gross margin'].max() else 'outside'} history.")
'''.strip()
        cell.outputs=[];cell.execution_count=None
        break

nb.cells.append(nbf.v4.new_markdown_cell("""
# Final CP10 controls — run after the original notebook

## Required changes before submission

This section resolves the outstanding CP10 controls without overwriting the prior workbook.

1. **Oracle FY2026:** The company A pipeline above is still based on FY2025. Before a final CP10 submission, replace it with Oracle's FY2026 10-K data and rerun its known-answer gate. The cited FY2026 filing is accession `0001193125-26-277521`, filed 2026-06-22; it is now cached at `lab6/cache/oracle_2026_10k.htm`.
2. **Beta:** The price pull succeeded, but the Compustat `comp.security` beta field does not exist in this WRDS schema. The next cell calculates beta from professional-source Compustat Security Daily return data instead. Do not call the provisional beta sourced until this succeeds and you review it.
3. **Manual inputs:** Fill `EDITION_A` with your handwritten Tuesday values. Confirm the FY2026 Oracle inventory line directly from the 10-K, then rebuild the Oracle company half and re-run the exhibit/flip-point cells.
4. **Writing:** Your recommendation, trigger thresholds, review dates, and peer note remain your own work. Use the model outputs, but revise the decision-line Markdown in your own words.
""".strip()))

nb.cells.append(nbf.v4.new_code_cell(r'''
# Professional-source beta control. Run this after market_prices has been populated.
# MANUAL REVIEW: confirm the data window and estimates before using them in the discount rate.
if market_prices.empty:
    print("BETA PENDING: run the WRDS / Compustat price cell first.")
else:
    try:
        import wrds
        beta_user = os.getenv("WRDS_USERNAME")
        if not beta_user:
            beta_user = input("WRDS username for return-based beta pull: ").strip()
        conn = wrds.Connection(wrds_username=beta_user)
        beta_sql = f"""
            select s.tic as ticker, d.datadate, d.trfd, d.sprtrn
            from comp.secd d
            join comp.security s on d.gvkey=s.gvkey and d.iid=s.iid
            where s.tic in ('ORCL','MSFT')
              and d.datadate between ('{PRICE_AS_OF}'::date - interval '2 years') and '{PRICE_AS_OF}'::date
              and d.trfd is not null and d.sprtrn is not null
            order by s.tic, d.datadate
        """
        beta_daily = conn.raw_sql(beta_sql, date_cols=["datadate"])
        conn.close()
        beta_daily["trfd"] = pd.to_numeric(beta_daily["trfd"], errors="coerce")
        beta_daily["sprtrn"] = pd.to_numeric(beta_daily["sprtrn"], errors="coerce")
        beta_daily["stock_return"] = beta_daily.groupby("ticker")["trfd"].pct_change()
        beta_daily = beta_daily.dropna(subset=["stock_return", "sprtrn"])
        beta_estimates = beta_daily.groupby("ticker").apply(
            lambda x: x["stock_return"].cov(x["sprtrn"]) / x["sprtrn"].var()
        ).rename("two_year_daily_beta").reset_index()
        display(beta_estimates)
        beta_estimates.to_csv(LAB / "outputs" / "wrds_compustat_return_betas.csv", index=False)
        print("MANUAL REVIEW: If these estimates are reasonable, copy them into the beta inputs and rerun the fairness, exhibit, and flip-point cells.")
    except Exception as exc:
        print(f"BETA PENDING — retain the error as a documented WRDS attempt: {type(exc).__name__}: {exc}")
'''.strip()))

nb.cells.append(nbf.v4.new_markdown_cell("""
## Submission status checklist — complete yourself

- [ ] I saved the notebook after replacing the flip-point cell with the infeasible-case-safe version.
- [ ] `EDITION_A` contains my actual handwritten prices, dates, and professional sources; any difference from the 2026-09-29 Compustat closes (ORCL $137.79; MSFT $508.96) is explained.
- [ ] I updated Oracle from FY2025 to FY2026 and its known-answer gate passes.
- [ ] I either loaded and reviewed return-calculated professional betas or named the documented WRDS beta-pull failure.
- [ ] I reran both full pro-formas, all check blocks, the fairness table, the two-company exhibit, and the flip point after the final inputs.
- [ ] My exhibit includes both value ranges, both dated prices, and percentage gaps.
- [ ] I wrote the recommendation, flip point, and two triggers in my own words, with dates I verified.
- [ ] I attached the real peer note I received and updated my AI disclosure.
""".strip()))

nbf.write(nb, target)
print(target)
