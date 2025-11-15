# Setup — Pack #6 (Variance & Stress Suite)

## 0) Prereqs
- Run Pack #2–#5 to have corr_matrix, bestlines, and slips (with stakes).

## 1) Quick demo
```bash
python3 scripts/stress_run.py   --bankroll 1000   --slips templates/slips_example.json   --bestlines outputs/bestlines.json   --corr artifacts/corr_matrix.json   --slip_stakes outputs/slip_stakes.json   --config configs/stress.yaml
```

## 2) Inspect
```bash
cat outputs/stress_summary.json
head -n 20 outputs/stress_paths_sample.csv
cat outputs/stress_per_slip.json
```
