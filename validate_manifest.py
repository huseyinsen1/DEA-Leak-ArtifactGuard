from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / 'SHA256_MANIFEST.json').read_text(encoding='utf-8'))
fail = []
for rel, expected in manifest.items():
    p = ROOT / rel
    if not p.is_file():
        fail.append([rel, 'missing'])
        continue
    got_sha = hashlib.sha256(p.read_bytes()).hexdigest()
    expected_sha = expected['sha256'] if isinstance(expected, dict) else expected
    if got_sha != expected_sha:
        fail.append([rel, 'sha256 mismatch'])
        continue
    if isinstance(expected, dict) and 'bytes' in expected and p.stat().st_size != expected['bytes']:
        fail.append([rel, 'size mismatch'])
print(json.dumps({'entries': len(manifest), 'failures': fail, 'verdict': 'PASS' if not fail else 'FAIL'}, indent=2))
raise SystemExit(0 if not fail else 2)
