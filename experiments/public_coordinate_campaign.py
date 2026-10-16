from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
from dea_solver import synthetic, solve_two_stage
from reconstruction import coordinate_reconstruct

def run():
    details=[]
    for k in range(5):
        X,Y=synthetic(20260810+k,55+5*k)
        for orientation in ['out','in']:
            for rts in ['vrs','crs']:
                score,L,SM,SP,TX,TY=solve_two_stage(X,Y,orientation,rts)
                inefficient=(score>1+1e-7) if orientation=='out' else (score<1-1e-7)
                counts={p:[0,0] for p in ['T0-X','T0-Y','T1-X','T1-Y']}
                for o in np.flatnonzero(inefficient):
                    rec=coordinate_reconstruct(X,Y,score,L,SM,SP,TX,TY,o,orientation)
                    truth={'T0-X':X[o],'T1-X':X[o],'T0-Y':Y[o],'T1-Y':Y[o]}
                    for p,val in rec.items():
                        if val is None: continue
                        counts[p][0]+=1
                        counts[p][1]+=int(np.allclose(val,truth[p],rtol=1e-8,atol=1e-8))
                row={'dataset':f'synthetic-{k+1}','orientation':orientation,'rts':rts,'n_inefficient':int(inefficient.sum())}
                for p,(eligible,exact) in counts.items():
                    row[p+'_eligible']=eligible; row[p+'_exact']=exact; row[p+'_rate']=exact/max(1,eligible)
                details.append(row)
    mins={p:min(d[p+'_rate'] for d in details if d[p+'_eligible']>0) for p in ['T0-X','T0-Y','T1-X','T1-Y']}
    return {'cases':len(details),'aggregate_min_rates':mins,'details':details,'verdict':'PASS' if min(mins.values())==1.0 else 'FAIL'}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out'); a=ap.parse_args(); r=run(); text=json.dumps(r,indent=2)
    if a.out: Path(a.out).write_text(text,encoding='utf-8')
    print(json.dumps({'cases':r['cases'],'aggregate_min_rates':r['aggregate_min_rates'],'verdict':r['verdict']},indent=2))
    return 0 if r['verdict']=='PASS' else 2
if __name__=='__main__': raise SystemExit(main())
