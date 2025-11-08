# EXPOSURE WORKFLOW PROTOCOL

## PURPOSE

Define the workflow for monitoring, updating, and surfacing exposure metrics to the user. Exposure tracking operates independently of slip acceptance and serves purely as real-time risk transparency. All exposure data is calculated and presented without enforcement mechanisms.

## EXPOSURE TRIGGER EVENTS

Exposure recalculation is triggered by the following events:

### 1. New Slip Entry
- **When:** User submits a valid slip through SLIP_INTAKE_PROTOCOL
- **Action:** System immediately recalculates exposure across all leagues
- **Output:** Updated exposure summary with new position totals
- **Timing:** Synchronous - completes before slip acceptance confirmation

### 2. Bet Settlement
- **When:** Bet result confirmed (Win/Loss/Push/Void)
- **Action:** Remove settled bet from active exposure
- **Action:** Recalculate running totals
- **Output:** Updated exposure showing impact on current position
- **Timing:** Asynchronous - processed within 60 seconds of settlement confirmation

### 3. Loss/Win Event
- **When:** Bet loses or wins
- **Action:** Immediately flag impact magnitude (% of active exposure affected)
- **Action:** Update cumulative performance metrics
- **Output:** Exposure context with performance delta
- **Timing:** Synchronous with settlement

### 4. Manual Query
- **When:** User explicitly requests exposure snapshot
- **Action:** Calculate exposure as of current moment
- **Output:** Complete exposure breakdown by sport/market
- **Timing:** Immediate

## RECALCULATION LOGIC

Exposure is recalculated using the framework defined in EXPOSURE_LOGIC.yaml with the following workflow:

### Step 1: Aggregate Active Bets
```
Active Bets = All non-settled bets in current tracking period
Grouped by: Sport, League, Market, Bet Type
```

### Step 2: Calculate League Exposure
```
League Exposure = Sum(Bet Amount) for each league
League Exposure % = (League Exposure / Current Active Capital) × 100
```

### Step 3: Calculate Market Exposure
```
Market Exposure = Sum(Bet Amount) for each market category
Market Exposure % = (Market Exposure / Current Active Capital) × 100
```

### Step 4: Calculate Correlated Risk
```
Correlated Exposure = Sum(Bet Amount) for correlated events
  - Same game parlay components
  - Same-day multi-game exposures
  - Cross-league correlated outcomes
Correlated % = (Correlated Exposure / Total Exposure) × 100
```

### Step 5: Calculate Drawdown Impact
```
IF recent loss detected:
  Loss Impact = Recent Loss Amount / Previous Session Capital
  Adjusted Capital = Previous Session Capital - Recent Loss Amount
  Exposure % = (Active Exposure / Adjusted Capital) × 100
ELSE:
  Use standard exposure % calculation
```

### Step 6: Surface All Metrics
```
Output: {
  "timestamp": ISO 8601,
  "league_exposure": { [league]: {amount, pct} },
  "market_exposure": { [market]: {amount, pct} },
  "correlated_exposure": {amount, pct, events},
  "total_active_exposure": amount,
  "total_exposure_pct": decimal,
  "active_capital": amount,
  "recent_performance": { [wins, losses, net_pnl] },
  "risk_flags": [ {flag, severity, detail} ]
}
```

## USER NOTIFICATIONS

Exposure information is surfaced through the following channels:

### 1. Post-Slip Confirmation
**When:** Immediately after slip acceptance
**Content:**
```
Exposure Update - [Sport]
Active Exposure: $X (Y% of capital)
League Breakdown:
  - [League A]: $X (Y%)
  - [League B]: $X (Y%)
  - [League C]: $X (Y%)
Correlated Events: X bets
```

**Non-blocking language:** "You now have $X exposure across [leagues]. These are your current positions."

### 2. Real-Time Exposure Dashboard
**Updated:** Every time exposure changes
**Display Elements:**
- League-by-league exposure with percentages
- Market breakdown with percentages
- Correlated exposure identification
- Recent performance summary (win/loss/net)
- Active capital remaining

