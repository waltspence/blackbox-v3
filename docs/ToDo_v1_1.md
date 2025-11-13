# To-Do v1.1 — Implementation Checklist & DoD

## Priority Order (this pack)
1) FairLine v1 — True Implied Odds (**DONE**)
2) SlipForge v1 — Slip Composer (**DONE**)
3) Goalscape v0.1 — Soccer goal bands (**DONE**)
4) LiveOps 2H v0.1 — Halftime reactions (**DONE**)
5) MIL schema v1 — Manager layer w/ examples (**DONE**)
6) No-Anchor Policy v1 — Threshold rules (**DONE**)
7) Availability Guard v0.1 — Injury/lineup (**DONE**)

## Definition of Done (DoD)
- YAML spec created, versioned, and stored.
- Integration notes: where it plugs into TIQT/Blackbox.
- Example records where applicable (MIL).
- No-Anchor policy enforced by SlipForge.
- Unit sanity tests (manual) verifying field parsing.

## Integration Notes
- **FairLine**: wrap as service function; requires odds parser for American/Decimal.
- **SlipForge**: expects candidate legs with p_model & edge_pct; reads guards policies.
- **Goalscape**: feed into SPX or run stand-alone for soccer totals.
- **LiveOps**: triggered from event feed; returns recommendation struct.
- **MIL**: keep fresh; drives SPX tempo modifiers & BCFI MIP component.
- **No-Anchor**: consumed at selection time; logs reasons for forbid.
- **Availability**: run pre-selection; block bad legs early.

## Next Extensions
- Covariance estimator from historical co-movement of legs (reduce parlay overconfidence).
- Automated data ingest to populate MIL/availability without manual entry.
- Calibration harness: MAE/Brier/CLV dashboards per week.
