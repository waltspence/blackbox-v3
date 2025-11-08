# AUDIT TRAIL FORMAT PROTOCOL

## PURPOSE

Define the permanent audit trail logging format for all system operations. The audit trail serves as an immutable record of all entries, decisions, settlements, and system state changes. Every action is logged with complete context, timestamps, and user decisions for future analysis and accountability.

## AUDIT TRAIL PRINCIPLES

### Immutability
- Once logged, audit trail entries can never be modified or deleted
- Audit trail records are append-only
- Timestamp indicates exact moment of logging
- No retroactive edits or corrections to historical records

### Completeness
- Every significant system action logged
- All user decisions captured
- All calculated values preserved
- All context information included

### Accessibility
- All audit records queryable by date range
- All audit records queryable by slip ID
- All audit records queryable by outcome
- Historical patterns analyzable

## REQUIRED AUDIT FIELDS

### Core Identification
```
slip_id: UUID (unique identifier for this slip/entry)
trail_id: UUID (unique identifier for this audit log entry)
timestamp: ISO 8601 (exact moment action occurred)
action_type: enum (entry, validation, calculation, settlement, query)
```

### Entry Information
```
league: enum (NBA, MLB, NFL, NHL, SOCCER)
market: string (e.g., "moneyline", "spread", "total", "parlay")
bet_amount: decimal (exact amount in currency)
sport_book: string (sportsbook identifier)
```

### User Context
```
user_id: string or UUID (identifies who submitted entry)
user_decision: string (what user decided: accepted/rejected/modified)
user_override: boolean (was system recommendation overridden?)
```

### Validation & Quality Checks
```
integrity_checks: {
  roster_check: boolean (passed/failed)
  injury_check: boolean (passed/failed)
  venue_check: boolean (passed/failed)
  odds_check: boolean (passed/failed)
  staleness_check: boolean (passed/failed)
}
check_summary: string ("all passed" or list of failures)
```

### Risk Metrics at Time of Entry
```
exposure_at_entry: {
  total_exposure: decimal,
  total_exposure_pct: decimal,
  league_exposure: decimal,
  league_exposure_pct: decimal,
  correlated_exposure: decimal,
  correlated_pct: decimal,
  active_capital: decimal
}
risk_flags_at_entry: array (any flags triggered)
```

### System Recommendations at Time of Entry
```
recommendations: [
  {
    recommendation_type: string (e.g., "correlation_alert", "concentration_alert"),
    severity: enum ("info", "warning", "critical"),
    recommendation_text: string (exact recommendation shown to user),
    user_response: enum ("accepted", "overridden", "ignored")
  }
]
```

### Slip Quality Assessment
```
rubric_scores: {
  match_context: decimal (0.0-1.0),
  form_quality: decimal (0.0-1.0),
  h2h_competitive_balance: decimal (0.0-1.0),
  squad_integrity: decimal (0.0-1.0),
  market_efficiency: decimal (0.0-1.0)
},
weighted_rsi: decimal (0.0-100.0),
rsi_grade: enum (A, B, C, D, F)
```

### Settlement Record (Added on Bet Completion)
```
settlement_timestamp: ISO 8601 (when bet result confirmed),
result: enum (WIN, LOSS, PUSH, VOID),
payout_amount: decimal (amount won/lost),
settlement_context: string (brief notes about the bet outcome)
```

### Performance Impact
```
performance_after_settlement: {
  win_loss_record: string (e.g., "5-3"),
  cumulative_pnl: decimal (net profit/loss),
  roi_pct: decimal (return on investment %),
  session_variance: decimal (standard deviation from expected)
}
```

## AUDIT LOG ENTRY STRUCTURE

### Entry on Slip Submission
```json
{
  "slip_id": "slip-20250101-001",
  "trail_id": "trail-001-entry",
  "timestamp": "2025-01-01T14:32:15.842Z",
  "action_type": "entry",
  
  "league": "NBA",
  "market": "moneyline",
  "bet_amount": 100.00,
  "sport_book": "DraftKings",
  
  "user_id": "user-12345",
  "user_decision": "accepted",
  "user_override": false,
  
  "integrity_checks": {
    "roster_check": true,
    "injury_check": true,
    "venue_check": true,
    "odds_check": true,
    "staleness_check": true
  },
  "check_summary": "all passed",
  
  "exposure_at_entry": {
    "total_exposure": 450.00,
    "total_exposure_pct": 22.5,
    "league_exposure": 250.00,
    "league_exposure_pct": 12.5,
    "correlated_exposure": 0.00,
    "correlated_pct": 0.0,
    "active_capital": 2000.00
  },
  "risk_flags_at_entry": [],
  
  "recommendations": [],
  
  "rubric_scores": {
    "match_context": 0.85,
    "form_quality": 0.72,
    "h2h_competitive_balance": 0.68,
    "squad_integrity": 0.90,
    "market_efficiency": 0.79
  },
  "weighted_rsi": 78.5,
  "rsi_grade": "B"
}
```

