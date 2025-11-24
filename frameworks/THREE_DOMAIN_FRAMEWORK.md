# THREE DOMAIN FRAMEWORK

## BlackBox v2 Architecture

The BlackBox v2 system is organized into three core domains that handle the complete sports betting workflow from market analysis to execution.

---

## Domain 1: Market Intelligence (Pricing & Odds)

**Purpose:** Determine true probability and fair value across markets

### Core Components:

#### FairLine v1
- **Function:** True odds engine
- **Input:** Raw market data, historical results, model outputs
- **Output:** Fair odds/probabilities for all markets (ML, spreads, totals, props)
- **Integration:** Feeds SPX, PropEngine, AutoShopper

#### PropEngine v1
- **Function:** Player-level prop bet pricing
- **Markets:** Shots, SOG (Shots on Goal), points, rebounds, assists
- **Features:**
  - VLE (Value-to-Line Efficiency) tagging
  - Player usage rates, minutes, role analysis
  - Integration with MIL (Manager Identity Layer) for lineup context
- **Output:** Fair props odds → FairLine

#### AutoShopper v1
- **Function:** Multi-book line shopping and aggregation
- **Input:** Normalized price data from multiple sportsbooks (JSON/CSV)
- **Process:** 
  - Adapter layer converts book-specific formats
  - Aggregates best available odds per leg
  - Tags VLE opportunities
- **Output:** `bestlines.json` → SlipForge

#### CrowdLens v1
- **Function:** Wisdom-of-crowd market calibration
- **Process:**
  - Ingests opening odds from multiple books
  - Calculates `p_crowd` (weighted consensus probability)
  - Compares vs closing line (CLS proxy)
  - Optimizes book weights via CLS calibration
  - ROI strategy: bet when line movement favors position
- **Output:** `configs/crowd.yaml` (trained weights) → FairLine
- **Training:** `scripts/auto_train_crowdlens.py`

---

## Domain 2: Statistical Modeling & Analysis

**Purpose:** Generate predictions, correlations, and model outputs

### Core Components:

#### SPX v1 (Score Prediction Exchange)
- **Function:** Match score prediction engine
- **Input:** Team stats, xG data, MIL manager context, recent form
- **Output:** Score projections (HT/FT), goal distributions
- **Integration:** Feeds FairLine for ML/totals/spreads pricing

#### BCFI v0.2 (Big Club Fade Index)
- **Function:** Public bias detection for marquee teams
- **Factors:**
  - Brand premium in odds
  - Public betting percentages
  - Historical overvaluation patterns
  - Manager tenure/pressure (from MIL)
- **Output:** Fade weights → FairLine adjustments

#### MIL Protocol (Manager Identity Layer)
- **Function:** Manager-specific context and impact
- **Data Scope:**
  - **Tier 1:** Manager name, tenure, L5 results, position, key injuries
  - **Tier 2:** Tactical system, home/away splits, xG trends, press intensity, subs aggressiveness
- **Update Frequency:** Monday 9 AM EST (primary) + Friday 9 AM EST (secondary)
- **Integration:** 
  - Feeds BCFI for recalculation
  - Informs SPX predictions
  - Guards PropEngine (lineup/injury status)
- **Output:** `mil/*.yaml` → BCFI, SPX, PropEngine

#### LegGraph v1
- **Function:** Correlation modeling and parlay joint probability
- **Method:** Gaussian copula (Cholesky decomposition + probit)
- **Process:**
  - Fit pairwise phi correlations from historical binary outcomes
  - Generate correlation matrix
  - Monte Carlo sampling for slip joint probability
- **Scripts:**
  - `scripts/corr_fit.py` (historical data → correlation matrix)
  - `scripts/joint_prob.py` (marginals + correlation → joint prob)
- **Output:** `artifacts/corr_matrix.json`, `outputs/joint_prob.json` → SlipForge, SlipKelly

---

## Domain 3: Execution & Risk Management

**Purpose:** Convert analysis into actionable bets with proper sizing and risk controls

### Core Components:

#### SlipForge v1
- **Function:** Bet slip composition and construction
- **Input:** `bestlines.json` (from AutoShopper), slip size constraints
- **Process:**
  - Composes single bets and parlays from available legs
  - Applies guards (injury/lineup filters)
  - Tags each slip with market type, combined odds
- **Output:** `outputs/slips.json` → SlipKelly, Stress/Variance

#### Guards (Injury/Lineup)
- **Function:** Pre-bet safety filters
- **Checks:**
  - Player availability (injury status, start probability)
  - Lineup confirmation
  - Manager tactical changes
- **Integration:** Filters legs before SlipForge composition
- **Script:** `guards/injury_lineup_guard.py`

#### SlipKelly v1
- **Function:** Kelly Criterion position sizing
- **Input:** 
  - Bankroll size
  - Joint probability (from LegGraph)
  - Best available odds (from AutoShopper)
  - Kelly fraction (typically 0.25-0.5 for fractional Kelly)
- **Process:**
  - Calculates edge per slip: `edge = (joint_p * decimal_odds) - 1`
  - Computes Kelly stake: `f = edge / (decimal_odds - 1)`
  - Applies fractional Kelly multiplier for risk management
- **Output:** `outputs/slip_stakes.json` (slip + stake size)
- **Script:** `scripts/slip_stake.py`

