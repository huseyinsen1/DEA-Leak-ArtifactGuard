from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np

def run(trials=1000,seed=20260810):
    rng=np.random.default_rng(seed); max_t0=max_t1=0.0
    for _ in range(trials):
        n=8;m=3;s=2;o=0
        X=rng.uniform(.5,10,(n,m));Y=rng.uniform(.5,10,(n,s)); lam=rng.uniform(0,1,n); lam[o]=rng.uniform(0,.3)
        # construct output-oriented identities from arbitrary tuple with denominators nonzero
        phi=rng.uniform(1.05,2); sm=rng.uniform(0,1,m); sp=rng.uniform(0,1,s)
        # force peers so identity gives target by defining target from RHS; this validates rearrangement itself
        dx=1-lam[o];dy=phi-lam[o]
        xo=(lam[1:]@X[1:]+sm)/dx; yo=(lam[1:]@Y[1:]-sp)/dy
        tx=xo-sm; ty=phi*yo+sp
        t0x=tx+sm;t0y=(ty-sp)/phi
        t1x=(lam[1:]@X[1:]+sm)/dx;t1y=(lam[1:]@Y[1:]-sp)/dy
        max_t0=max(max_t0,float(np.max(np.abs(np.r_[t0x-xo,t0y-yo]))))
        max_t1=max(max_t1,float(np.max(np.abs(np.r_[t1x-xo,t1y-yo]))))
    verdict=max(max_t0,max_t1)<1e-12
    return {'trials':trials,'max_abs_T0':max_t0,'max_abs_T1':max_t1,'verdict':'PASS' if verdict else 'FAIL'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out');a=ap.parse_args();r=run();text=json.dumps(r,indent=2)
    if a.out:Path(a.out).write_text(text,encoding='utf-8')
    print(text);return 0 if r['verdict']=='PASS' else 2
if __name__=='__main__':raise SystemExit(main())
