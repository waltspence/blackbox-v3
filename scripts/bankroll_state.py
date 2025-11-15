#!/usr/bin/env python3
import json, argparse, os, datetime

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--bankroll', type=float, required=True)
    ap.add_argument('--wager_sum', type=float, required=True)
    ap.add_argument('--note', type=str, default='')
    args=ap.parse_args()

    os.makedirs('artifacts', exist_ok=True)
    path='artifacts/bankroll_state.json'
    state={'history': []}
    if os.path.exists(path):
        try:
            state=json.load(open(path,'r',encoding='utf-8'))
        except Exception:
            state={'history': []}

    after = args.bankroll - args.wager_sum
    state['history'].append({'ts': datetime.datetime.utcnow().isoformat()+"Z", 'before': args.bankroll, 'wagered': args.wager_sum, 'after': after, 'note': args.note})
    with open(path,'w',encoding='utf-8') as f: json.dump(state,f,indent=2)
    print(json.dumps({'after_bankroll': after, 'snapshots': len(state['history'])}, indent=2))

if __name__=='__main__':
    main()
