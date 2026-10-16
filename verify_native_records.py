from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
checks=[]
for f in ['benchmarking_charnes_verification.json','dear_fixture_verification.json']:
    d=json.loads((ROOT/'native_results'/f).read_text())
    checks.append({'file':f,'verdict':d.get('verdict'),'note':d.get('note')})
if checks[0]['verdict']!='PASS' or checks[1]['verdict']!='PASS': raise SystemExit('native frozen-record validation failed')
print(json.dumps({'checks':checks,'verdict':'PASS'},indent=2))
