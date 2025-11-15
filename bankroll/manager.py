from bankroll.kelly import fractional_kelly, american_to_decimal
from bankroll.rsi import cap_by_rsi

def suggest_stake_for_leg(leg, bankroll, unit, kelly_frac, rsi_level, rsi_caps):
    p = float(leg['marginal_p']); A = int(leg['best_american'])
    fk = fractional_kelly(p, A, frac=kelly_frac)
    unit_mult, br_frac_cap = cap_by_rsi(1.0, fk, rsi_level, rsi_caps)
    s_by_unit = unit_mult * unit
    s_by_br   = br_frac_cap * bankroll
    s_by_kelly= fk * bankroll
    stake = min(s_by_unit, s_by_br, s_by_kelly)
    return round(max(0.0, stake), 2)

def enforce_template(stake, unit, template_name, templates_cfg):
    t = templates_cfg.get(template_name, {})
    min_u = float(t.get('min_unit', 0.0)); max_u = float(t.get('max_unit', 10.0))
    units = 0.0 if unit<=0 else (stake / unit)
    units = max(min_u, min(units, max_u))
    return round(units * unit, 2)

def process_legs(priced_bestlines, bankroll, unit, kelly_frac, rsi_level, rsi_caps, template_name, templates_cfg):
    out = []
    for leg in priced_bestlines:
        stake0 = suggest_stake_for_leg(leg, bankroll, unit, kelly_frac, rsi_level, rsi_caps)
        stake  = enforce_template(stake0, unit, template_name, templates_cfg)
        ev = leg['marginal_p'] * (american_to_decimal(leg['best_american']) - 1) - (1 - leg['marginal_p'])
        out.append({
            'leg_id': leg.get('leg_id'),
            'player': leg.get('player'),
            'market': leg.get('market'),
            'line': leg.get('line'),
            'book': leg.get('best_book'),
            'american': leg.get('best_american'),
            'p': round(leg['marginal_p'],4),
            'kelly_frac': kelly_frac,
            'rsi_level': rsi_level,
            'stake': stake,
            'stake_units': round(stake/unit,2) if unit>0 else 0.0,
            'ev_per_dollar': round(ev,4)
        })
    return out
