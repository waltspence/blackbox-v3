# Blackbox v2 — Elite Sports Betting Quant System

**Date:** 2025-11-15

Complete production-ready quantitative betting system with 7 integrated packs:

## System Architecture

### Pack #1: PlayerLayer + PropEngine
- Player data schemas (minutes, role, usage, shots/90, xG/90, passes/90)
- Markets: Shots, Shots on Goal (SOG) for soccer and NBA
- VLE (Value-to-Line Efficiency) tagging
- Runnable pricing script (projections → fair odds, EV, VLE)

### Pack #2: LegGraph
- Correlation modeling with Gaussian copula
- Multi-leg dependency analysis
- SGP true probability calculation

### Pack #3: AutoShopper
- Multi-book line shopping
- Best available odds finder
- Book comparison engine

### Pack #4: Bankroll Manager
- Kelly Criterion implementation
- RSI caps and drawdown protection
- Dynamic stake sizing

### Pack #5: SlipKelly
- Correlation-aware slip-level staking
- Multi-leg parlay optimization
- Risk-adjusted position sizing

### Pack #6: Variance & Stress Suite
- Monte Carlo PnL simulation
- VaR (Value at Risk) calculation
- Expected Shortfall (ES) analysis

### Pack #7: CrowdLens (Wisdom of the Crowd)
- Reliability-weighted book consensus
- Continuous Learning Score (CLS) calibration
- Bookmaker credibility ranking
- Training script: `scripts/auto_train_crowdlens.py`

## Quick Start

### 1. Price Props
```bash
python scripts/price_props.py templates/players_example.csv templates/legs_input.csv
```

### 2. Train CrowdLens
```bash
# Put historical CSV files in data/
python3 scripts/auto_train_crowdlens.py \
  --csv data/E0_2024-25.csv data/SP1_2024-25.csv \
  --out_dir outputs \
  --config_out configs/crowd.yaml
```

### 3. Check Outputs
- Priced legs: `outputs/priced_legs.json`, `outputs/priced_legs.csv`
- Trained weights: `configs/crowd.yaml`

## Integration Map

- **MIL → PlayerLayer:** Manager style (tempo/press/subs) + rotation risk
- **SPX → PropEngine:** Match tempo/volatility adjusts attempt rates
- **FairLine:** Fair probability calculation and EV vs book
- **SlipForge:** Canonical leg output with metadata
- **CrowdLens:** Book reliability weights inform consensus priors

## Deployment

### Local
```bash
cd ~/Downloads/blkbx-spaces-v2
./scripts/auto_train_crowdlens.py --csv data/*.csv
```

### Cloud (DigitalOcean App Platform)
```bash
git push origin main
# Connect repo at cloud.digitalocean.com/apps
```

## Directory Structure

```
adapters/     # Book API integrations
bankroll/     # Kelly + RSI bankroll management
configs/      # YAML configs (crowd.yaml, etc.)
core/         # Core odds/probability utilities
crowd/        # CrowdLens wisdom-of-crowd engine
data/         # Historical training data
docs/         # Documentation
engines/      # Correlation + pricing engines
frameworks/   # LegGraph correlation framework
guards/       # Injury/lineup guards
models/       # PropEngine + player models
ops/          # Operations utilities
props/        # Prop pricing logic
schemas/      # Data schemas
scripts/      # Executable scripts
slipforge/    # Slip construction
sliprisk/     # SlipKelly staking
stress/       # Variance + stress testing
templates/    # Input templates
outputs/      # Generated outputs
```

## License

MIT
