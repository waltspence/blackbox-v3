# Pack #6 — Variance & Stress Suite v1
Date: 2025-11-15

Monte Carlo **PnL simulation** for a slate of slips using leg-level marginals and the correlation matrix (Pack #2).
Outputs VaR / Expected Shortfall and suggests **Spray Throttle** factors when risk spikes.

**Consumes**
- Pack #2: `artifacts/corr_matrix.json`
- Pack #3: `outputs/bestlines.json`
- Pack #4: `outputs/stakes.json` (per-leg) — optional
- Pack #5: `outputs/slip_stakes.json` (per-slip) and your `slips` file

**Produces**
- `outputs/stress_summary.json` — VaR/ES/mean/std + suggested throttle
- `outputs/stress_paths_sample.csv` — sample of simulated PnL paths
- `outputs/stress_per_slip.json` — win rates & contribution stats
