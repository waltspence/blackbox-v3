#!/usr/bin/env python3
import json, argparse

def recompute_bcfi(entry):
    w = 0.4*entry.get('tenure_years',0) + 0.3*entry.get('press_intensity',0) + 0.3*entry.get('subs_aggressiveness',0)
    return round(min(1.0, w/10.0), 3)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--mil_in', required=True); ap.add_argument('--out', default='outputs/mil_bcfi.json'); args=ap.parse_args()
    data=json.load(open(args.mil_in,'r',encoding='utf-8'))
    for d in data: d['bcfi_weight']=recompute_bcfi(d)
    with open(args.out,'w',encoding='utf-8') as jf: json.dump(data, jf, indent=2)
    print(json.dumps({'managers': len(data), 'out': args.out}, indent=2))

if __name__=='__main__':
    main()
