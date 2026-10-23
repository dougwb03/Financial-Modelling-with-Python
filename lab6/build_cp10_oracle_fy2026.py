from pathlib import Path
import nbformat as nbf

root=Path(__file__).resolve().parent
nb=nbf.read(root/'Lab6_CP10_Oracle_Microsoft_final.ipynb',as_version=4)
target=root/'Lab6_CP10_Oracle_Microsoft_OracleFY2026.ipynb'
def replace(needle,source):
    for cell in nb.cells:
        if needle in cell.source:
            cell.source=source.strip();cell.outputs=[];cell.execution_count=None;return
    raise RuntimeError(needle)

replace('def history(a):',r'''
# Oracle FY2026 company half. SEC 10-K: accession 0001193125-26-277521, filed 2026-06-22.
# The values below are USD millions and come from cached Company Facts / the filed statement mapping.
oracle.loc[2026] = {"start":"2025-06-01","end":"2026-05-31","days":365,"accession":"0001193125-26-277521","filed":"2026-06-22","revenue":67357.,"cost_of_revenue":26530.,"gross_profit_derived":40827.,"operating_expenses_below_gross_profit":20221.,"operating_income":20606.,"pretax_income":19554.,"income_tax":2467.,"net_income":17087.,"depreciation_and_amortization":9294.,"operating_cash_flow":31977.,"capital_expenditure":55663.,"inventory":303.,"ppe_net":99957.,"total_assets":261759.,"total_liabilities":219251.,"shareholders_equity":42508.}
def history(a):
 h=pd.DataFrame(index=a.index);h['revenue growth']=a.revenue.pct_change();h['gross margin']=1-a.cost_of_revenue/a.revenue;h['cash costs / revenue']=(a.operating_expenses_below_gross_profit-a.depreciation_and_amortization)/a.revenue;h['D&A / revenue']=a.depreciation_and_amortization/a.revenue;h['tax / pretax']=a.income_tax/a.pretax_income;h['capex / revenue']=a.capital_expenditure/a.revenue;h['inventory / revenue']=a.inventory/a.revenue;return h
oh=history(oracle);display(oh.map(lambda x:'—' if pd.isna(x) else f'{x:.1%}'))
print('MANUAL VERIFY: $303m FY2025 inventory is temporarily held constant because FY2026 inventory is not separately tagged in the cached Company Facts. Confirm it directly in the FY2026 10-K before submission.')
avg=lambda col:float(oh.loc[2025:2026,col].mean());z=oracle.loc[2026]
facts=json.load(open(LAB/'cache'/'CIK0001341439_companyfacts.json'))['facts']['us-gaap']
def fact26(tag):return next(x['val']/1e6 for x in reversed(facts[tag]['units']['USD']) if x.get('end')=='2026-05-31' and x.get('form')=='10-K')
current_assets,current_liabilities,current_debt=map(fact26,['AssetsCurrent','LiabilitiesCurrent','DebtCurrent'])
nwc=(current_assets-31289.)-(current_liabilities-current_debt)
ORACLE={'name':'Oracle','opening_year':2026,'opening':{'revenue':z.revenue,'inventory':z.inventory,'ppe':z.ppe_net,'cash':31289.,'debt':129541.,'equity':z.shareholders_equity,'assets':z.total_assets,'liabilities':z.total_liabilities},'drivers':{'growth':[avg('revenue growth')]*5,'gm':[avg('gross margin')]*5,'cash_cost':[avg('cash costs / revenue')]*5,'da':[avg('D&A / revenue')]*5,'tax':[avg('tax / pretax')]*5,'capex':[avg('capex / revenue')]*5,'inventory':[avg('inventory / revenue')]*5,'nwc':[nwc/z.revenue]*5,'interest_rate':(z.operating_income-z.pretax_income)/129541.,'noncash':0.,'paydown':0.,'buyback':0.,'cash_floor':5000.,'revolver_cap':25000.},'valuation':{'r':.09,'g':.025,'shares':3023.736,'shares_are_millions':True}}
labels={'growth':'history: FY2025–26 mean','gm':'history: FY2025–26 mean','cash_cost':'history: FY2025–26 mean, D&A separated','da':'history: FY2025–26 mean','tax':'history: FY2025–26 mean','capex':'history: FY2025–26 mean','inventory':'MANUAL VERIFY: FY2025 value held pending FY2026 10-K read','nwc':'fact: FY2026 operating NWC / revenue','interest_rate':'history proxy: FY2026 EBIT-to-pretax bridge / opening debt','paydown':'judgment: zero pending debt guidance','buyback':'judgment: zero pending repurchase guidance','cash_floor':'judgment: $5bn','r':'CAPM placeholder until professional beta rerun','g':'judgment: terminal growth'}
ledger=pd.DataFrame([(k,v,labels.get(k,'judgment')) for k,v in ORACLE['drivers'].items() if k not in ('noncash','revolver_cap')]+[('cost of equity',ORACLE['valuation']['r'],labels['r']),('terminal growth',ORACLE['valuation']['g'],labels['g']),('shares (millions)',ORACLE['valuation']['shares'],'fact: latest filed cover')],columns=['input','value','label / basis']);display(ledger)
''')

replace('def rebuild_filed(a):',r'''
def rebuild_filed(a):
 gp=a.revenue-a.cost_of_revenue;cash_cost=a.operating_expenses_below_gross_profit-a.depreciation_and_amortization;ebit=gp-cash_cost-a.depreciation_and_amortization;ni=a.pretax_income-a.income_tax;return pd.Series({'Revenue':a.revenue,'Operating income':ebit,'Net income':ni,'Latest shares (millions)':3023.736,'Net debt':129541.-31289.})
filed=pd.Series({'Revenue':67357.,'Operating income':20606.,'Net income':17087.,'Latest shares (millions)':3023.736,'Net debt':98252.})
gate=pd.DataFrame({'filed FY2026':filed,'model FY2026':rebuild_filed(oracle.loc[2026])});gate['difference']=gate.iloc[:,1]-gate.iloc[:,0];gate['pass']=gate.difference.abs()<.01;display(gate);assert gate['pass'].all()
''')

for cell in nb.cells:
    cell.source=cell.source.replace('Oracle FY2025','Oracle FY2026').replace('FY2023–25 gross-margin','FY2024–26 gross-margin')
nbf.write(nb,target);print(target)
