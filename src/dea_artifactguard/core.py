from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Iterable, Mapping, Sequence
from itertools import product
import math
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

RELEASE_ARTIFACTS = frozenset({
    'score', 'target_x', 'target_y', 'slack_x', 'slack_y', 'lambda', 'peer_ids'
})
AUX_ARTIFACTS = frozenset({'peer_x', 'peer_y', 'zero_slack_x', 'zero_slack_y'})

@dataclass(frozen=True)
class AttackPath:
    name: str
    scope: str
    exactness: str
    required: frozenset[str]
    components: tuple[str, ...] = ()

@dataclass(frozen=True)
class Analysis:
    orientation: str
    release_fields: tuple[str, ...]
    auxiliary_fields: tuple[str, ...]
    active_exact_coordinate_paths: tuple[str, ...]
    active_conditional_coordinate_paths: tuple[str, ...]
    active_exact_full_record_paths: tuple[str, ...]
    legacy_findings: tuple[str, ...]
    hybrid_full_record_paths: tuple[str, ...]

@dataclass(frozen=True)
class SanitizationResult:
    protection: str
    feasible: bool
    suppressed: tuple[str, ...]
    retained: tuple[str, ...]
    utility_loss: float
    utility_retained_ratio: float
    blocked_paths: tuple[str, ...]
    remaining_paths: tuple[str, ...]
    message: str


def coordinate_paths(orientation: str) -> list[AttackPath]:
    if orientation not in {'out','in'}:
        raise ValueError('orientation must be out or in')
    if orientation == 'out':
        exact = [
            AttackPath('T0-X','input-coordinate','exact',frozenset({'target_x','slack_x'})),
            AttackPath('T1-X','input-coordinate','exact',frozenset({'lambda','peer_x','slack_x'})),
            AttackPath('T0-Y','output-coordinate','exact',frozenset({'score','target_y','slack_y'})),
            AttackPath('T1-Y','output-coordinate','exact',frozenset({'score','lambda','peer_y','slack_y'})),
        ]
        conditional = [
            AttackPath('T2-X','input-coordinate','conditional',frozenset({'lambda','peer_x'})),
            AttackPath('T2-Y','output-coordinate','conditional',frozenset({'score','lambda','peer_y'})),
        ]
    else:
        exact = [
            AttackPath('T0-X','input-coordinate','exact',frozenset({'score','target_x','slack_x'})),
            AttackPath('T1-X','input-coordinate','exact',frozenset({'score','lambda','peer_x','slack_x'})),
            AttackPath('T0-Y','output-coordinate','exact',frozenset({'target_y','slack_y'})),
            AttackPath('T1-Y','output-coordinate','exact',frozenset({'lambda','peer_y','slack_y'})),
        ]
        conditional = [
            AttackPath('T2-X','input-coordinate','conditional',frozenset({'score','lambda','peer_x'})),
            AttackPath('T2-Y','output-coordinate','conditional',frozenset({'lambda','peer_y'})),
        ]
    return exact + conditional


def full_record_paths(orientation: str) -> list[AttackPath]:
    coords = coordinate_paths(orientation)
    ins = [p for p in coords if p.scope == 'input-coordinate' and p.exactness == 'exact']
    outs = [p for p in coords if p.scope == 'output-coordinate' and p.exactness == 'exact']
    res=[]
    for a,b in product(ins, outs):
        res.append(AttackPath(
            name=f'{a.name}+{b.name}', scope='full-record', exactness='exact',
            required=frozenset(a.required | b.required), components=(a.name,b.name)
        ))
    return res


def _active(paths: Sequence[AttackPath], available: set[str]) -> list[AttackPath]:
    return [p for p in paths if p.required <= available]


def legacy_v1_findings(release_fields: Iterable[str], auxiliary_fields: Iterable[str]) -> list[str]:
    f=set(release_fields); a=set(auxiliary_fields); out=[]
    if {'score','target_x','target_y','slack_x','slack_y'} <= f: out.append('T0')
    if {'score','lambda','slack_x','slack_y'} <= f and {'peer_x','peer_y'} <= a:
        out.append('T1')
    elif {'score','lambda'} <= f and {'peer_x','peer_y'} <= a:
        out.append('T2')
    return out


def analyze_release(release_fields: Iterable[str], orientation: str,
                    auxiliary_fields: Iterable[str]=()) -> Analysis:
    r=set(release_fields); a=set(auxiliary_fields); available=r|a
    unknown=(r-RELEASE_ARTIFACTS) | (a-AUX_ARTIFACTS)
    if unknown: raise ValueError(f'unknown artifact(s): {sorted(unknown)}')
    coords=coordinate_paths(orientation); full=full_record_paths(orientation)
    ae=_active([p for p in coords if p.exactness=='exact'],available)
    ac=_active([p for p in coords if p.exactness=='conditional'],available)
    af=_active(full,available)
    legacy=legacy_v1_findings(r,a)
    hybrids=[p.name for p in af if p.name not in {'T0-X+T0-Y','T1-X+T1-Y'}]
    return Analysis(
        orientation=orientation, release_fields=tuple(sorted(r)), auxiliary_fields=tuple(sorted(a)),
        active_exact_coordinate_paths=tuple(p.name for p in ae),
        active_conditional_coordinate_paths=tuple(p.name for p in ac),
        active_exact_full_record_paths=tuple(p.name for p in af),
        legacy_findings=tuple(legacy), hybrid_full_record_paths=tuple(hybrids),
    )


