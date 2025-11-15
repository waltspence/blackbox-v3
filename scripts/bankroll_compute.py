#!/usr/bin/env python3
import json, argparse, os, csv
from bankroll.manager import process_legs
from bankroll.rsi import load_rsi_caps

def load_bestlines(path):
    try:
        return json.load(open(path,'r',encoding='utf-8'))
    except Exception:
        return []

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--bankroll', type=float, required=True)
    ap.add_argument('--unit', type=float, required=True)
    ap.add_argument('--kelly_frac', type=float, default=0.5)
    ap.add_argument('--policy', choices=['bank_builder','spray'], default='bank_builder')
    ap.add_argument('--rsi_file', default='configs/rsi_rules.yaml')
    ap.add_argument('--bestlines', default='outputs/bestlines.json')
    args=ap.parse_args()

    rsi_caps, templates_cfg = load_rsi_caps(args.rsi_file)
    bestlines = load_bestlines(args.bestlines)
    if not bestlines:
        print('No bestlines.json found. Run Pack #3 first.')
        return

    stakes = process_legs(bestlines, args.bankroll, args.unit, args.kelly_frac, 'medium', rsi_caps, args.policy, templates_cfg)
    os.makedirs('outputs', exist_ok=True)
    with open('outputs/stakes.json','w',encoding='utf-8') as jf: json.dump(stakes,jf,indent=2)
    with open('outputs/stakes.csv','w',encoding='utf-8', newline='') as cf:
        w=csv.DictWriter(cf, fieldnames=list(stakes[0].keys()))
        w.writeheader(); [w.writerow(r) for r in stakes]
    print(json.dumps({'legs': len(stakes), 'policy': args.policy, 'out': 'outputs/stakes.json'}, indent=2))

if __name__=='__main__':
    main()