**Interaction:** User can click any league/market to see detailed breakdown with specific bets

### 3. Post-Settlement Alert
**When:** Bet settles
**Content:**
```
Bet Settled - [Sport]
Result: WIN / LOSS / PUSH
Amount: $X
Updated Exposure:
  Previous: $X (Y%)
  Current: $X (Y%)
  Change: $X delta
```

**Non-blocking language:** "Your exposure changed by $X. You're now at $X total exposure."

### 4. Performance Context Display
**Updated:** After each settlement
**Elements:**
- Win/Loss record for session
- Net PnL (Win amount - Loss amount)
- ROI % on active bets
- Win rate %

**Non-blocking language:** "You're 5-3 today for +$240 net."

## REBALANCING RECOMMENDATIONS

Exposure-based recommendations follow this framework:

### Recommendation Trigger 1: High Correlated Exposure
**Condition:** Correlated % > 40% of total exposure
**Recommendation:**
```
"Your correlated exposure is $X (40% of total). These outcomes are linked.
 Consider reducing exposure in one of: [specific bets listed]
Decision: Yours."
```

**Mechanism:** Recommendation surfaces, user decides to reduce or continue
**Override:** User can accept slip despite recommendation

### Recommendation Trigger 2: League Concentration
**Condition:** Single league > 50% of total exposure
**Recommendation:**
```
"[League] is 50% of your active exposure ($X).
You have opportunities in [other leagues].
Decision: Yours."
```

**Mechanism:** Recommendation surfaces, user decides to diversify or continue
**Override:** User can accept slip despite recommendation

### Recommendation Trigger 3: Post-Loss Context
**Condition:** Recent loss detected + exposure % elevated
**Recommendation:**
```
"You just lost $X. Your current exposure is $Y (Z% of adjusted capital).
You're tracking at [variance context].
Decision: Yours."
```

**Mechanism:** Provides variance context without suggesting pullback
**Override:** User can accept slip despite context
**Critical:** No language suggesting user should "cool off" or "take a break"

### Recommendation Trigger 4: Exposure Threshold Approaching
**Condition:** Total exposure > 75% of safety threshold defined in EXPOSURE_LOGIC
**Recommendation:**
```
"Your exposure is now $X ($Y% of tracked capital).
This is at 75% of your historical ceiling.
Decision: Yours."
```

**Mechanism:** Transparent metric, user decides action
**Override:** User can accept slip despite threshold proximity
**Critical:** No hard limit enforced

## NON-BLOCKING NATURE

All exposure recommendations and alerts follow this protocol:

### What NEVER Happens
- ✗ Slips blocked due to exposure levels
- ✗ Recommendations phrased as requirements ("You should...", "You must...")
- ✗ Emotional language ("Be careful...", "Consider pulling back...")
- ✗ Soft-pedal language ("Maybe you should...", "It might be good to...")
- ✗ Tilt-guard mechanics ("Come back later", "You're running hot")
- ✗ Automatic bet rejection based on streak
- ✗ Messages designed to discourage entry

### What ALWAYS Happens
- ✓ All exposure metrics surfaced transparently
- ✓ Recommendations presented as transparent data
- ✓ User retains 100% control over entry decision
- ✓ Specific numbers provided (never vague thresholds)
- ✓ Context provided (league breakdown, correlation, performance)
- ✓ "Decision: Yours" explicitly stated on recommendations
- ✓ All metrics available for user review

## INTEGRATION WITH OTHER PROTOCOLS

### Integration with SLIP_INTAKE_PROTOCOL
- Exposure calculation happens AFTER slip validation but BEFORE acceptance confirmation
- Exposure data surfaces in acceptance response
- User sees current exposure context when deciding to accept slip
- Rejection of slip due to exposure metrics not supported

### Integration with EXPOSURE_LOGIC.yaml
- All calculations use EXPOSURE_LOGIC thresholds and formulas
- League groupings defined in EXPOSURE_LOGIC respected
- Market categories from EXPOSURE_LOGIC used for breakdown
- Correlated event definitions from EXPOSURE_LOGIC applied