def paths_for_protection(orientation: str, protection: str) -> list[AttackPath]:
    coords=coordinate_paths(orientation)
    if protection=='full_exact': return full_record_paths(orientation)
    if protection=='coordinate_exact': return [p for p in coords if p.exactness=='exact']
    if protection=='coordinate_exact_plus_conditional': return coords
    raise ValueError('unknown protection')


def sanitize_release(release_fields: Iterable[str], orientation: str,
                     auxiliary_fields: Iterable[str]=(), utility_cost: Mapping[str,float] | None=None,
                     mandatory_fields: Iterable[str]=(), protection: str='full_exact') -> SanitizationResult:
    r=set(release_fields); a=set(auxiliary_fields); available=r|a; mandatory=set(mandatory_fields)
    unknown=(r-RELEASE_ARTIFACTS) | (a-AUX_ARTIFACTS)
    if unknown: raise ValueError(f'unknown artifact(s): {sorted(unknown)}')
    if not mandatory <= r: raise ValueError('mandatory fields must be released fields')
    utility_cost=dict(utility_cost or {x:1.0 for x in r})
    for x in r:
        utility_cost.setdefault(x,1.0)
        if utility_cost[x] < 0: raise ValueError('utility costs must be nonnegative')
    all_paths=paths_for_protection(orientation,protection); active=_active(all_paths,available)
    if not active:
        return SanitizationResult(protection,True,(),tuple(sorted(r)),0.0,1.0,(),(),
                                  'No active path for requested protection level.')
    candidates=sorted(r-mandatory)
    for p in active:
        if not (p.required & set(candidates)):
            return SanitizationResult(protection,False,(),tuple(sorted(r)),math.inf,0.0,
                                      (),tuple(x.name for x in active),
                                      f'Path {p.name} contains no suppressible released artifact.')
    c=np.array([utility_cost[x] for x in candidates],float)
    A=np.zeros((len(active),len(candidates)),float)
    for row,p in enumerate(active):
        for j,x in enumerate(candidates):
            if x in p.required: A[row,j]=1.0
    constraints=LinearConstraint(A,lb=np.ones(len(active)),ub=np.full(len(active),np.inf))
    res=milp(c,integrality=np.ones(len(candidates)),bounds=Bounds(np.zeros(len(candidates)),np.ones(len(candidates))),
             constraints=constraints,options={'disp':False})
    if not res.success:
        return SanitizationResult(protection,False,(),tuple(sorted(r)),math.inf,0.0,(),
                                  tuple(x.name for x in active),res.message)
    suppressed={candidates[i] for i,z in enumerate(res.x) if z>0.5}; retained=r-suppressed
    remaining=_active(all_paths,retained|a); remaining_names={p.name for p in remaining}
    blocked=[p.name for p in active if p.name not in remaining_names]
    loss=sum(utility_cost[x] for x in suppressed); total=sum(utility_cost[x] for x in r)
    ratio=1.0 if total==0 else (total-loss)/total
    return SanitizationResult(
        protection,not remaining,tuple(sorted(suppressed)),tuple(sorted(retained)),loss,ratio,
        tuple(sorted(blocked)),tuple(p.name for p in remaining),'Optimal minimum-utility-loss suppression.'
    )


def public_lite(release_fields: Iterable[str], utility_cost: Mapping[str,float] | None=None):
    r=set(release_fields); utility_cost=dict(utility_cost or {x:1.0 for x in r})
    keep={'score','peer_ids'} & r; suppressed=r-keep
    total=sum(utility_cost.get(x,1.0) for x in r); loss=sum(utility_cost.get(x,1.0) for x in suppressed)
    return {'suppressed':tuple(sorted(suppressed)),'retained':tuple(sorted(keep)),
            'utility_loss':loss,'utility_retained_ratio':1.0 if total==0 else (total-loss)/total}


def infer_release_schema(file_names: Iterable[str]) -> set[str]:
    names=[str(x).lower() for x in file_names]; f=set()
    if any(x.endswith('_eff.csv') for x in names): f.add('score')
    if any(x.endswith('_lambda.csv') for x in names): f.add('lambda')
    if any(x.endswith('_sx.csv') for x in names): f.add('slack_x')
    if any(x.endswith('_sy.csv') for x in names): f.add('slack_y')
    if any(x.endswith('_tx.csv') for x in names): f.add('target_x')
    if any(x.endswith('_ty.csv') for x in names): f.add('target_y')
    return f


def to_dict(obj):
    return asdict(obj)
