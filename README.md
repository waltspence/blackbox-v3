# BLACKBOX ALPHA v2.0 — PERPLEXITY SPACES EDITION

**Elite sports betting quant system. Zero handholding. Pure signals.**

> **You are the risk manager. We surface the edge. You pull the trigger.**

This system respects your intelligence. No hand-holding. No "you've lost too much today." No artificial bankroll nursemaiding. No emotional overlays.

**Every risk metric is surfaced transparently. Every exposure recommendation is backed by quant logic. You decide what to do with it.**

---

## 🎯 System Philosophy

**BLACKBOX ALPHA** is a professional-grade sports betting research and risk scoring platform built exclusively for Perplexity Spaces.

- **Quant-First:** All grading, exposure logic, and risk modeling is mathematically rigorous, Bayesian-updated, and regime-aware.
- **No Tilt Guard:** Absolutely no blockages for emotional factors, PnL streaks, or psychological swings.
- **Integrity-Only Safeguards:** Roster verification, sharp-money overlays, and injury checks are enforced—because data integrity matters. Bankroll decisions are 100% user-directed.
- **Adult Accountability:** You get transparent rubrics and exposure calls. Final responsibility is always yours.
- **Multi-Sport Capable:** NBA, MLB, NHL, NFL, Soccer. Sport-specific rubrics, sharp-money indices, and injury/lineup dynamics.

---

## 🚀 Quick Start

