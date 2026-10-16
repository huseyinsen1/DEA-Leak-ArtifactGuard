from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from itertools import combinations
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from dea_artifactguard import analyze_release,sanitize_release,paths_for_protection,public_lite

ALL=['score','target_x','target_y','slack_x','slack_y','lambda','peer_ids']; AUX={'peer_x','peer_y'}
PROFILES={
 'balanced':{x:1.0 for x in ALL},
 'explanation_heavy':{'score':5,'target_x':4,'target_y':4,'slack_x':3,'slack_y':3,'lambda':4,'peer_ids':2},
 'slack_expensive':{'score':5,'target_x':2,'target_y':2,'slack_x':8,'slack_y':8,'lambda':1,'peer_ids':2},
 'lambda_expensive':{'score':5,'target_x':2,'target_y':2,'slack_x':1,'slack_y':1,'lambda':9,'peer_ids':2},
}

def brute(release,orientation,cost,mandatory,protection):
    release=set(release);mandatory=set(mandatory);cand=sorted(release-mandatory);best=None
    for k in range(len(cand)+1):
        for combo in combinations(cand,k):
            kept=release-set(combo)
            active=[p for p in paths_for_protection(orientation,protection) if p.required <= (kept|AUX)]
            if active: continue
            loss=sum(cost.get(x,1) for x in combo); key=(loss,len(combo),tuple(sorted(combo)))
            if best is None or key<best[0]:best=(key,set(combo))
    return best

def run():
    gap={}; oracle={}; sanit={}; checked_total=0
    for orient in ['out','in']:
        risky=miss=full=fullmiss=0
        for mask in range(1<<len(ALL)):
            r={ALL[i] for i in range(len(ALL)) if mask>>i&1};an=analyze_release(r,orient,AUX)
            legacy=any(x in {'T0','T1'} for x in an.legacy_findings)
            if an.active_exact_coordinate_paths:
                risky+=1;miss+=int(not legacy)
            if an.active_exact_full_record_paths:
                full+=1;fullmiss+=int(not legacy)
        gap[orient]={'coordinate_risky':risky,'legacy_coordinate_false_negatives':miss,'false_negative_rate':miss/risky,
                     'full_record_risky':full,'legacy_full_record_false_negatives':fullmiss}
        mismatches=checked=0
        for protection in ['full_exact','coordinate_exact']:
            for mask in range(1<<len(ALL)):
                r={ALL[i] for i in range(len(ALL)) if mask>>i&1}; mandatory={'score'} if 'score' in r else set()
                active=[p for p in paths_for_protection(orient,protection) if p.required <= (r|AUX)]
                if not active: continue
                checked+=1; checked_total+=1
                sol=sanitize_release(r,orient,AUX,PROFILES['balanced'],mandatory,protection); br=brute(r,orient,PROFILES['balanced'],mandatory,protection)
                ok=(br is None and not sol.feasible) or (br is not None and sol.feasible and abs(sol.utility_loss-br[0][0])<1e-9)
                mismatches+=int(not ok)
        oracle[orient]={'checked_risky_instances':checked,'objective_mismatches':mismatches}
        full_release=set(ALL)-{'peer_ids'}; sanit[orient]={}
        for pname,cost in PROFILES.items():
            sol=sanitize_release(full_release,orient,AUX,cost,{'score'},'coordinate_exact');pl=public_lite(full_release,cost)
            sanit[orient][pname]={'optimal_suppression':list(sol.suppressed),'utility_loss':sol.utility_loss,
                                  'public_lite_loss':pl['utility_loss'],'loss_reduction_vs_public_lite':1-sol.utility_loss/pl['utility_loss']}
    verdict=(all(gap[o]['coordinate_risky']==62 and gap[o]['legacy_coordinate_false_negatives']==52 and gap[o]['full_record_risky']==10 and gap[o]['legacy_full_record_false_negatives']==0 for o in gap)
             and all(oracle[o]['objective_mismatches']==0 for o in oracle) and checked_total==144)
    return {'legacy_gap':gap,'optimizer_oracle':oracle,'optimizer_checked_total':checked_total,'sanitization':sanit,'verdict':'PASS' if verdict else 'FAIL'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out');a=ap.parse_args();r=run();text=json.dumps(r,indent=2)
    if a.out:Path(a.out).write_text(text,encoding='utf-8')
    print(json.dumps({'legacy_gap':r['legacy_gap'],'optimizer_checked_total':r['optimizer_checked_total'],'optimizer_oracle':r['optimizer_oracle'],'verdict':r['verdict']},indent=2))
    return 0 if r['verdict']=='PASS' else 2
if __name__=='__main__':raise SystemExit(main())
