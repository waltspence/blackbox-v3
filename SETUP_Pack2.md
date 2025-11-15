# Setup — Pack #2 (LegGraph v1)

## 1) Fit correlations from the example data
```bash
python3 scripts/corr_fit.py templates/historical_binary_legs.csv artifacts/corr_matrix.json
```

## 2) Demo joint win probability (requires Pack #1 outputs)
```bash
python3 - << 'PY'
import json
from slipforge.corr_adapter import joint_win_prob
# marginals from Pack #1 (fallback if missing)
try:
    legs = json.load(open('outputs/priced_legs.json'))
    L = legs[:2]
    p = [r['p_model'] for r in L]
    keys = [r['leg_id'] for r in L]
except Exception:
    p = [0.58, 0.62]; keys = ["LEG_A","LEG_B"]
C = json.load(open('artifacts/corr_matrix.json'))
n=len(p); R=[[1.0]*n for _ in range(n)]
for i in range(n):
  for j in range(n):
    if i!=j:
      pair="|".join(sorted((keys[i],keys[j])))
      R[i][j]=C.get(pair, 0.0)
jp = joint_win_prob(p, R, mc_samples=10000, seed=123)
print("Marginals:", p)
print("Joint (LegGraph):", round(jp,4), " | Naive:", round(p[0]*p[1],4))
PY
```