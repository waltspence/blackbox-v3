# Setup — Pack #4

## Per‑leg stakes
python3 scripts/bankroll_compute.py --bankroll 1000 --unit 25 --kelly_frac 0.5 --policy bank_builder --rsi_file configs/rsi_rules.yaml

## Spray template
python3 scripts/bankroll_compute.py --bankroll 1000 --unit 25 --kelly_frac 0.5 --policy spray --rsi_file configs/rsi_rules.yaml
