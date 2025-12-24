#!/usr/bin/env python3
"""
Team-Level Soccer Props Pricing Module

Handles BTTS (Both Teams To Score), Team Total Goals, and Team Corners.
Part of Phase 3 implementation for US market-focused prop expansion.

Author: BlackBox v3 Team
Based on Gemini soccer props gap analysis recommendations.
"""

import sys, os, csv, json, math, datetime
from scipy import stats

# Configuration constants
DEFAULT_VIG_HAIRCUT = 0.045
DEFAULT_CORRELATION = 0.15  # Team correlation for BTTS

def american_to_decimal(A):
    return 1 + (A/100.0) if A > 0 else 1 + (100.0/abs(A))

def implied_from_american(A):
    return (A/(A+100.0)) if A>0 else (100.0/(abs(A)+100.0))

def de_vig_single_side(p_raw, haircut=DEFAULT_VIG_HAIRCUT):
    return max(0.01, min(0.99, p_raw * (1 - haircut)))

def poisson_pmf(k, lam):
    """Calculate P(X = k) using Poisson distribution."""
    if lam <= 0:
        return 0.0
    return stats.poisson.pmf(k, lam)

def poisson_sf(k, lam):
    """Calculate P(X > k) using scipy for accuracy."""
    if lam <= 0:
        return 0.0
    return stats.poisson.sf(k, lam)

def load_players(path):
    """Load player panel to derive team-level xG."""
    panel = {}
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["sport"].strip().lower(), row["player_name"].strip(), row["team"].strip())
            panel[key] = {
                "sport": row["sport"].strip().lower(),
                "player_name": row["player_name"],
                "team": row["team"],
                "minutes_proj": float(row["minutes_proj"]) if row["minutes_proj"] else 0.0,
                "xg_per90": float(row["xg_per90"]) if row["xg_per90"] else 0.0,
                "usage_adj": float(row["usage_adj"]) if row["usage_adj"] else 1.0,
                "mil_manager_tempo": float(row["mil_manager_tempo"]) if row["mil_manager_tempo"] else 0.50,
            }
    return panel

def aggregate_team_xg(players, team_name, sport="soccer"):
    """Aggregate player xG to derive team-level expected goals."""
    team_xg = 0.0
    for key, player in players.items():
        if player["sport"] == sport and player["team"] == team_name:
            minutes = player["minutes_proj"]
            xg = player["xg_per90"] or 0.0
            usage = player["usage_adj"] or 1.0
            # Normalize to per-game contribution
            team_xg += xg * (minutes / 90.0) * usage
    return team_xg

def price_btts(home_xg, away_xg, correlation=DEFAULT_CORRELATION):
    """Price Both Teams To Score market.
    
    Args:
        home_xg: Home team expected goals
        away_xg: Away team expected goals
        correlation: Negative correlation adjustment (both teams scoring is slightly negatively correlated)
    
    Returns:
        Probability of BTTS (both teams scoring at least 1 goal)
    """
    # P(Home scores) = 1 - P(Home = 0)
    p_home_scores = 1.0 - poisson_pmf(0, home_xg)
    # P(Away scores) = 1 - P(Away = 0)
    p_away_scores = 1.0 - poisson_pmf(0, away_xg)
    
    # Assuming independence (simplified, could use Gaussian Copula for correlation)
    p_btts_independent = p_home_scores * p_away_scores
    
    # Apply slight negative correlation adjustment
    p_btts = p_btts_independent * (1 - correlation)
    
    return max(0.01, min(0.99, p_btts))

def price_team_total(team_xg, line, over=True):
    """Price Team Total Goals over/under.
    
    Args:
        team_xg: Team expected goals (lambda for Poisson)
        line: Betting line (e.g., 1.5, 2.5)
        over: True for over, False for under
    
    Returns:
        Probability of over/under the line
    """
    if over:
        # P(X > line) - for over 1.5 means P(X >= 2)
        k_threshold = int(math.floor(line))
        p_over = poisson_sf(k_threshold, team_xg)
        return max(0.01, min(0.99, p_over))
    else:
        # P(X <= line) - for under 1.5 means P(X <= 1)
        k_threshold = int(math.floor(line))
        p_under = sum(poisson_pmf(k, team_xg) for k in range(k_threshold + 1))
        return max(0.01, min(0.99, p_under))

