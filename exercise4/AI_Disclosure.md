# Exercise 4 AI disclosure — Oracle

Codex assisted with notebook structure, code, data-extraction organization, and presentation. I independently verified the SEC Company Facts data and Oracle FY2026 filing data used in the model, including revenue ($67,357m), operating income ($20,606m), net income ($17,087m), capex ($55,663m), cash ($31,289m), and filing accession 0001193125-26-277521.

ChatGPT plus was used to review the notebook, form prompts and ensure the work met the required criteria. 

The final beta is independently recalculated in the notebook from the saved WRDS Compustat Security Daily `prccd` closing-price return series for ORCL and SPY. I rejected the earlier `trfd` beta approach after verification because `trfd` is an adjustment factor, not a daily-return series.

I retained responsibility for the OCI/AI capacity and utilisation assumptions, the scenario and tornado interpretation, the debt-cost judgment, the final market comparison, and the conclusion.
