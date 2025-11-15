# Blackbox Pack #1 — PlayerLayer + PropEngine (v1)
Date: 2025-11-13

Production-ready stubs for **PlayerLayer** and **PropEngine**, covering:
- Schemas for player data (minutes, role, usage, shots/90, xG/90, passes/90)
- Two markets: **Shots** and **Shots on Goal (SOG)** for **soccer** and **NBA**
- **VLE (Value-to-Line Efficiency)** tagging
- Runnable pricing script (projections → fair odds, EV, VLE)
- Integration points with **MIL**, **SPX**, **FairLine**, and **SlipForge**
- Guards for injury/lineup status

## Quick Start
1) Fill `templates/players_example.csv` and `templates/legs_input.csv` with real slate data.
2) Run: `python scripts/price_props.py templates/players_example.csv templates/legs_input.csv`
3) Outputs in `outputs/`: `priced_legs.json` and `priced_legs.csv`

## Integration Map
- **MIL → PlayerLayer:** manager style (tempo/press/subs) + rotation risk inform `minutes_proj` and `usage_adj`.
- **SPX → PropEngine:** match tempo/volatility -> adjusts attempt rates (`tempo_adj`).
- **FairLine:** script computes fair probs → fair decimal/American; EV vs book.
- **SlipForge:** emits canonical legs with `leg_id, market, team, player, p_model, american_odds, tags, guards`.