def main(players_csv, team_props_csv):
    """Main function to price team-level props.
    
    Args:
        players_csv: Path to player panel CSV
        team_props_csv: Path to team props legs CSV with columns:
                        - leg_id, sport, home_team, away_team, market, line, american_odds, tempo_adj
    """
    players = load_players(players_csv)
    out = []
    dropped = []
    
    with open(team_props_csv, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sport = row["sport"].strip().lower()
            home_team = row["home_team"].strip()
            away_team = row["away_team"].strip()
            market = row["market"].strip().lower()
            line = float(row.get("line", 0)) if row.get("line") else None
            A = int(row["american_odds"])
            tempo_adj = float(row.get("tempo_adj", 1.0)) if row.get("tempo_adj") else 1.0
            
            # Aggregate team xG
            home_xg = aggregate_team_xg(players, home_team, sport) * tempo_adj
            away_xg = aggregate_team_xg(players, away_team, sport) * tempo_adj
            
            if home_xg <= 0 or away_xg <= 0:
                dropped.append({"leg_id": row["leg_id"], "reason": "insufficient_team_data"})
                continue
            
            p_model = None
            
            if market == "btts" or market == "both_teams_to_score":
                p_model = price_btts(home_xg, away_xg)
            elif market == "home_total_over":
                if line is None:
                    dropped.append({"leg_id": row["leg_id"], "reason": "missing_line"})
                    continue
                p_model = price_team_total(home_xg, line, over=True)
            elif market == "home_total_under":
                if line is None:
                    dropped.append({"leg_id": row["leg_id"], "reason": "missing_line"})
                    continue
                p_model = price_team_total(home_xg, line, over=False)
            elif market == "away_total_over":
                if line is None:
                    dropped.append({"leg_id": row["leg_id"], "reason": "missing_line"})
                    continue
                p_model = price_team_total(away_xg, line, over=True)
            elif market == "away_total_under":
                if line is None:
                    dropped.append({"leg_id": row["leg_id"], "reason": "missing_line"})
                    continue
                p_model = price_team_total(away_xg, line, over=False)
                            elif market == "home_corners_over" or market == "away_corners_over":
                # Team corners - requires corners data. Estimate from pressure/possession
                # Note: Corners data not currently in schema. Placeholder for future implementation
                if line is None:
                    dropped.append({"leg_id": row["leg_id"], "reason": "missing_line"})
                    continue
                # Estimate: ~5 corners per team per game baseline, adjusted by xG dominance
                team_xg = home_xg if "home" in market else away_xg
                opp_xg = away_xg if "home" in market else home_xg
                xg_ratio = team_xg / (team_xg + opp_xg) if (team_xg + opp_xg) > 0 else 0.5
                corners_expected = 5.0 * (1 + 0.5 * (xg_ratio - 0.5))  # Adjust from baseline
                p_model = price_team_total(corners_expected, line, over=True)
            elif market == "home_corners_under" or market == "away_corners_under":
                if line is None:
                    dropped.append({"leg_id": row["leg_id"], "reason": "missing_line"})
                    continue
                team_xg = home_xg if "home" in market else away_xg
                opp_xg = away_xg if "home" in market else home_xg
                xg_ratio = team_xg / (team_xg + opp_xg) if (team_xg + opp_xg) > 0 else 0.5
                corners_expected = 5.0 * (1 + 0.5 * (xg_ratio - 0.5))
                p_model = price_team_total(corners_expected, line, over=False)
            else:
                dropped.append({"leg_id": row["leg_id"], "reason": "unsupported_market"})
                continue
            
            # Calculate fair odds and VLE
            fair_dec = 1.0 / max(1e-6, p_model)
            fair_amer = round((fair_dec-1.0)*100) if fair_dec >= 2.0 else round(-100.0/(fair_dec-1.0))
            p_raw = (A/(A+100.0)) if A>0 else (100.0/(abs(A)+100.0))
            p_vigless = de_vig_single_side(p_raw)
            vle = p_model - p_vigless
            tag = "Underpriced" if vle >= 0.04 else ("Overpriced" if vle <= -0.04 else "Fair")
            EV100 = p_model*100.0*(american_to_decimal(A)-1.0) - (1.0 - p_model)*100.0
            
            out.append({
                "leg_id": row["leg_id"],
                "sport": sport,
                "home_team": home_team,
                "away_team": away_team,
                "market": market,
                "line": line if line is not None else "",
                "home_xg": round(home_xg, 3),
                "away_xg": round(away_xg, 3),
                "p_model": round(p_model, 4),
                "fair_decimal": round(fair_dec, 2),
                "fair_american": int(fair_amer),
                "book_american": A,
                "p_vigless": round(p_vigless, 4),
                "vle": round(vle, 4),
                "vle_tag": tag,
                "EV_$100": round(EV100, 2),
                "ts": datetime.datetime.utcnow().isoformat()+"Z"
            })
    
    # Output results
    out_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
    os.makedirs(out_dir, exist_ok=True)
    
    with open(os.path.join(out_dir, "priced_team_props.json"), "w", encoding="utf-8") as jf:
        json.dump(out, jf, indent=2)
    
    with open(os.path.join(out_dir, "priced_team_props.csv"), "w", encoding="utf-8", newline="") as cf:
        if out:
            w = csv.DictWriter(cf, fieldnames=list(out[0].keys()))
            w.writeheader()
            for r in out:
                w.writerow(r)
    
    with open(os.path.join(out_dir, "dropped_team_props.json"), "w", encoding="utf-8") as df:
        json.dump(dropped, df, indent=2)
    
    print(json.dumps({"priced_count": len(out), "dropped": dropped[:10]}, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/price_team_props.py <players_csv> <team_props_csv>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
