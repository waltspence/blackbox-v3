import json, math, statistics as stats
from stress.copula import joint_samples

def american_to_decimal(A):
    return 1 + (A/100.0) if A > 0 else 1 + (100.0/abs(A))

def build_corr_submatrix(leg_keys, corr_json):
    C = json.load(open(corr_json, 'r', encoding='utf-8'))
    n = len(leg_keys)
    R = [[1.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            k = "|".join(sorted((leg_keys[i], leg_keys[j])))
            rho = float(C.get(k, 0.0))
            if rho > 0.95: rho=0.95
            if rho < -0.95: rho=-0.95
            R[i][j]=R[j][i]=rho
    return R

def slip_pnl(legs, stake, outcomes_row):
    # all legs must be 1 to win the parlay
    all_win = all(outcomes_row[i]==1 for i in range(len(legs)))
    if not all_win:
        return -stake
    dec = 1.0
    for L in legs:
        A = int(L['best_american'])
        d = american_to_decimal(A)
        dec *= d
    return stake * (dec - 1.0)

def simulate(slips, legmap, corr_json, sims=20000):
    # flatten unique legs & build index
    unique_ids = []
    id_to_idx = {}
    for s in slips:
        for lid in s['legs']:
            if lid not in id_to_idx and lid in legmap:
                id_to_idx[lid] = len(unique_ids)
                unique_ids.append(lid)
    marg = [float(legmap[lid]['marginal_p']) for lid in unique_ids]
    R = build_corr_submatrix(unique_ids, corr_json)
    outcomes = joint_samples(marg, R, samples=sims, seed=23)
    # per-run PnL
    path_pnl = [0.0]*sims
    per_slip = {s['slip_id']: {"wins":0, "losses":0} for s in slips}
    for r in range(sims):
        row = outcomes[r]
        pnl = 0.0
        for s in slips:
            legs = [legmap[lid] for lid in s['legs'] if lid in legmap]
            if len(legs) == 0: 
                continue
            # align indices
            idxs = [id_to_idx[lid] for lid in s['legs'] if lid in id_to_idx]
            slip_outcomes = [row[i] for i in idxs]
            stake = float(s.get('stake', 0.0))
            p = slip_pnl(legs, stake, slip_outcomes)
            pnl += p
            if all(slip_outcomes): per_slip[s['slip_id']]['wins'] += 1
            else: per_slip[s['slip_id']]['losses'] += 1
        path_pnl[r] = pnl
    # stats
    path_sorted = sorted(path_pnl)
    n = len(path_sorted)
    mean = sum(path_sorted)/n if n else 0.0
    sd = stats.pstdev(path_sorted) if n else 0.0
    return path_pnl, mean, sd, per_slip

def var_es(paths, alpha=0.05):
    n = len(paths)
    if n==0: return 0.0, 0.0
    sorted_p = sorted(paths)
    idx = max(0, int(alpha*n)-1)
    var = sorted_p[idx]
    tail = sorted_p[:idx+1] if idx>=0 else []
    es = sum(tail)/len(tail) if tail else var
    return var, es
