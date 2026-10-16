from __future__ import annotations
import numpy as np

def coordinate_reconstruct(X,Y,score,L,SM,SP,TX,TY,o,orientation):
    lo=L[o,o]
    if orientation=='out':
        ax=1.0; ay=score[o]
        t0x=TX[o]+SM[o]
        t0y=(TY[o]-SP[o])/score[o]
    else:
        ax=score[o]; ay=1.0
        t0x=(TX[o]+SM[o])/score[o]
        t0y=TY[o]-SP[o]
    dx=ax-lo; dy=ay-lo
    t1x=t1y=None
    if abs(dx)>=1e-10:
        t1x=(L[o]@X-lo*X[o]+SM[o])/dx
    if abs(dy)>=1e-10:
        t1y=(L[o]@Y-lo*Y[o]-SP[o])/dy
    return {'T0-X':t0x,'T0-Y':t0y,'T1-X':t1x,'T1-Y':t1y}

def full_reconstruct(X,Y,score,L,SM,SP,TX,TY,o,orientation):
    c=coordinate_reconstruct(X,Y,score,L,SM,SP,TX,TY,o,orientation)
    return np.r_[c['T0-X'],c['T0-Y']], None if c['T1-X'] is None or c['T1-Y'] is None else np.r_[c['T1-X'],c['T1-Y']]
