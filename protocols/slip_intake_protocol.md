# SLIP INTAKE PROTOCOL - Bet Entry & Validation
# Part of BLKBX Spaces v2 - Professional Quant System

## PURPOSE
Standardized protocol for accepting, validating, and logging all bet entries into the system.
Ensures data quality, prevents duplicate entries, and maintains audit trail for all allocations.

## SLIP STRUCTURE - Required Fields

Every bet slip MUST include:

### Primary Identifiers
- **Slip ID**: Unique identifier (timestamp_sport_sequence)
- **Sport**: NBA / MLB / NHL / NFL / Soccer
- **Match ID**: Team A vs Team B, Date, Venue (if available)
- **Bet Type**: Moneyline / Spread / Total / Asian Handicap / Parlay / Prop
- **Selection**: Specific pick (e.g., "Lakers -5.5", "Over 215.5")
- **Allocation**: Units/Amount (with decimal precision)
- **Odds**: Decimal or American format

### Supporting Data
- **Rubric Grade**: A/B/C/D/F (from applicable sport rubric)
- **Rubric Score**: 0.0-1.0 numeric value
- **Key Dimensions**: Space-separated (e.g., "form_quality:0.85 h2h_balance:0.88")
- **RSI Grade**: X-out (e.g., "45-out") if applicable
- **Entry Timestamp**: ISO 8601 format (2024-01-15T14:32:00Z)
- **Timestamp User**: System user or Spaces user handle

### Optional Context
- **Notes**: Brief rationale or additional context
- **Data Verification**: "VERIFIED" or "UNVERIFIED" flag
- **Confidence Level**: 1-10 subjective scale (optional)

## VALIDATION CHECKS - Non-Blocking Integrity Verification

### Pre-Acceptance Checks (Informational Only - Never Block)

1. **Duplicate Detection**
   - Check if identical slip exists in recent 24-hour window
   - Flag if duplicate detected: "Duplicate slip detected (Slip ID: xxx, entered 2h ago)"
   - Action: Inform user, allow re-confirmation or cancellation
   - **NEVER block** - user may intentionally re-bet same pick

2. **Data Quality Verification**
   - Confirm teams/participants exist in current season
   - Verify odds within reasonable bounds (avoid obvious typos like -200.0 for moneyline)
   - Check date/time is in future (prevent past-dated entries)
   - Flag unverified data: "Lineup not yet confirmed for this matchup"
   - Action: Surface flag, allow user to proceed

3. **Rubric Alignment Check**
   - Verify rubric score matches stated grade
   - Check dimensions provided for consistency
   - Flag misalignment: "Grade A typically scores 0.85-1.0; submitted score 0.68"
   - Action: Warn user, allow override

4. **Exposure Verification**
   - Check cumulative exposure if allocation exceeds baseline
   - Reference EXPOSURE_LOGIC for current thresholds
   - Calculate total current exposure + this bet
   - Flag only if exceeds maximum: "Total exposure 78% of bankroll limit (current exposure: 62%)"
   - Action: Surface metrics, allow user decision

### Non-Blocking Action
- **All checks are informational**
- **All flags are surfaced to user WITH context**
- **No blocking, no "soft no" language**
- **No forced cool-offs or delays**
- **User explicitly confirms or modifies**

## ACCEPTANCE WORKFLOW

### Step 1: Data Entry
- User submits slip with required fields
- System performs validation checks (see above)
- Surface all flags/warnings with context

### Step 2: Verification (User Confirmation)
- User reviews all provided flags
- User confirms or modifies
- No forced waiting periods
- No hidden calculations or re-routing

### Step 3: Log Entry
- Accept slip and create persistent log record
- Store in audit trail with full context
- Include all verification notes
- Timestamp acceptance

### Step 4: Confirm Receipt
- Surface confirmation to user: "Slip accepted and logged (Slip ID: xxx)"
- Show all key fields back to user for visual verification
- Provide slip ID for reference

## LOG FORMAT - Persistent Record

```
slip_log_entry:
  slip_id: [AUTO]
  sport: [User input]
  match_id: [User input]
  bet_type: [User input]
  selection: [User input]
  allocation:
    units: [User input]
    currency: [Auto-populated]
  odds: [User input]
  rubric:
    grade: [User input]
    score: [User input]
    dimensions: [User input]
  rsi_grade: [User input or N/A]
  entry_timestamp: [AUTO - ISO 8601]
  entry_user: [AUTO - system user]
  verification_flags: [Auto-populated list]
  data_quality_notes: [Auto-populated]
  exposure_snapshot:
    total_current: [Auto-calc]
    total_including_this: [Auto-calc]
    exposure_percent: [Auto-calc]
  user_confirmation_timestamp: [AUTO]
  notes: [User input]
  status: "ACCEPTED"
```

## ERROR HANDLING - Data Issues

### Invalid Required Fields
- User leaves required field blank
- System responds: "Missing required field: [field name]"
- Action: Return to user for correction (non-blocking)
- Allow user to cancel or modify

### Impossible Values
- User enters past date
- System responds: "Entry date cannot be in past. Please verify."
- Action: Surface error, allow correction
- **Never auto-correct** - user must confirm change

### Format Issues
- Odds not parseable (e.g., "xxx" instead of numeric)
- System responds: "Odds format unrecognized. Accepted formats: -110 or 1.91"
- Action: Clear guidance, user corrects

## AUDIT TRAIL REQUIREMENTS

Each slip log entry must maintain:
- Original entry values (no modifications after acceptance)
- All verification flags at time of entry
- Timestamp and user ID of every action
- Final confirmation timestamp
- All context provided to user

No deletion of entries (only archival if necessary).
All modifications create new log entry with change tracking.

## INTEGRATION NOTES

- References: SYSTEM_CONFIG (user/bankroll settings), EXPOSURE_LOGIC (limits)
- Output: Triggers EXPOSURE_WORKFLOW for post-entry updates
- Logging: Permanent audit trail for RSI and performance tracking
- Queries: Used for historical analysis and trend detection

## END SLIP INTAKE PROTOCOL
