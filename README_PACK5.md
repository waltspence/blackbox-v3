# Pack #5 — SlipKelly v1 (Portfolio Slip Staking w/ Correlation)
Date: 2025-11-15

Slip-level staking using **Kelly on the whole slip**, with covariance awareness via the correlation matrix from Pack #2.
- Consumes: Pack #1 (priced legs), Pack #2 (corr_matrix.json), Pack #3 (bestlines.json), Pack #4 (unit/bankroll policy).
- Optimizes stake per slip given bankroll, risk budget, and RSI caps.
- Handles 2–8 leg slips; falls back to independence if correlation missing.

**Core ideas**
- Joint win probability via Gaussian copula on leg marginals + pairwise ρ.
- Parlay payout uses product of chosen **best-line decimals** per leg.
- Kelly fraction `f = max(0, (p*b - (1-p))/b)` at slip level; then apply risk throttles.
- Portfolio safety: per-player/team exposure caps and total risk budget.

**Outputs**
- `outputs/slip_stakes.json` and `.csv` with per-slip stake and diagnostics.
