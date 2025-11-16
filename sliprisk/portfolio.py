import math

def american_to_decimal(a):
    return 1 + (a/100.0) if a>0 else 1 + (100.0/abs(a))

def kelly_fraction(p, dec):
    b=dec-1.0; q=1.0-p; num=b*p-q; den=b
    return max(0.0, num/den) if den>0 else 0.0

def slip_decimal(legs):
    dec=1.0
    for L in legs:
        dec*=american_to_decimal(int(L['best_american']))
    return dec

def stake_for_slip(legs, bankroll, kelly_frac=0.5, p_joint=0.0, unit_cap=None):
    dec=slip_decimal(legs); f=kelly_fraction(p_joint, dec); stake=bankroll*f*kelly_frac
    if unit_cap is not None: stake=min(stake, unit_cap)
    return max(0.0, round(stake,2))
