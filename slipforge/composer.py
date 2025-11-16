#!/usr/bin/env python3
import json, argparse, itertools

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--legs', required=True); ap.add_argument('--size', type=int, default=2); ap.add_argument('--max_slips', type=int, default=10); ap.add_argument('--out', default='outputs/slips.json'); args=ap.parse_args()
    legs=json.load(open(args.legs,'r',encoding='utf-8')); ids=[l['leg_id'] for l in legs]
    slips=[]
    for i, combo in enumerate(itertools.combinations(ids, args.size)):
        slips.append({'slip_id': f'S{i+1:03d}', 'legs': list(combo)})
        if len(slips)>=args.max_slips: break
    with open(args.out,'w',encoding='utf-8') as jf: json.dump(slips, jf, indent=2)
    print(json.dumps({'slips': len(slips), 'out': args.out}, indent=2))

if __name__=='__main__':
    main()
