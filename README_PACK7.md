# Pack #7 — CrowdLens v1 (Wisdom of the Crowd)
Date: 2025-11-15

Reliability-weighted crowd prior + Bayesian/stacked blend with your model.
Consumes AutoShopper odds & model marginals; produces crowd-adjusted probabilities with confidence/dispersion tags.

Consumes:
- outputs/bestlines.json (Pack #3)
- templates/crowd_sources_sample.csv
- configs/crowd.yaml

Produces:
- outputs/crowd/legs_crowd.json
- outputs/bestlines_crowd.json
- outputs/crowd/legs_crowd.csv
