# Step 10 — observation not otherwise requested

Evidence: in the retained NVDA Yahoo extract, the 2024-06-10 row carries `Stock Splits = 10.0`, while the same row’s OHLC values are already quoted on the post-split scale (Open 120.37, Close 121.79). The return window starts on that date.

Finding: a corporate-action field and the displayed OHLC fields can encode different aspects of the same split. Treating `Stock Splits = 10.0` as a command to divide that day’s displayed prices again would create a tenfold error. I tested this by retaining `auto_adjust=False`, checking the row against the previous close, and separately preserving both `Close` and `Adj Close`; the price is economically continuous around the split on the displayed scale. The practical rule I am taking to Week 2 is to inspect split events before applying any additional split adjustment and to preserve the vendor’s unadjusted and adjusted columns separately.
