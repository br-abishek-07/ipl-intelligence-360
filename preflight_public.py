"""Offline stdlib-only QA for deployment-ready IPL 360 sources."""
from pathlib import Path
import ast
ROOT=Path(__file__).resolve().parent
required=['app.py','requirements.txt','.python-version','.streamlit/config.toml','dashboard/views.py','dashboard/data.py','pages/26_Cricket_Debate_Lab.py','data/analytics/matches_enriched.csv','reports/data_quality_audit.json']
missing=[p for p in required if not (ROOT/p).is_file()]
assert not missing, f'Missing deployment inputs: {missing}'
files=list((ROOT/'dashboard').rglob('*.py')) + list((ROOT/'pages').rglob('*.py')) + [ROOT/'app.py']
for p in files: ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
assert not (ROOT/'.streamlit/secrets.toml').exists(), 'Do not publish secrets.toml'
assert not (ROOT/'.env').exists(), 'Do not publish .env'
print(f'PASS: {len(files)} application source files parse, all required files present, and no local secret files detected.')
