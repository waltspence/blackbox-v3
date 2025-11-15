#!/usr/bin/env python3
import json, argparse, os, csv
from sliprisk.portfolio import stake_for_slip

def load_bestlines(path):
    try:
        return json.load(open(path, 'r', encoding='utf-8'))
    except Exception:
        return []

def map_by_leg(bestlines):
    return {b["leg_id"]: b for b in bestlines}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bankroll', type=float, required=True)
    ap.add_argument('--unit', type=float, required=True)
    ap.add_argument('--kelly_frac', type=float, default=0.5)
    ap.add_argument('--slips', required=True, help='JSON array of slips with leg_id list')
    ap.add_argument('--corr', required=True, help='artifacts/corr_matrix.json')
    ap.add_argument('--bestlines', default='outputs/bestlines.json')
    ap.add_argument('--policy', default='configs/slip_policy.yaml')
    args = ap.parse_args()

    bestlines = load_bestlines(args.bestlines)
    if not bestlines:
        print('bestlines.json missing; run Pack #3.')
        return
    legmap = map_by_leg(bestlines)

    slips = json.load(open(args.slips, 'r', encoding='utf-8'))
    out = []
    total_stake = 0.0
    for s in slips:
        legs = []
        for lid in s['legs']:
            if lid not in legmap: 
                continue
            legs.append(legmap[lid])
        if len(legs) < 2:
            continue
        stake, pj, dec_out, f_full, f_use = stake_for_slip(
            legs=legs,
            bankroll=args.bankroll,
            unit=args.unit,
            corr_json=args.corr,
            kelly_frac=args.kelly_frac,
            policy_yaml=args.policy
        )
        total_stake += stake
        out.append({
            "slip_id": s.get("slip_id"),
            "legs": [l["leg_id"] for l in legs],
            "n_legs": len(legs),
            "p_joint": round(pj,4),
            "decimal_payout": round(dec_out,4),
            "kelly_full": round(f_full,4),
            "kelly_used": round(f_use,4),
            "stake": stake
        })

    os.makedirs('outputs', exist_ok=True)
    with open('outputs/slip_stakes.json','w',encoding='utf-8') as jf:
        json.dump(out, jf, indent=2)
    if out:
        with open('outputs/slip_stakes.csv','w',encoding='utf-8',newline='') as cf:
            w = csv.DictWriter(cf, fieldnames=list(out[0].keys()))
            w.writeheader()
            for r in out: w.writerow(r)
    print(json.dumps({"slips": len(out), "total_stake": total_stake, "out": "outputs/slip_stakes.json"}, indent=2))

if __name__ == '__main__':
    main()
