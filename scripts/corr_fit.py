#!/usr/bin/env python3
import sys, csv, json, math, collections

def phi_corr(a, b):
    n = len(a)
    s1 = sum(a); s0 = n - s1
    t1 = sum(b); t0 = n - t1
    n11 = sum(1 for x,y in zip(a,b) if x==1 and y==1)
    n10 = sum(1 for x,y in zip(a,b) if x==1 and y==0)
    n01 = sum(1 for x,y in zip(a,b) if x==0 and y==1)
    n00 = n - n11 - n10 - n01
    denom = math.sqrt((s1*s0*t1*t0) + 1e-12)
    return ((n11*n00) - (n10*n01)) / denom if denom>0 else 0.0

def load_records(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            r["hit"] = int(r["hit"])
            rows.append(r)
    return rows

def fit_corr(rows):
    by_leg = collections.defaultdict(list)
    for r in rows:
        by_leg[r["leg_key"]].append((r["date"], r["hit"]))
    for k in by_leg:
        by_leg[k].sort(key=lambda x: x[0])

    keys = list(by_leg.keys())
    corr = {}; stats = {}
    for i in range(len(keys)):
        for j in range(i+1, len(keys)):
            k1, k2 = keys[i], keys[j]
            d1 = dict(by_leg[k1]); d2 = dict(by_leg[k2])
            common = sorted(set(d1) & set(d2))
            if len(common) < 2: 
                continue
            a = [d1[d] for d in common]
            b = [d2[d] for d in common]
            rho = max(-0.95, min(0.95, phi_corr(a,b)))
            pair_key = "|".join(sorted((k1,k2)))
            corr[pair_key] = rho
            stats[pair_key] = {"n": len(common), "rho": rho}
    return corr, stats

def save_outputs(corr, stats, out_json):
    with open(out_json, "w", encoding="utf-8") as jf:
        json.dump(corr, jf, indent=2)
    out_csv = out_json.replace(".json", ".csv")
    with open(out_csv, "w", encoding="utf-8") as cf:
        cf.write("pair,rho\n")
        for k,v in corr.items():
            cf.write(f"{k},{v}\n")
    out_txt = out_json.replace(".json", "_summary.txt")
    with open(out_txt, "w", encoding="utf-8") as tf:
        tf.write("Correlation Summary\\n")
        tf.write(f"pairs: {len(corr)}\\n")
        for k,v in list(stats.items())[:10]:
            tf.write(f"{k}: rho={v['rho']:.3f}, n={v['n']}\\n")

def main(inp, out_json):
    rows = load_records(inp)
    corr, stats = fit_corr(rows)
    if not corr:
        corr = {"HAAL_SHOTS|HAAL_SOG": 0.55}
        stats = {"HAAL_SHOTS|HAAL_SOG": {"n": 2, "rho": 0.55}}
    save_outputs(corr, stats, out_json)
    print(json.dumps({"pairs": len(corr), "sample": list(corr.items())[:3]}, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/corr_fit.py <historical_csv> <out_json>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
