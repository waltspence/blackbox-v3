import json
from leggraph.copula import joint_binary_samples

def american_to_decimal(a):
    return 1 + (a/100.0) if a>0 else 1 + (100.0/abs(a))

def slip_pnl(legs, stake, outcomes_row):
    all_win=all(outcomes_row[i]==1 for i in range(len(legs)))
    if not all_win: return -stake
    dec=1.0
    for L in legs: dec*=american_to_decimal(int(L['best_american']))
    return stake*(dec-1.0)

def build_corr_submatrix(leg_keys, corr_json):
    C=json.load(open(corr_json,'r',encoding='utf-8'))
    n=len(leg_keys)
    R=[[1.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            k='|'.join(sorted((leg_keys[i],leg_keys[j])))
            rho=float(C.get(k,0.0)); rho=max(-0.95,min(0.95,rho)); R[i][j]=R[j][i]=rho
    return R

def simulate(slips, legmap, corr_json, sims=20000):
    uniq=[]; idx={}
    for s in slips:
        for lid in s['legs']:
            if lid in legmap and lid not in idx:
                idx[lid]=len(uniq); uniq.append(lid)
    marg=[float(legmap[l]['marginal_p']) for l in uniq]
    R=build_corr_submatrix(uniq, corr_json)
    outcomes=joint_binary_samples(marg, R, samples=sims, seed=99)
    paths=[0.0]*sims
    per_slip={s['slip_id']:{'wins':0,'losses':0} for s in slips}
    for r in range(sims):
        row=outcomes[r]
        pnl=0.0
        for s in slips:
            legs=[legmap[l] for l in s['legs'] if l in legmap]
            idxs=[idx[l] for l in s['legs'] if l in idx]
            slip_out=[row[i] for i in idxs]
            stake=float(s.get('stake',0.0))
            pnl += slip_pnl(legs, stake, slip_out)
            if all(slip_out): per_slip[s['slip_id']]['wins']+=1
            else: per_slip[s['slip_id']]['losses']+=1
        paths[r]=pnl
    import statistics as S
    n=len(paths); mean=sum(paths)/n if n else 0.0; sd=S.pstdev(paths) if n else 0.0
    return paths, mean, sd, per_slip

def var_es(paths, alpha=0.05):
    n=len(paths)
    if n==0: return 0.0,0.0
    s=sorted(paths)
    idx=max(0,int(alpha*n)-1)
    var=s[idx]
    tail=s[:idx+1] if idx>=0 else []
    es = sum(tail)/len(tail) if tail else var
    return var, es
