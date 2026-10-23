from pathlib import Path
import nbformat as nbf

cap=Path(__file__).resolve().parent
src=cap/'Capstone_Oracle_Microsoft_FINAL.ipynb'
dst=cap/'Capstone_Oracle_Microsoft.ipynb'
nb=nbf.read(src,as_version=4)
nb.cells[0].source='''# Capstone_Oracle_Microsoft

## Oracle (ORCL) and Microsoft (MSFT) comparative valuation capstone

This duplicate preserves the completed Oracle authority and every Microsoft input except the explicit Microsoft FY2027–FY2031 revenue-growth path: 19%, 17%, 15%, 13%, and 7%. The changed path reflects the student’s stronger view that Azure demand, recurring subscriptions, and Copilot enterprise monetisation sustain elevated growth through FY2030 before convergence.'''
for c in nb.cells:
    if c.cell_type=='code' and "MB=dict(growth=[.15,.13,.11,.09,.07]" in c.source:
        c.source=c.source.replace("MB=dict(growth=[.15,.13,.11,.09,.07]", "MB=dict(growth=[.19,.17,.15,.13,.07]")
        c.source=c.source.replace("'15%, 13%, 11%, 9%, 7%'", "'19%, 17%, 15%, 13%, 7%'")
        c.source=c.source.replace("'Azure/subscriptions and uncertain Copilot monetisation'", "'Stronger Azure demand, recurring subscriptions, and Copilot enterprise monetisation through FY2030; convergence in FY2031'")
    if c.cell_type=='code' and "MSC={'Low'" in c.source:
        c.source=c.source.replace("'FY2027 revenue growth':('growth',0,.08,.20)", "'FY2027 revenue growth':('growth',0,.10,.23)")
    if c.cell_type=='code' and "Microsoft','FY2027 revenue growth'" in c.source:
        c.source=c.source.replace("f'{MB[\"growth\"][0]:.1%} base; {MSC[\"Low\"][\"growth\"][0]:.1%} low'", "f'{MB[\"growth\"][0]:.1%} base; {MSC[\"Low\"][\"growth\"][0]:.1%} low'")
nbf.write(nb,dst)
print(dst)
