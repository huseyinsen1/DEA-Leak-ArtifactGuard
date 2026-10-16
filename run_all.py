from __future__ import annotations
import os,sys,subprocess,json,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ENV=dict(os.environ);ENV['PYTHONPATH']=str(ROOT/'src')+os.pathsep+str(ROOT/'experiments')+os.pathsep+ENV.get('PYTHONPATH','')
commands=[
 [sys.executable,'experiments/algebra_selftest.py','--out','rerun_algebra.json'],
 [sys.executable,'experiments/public_coordinate_campaign.py','--out','rerun_coordinate_campaign.json'],
 [sys.executable,'experiments/exhaustive_release_audit.py','--out','rerun_release_audit.json'],
 [sys.executable,'-m','unittest','discover','-s','tests','-v'],
 [sys.executable,'verify_native_records.py'],
]
for cmd in commands:
    print('>>>',' '.join(cmd),flush=True)
    subprocess.run(cmd,cwd=ROOT,env=ENV,check=True)
print('OVERALL PASS')
