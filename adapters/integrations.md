
# Integrations

## MIL → PlayerLayer
- `mil_manager_tempo` → `tempo_adj = 0.95 + 0.2*(tempo - 0.5)`
- `injury_status`, `lineup_status` → guards

## SPX → PropEngine
- Use SPX tempo/volatility to override `tempo_adj` when present.

## FairLine
- Use `p_model` for fair odds conversion and EV vs `book_american`.

## SlipForge
- Canonical output fields: `leg_id, sport, team, player, market, line, p_model, book_american, vle_tag, EV_$100`.
