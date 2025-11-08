# INTEGRITY CHECKS PROTOCOL - Data Quality Verification
# Part of BLKBX Spaces v2 - Professional Quant System

## PURPOSE
Define data quality checks for sports betting inputs.
All checks are **informational only - never blocking**.
Surface quality concerns to user; all decisions remain with user.

## CHECK CATEGORIES

### 1. ROSTER & PARTICIPATION VERIFICATION

#### Team/Participant Existence
- Verify team/player exists in current season
- Confirm not in IR/inactive list (for solo props)
- Flag unverified or moved teams

Example flags:
- "Team 'Lakers' confirmed in NBA 2024-25 season"
- "Luka Doncic currently active with Dallas Mavericks (unverified status as of last update)"
- "Team status unconfirmed for this date"

#### Lineup Confirmation Status
- Check if lineups are publicly announced
- Note when lineups are TBD/pending
- Surface "typical" lineup vs confirmed

Example flags:
- "✓ Official lineup confirmed (announced 1 hour before match)"
- "? Lineup TBD - coaches often change starting XI at tipoff"
- "✓ Regular starting XI expected based on recent form"

### 2. INJURY & SUSPENSION VERIFICATION

#### Key Player Status
- Confirm reported injuries from official team sources
- Track suspension status from league
- Surface unconfirmed or conflicting reports

Example flags:
- "✓ Squad list updated from official source"
- "Injury report: Player X 'Out' (official)"
- "? Injury status uncertain - conflicting reports from local media"
- "UNCONFIRMED: Last update 4 hours ago"

#### Impact Level
- Identify if absent player is starter/reserve
- Note if replacement available in squad
- Surface tactical impact

Example flags:
- "Starter absence: Quarterback out (backup available with 10+ starts)"
- "Reserve player out (minimal lineup impact expected)"
- "CRITICAL: Starting pitcher and closer both questionable"

### 3. VENUE & COMPETITION VERIFICATION

#### Venue Information
- Confirm stadium/venue exists
- Check if home/away correctly identified
- Note unusual venues (neutral site, outdoor in winter, etc.)

Example flags:
- "✓ Venue confirmed: Staples Center, Los Angeles"
- "Away game at high altitude (Denver, 5,280 ft)"
- "Neutral site venue: NFL Playoffs at agreed location"

#### Competition Tier
- Verify league/tournament level
- Confirm not preseason/friendly/low-tier
- Surface playoff vs regular season

Example flags:
- "✓ Regular season match (Week 10 of 17)"
- "Preseason match (not included in standard analysis)"
- "Playoff qualifier - high stakes"

### 4. ODDS & PRICING VERIFICATION

#### Format Validation
- Confirm odds in expected format (American, Decimal, etc.)
- Check odds within reasonable range
- Flag obvious typos/errors

Example flags:
- "✓ American odds format: -110 (standard)"
- "Decimal odds: 1.91 (equivalent to -110 American)"
- "⚠ Odds -2000 seems extreme for this matchup; verify sportsbook"

#### Line Reasonableness
- Compare to market ranges
- Check for public/sharp action
- Surface unusual line movement

Example flags:
- "✓ Moneyline -140/-140 typical for even matchup"
- "Spread +5.5 appears within normal range vs preseason consensus -4"
- "Line moved 2 points since opening (public money vs closing line)"

### 5. DATA STALENESS VERIFICATION

#### Recency Checks
- Track when data was last updated
- Flag old injury reports
- Surface lineup TBD vs confirmed

Example flags:
- "Data updated: 15 minutes ago (current)"
- "Injury status last updated: 6 hours ago (may be stale)"
- "Lineup confirmation: TBD (expected 1 hour before game)"

## VERIFICATION OUTPUT FORMAT

For each check, output:
```
check_name: [name]
status: [VERIFIED / UNVERIFIED / FLAGGED]
detail: [specific finding]
timestamp: [ISO 8601 when checked]
source: [where data came from]
action: [what user should do]
```

Example:
```
check_name: Roster Verification
status: VERIFIED
detail: Los Angeles Lakers confirmed active in NBA 2024-25 season
timestamp: 2024-01-15T14:32:00Z
source: Official NBA roster
action: No action needed - proceed normally
```

## NON-BLOCKING PROTOCOL

### Critical Principle
- **NO verification check blocks bet entry**
- **NO "soft no" language or friction**
- **All findings surfaced with context**
- **User explicitly confirms or modifies**

### User Interaction Pattern
1. System performs checks
2. Surface all findings with status
3. If any FLAGGED status: explain concern
4. User confirms aware or modifies entry
5. Accept and log

Example interaction:
```
User enters: Moneyline on Team X
Systems checks:
  ✓ Roster verified
  ✓ Venue confirmed
  ? Injury status unconfirmed (last update 8 hours ago)
  ✓ Odds format valid

System output to user:
"One data quality note: Team X injury status last confirmed 8 hours ago.
Recent roster updates may not be reflected. Do you want to proceed?"

User: "Yes, proceed" or "Wait, let me check latest injury news"
```

## INTEGRATION

- **Referenced by**: SLIP_INTAKE_PROTOCOL (validation phase)
- **Input source**: Official team/league sources, sportsbook APIs
- **Output**: Verification flags included in bet slip log
- **Timing**: Checks run at slip entry time, not as blocking gate

## END INTEGRITY CHECKS