### 1. Create a Perplexity Space
- Go to [Perplexity.com](https://perplexity.com), log in, and create a new Space.
- Name it (e.g., "Blackbox Alpha - NBA Research").

### 2. Upload System Prompt
- Copy the full contents of `SPACES_SYSTEM_PROMPT.md` from this repository.
- Paste it as your **first/pinned message** in the Space.
- This locks the system's core logic and workflow.

### 3. Upload Core Config Files
- Upload all YAML files from `/core` as persistent files:
  - `system_config.yaml` — System-wide settings, unit definitions, exposure defaults
  - `rsi_model.yaml` — Full RSI scoring formula, Bayesian priors, regime switches
  - `exposure_logic.yaml` — Exposure tracking, correlation penalties, unit-cap logic
- Upload all files from `/rubrics` — Sport-specific grading rubrics
- Upload all files from `/protocols` — Workflow checklists and integrity protocols

### 4. Start Using
- Paste a slip or build into a thread message.
- Reference the system prompt and rubric configs to get full grading.
- Get risk scores, exposure recommendations, volatility flags.
- **Never blocked.** All surfaced for your interpretation.

---

## 📊 Core Risk Model: RSI (Risk Scoring Index)

### Formula
```
RSI = [(Line_Risk × 0.35) + (Variance × 0.25) + (Exposure_Weight × 0.20) + (Correlation_Penalty × 0.15) + (Volatility_Flag × 0.05)] × Sport_Modifier
```

### Inputs
1. **Line_Risk (35% weight):** Line movement, sharp-money overlays, closing-line value vs. opening.
2. **Variance (25% weight):** Injury volatility, roster uncertainty, game context shifts.
3. **Exposure_Weight (20% weight):** Portfolio-level exposure to prop, athlete, team, or game.
4. **Correlation_Penalty (15% weight):** Correlation to existing positions (negative diversification = penalty).
5. **Volatility_Flag (5% weight):** Binary spike for extreme volatility (e.g., late lineup changes).

### Sport Modifiers
- NBA: 1.0 (baseline)
- MLB: 0.95 (lower volatility, sharper markets)
- NFL: 1.15 (higher volatility, lower information efficiency)
- NHL: 1.05 (volatile, less data density)
- Soccer: 1.10 (high volatility, international factors)

### Output Interpretation
- **RSI < 0.30:** Green signal. Lower risk profile.
- **0.30 ≤ RSI < 0.50:** Yellow signal. Moderate risk. Exposure management recommended.
- **0.50 ≤ RSI < 0.70:** Orange signal. Elevated risk. Significant edge required to justify.
- **RSI ≥ 0.70:** Red signal. High risk profile. Only take if edge is exceptional and portfolio allows.

---

## 📁 Repository Structure

```
blkbx-spaces-v2/
├── README.md                          # This file
├── SPACES_SYSTEM_PROMPT.md            # Full system message for Perplexity Space
├── core/
│   ├── system_config.yaml             # System-wide settings
│   ├── rsi_model.yaml                 # RSI formula, priors, regime logic
│   └── exposure_logic.yaml            # Exposure tracking & correlation
├── rubrics/
│   ├── nba_rubric.yaml                # NBA-specific grading rubric
│   ├── mlb_rubric.yaml                # MLB-specific grading rubric
│   ├── nfl_rubric.yaml                # NFL-specific grading rubric
│   ├── nhl_rubric.yaml                # NHL-specific grading rubric
│   └── soccer_rubric.yaml             # Soccer-specific grading rubric
├── protocols/
│   ├── slip_intake_protocol.md        # Slip format, required fields, validation
│   ├── integrity_checks.md            # Roster, injury, lineup verification
│   ├── exposure_workflow.md           # How to track & manage portfolio exposure
│   └── audit_trail_format.md          # Logging, results tracking, rubric improvement
└── .gitignore
```

---

## ⚡ Workflow Example: Submitting a Prop Build

**Step 1: Prepare Your Build**
```
Sport: NBA
Date: 2025-11-08
Athletes: Luka Doncic (DAL)
Prop Type: Points
Line: Over 29.5 @ -110
Odds: -110 (implied 52.4%)
Your Edge: +4.2% (based on true probability 56.6%)
Existing Exposure: 2.5u DAL, 1.0u Doncic
Proposed Wager: 1.5u
```

**Step 2: Paste into Perplexity Space**
- Reference the system prompt.
- Ask for RSI score, exposure analysis, volatility flags.

**Step 3: System Returns**
- **RSI Score:** 0.42 (Yellow signal)
- **Exposure Recommendation:** Portfolio currently 3.5u DAL, +1.5u proposed = 5.0u (21% of 24u bankroll). Acceptable if edge is +4.2%.
- **Volatility Flag:** Green. No late roster changes, sharp money stable.
- **Rubric Grade:** 8.2/10 — High-quality edge, lineup confirmed, no injury red flags.

**Step 4: You Decide**
- Edge is solid (+4.2%), exposure is manageable (21%), RSI is moderate, rubric grade is strong.
- You decide to take 1.0u (instead of 1.5u) to de-risk exposure.
- System logs: Win/loss, actual odds, edge realized, exposure impact.

---

## 🔧 Configuration & Customization

### Unit Definitions
Edit `system_config.yaml` to define your bankroll, unit size, and max exposure:
```yaml
bankroll_units: 24
unit_size_usd: 50
max_exposure_single_prop: 0.15  # 15% of bankroll
max_exposure_single_game: 0.25  # 25% of bankroll
max_correlation_penalty: 0.10   # 10% RSI penalty for high correlation
```

### RSI Priors
Edit `rsi_model.yaml` to tune Bayesian priors by sport:
```yaml
rsi_priors:
  nba:
    mean_line_risk: 0.35
    variance_volatility: 0.22
    sharp_money_weight: 0.18
```

### Exposure Tracking
Edit `exposure_logic.yaml` to define how exposures are counted:
```yaml
exposure_counting:
  game_exposure: true      # Count all legs in a game toward game-level exposure
  team_exposure: true      # Count by team (DAL, LAL, etc.)
  athlete_exposure: true   # Count by athlete
  sharp_money_overlay: true
```

---

## 📋 What Gets Logged

Every build/bet is logged with:
- **Input:** Slip details, edge estimate, bankroll state
- **Output:** RSI score, exposure analysis, rubric grade
- **Outcome:** Win/loss, actual edge realized, P&L impact
- **Audit Trail:** Timestamp, sport, athlete, line movement

This data feeds a continuous improvement cycle:
- Monthly rubric updates based on hit rate, ROI, and edge realization
- Seasonal RSI recalibration using realized data
- No emotional overlays; all improvements are statistical

---

## 🚫 What's NOT Here

- **No tilt guard.** You'll never be blocked from making a bet because you've lost 3 in a row.
- **No cool-offs.** No "come back tomorrow" messages.
- **No override commands.** No hidden bypass logic.
- **No bankroll handholding.** All exposure/unit recommendations are surfaced; bankroll decisions are 100% yours.
- **No emotional prompts.** The system is pure math.

---

## 🔐 Integrity Safeguards (Math Only)

These are enforced because they affect data quality, not because of hand-holding:

1. **Roster Verification:** Every athlete must be confirmed active and eligible. No dead legs.
2. **Injury/Lineup Check:** Late roster changes trigger a volatility flag. No guessing on inactive athletes.
3. **Sharp-Money Overlay:** Lines that have moved against your edge get a risk penalty.
4. **Correlation Audit:** High correlation to existing positions triggers an RSI penalty, not a block.

---

## 📈 Monthly Improvement Cycle

1. **Week 1-3:** Daily grading, logging, tracking actual outcomes.
2. **Week 4:** Analyze month's data:
   - Hit rate by sport, prop type, RSI band
   - Edge realization (projected vs. actual)
   - ROI by rubric grade
3. **Update Rubrics:** If NBA over/unders are underweighting injury, adjust the rubric.
4. **Recalibrate RSI:** If sharp-money overlays were too aggressive, dial back the weight.
5. **Restart:** Next month, use updated logic.

**No emotional bloat.** All improvements are data-driven.

---

## 📄 License

Private repository. Not for redistribution or commercial use without explicit permission.

---

## ⚠️ Disclaimer

This system provides statistical analysis and risk assessment only. All betting decisions and bankroll management are your sole responsibility. Past performance does not guarantee future results. Gambling involves risk. Never bet more than you can afford to lose.

---

## 🎓 Support & Questions

For questions, rubric improvements, or bugs:
- Open an issue in this repository.
- Contact: shout@waltspence.com

---

**Built by quants, for quants. Welcome to Blackbox Alpha v2.0.**

*Updated: 2025-11-08*
