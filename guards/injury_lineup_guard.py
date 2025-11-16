#!/usr/bin/env python3
import json, argparse

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--legs', required=True); ap.add_argument('--availability', required=True); ap.add_argument('--out', default='outputs/legs_guarded.json'); args=ap.parse_args()
    legs=json.load(open(args.legs,'r',encoding='utf-8')); avail=json.load(open(args.availability,'r',encoding='utf-8'))
    out=[]
    for L in legs:
        subj=L.get('subject'); st=avail.get(subj,{})
        if st.get('inj')=='out': continue
        if float(st.get('start_prob',1.0)) < 0.5: continue
        out.append(L)
    with open(args.out,'w',encoding='utf-8') as jf: json.dump(out, jf, indent=2)
    print(json.dumps({'in': len(legs), 'out': len(out), 'file': args.out}, indent=2))

if __name__=='__main__':
    main()
