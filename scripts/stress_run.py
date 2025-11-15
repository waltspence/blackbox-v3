#!/usr/bin/env python3
import json, argparse, os, csv, yaml
from stress.monte import simulate, var_es

def load_json(path):
    try:
        return json.load(open(path,'r',encoding='utf-8'))
    except Exception:
        return None

def map_by_leg(bestlines):
    return {b['leg_id']: b for b in bestlines}

def attach_stakes_to_slips(slips, slip_stakes):
    # map slip_id to stake if provided, else leave 0
    by_id = {s['slip_id']: s for s in slip_stakes} if slip_stakes else {}
    for s in slips:
        stake = 0.0
        if s.get('slip_id') in by_id:
            stake = float(by_id[s['slip_id']].get('stake', 0.0))
        s['stake'] = stake
    return slips

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bankroll', type=float, required=True)
    ap.add_argument('--slips', required=True)
    ap.add_argument('--bestlines', default='outputs/bestlines.json')
    ap.add_argument('--corr', required=True)
    ap.add_argument('--slip_stakes', default='outputs/slip_stakes.json')
    ap.add_argument('--config', default='configs/stress.yaml')
    args = ap.parse_args()

    cfg = yaml.safe_load(open(args.config, 'r', encoding='utf-8'))
    sims = int(cfg.get('sims', 20000))
    var_alpha = float(cfg.get('var_alpha', 0.05))
    es_alpha  = float(cfg.get('es_alpha', 0.05))
    spray_var_limit = float(cfg.get('spray_var_limit', 0.03))
    spray_min_factor = float(cfg.get('spray_min_factor', 0.5))
    spray_max_factor = float(cfg.get('spray_max_factor', 1.0))

    bestlines = load_json(args.bestlines) or []
    legmap = map_by_leg(bestlines)
    slips = load_json(args.slips) or []
    slip_stakes = load_json(args.slip_stakes) or []
    slips = attach_stakes_to_slips(slips, slip_stakes)

    paths, mean, sd, per_slip = simulate(slips, legmap, args.corr, sims=sims)
    VaR, ES = var_es(paths, alpha=var_alpha)

    # Spray throttle suggestion: if VaR breaches % of bankroll, scale spray slips
    throttle = 1.0
    if args.bankroll > 0:
        var_ratio = abs(min(VaR, 0)) / args.bankroll
        if var_ratio > spray_var_limit:
            # linear scale down to min factor at 2x breach
            over = min(2.0, var_ratio / spray_var_limit)
            throttle = max(spray_min_factor, spray_max_factor - (over-1.0)*(spray_max_factor - spray_min_factor))

    os.makedirs('outputs', exist_ok=True)
    with open('outputs/stress_summary.json','w',encoding='utf-8') as jf:
        json.dump({
            "sims": sims,
            "mean_pnl": round(mean,2),
            "std_pnl": round(sd,2),
            f"VaR_{int(var_alpha*100)}%": round(VaR,2),
            f"ES_{int(es_alpha*100)}%": round(ES,2),
            "spray_throttle": round(throttle,2)
        }, jf, indent=2)

    # sample of paths
    with open('outputs/stress_paths_sample.csv','w',encoding='utf-8',newline='') as cf:
        w = csv.writer(cf)
        w.writerow(["path_idx","pnl"])
        for i, p in enumerate(paths[:200]):
            w.writerow([i, round(p,2)])

    with open('outputs/stress_per_slip.json','w',encoding='utf-8') as jf:
        json.dump(per_slip, jf, indent=2)

    print(json.dumps({"sims": sims, "out": "outputs/stress_summary.json"}, indent=2))

if __name__ == '__main__':
    main()