#### Variance/Stress Module v1
- **Function:** Portfolio risk analysis and VaR calculation
- **Method:** Monte Carlo simulation
- **Process:**
  - Simulates portfolio outcomes using correlation matrix
  - Calculates Value at Risk (VaR) and Expected Shortfall (ES)
  - Applies "Spray Slip" throttle rule (max exposure constraints)
- **Output:** `outputs/stress_summary.json` (VaR, ES, portfolio metrics)
- **Scripts:**
  - `stress/monte.py` (simulation engine)
  - `scripts/stress_run.py` (runner + report)

#### RSI/Bankroll v1
- **Function:** Bankroll management and bet ledger
- **Features:**
  - Unit sizing with caps
  - CLV (Closing Line Value) capture tracking
  - Session limits and throttles
  - Drawdown protection
- **Output:** Ledger entries, bankroll updates

---

## Data Flow Overview

```
[Market Data] → FairLine v1 → [Fair Odds]
                    ↓
[Player Data] → PropEngine v1 → FairLine
                    ↓
[Historical] → CrowdLens v1 → [Calibrated Weights] → FairLine
                    ↓
[Team Stats] → SPX v1 → [Score Predictions] → FairLine
                    ↓
[Manager Data] → MIL Protocol → [Context] → SPX, BCFI, PropEngine
                    ↓
[Multi-Book Prices] → AutoShopper v1 → [Best Lines]
                    ↓
[Best Lines] + [Fair Odds] → SlipForge v1 → [Slips]
                    ↓
[Historical Legs] → LegGraph v1 → [Correlations + Joint Prob]
                    ↓
[Slips] + [Joint Prob] + [Bankroll] → SlipKelly v1 → [Sized Bets]
                    ↓
[Sized Bets] + [Correlations] → Stress/Variance → [Risk Metrics]
                    ↓
               [Execution]
```

---

## Integration Points

### Primary Workflows:

1. **Pre-Match Workflow:**
   - MIL update (Mon/Fri 9 AM EST)
   - SPX generates predictions
   - FairLine computes fair odds
   - AutoShopper finds best lines
   - SlipForge composes slips
   - LegGraph calculates joint probabilities
   - SlipKelly sizes bets
   - Stress module validates portfolio

2. **Live/In-Play Workflow:**
   - Real-time odds monitoring
   - LiveOps 2H (halftime recalibration)
   - Dynamic FairLine updates
   - Rapid execution via AutoShopper

3. **Post-Match Workflow:**
   - Result ingestion
   - CLV calculation
   - Correlation matrix updates
   - CrowdLens retraining
   - BCFI recalibration

---

## Directory Structure

```
blkbx-spaces-v2/
├── adapters/          # Book-specific price adapters
├── artifacts/         # Generated data (correlations, matrices)
├── configs/           # YAML configurations (crowd.yaml, etc.)
├── data/              # Raw input data (CSVs, JSONs)
├── frameworks/        # Architecture docs (this file)
├── guards/            # Pre-bet safety filters
├── leggraph/          # Correlation & copula modules
├── mil/               # Manager Identity Layer
├── models/            # Trained models and artifacts
├── outputs/           # Generated outputs (slips, stakes, reports)
├── players/           # Player-level data and schemas
├── props/             # Prop bet engine
├── schemas/           # JSON schemas for data validation
├── scripts/           # Runnable CLI scripts
├── slipforge/         # Slip composition engine
├── sliprisk/          # Kelly & portfolio modules
├── stress/            # Monte Carlo & VaR modules
└── templates/         # Historical data templates
```

---

## Key Scripts Reference

### Domain 1 (Market Intelligence)
- `scripts/bestline_shop.py` - Multi-book line shopping
- `scripts/auto_train_crowdlens.py` - CLS-calibrated crowd weights

### Domain 2 (Statistical Modeling)
- `scripts/corr_fit.py` - Fit correlation matrix from historical legs
- `scripts/joint_prob.py` - Calculate parlay joint probability

### Domain 3 (Execution & Risk)
- `scripts/slip_stake.py` - Kelly sizing for slips
- `scripts/stress_run.py` - Portfolio Monte Carlo & VaR
- `guards/injury_lineup_guard.py` - Pre-bet safety checks

---

## Deployment Status

**Production-Ready Modules:**
- ✅ FairLine v1
- ✅ SPX v1
- ✅ AutoShopper v1
- ✅ CrowdLens v1 (with auto-trainer)
- ✅ LegGraph v1 (Gaussian copula)
- ✅ SlipForge v1
- ✅ SlipKelly v1
- ✅ Variance/Stress v1
- ✅ MIL Protocol v1
- ✅ BCFI v0.2
- ✅ Guards (injury/lineup)

**Next Priority Additions:**
1. PropEngine v1 expansion (more markets)
2. LiveOps 2H automation
3. Advanced player analytics
4. Automated execution pipeline

---

## Version History

- **v1.0** (Nov 2025) - Initial THREE DOMAIN framework
- Complete separation of market intelligence, statistical modeling, and execution
- Production deployment of all core modules
- Gaussian copula implementation for correlations
- CLS-calibrated crowd consensus weighting

---

*Last Updated: November 24, 2025*
*Author: Walt Spence*
*Repository: https://github.com/waltspence/blkbx-spaces-v2*