### Settlement Record Addition
```json
{
  "slip_id": "slip-20250101-001",
  "trail_id": "trail-001-settlement",
  "timestamp": "2025-01-01T22:15:47.293Z",
  "action_type": "settlement",
  
  "result": "WIN",
  "payout_amount": 115.00,
  "settlement_timestamp": "2025-01-01T22:15:47.293Z",
  "settlement_context": "Bet won as submitted",
  
  "performance_after_settlement": {
    "win_loss_record": "6-3",
    "cumulative_pnl": 115.00,
    "roi_pct": 5.75,
    "session_variance": 0.32
  }
}
```

## AUDIT TRAIL QUERIES

The audit trail must support the following query patterns:

### Query Pattern 1: Historical Slip Analysis
**Purpose:** Understand pattern across all entries
```
QUERY: Select all audit records
WHERE: action_type = "entry"
AND: timestamp BETWEEN [date_start] AND [date_end]
RETURN: slip_id, rsi_grade, result, payout_amount
```

**Use Case:** "Show me all bets I made in the last week, their quality grades, and outcomes"

### Query Pattern 2: Performance Analysis
**Purpose:** Understand how quality correlates to outcomes
```
QUERY: Select all audit records
WHERE: action_type = "entry" OR action_type = "settlement"
GROUP BY: rsi_grade
RETURN: rsi_grade, COUNT(entries), win_rate_pct, avg_roi_pct
```

**Use Case:** "How do my A-grade bets perform vs my C-grade bets?"

### Query Pattern 3: Recommendation Impact
**Purpose:** Understand if recommendations correlate to outcomes
```
QUERY: Select all audit records
WHERE: action_type = "entry"
AND: recommendations NOT NULL
GROUP BY: recommendations[0].recommendation_type
RETURN: type, user_override_rate_pct, win_rate_if_accepted, win_rate_if_overridden
```

**Use Case:** "When I ignore exposure recommendations, what happens to my results?"

### Query Pattern 4: Exposure Pattern Analysis
**Purpose:** Understand exposure decision patterns
```
QUERY: Select all audit records
WHERE: action_type = "entry"
ORDER BY: timestamp DESC
RETURN: timestamp, total_exposure_pct, league_exposure_pct, user_decision
```

**Use Case:** "What levels of exposure do I typically accept bets at?"

### Query Pattern 5: Bet Cluster Analysis
**Purpose:** Identify correlated entries
```
QUERY: Select all audit records
WHERE: action_type = "entry"
AND: correlated_pct > 30
GROUP BY: DATE(timestamp)
RETURN: date, count, avg_correlated_pct, outcome_of_cluster
```

**Use Case:** "How often do I take high-correlation bets, and what are the outcomes?"

## INTEGRATION WITH OTHER PROTOCOLS

### Integration with SLIP_INTAKE_PROTOCOL
- Every slip submission logged immediately
- All validation results captured
- User decision captured (accept/reject)
- Exposure state at moment of decision logged

### Integration with INTEGRITY_CHECKS
- All check results logged in audit trail
- Any check failures recorded
- User's response to failed checks recorded

### Integration with EXPOSURE_WORKFLOW
- All exposure calculations logged
- All recommendations surfaced logged
- User's response to recommendations logged
- Exposure state before and after each entry logged

## AUDIT TRAIL RETENTION

**Retention Policy:**
- All entries retained indefinitely
- No archival or deletion
- All records permanently accessible
- Performance queries optimized for date ranges

**Storage Requirements:**
- Audit trail persists across sessions
- Audit trail accessible from any interface
- Historical data never purged
- Backup copies maintained separately

## COMPLIANCE NOTES

- Audit trail is THE source of truth for all historical decisions
- Audit trail enables complete historical replay of system state
- Audit trail allows attribution of all decisions to specific moments
- Audit trail supports variance analysis and pattern recognition
- Audit trail respects user privacy (no PII beyond user_id)
- Audit trail provides non-repudiation (proof actions occurred)

## TECHNICAL SPECIFICATIONS

**Entry Format:**
- JSON format for all entries
- ISO 8601 timestamps with millisecond precision
- Decimal precision for all currency values (never floating point)
- UUIDs for all ID fields
- Enums for categorical fields

**Query Performance:**
- All queries must complete within 5 seconds
- Indexes on: slip_id, timestamp, action_type, league
- Full-text search on: settlement_context, recommendation_text

**Logging Performance:**
- Audit log writes must not block slip entry
- Asynchronous logging acceptable (batch writes)
- Maximum 100ms delay between action and audit entry

**Data Integrity:**
- Checksums on all audit entries for corruption detection
- All writes verified with confirmation
- No partial writes (all-or-nothing semantics)

## AUDIT TRAIL ANALYSIS FRAMEWORK

**Recommended Regular Analysis:**

1. **Weekly Review**
   - Win rate by RSI grade (A-F)
   - Performance vs exposure levels
   - Recommendation acceptance rate

2. **Monthly Review**
   - ROI by league
   - Correlation impact analysis
   - User decision pattern trends

3. **Quarterly Review**
   - Long-term variance analysis
   - Strategy efficacy assessment
   - Recommendation accuracy tracking

4. **Ad-hoc Analysis**
   - Equity drawdown analysis
   - Cluster outcome tracking
   - Recommendation follow-up studies
