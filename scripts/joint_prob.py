#!/usr/bin/env python3
import argparse, json
from leggraph.copula import joint_binary_samples

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--marginals', required=True); ap.add_argument('--corr_json', required=True); ap.add_argument('--leg_keys', required=True); ap.add_argument('--samples', type=int, default=20000); ap.add_argument('--out', default='outputs/joint_prob.json'); args=ap.parse_args()
    marg=json.load(open(args.marginals,'r',encoding='utf-8'))
    keys=json.load(open(args.leg_keys,'r',encoding='utf-8'))
    C=json.load(open(args.corr_json,'r',encoding='utf-8'))
    n=len(keys); R=[[1.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            k='|'.join(sorted((keys[i],keys[j]))); rho=float(C.get(k,0.0)); rho=max(-0.95,min(0.95,rho)); R[i][j]=R[j][i]=rho
    S=joint_binary_samples(marg,R,samples=args.samples,seed=23)
    wins=sum(1 for row in S if all(row)); p=wins/len(S) if S else 0.0
    with open(args.out,'w',encoding='utf-8') as f: json.dump({'joint_p': round(p,6), 'samples': len(S)}, f, indent=2)
    print(json.dumps({'joint_p': round(p,6), 'samples': len(S), 'out': args.out}, indent=2))

if __name__=='__main__':
    main()
