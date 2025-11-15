import json, math, yaml
from sliprisk.copula import joint_win_prob

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

def slip_joint_prob(legs, corr_json):
    p = [float(L['marginal_p']) for L in legs]
    keys = [L['leg_id'] for L in legs]
    R = build_corr_submatrix(keys, corr_json)
    return joint_win_prob(p, R, mc_samples=12000, seed=7)

def slip_decimal_payout(legs):
    decs = []
    for L in legs:
        A = int(L['best_american'])
        d = 1 + (A/100.0) if A>0 else 1 + (100.0/abs(A))
        decs.append(d)
    out = 1.0
    for d in decs:
        out *= d
    return out

def kelly_fraction(p_joint, decimal_payout):
    b = decimal_payout - 1.0
    edge = p_joint*b - (1 - p_joint)
    if b <= 0: return 0.0
    f = edge / b
    return max(0.0, f)

def apply_caps(f, bankroll, unit, policy_yaml, rsi_level='medium'):
    cfg = yaml.safe_load(open(policy_yaml, 'r', encoding='utf-8'))
    rsi = cfg.get('rsi_caps', {}).get(rsi_level, {"unit_cap":0.75,"br_cap":0.015})
    per_slip_unit_cap = float(cfg.get('risk_budget',{}).get('per_slip_unit_cap', 1.2))
    # translate caps
    cap_unit = per_slip_unit_cap * unit
    cap_br   = rsi.get('br_cap', 0.015) * bankroll
    return min(f*bankroll, cap_unit, cap_br)

def stake_for_slip(legs, bankroll, unit, corr_json, kelly_frac, policy_yaml):
    p_joint = slip_joint_prob(legs, corr_json)
    dec_out = slip_decimal_payout(legs)
    f_full  = kelly_fraction(p_joint, dec_out)
    f_use   = f_full * float(kelly_frac)
    stake   = apply_caps(f_use, bankroll, unit, policy_yaml, rsi_level='medium')
    return max(0.0, round(stake, 2)), p_joint, dec_out, f_full, f_use
