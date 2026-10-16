from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'SHA256_MANIFEST.json').read_text())
fail=[]
for rel,expected in manifest.items():
    p=ROOT/rel
    if not p.is_file(): fail.append([rel,'missing']); continue
    got=hashlib.sha256(p.read_bytes()).hexdigest()
    if got!=expected: fail.append([rel,'sha256 mismatch'])
print(json.dumps({'entries':len(manifest),'failures':fail,'verdict':'PASS' if not fail else 'FAIL'},indent=2))
raise SystemExit(0 if not fail else 2)
