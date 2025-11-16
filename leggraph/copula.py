import math, random

def cholesky_psd(A):
    n=len(A)
    L=[[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            s=A[i][j]
            for k in range(j): s-=L[i][k]*L[j][k]
            if i==j:
                if s<=1e-12: s=1e-12
                L[i][j]=math.sqrt(s)
            else:
                L[i][j]=s/L[j][j]
    return L

def phi_inv(p):
    if p<=0.0: return -10.0
    if p>=1.0: return 10.0
    import math
    a1=-39.69683028665376; a2=220.9460984245205; a3=-275.9285104469687
    a4=138.3577518672690; a5=-30.66479806614716; a6=2.506628277459239
    b1=-54.47609879822406; b2=161.5858368580409; b3=-155.6989798598866
    b4=66.80131188771972; b5=-13.28068155288572
    c1=-0.007784894002430293; c2=-0.3223964580411365; c3=-2.400758277161838
    c4=-2.549732539343734; c5=4.374664141464968; c6=2.938163982698783
    d1=0.007784695709041462; d2=0.3224671290700398; d3=2.445134137142996; d4=3.754408661907416
    plow=0.02425; phigh=1-plow
    if p<plow:
        q=math.sqrt(-2*math.log(p))
        return (((((c1*q+c2)*q+c3)*q+c4)*q+c5)*q+c6)/((((d1*q+d2)*q+d3)*q+d4))
    if p>phigh:
        q=math.sqrt(-2*math.log(1-p))
        return -(((((c1*q+c2)*q+c3)*q+c4)*q+c5)*q+c6)/((((d1*q+d2)*q+d3)*q+d4))
    q=p-0.5; r=q*q
    return (((((a1*r+a2)*r+a3)*r+a4)*r+a5)*r+a6)*q/(((((b1*r+b2)*r+b3)*r+b4)*r+b5)*r+1)

def joint_binary_samples(marginals, R, samples=10000, seed=42):
    n=len(marginals)
    for i in range(n):
        R[i][i]=1.0
        for j in range(i+1,n):
            val=max(-0.95,min(0.95,R[i][j]))
            R[i][j]=R[j][i]=val
    L=cholesky_psd(R)
    random.seed(seed)
    thr=[phi_inv(p) for p in marginals]
    outs=[]
    for _ in range(samples):
        z0=[random.gauss(0,1) for _ in range(n)]
        z=[sum(L[i][k]*z0[k] for k in range(i+1)) for i in range(n)]
        outs.append([1 if z[i]<=thr[i] else 0 for i in range(n)])
    return outs