### Integration with Sport Rubrics
- Exposure tracking respects sport-specific market categories
- Rubric scoring does not influence exposure calculations
- Exposure metrics independent of bet quality assessment

### Integration with INTEGRITY_CHECKS
- Integrity check results do not affect exposure calculation
- Exposure surfaced regardless of check status
- Failed checks may surface as risk flag context but do not block exposure display

## EXAMPLE SCENARIOS

### Scenario 1: New NBA Slip Post-Loss
```
Context:
- User just lost $150
- Active exposure: $400
- Capital: $2,000
- New NBA slip: $100

Trigger: New slip entry

System Response:
1. Validate slip (SLIP_INTAKE_PROTOCOL)
2. Calculate new exposure:
   - NBA: $400 → $500
   - Total: $400 → $500 (25% of $2,000)
   - Correlated: Check for same-game components
3. Display to user:
   "Slip Accepted.
   
   Exposure Update - NBA
   Active Exposure: $500 (25% of capital)
   NBA Exposure: $500
   Other Leagues: $0
   
   Session Record: 3W - 4L (-$150)
   
   Your current exposure is $500. Decision: Yours."
4. Continue normal workflow
```

### Scenario 2: High Correlated Exposure
```
Context:
- User has 3 bets in same game parlay
- Combined exposure: $150
- Total active exposure: $200
- New slip submitted: $75 same-game component

Trigger: New slip entry

System Response:
1. Validate slip (SLIP_INTAKE_PROTOCOL)
2. Calculate correlated exposure:
   - Same game components: $225 (45% of $500 total)
3. Display recommendation:
   "Slip Accepted.
   
   Exposure Alert - Correlation
   Your correlated exposure is now $225 (45% of total).
   These outcomes are linked: [Bet 1], [Bet 2], [Bet 3], [Bet 4]
   
   You could reduce exposure in: [specific bets]
   
   Decision: Yours."
4. Continue normal workflow - slip is accepted despite high correlation
```

### Scenario 3: League Concentration
```
Context:
- NBA: $600
- Total exposure: $1,000
- New MLB slip submitted: $100

Trigger: New slip entry

System Response:
1. Validate slip (SLIP_INTAKE_PROTOCOL)
2. Calculate league exposure:
   - NBA: $600 (60% of total)
3. Display to user:
   "Slip Accepted.
   
   Exposure Update
   Active Exposure: $1,100 (55% of capital)
   
   League Breakdown:
   - NBA: $600 (55%)
   - MLB: $500 (45%)
   
   NBA represents 55% of your exposure.
   You have opportunities in other sports.
   
   Decision: Yours."
4. Continue normal workflow
```

### Scenario 4: Settlement Impact
```
Context:
- Active exposure before settlement: $800 (40% of $2,000)
- Bet settles LOSS: -$200
- Active exposure after: $600

Trigger: Bet settlement

System Response:
Display to user:
"Bet Settled - MLB
Result: LOSS
Amount: -$200

Updated Exposure:
Previous: $800 (40% of capital)
Current: $600 (30% of capital)
Change: -$200

Session Record: 5W - 6L (-$200)

Your exposure dropped by $200."
```

## AUDIT TRAIL REQUIREMENTS

All exposure calculations and recommendations must be logged (see AUDIT_TRAIL_FORMAT):

- Timestamp of exposure calculation
- Trigger event (new slip, settlement, etc.)
- Previous exposure state
- New exposure state
- Any recommendations surfaced
- User action (accepted/rejected recommendation if applicable)
- All supporting metrics used in calculation

## TECHNICAL INTEGRATION NOTES

- Exposure calculations must complete within 500ms of trigger event
- Dashboard must update within 1s of metric change
- Recommendation display must not block slip acceptance flow
- All exposure data must be queryable for historical analysis
- Calculations must be deterministic and reproducible
- Performance metrics must be recalculated on every settlement
