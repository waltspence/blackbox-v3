#!/usr/bin/env python3
import argparse, json, os
from adapters.common import load_json_many

def implied_from_american(a):
    return (100.0/(a+100.0)) if a>0 else (abs(a)/(abs(a)+100.0))

def bestline(prices):
    by_id={}
    for r in prices:
        lid=r['leg_id']
        by_id.setdefault(lid,[]).append(r)
    out=[]
    for lid, rows in by_id.items():
        best=max(rows, key=lambda x: x.get('decimal',1.0))
        p=implied_from_american(best['american'])
        out.append({'leg_id':lid,'book':best['book'],'best_american':best['american'],'best_decimal':best['decimal'],'marginal_p':round(p,6),'subject':best.get('subject'),'market':best.get('market'),'line':best.get('line')})
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--inputs', nargs='+', required=True)
    ap.add_argument('--out', default='outputs/bestlines.json')
    args=ap.parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True) if os.path.dirname(args.out) else None
    rows=load_json_many(args.inputs)
    bl=bestline(rows)
    with open(args.out,'w',encoding='utf-8') as f: json.dump(bl,f,indent=2)
    print(f"Wrote {len(bl)} bestlines -> {args.out}")

if __name__=='__main__':
    main()
