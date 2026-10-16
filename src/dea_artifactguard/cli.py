from __future__ import annotations
import argparse, json
from .core import analyze_release, sanitize_release, to_dict

def csvset(s): return {x.strip() for x in s.split(',') if x.strip()}

def main(argv=None):
    p=argparse.ArgumentParser(prog='artifactguard', description='DEA result-release reconstruction-path analyzer')
    p.add_argument('--orientation', choices=['out','in'], required=True)
    p.add_argument('--release', required=True, help='comma-separated released fields')
    p.add_argument('--aux', default='', help='comma-separated attacker auxiliary fields')
    p.add_argument('--protection', choices=['full_exact','coordinate_exact','coordinate_exact_plus_conditional'])
    p.add_argument('--mandatory', default='', help='comma-separated fields that cannot be suppressed')
    p.add_argument('--costs', default='', help='JSON object of suppression utility costs')
    args=p.parse_args(argv)
    release=csvset(args.release); aux=csvset(args.aux)
    out={'analysis':to_dict(analyze_release(release,args.orientation,aux))}
    if args.protection:
        costs=json.loads(args.costs) if args.costs else None
        out['sanitization']=to_dict(sanitize_release(release,args.orientation,aux,costs,csvset(args.mandatory),args.protection))
    print(json.dumps(out,indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
