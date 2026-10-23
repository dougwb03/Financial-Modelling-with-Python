# Exercise 4 — Oracle summary

FY2026, ended 31 May 2026, is the opening year. The SEC Company Facts known-answer gate passes for revenue ($67,357m), operating income ($20,606m), net income ($17,087m), and the balance-sheet facts. Latest filed shares are 3,023.736m and net debt is $98,252m.

The final beta is **1.6369**, calculated from 501 matched daily ORCL and SPY closing-price returns in WRDS Compustat Security Daily `prccd`, from 1 October 2024 through 30 September 2026. The local WRDS audit and return series are required inputs; the notebook refuses to produce a valuation if either fails validation. The earlier `trfd` approach was rejected after verification because `trfd` is an adjustment factor, not a daily-return series.

AI helped with notebook structure, extraction organisation, and code; I independently verified the SEC Company Facts and Oracle FY2026 10-K figures used in the model, and specifically rejected the earlier WRDS `trfd` beta approach after verifying that it is an adjustment factor, not a daily-return series, replacing it with beta calculated from saved WRDS Compustat Security Daily `prccd` returns.

At the dated 29 September 2026 WRDS price of $137.79, the model uses a 5.06% risk-free rate, 4.234% ERP, 4.5% estimated blended pre-tax cost of existing debt, and the final WRDS beta. Cost of equity is 11.99% and WACC is **9.98%**. The 4.5% debt-cost input is not a new-borrowing rate; it estimates the blended cost of debt issued earlier, which is why it can sit below the contemporaneous Treasury yield.

The OCI/AI monetisation base case assumes revenue growth of 20%, 18%, 16%, 10%, and 7%; EBIT margin of 31.5% rising to 35.0%; and capex/revenue of 70%, 55%, 42%, 32%, and 25%. This is an optimistic OCI/AI monetisation base case, not a conservative one. It assumes utilisation and operating leverage outweigh the new data-centre cost and depreciation burden. The deliberately high early capex is a gradual payback of FY2026’s infrastructure build, not an average that smooths the spike away. Accordingly, FY2027–FY2028 FCFF is negative and the model borrows to preserve a $10bn cash floor.

**Oracle-specific driver:** OCI/AI data-centre capacity and utilisation, unlike the ABG template, is implemented through Oracle-specific high capex/revenue, PP&E-linked D&A, utilisation-driven margin expansion, and the possibility of early negative FCFF/additional borrowing.

The DCF produces a **$48.74–$83.67 per-share** low/base/high range, with a base case of **$66.02**. Base enterprise value is $297,870m, implied EV/FY2027 EBIT is **11.70x**, and the base value is **52.1% below** the dated WRDS price. Terminal value is **100.7% of enterprise value** because discounted early FCFF is negative. This must be stated plainly: the outcome depends heavily on Oracle eventually converting the infrastructure build into sustainable FY2031 cash flow. The DCF is an assumption-sensitive range, not a precise target price.

The tornado covers revenue growth, operating margin, capex/revenue, and terminal growth; FY2031 operating margin is the largest business-driver swing ($52.86–$79.18 per share). FY2031 operating margin is the single assumption most likely to move the valuation. Its low case requires OCI/AI capacity utilisation and booked demand to miss sufficiently that new data centres earn inadequate returns. Its high case requires sustained OCI/AI demand and utilisation high enough for operating leverage to overcome cost and depreciation while capacity converts into cash flow.

Four checks:

- FY2026 known-answer gate: revenue, operating income, net income, shares, and net debt matched.
- Forecast balance identity: passed FY2027–FY2031.
- Cash-flow tie: passed FY2027–FY2031.
- Cash floor: passed FY2027–FY2031.

My base case assumes strong OCI growth but slower cash-flow conversion and margin realisation than the market appears to expect. The market price implies a faster or more profitable payback from Oracle’s data-centre investment than my base case supports.

Judgment after sensitivity analysis: The sensitivity table made me less confident in treating the $66.02 base case as a standalone estimate and more focused on the $48.74–$83.67 valuation range. In particular, seeing FY2031 operating margin produce the largest business-driver swing ($52.86–$79.18 per share) reinforced that Oracle’s valuation depends less on simply achieving strong OCI/AI revenue growth and more on whether its large data-centre investment ultimately produces sufficient utilisation, operating leverage, and cash-flow conversion. This shifted my judgment toward viewing execution on margins and infrastructure returns as the central valuation risk, rather than revenue growth alone.