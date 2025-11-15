# Setup — Pack #5 (SlipKelly v1)

## 0) Prereqs
- `outputs/bestlines.json` from Pack #3
- `artifacts/corr_matrix.json` from Pack #2

## 1) Run sample (uses templates/slips_example.json)
```bash
python3 scripts/slip_stake.py   --bankroll 1000   --unit 25   --kelly_frac 0.5   --slips templates/slips_example.json   --corr artifacts/corr_matrix.json   --bestlines outputs/bestlines.json   --policy configs/slip_policy.yaml
```

## 2) Inspect
```bash
echo "---- slip_stakes.csv ----"
head -n 10 outputs/slip_stakes.csv
```
