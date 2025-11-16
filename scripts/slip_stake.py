#!/usr/bin/env python3
import argparse, json, os
from sliprisk.portfolio import stake_for_slip

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--bankroll', type=float, required=True); ap.add_argument('--kelly_frac', type=float, default=0.5); ap.add_argument('--unit_cap', type=float, default=None); ap.add_argument('--slips', required=True); ap.add_argument('--bestlines', required=True); ap.add_argument('--out', default='outputs/slip_stakes.json'); args=ap.parse_args()
    slips=json.load(open(args.slips,'r',encoding='utf-8')); best=json.load(open(args.bestlines,'r',encoding='utf-8')); by_leg={b['leg_id']: b for b in best}
    out=[]
    for s in slips:
        legs=[by_leg[lid] for lid in s['legs'] if lid in by_leg]
        p_joint=float(s.get('joint_p',0.0))
        stake=stake_for_slip(legs, args.bankroll, kelly_frac=args.kelly_frac, p_joint=p_joint, unit_cap=args.unit_cap)
        out.append({'slip_id': s['slip_id'], 'stake': stake, 'joint_p': p_joint, 'legs': s['legs']})
    os.makedirs(os.path.dirname(args.out), exist_ok=True) if os.path.dirname(args.out) else None
    with open(args.out,'w',encoding='utf-8') as jf: json.dump(out, jf, indent=2)
    print(json.dumps({'slips': len(out), 'out': args.out}, indent=2))

if __name__=='__main__':
    main()
