# System Architecture

## Overview

BlackBox v3 abandons the monolithic "Black Box" AI approach. Instead of feeding features into a single Neural Network, we decouple the prediction process into interpretable layers.

This allows the system to explain *why* a bet is valuable (e.g., "Market overreacting to injury news" vs "Fundamental mismatch").

## 1. The Three-Domain Pipeline

### Data Flow

`Raw Data (API)` → `GameStory (Context)` → `Domain Engine (Math)` → `Firestore (Storage)` → `Discord (User)`

### Domain Breakdown

#### Domain I: Fundamental Skill (Base Probability)

* **Input:** Historical xG, squad value, ELO ratings.
* **Operation:** Logistic Regression / Power Rating delta.
* **Output:** `Base_Prob` (e.g., Home Win 55%).

#### Domain II: Context Layer (The Adjustment)

* **Input:** Standings, Injuries, Form, Motivation (Must-Win/Dead-Rubber).
* **Operation:** Additive adjustments to skill rating.
* **Output:** `Skill_Adjustment` (e.g., -0.05 due to injuries).

#### Domain III: Variance (The Distribution)

* **Input:** Derby status, Weather, Playstyle matchup.
* **Operation:** Widening/Narrowing of the probability distribution (Sigma adjustment).
* **Output:** `Variance_Boost` (Used for Kelly Criterion sizing).

---

## 2. Infrastructure & Persistence

### Discord Bot (Interface)

Acts as a thin client. It holds no state. It parses user commands, invokes the Python pipeline, and renders Rich Embeds based on the returned data.

### Google Firestore (Database Schema)

The database is NoSQL, document-based.

#### Collection: `matches`

The source of truth for analytical data.

```json
{
  "match_id": "EPL_2025_GW10_ARS_LIV",
  "status": "analyzed",
  "pipeline_metrics": {
    "final_prob_home": 0.62,
    "fair_odds_home": 1.61,
    "edge": 0.05
  },
  "game_story": {
    "narrative": "Derby Match. Home must win to qualify.",
    "risk_flags": ["high_intensity", "rotation_risk"]
  }
}
```

#### Collection: `ledger`

Tracks user performance.

```json
{
  "bet_id": "user123_match456_timestamp",
  "user_id": "123456789",
  "selection": "HOME_WIN",
  "stake": 50.00,
  "odds": 2.10,
  "result": "PENDING"
}
```

## 3. Integration Diagram

```
graph TD
    User[User via Discord] -->|/analyze| Bot[Discord Bot Container]
    Bot -->|Fetch Data| API[Odds & Stats API]
    API -->|Raw JSON| GS[GameStory Module]
    GS -->|Context Object| Pipeline[Three-Domain Pipeline]
    Pipeline -->|Score & Edge| DB[(Firestore DB)]
    DB -->|Cached Result| Bot
    Bot -->|Embed Response| User
```
