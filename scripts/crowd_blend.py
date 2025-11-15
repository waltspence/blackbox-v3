#!/usr/bin/env python3
import csv, json, argparse, os, datetime, yaml
from collections import defaultdict
from scripts._crowd_utils import hb_blend, dispersion

def load_bestlines(path):
    try:
        return json.load(open(path,'r',encoding='utf-8'))
    except Exception:
        return []

def read_crowd_csv(path):
    buckets = defaultdict(list)
    with open(path,'r',encoding='utf-8') as f:
        for r in csv.DictReader(f):
            try:
                leg_id = r['leg_id']
                src = (r.get('src') or '').strip()
                kind = (r.get('kind') or 'book').strip()
                p = float(r['p'])
                liq = float(r.get('liquidity') or 0.0)
                buckets[leg_id].append({'src':src,'kind':kind,'p':p,'liquidity':liq})
            except Exception:
                continue
    return buckets

def reliability_weight(row, cfg):
    kind = row.get('kind','book')
    base = 0.0
    if kind=='book': base = float(cfg['weights'].get('book_base',0.25))
    elif kind=='exchange':
        base = float(cfg['weights'].get('exchange_base',0.40))
        base += float(cfg['weights'].get('liq_scale',0.0)) * float(row.get('liquidity',0.0))
    elif kind=='tipster': base = float(cfg['weights'].get('tipster_base',0.20))
    elif kind=='public': base = float(cfg['weights'].get('public_base',0.10))
    return max(0.0, base)

def weighted_mean(ps, ws):
    s = sum(ws)
    if s<=0: return None
    return sum(p*w for p,w in zip(ps,ws))/s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bestlines', required=True)
    ap.add_argument('--crowd_csv', required=True)
    ap.add_argument('--config', default='configs/crowd.yaml')
    args = ap.parse_args()

    cfg = yaml.safe_load(open(args.config,'r',encoding='utf-8'))
    blend_mode = (cfg.get('blend',{}) or {}).get('mode','HB').upper()
    shrink_floor = float((cfg.get('blend',{}) or {}).get('shrink_floor',0.15))
    shrink_ceiling = float((cfg.get('blend',{}) or {}).get('shrink_ceiling',0.65))

    bestlines = load_bestlines(args.bestlines)
    by_leg = {b['leg_id']: b for b in bestlines}

    crowd = read_crowd_csv(args.crowd_csv)

    out = []
    now = datetime.datetime.utcnow().isoformat()+'Z'
    for leg_id, model_row in by_leg.items():
        p0 = float(model_row.get('marginal_p', 0.5))
        rows = crowd.get(leg_id, [])
        if len(rows) < int(cfg['guards'].get('min_sources',2)):
            out.append({
                'leg_id': leg_id,
                'p_model': p0,
                'p_crowd_mean': p0,
                'p_crowd_post': p0,
                'crowd_conf': 0.0,
                'dispersion': 0.0,
                'sources': [],
                'flags': ['LowCoverage'],
                'updated_at': now
            })
            continue
        ps = [r['p'] for r in rows]
        ws = [reliability_weight(r, cfg) for r in rows]
        mean = weighted_mean(ps, ws)
        if mean is None:
            mean = sum(ps)/len(ps)
        disp = dispersion(ps)
        mass = sum(ws)
        crowd_conf = max(0.0, min(1.0, (mass / (mass + 3.0)) * (1.0 - min(disp,0.5)*1.5)))

        if blend_mode == 'MEAN':
            alpha = max(shrink_floor, min(shrink_ceiling, crowd_conf))
            p_star = (1.0 - alpha) * p0 + alpha * mean
        else:
            sigma_model = max(0.4, 1.2*(0.5 - abs(0.5 - p0)))
            sigma_crowd = max(0.3, 2.0*disp + (0.8 - 0.6*crowd_conf))
            hb = hb_blend(p0, mean, sigma_model=sigma_model, sigma_crowd=sigma_crowd)
            alpha = max(shrink_floor, min(shrink_ceiling, crowd_conf))
            p_star = (1.0 - alpha) * p0 + alpha * hb

        out.append({
            'leg_id': leg_id,
            'p_model': round(p0,4),
            'p_crowd_mean': round(mean,4),
            'p_crowd_post': round(p_star,4),
            'crowd_conf': round(crowd_conf,4),
            'dispersion': round(disp,4),
            'sources': rows,
            'flags': (['LowDispersion'] if disp<0.03 else []) + (['HighDispersion'] if disp>0.12 else []),
            'updated_at': now
        })

    os.makedirs('outputs/crowd', exist_ok=True)
    with open('outputs/crowd/legs_crowd.json','w',encoding='utf-8') as jf:
        json.dump(out, jf, indent=2)

    with open('outputs/crowd/legs_crowd.csv','w',encoding='utf-8',newline='') as cf:
        w = csv.DictWriter(cf, fieldnames=['leg_id','p_model','p_crowd_mean','p_crowd_post','crowd_conf','dispersion','updated_at'])
        w.writeheader()
        for r in out:
            w.writerow({k:r[k] for k in w.fieldnames})

    merged = []
    for b in bestlines:
        leg_id = b.get('leg_id')
        k = next((r for r in out if r['leg_id']==leg_id), None)
        if k:
            b2 = dict(b)
            b2['p_crowd_mean'] = k['p_crowd_mean']
            b2['p_crowd_post'] = k['p_crowd_post']
            b2['crowd_conf'] = k['crowd_conf']
            b2['dispersion'] = k['dispersion']
            merged.append(b2)
        else:
            merged.append(b)
    with open('outputs/bestlines_crowd.json','w',encoding='utf-8') as jf:
        json.dump(merged, jf, indent=2)

    print(json.dumps({'legs': len(out), 'out': 'outputs/crowd/legs_crowd.json'}, indent=2))

if __name__ == '__main__':
    main()
