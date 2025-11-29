# API Reference

This reference documents the core analytical modules found in `frameworks/` and service adapters in `services/`.

---

## Module: `frameworks.game_story`

Handles the "Pre-Betting Context Layer". Parses raw data into narrative adjustments.

### `build_game_context(match_data: Dict[str, Any]) -> GameContext`

Parses raw dictionary input (from API) into a structured `GameContext` object using Pydantic validation.

* **Args:**
  * `match_data`: Dictionary containing `competition`, `home_team`, `away_team`, and `meta` keys.
* **Returns:** `GameContext` object populated with calculated confidence, rotation risk, and narrative strings.
* **Notes:** Automatically calculates `rotation_risk` if `upcoming_fixtures` list is present.

### `get_domain_adjustments(context: GameContext) -> Dict[str, Any]`

Translates the narrative context into mathematical adjustments for the pipeline.

* **Args:**
  * `context`: A populated `GameContext` object.
* **Returns:** Dictionary containing:
  * `domain_i_adjustment`: Float (Skill tweak, clamped between -0.15 and 0.15).
  * `domain_ii_adjustment`: Float (Tempo/Environment tweak).
  * `domain_iii_variance_boost`: Float (Volatility injection, clamped 0.0 to 0.30).
  * `risk_flags`: List of strings (e.g., `['high_intensity', 'home_desperation']`).

### `clamp(n: float, minn: float, maxn: float) -> float`

Helper utility to restrict values within safe mathematical bounds.

---

## Module: `services.db`

Handles interactions with Google Firestore.

### `init_db(cred_path: str = None)`

Initializes the Firebase Admin SDK.

* **Args:** `cred_path` (Optional) - Path to `service-account.json`. Defaults to env var `FIREBASE_CREDENTIALS_JSON`.

### `save_match_analysis(match_id: str, match_input: Dict, game_context: Any, pipeline_results: Dict)`

Upserts a match analysis record.

* **Args:**
  * `match_id`: Unique identifier (e.g., "EPL_ARS_LIV").
  * `match_input`: The raw data used for analysis.
  * `game_context`: The `GameContext` dataclass (converted to dict automatically).
  * `pipeline_results`: Final probabilities and edges.

### `log_user_bet(user_id: str, match_id: str, selection: str, stake: float, odds: float)`

Records a wager in the `ledger` collection.

* **Returns:** `bet_id` (String).
