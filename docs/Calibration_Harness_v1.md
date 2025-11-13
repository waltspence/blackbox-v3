# Calibration Harness v1 — Metrics & Procedure

## Objective
Measure whether SPX/BCFI outputs are **calibrated** and **actionable** across a full slate.

## Metrics
- **MAE (Totals):** |pred_total - actual_total|
- **Band Accuracy:** % of band calls that land within band (e.g., Under 2.5 hit rate)
- **Brier Score:** mean((p_pred - outcome)^2) for probabilistic bands (e.g., Over 2.5)
- **Calibration Buckets:** group probabilities (0.50–0.60, 0.60–0.70, …) and compare predicted vs observed
- **Anchor Confusion Matrix:** BCFI-driven (TP, FP, TN, FN) for No-Anchor decisions
- **CLV:** Our fair line vs closing book line; average delta across plays

## Procedure
1. **Fixture Lock:** Save pre-kickoff inputs (JSONL) for every match (see templates).
2. **Run SPX + BCFI:** Produce band probabilities + labels.
3. **Score:** Join with final scores; compute metrics via the `metrics_compute.py` skeleton.
4. **One Change Rule:** Adjust at most one coefficient/threshold, then re-test on a different weekend (out-of-sample).

## Files
- `templates/fixtures_lock.jsonl` — one JSON object per match with pre-kick inputs
- `templates/results.csv` — ground truth (final scores)
- `metrics_compute.py` — parses both to compute metrics (to be filled in when data is ready)
