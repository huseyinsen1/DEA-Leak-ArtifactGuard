from __future__ import annotations
import numpy as np
from scipy.optimize import linprog

def synthetic(seed: int, n: int, m: int=3, s: int=2):
    rng=np.random.default_rng(seed)
    X=rng.lognormal(mean=2.0,sigma=.45,size=(n,m))
    # nonlinear but monotone production with heterogeneous inefficiency
    base=(X[:,0]**.42)*(X[:,1]**.31)*(X[:,2]**.19)
    eff=rng.uniform(.55,1.0,n)
    Y=np.column_stack([
        4.2*base*eff*rng.lognormal(0,.04,n),
        2.8*base*(.75+.25*eff)*rng.lognormal(0,.04,n),
    ])
    return X.astype(float),Y.astype(float)

def solve_two_stage(X,Y,orientation='out',rts='vrs'):
    X=np.asarray(X,float); Y=np.asarray(Y,float); n,m=X.shape; s=Y.shape[1]
    scores=np.empty(n); L=np.zeros((n,n)); SM=np.zeros((n,m)); SP=np.zeros((n,s)); TX=np.zeros((n,m)); TY=np.zeros((n,s))
    for o in range(n):
        if orientation=='out':
            # variables lambda[n], phi
            c=np.r_[np.zeros(n),-1.0]
            Aub=[]; bub=[]
            for i in range(m): Aub.append(np.r_[X[:,i],0.0]); bub.append(X[o,i])
            for r in range(s): Aub.append(np.r_[-Y[:,r],Y[o,r]]); bub.append(0.0)
            Aeq=None; beq=None
            if rts=='vrs': Aeq=np.array([np.r_[np.ones(n),0.0]]); beq=np.array([1.0])
            res=linprog(c,A_ub=np.array(Aub),b_ub=np.array(bub),A_eq=Aeq,b_eq=beq,bounds=[(0,None)]*n+[(1,None)],method='highs')
            if not res.success: raise RuntimeError(res.message)
            score=res.x[-1]
        else:
            # variables lambda[n], theta
            c=np.r_[np.zeros(n),1.0]
            Aub=[]; bub=[]
            for i in range(m): Aub.append(np.r_[X[:,i],-X[o,i]]); bub.append(0.0)
            for r in range(s): Aub.append(np.r_[-Y[:,r],0.0]); bub.append(-Y[o,r])
            Aeq=None; beq=None
            if rts=='vrs': Aeq=np.array([np.r_[np.ones(n),0.0]]); beq=np.array([1.0])
            res=linprog(c,A_ub=np.array(Aub),b_ub=np.array(bub),A_eq=Aeq,b_eq=beq,bounds=[(0,None)]*n+[(0,1)],method='highs')
            if not res.success: raise RuntimeError(res.message)
            score=res.x[-1]
        scores[o]=score
        # stage 2, score fixed, maximize normalized slacks
        # vars lambda, sm[m], sp[s]
        nv=n+m+s
        c2=np.r_[np.zeros(n), -1/np.maximum(X[o],1e-12), -1/np.maximum(Y[o],1e-12)]
        Aeq=[]; beq=[]
        if orientation=='out':
            for i in range(m):
                row=np.zeros(nv); row[:n]=X[:,i]; row[n+i]=1; Aeq.append(row); beq.append(X[o,i])
            for r in range(s):
                row=np.zeros(nv); row[:n]=Y[:,r]; row[n+m+r]=-1; Aeq.append(row); beq.append(score*Y[o,r])
        else:
            for i in range(m):
                row=np.zeros(nv); row[:n]=X[:,i]; row[n+i]=1; Aeq.append(row); beq.append(score*X[o,i])
            for r in range(s):
                row=np.zeros(nv); row[:n]=Y[:,r]; row[n+m+r]=-1; Aeq.append(row); beq.append(Y[o,r])
        if rts=='vrs':
            row=np.zeros(nv); row[:n]=1; Aeq.append(row); beq.append(1.0)
        res2=linprog(c2,A_eq=np.array(Aeq),b_eq=np.array(beq),bounds=[(0,None)]*nv,method='highs')
        if not res2.success: raise RuntimeError(res2.message)
        lam=res2.x[:n]; sm=res2.x[n:n+m]; sp=res2.x[n+m:]
        L[o]=lam; SM[o]=sm; SP[o]=sp
        if orientation=='out': TX[o]=X[o]-sm; TY[o]=score*Y[o]+sp
        else: TX[o]=score*X[o]-sm; TY[o]=Y[o]+sp
    return scores,L,SM,SP,TX,TY
