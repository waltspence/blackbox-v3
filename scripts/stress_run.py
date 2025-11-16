#!/usr/bin/env python3
import argparse, json, os
from stress.monte import simulate, var_es

def jload(p):
    try: return json.load(open(p,'r',encoding='utf-8'))
    except: return None

def map_by_leg(best):
    return {b['leg_id']: b for b in best}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--bankroll', type=float, required=True); ap.add_argument('--slips', required=True); ap.add_argument('--bestlines', default='outputs/bestlines.json'); ap.add_argument('--corr', required=True); ap.add_argument('--slip_stakes', default='outputs/slip_stakes.json'); args=ap.parse_args()
    best=jload(args.bestlines) or []; legs=map_by_leg(best); slips=jload(args.slips) or []; stakes=jload(args.slip_stakes) or []
    byid={s['slip_id']: s for s in stakes}
    for s in slips: s['stake']=float(byid.get(s['slip_id'],{}).get('stake',0.0))
    paths, mean, sd, per_slip = simulate(slips, legs, args.corr, sims=20000)
    VaR, ES = var_es(paths, alpha=0.05)
    os.makedirs('outputs', exist_ok=True)
    with open('outputs/stress_summary.json','w',encoding='utf-8') as jf:
        json.dump({'mean_pnl': round(mean,2),'std_pnl': round(sd,2),'VaR_5%': round(VaR,2),'ES_5%': round(ES,2)}, jf, indent=2)
    with open('outputs/stress_per_slip.json','w',encoding='utf-8') as jf:
        json.dump(per_slip, jf, indent=2)
    print(json.dumps({'out':'outputs/stress_summary.json'}, indent=2))

if __name__=='__main__':
    main()
