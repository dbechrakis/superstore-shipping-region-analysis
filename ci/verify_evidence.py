"""Validate committed evidence without pretending to retrain external-data models."""
from pathlib import Path
import ast, csv, hashlib, json, math, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from analysis.margin_drivers import analyze
for p in ROOT.rglob('*.py'):
    if not any(x in p.parts for x in ['.git','.venv','node_modules']): ast.parse(p.read_text())
for p in ROOT.rglob('*.ipynb'):
    n=json.loads(p.read_text()); assert n['nbformat']==4
    for c in n['cells']:
        assert c['cell_type'] in ['code','markdown','raw']
        assert not any(o.get('output_type')=='error' for o in c.get('outputs',[])), str(p)
def table(path):
    with (ROOT/path).open(newline='',encoding='latin1' if str(path).startswith('data/') else 'utf-8') as f:return list(csv.DictReader(f))
def close(a,b,tol=1e-6): assert math.isclose(float(a),float(b),abs_tol=tol,rel_tol=tol),(a,b)
rows=table('data/Sample - Superstore.csv')
v=json.loads((ROOT/'outputs/validation.json').read_text())
close(sum(float(r['Sales']) for r in rows),v['sales']);close(sum(float(r['Profit']) for r in rows),v['profit'])
assert len(rows)==v['lines'] and len({r['Order ID'] for r in rows})==v['orders']
for out in table('outputs/regional_metrics.csv'):
    selected=[r for r in rows if r['Region']==out['Region']]
    sales=sum(float(r['Sales']) for r in selected);profit=sum(float(r['Profit']) for r in selected)
    close(sales,out['Sales']);close(profit,out['Profit']);close(100*profit/sales,out['Margin (%)'])

# Recompute the new accounting views from original rows, not from the exported results.
driver=json.loads((ROOT/'outputs/margin_drivers.json').read_text())
assert driver['source_sha256']==v['source_sha256']==hashlib.sha256((ROOT/'data/Sample - Superstore.csv').read_bytes()).hexdigest()
actual=analyze(rows,driver['focus'],driver['reference'])
close(driver['gap_pp'],actual['gap_pp'])
for region,margin in actual['margins_pct'].items(): close(driver['margins_pct'][region],margin)
close(driver['reconciliation_residual_pp'],actual['reconciliation_residual_pp'])
close(driver['shipping_reconciliation_residual_pp'],actual['shipping_reconciliation_residual_pp'])
for name in ('product_effects_pp','shipping_effects_pp'):
    for factor,value in actual[name].items(): close(driver[name][factor],value)
    close(sum(driver[name].values()),driver['gap_pp'])
for filename,expected,keys in (
    ('product_margin_contributions.csv',actual['product_rows'],('category','subcategory','factor')),
    ('shipping_mode_contributions.csv',actual['shipping_rows'],('ship_mode','factor')),
):
    committed=table('outputs/'+filename)
    assert len(committed)==len(expected)
    reference={tuple(r[k] for k in keys):r['contribution_pp'] for r in expected}
    assert len(reference)==len(expected)
    for record in committed:
        key=tuple(record[k] for k in keys)
        close(record['contribution_pp'],reference.pop(key))
    assert not reference
discount=table('outputs/discount_diagnostic.csv')
assert len(discount)==len(actual['discount_rows'])
reference={(r['region'],r['category'],r['subcategory']):r for r in actual['discount_rows']}
for record in discount:
    key=(record['region'],record['category'],record['subcategory'])
    expected=reference.pop(key)
    assert int(record['lines'])==expected['lines']
    for field in ('sales','profit','margin_pct','sales_weighted_discount_pct','sales_share_discount_ge_30_pct'):
        close(record[field],expected[field])
assert not reference

print('Committed evidence and syntax checks passed; see VALIDATION.md for rerun scope.')
