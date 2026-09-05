"""Validate committed evidence without pretending to retrain external-data models."""
from pathlib import Path
import ast, csv, json, math
ROOT=Path(__file__).resolve().parents[1]
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

print('Committed evidence and syntax checks passed; see VALIDATION.md for rerun scope.')
