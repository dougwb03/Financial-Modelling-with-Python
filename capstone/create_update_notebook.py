from pathlib import Path
import nbformat as nbf

cap = Path(__file__).resolve().parent
source = cap / 'Capstone_Oracle_Microsoft_Final.ipynb'
target = cap / 'Capstone_Oracle_Microsoft_UPDATE.ipynb'
nb = nbf.read(source, as_version=4)
nb.cells[0].source = '''# Capstone_Oracle_Microsoft_UPDATE

This update retains the completed Oracle section, Microsoft FY2026 known-answer gate, valuation logic, assumptions, and strict Microsoft WRDS `prccd` beta gate unchanged. The required Microsoft evidence paths are `exercise4/wrds_msft_beta_audit.csv` and `exercise4/wrds_compustat_msft_spy_daily_returns.csv`.'''
manual_markdown = nbf.v4.new_markdown_cell('''## Manual interactive WRDS extraction — MSFT/SPY `prccd`

Run the next cell only in your local VS Code notebook kernel. It asks WRDS to authenticate interactively and writes the two evidence files required by the unchanged Microsoft beta gate. It has no fallback source and does not use `trfd`.''')
manual_code = nbf.v4.new_code_cell(r'''# MANUAL LOCAL VS CODE STEP — do not run in a non-interactive kernel.
# Authenticates only through wrds.Connection(); do not place credentials in this notebook.
import wrds

# The 2024-09-30 close is queried only to calculate the first in-window
# 2024-10-01 return; saved returns remain exactly 2024-10-01 to 2026-09-30.
WRDS_PRICE_START, WRDS_RETURN_START, WRDS_END = '2024-09-30', '2024-10-01', '2026-09-30'
WRDS_TICKERS = ('MSFT', 'SPY')
wrds_conn = wrds.Connection()
try:
    wrds_sql = """
        select s.tic as ticker, d.datadate, d.prccd
        from comp.secd d
        join comp.security s
          on d.gvkey = s.gvkey and d.iid = s.iid
        where s.tic in ('MSFT', 'SPY')
          and d.datadate between %(price_start)s and %(end)s
          and d.prccd is not null and d.prccd > 0
        order by d.datadate, s.tic
    """
    raw_prices = wrds_conn.raw_sql(wrds_sql, params={'price_start': WRDS_PRICE_START, 'end': WRDS_END}, date_cols=['datadate'])
finally:
    wrds_conn.close()

if raw_prices.empty:
    raise RuntimeError('WRDS returned no Compustat Security Daily prccd observations for MSFT/SPY.')
if set(raw_prices['ticker']) != set(WRDS_TICKERS):
    raise RuntimeError('WRDS ticker/security identification did not return exactly MSFT and SPY.')
if raw_prices.duplicated(['datadate', 'ticker']).any():
    raise RuntimeError('WRDS ticker/security identification produced duplicate daily observations; resolve in WRDS before saving evidence.')

prices = raw_prices.pivot(index='datadate', columns='ticker', values='prccd').sort_index()
if not {'MSFT', 'SPY'}.issubset(prices.columns):
    raise RuntimeError('WRDS prccd pivot lacks MSFT and/or SPY.')
returns = pd.DataFrame({
    'MSFT': prices['MSFT'] / prices['MSFT'].shift(1) - 1,
    'SPY': prices['SPY'] / prices['SPY'].shift(1) - 1,
}).dropna().reset_index()
returns = returns[(returns['datadate'] >= pd.Timestamp(WRDS_RETURN_START)) & (returns['datadate'] <= pd.Timestamp(WRDS_END))][['datadate', 'MSFT', 'SPY']]
if len(returns) < 100:
    raise RuntimeError(f'Only {len(returns)} matched MSFT/SPY prccd return observations; at least 100 are required.')
msft_beta = returns['MSFT'].cov(returns['SPY']) / returns['SPY'].var()
if not .20 <= msft_beta <= 3.00:
    raise RuntimeError(f'Calculated MSFT prccd beta {msft_beta:.4f} failed the plausibility gate.')

msft_returns_path = OUT / 'wrds_compustat_msft_spy_daily_returns.csv'
msft_audit_path = OUT / 'wrds_msft_beta_audit.csv'
returns.to_csv(msft_returns_path, index=False)
pd.DataFrame([{
    'run_date': date.today().isoformat(),
    'source': 'WRDS Compustat Security Daily: MSFT and SPY prccd',
    'status': 'success',
    'detail': f'{len(returns)} matched daily return observations; {returns.datadate.min().date()} to {returns.datadate.max().date()}; beta={msft_beta:.4f}; calculated as cov(MSFT return, SPY return) / var(SPY return) from prccd / lag(prccd) - 1.'
}]).to_csv(msft_audit_path, index=False)
display(returns.head()); display(returns.tail())
print(f'MSFT WRDS prccd beta = {msft_beta:.4f}; observations={len(returns)}; {returns.datadate.min().date()} to {returns.datadate.max().date()}')
print('Saved:', msft_returns_path)
print('Saved:', msft_audit_path)''')
gate_index = next(i for i, cell in enumerate(nb.cells) if cell.cell_type == 'code' and "MSFT_AUDIT=OUT/'wrds_msft_beta_audit.csv'" in cell.source)
nb.cells[gate_index:gate_index] = [manual_markdown, manual_code]
nbf.write(nb, target)
print(target)
