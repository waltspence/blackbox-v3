#!/usr/bin/env python3
import sys, os, csv, json, math, datetime

def american_to_decimal(A):
    return 1 + (A/100.0) if A > 0 else 1 + (100.0/abs(A))

def implied_from_american(A):
    return (A/(A+100.0)) if A>0 else (100.0/(abs(A)+100.0))

def de_vig_single_side(p_raw, haircut=0.045):
    return max(0.01, min(0.99, p_raw * (1 - haircut)))

def poisson_sf(k, lam):
    thr = math.floor(k) + 1
    s = 0.0
    for i in range(thr):
        s += math.exp(-lam) * (lam**i) / math.factorial(i)
    return 1.0 - s

def guard_ok(player, leg, sport):
    if leg.get("injury_guard", True):
        if player["injury_status"] == "out":
            return False, "injury_out"
    if leg.get("lineup_guard", True):
        if player["lineup_status"] not in ("confirmed","expected"):
            return False, "lineup_unconfirmed"
    minutes = leg.get("minutes_override") or player["minutes_proj"]
    if not minutes or float(minutes) <= 0:
        return False, "no_minutes"
    if sport == "soccer" and float(minutes) < 8:
        return False, "minutes_too_low"
    if sport == "nba" and float(minutes) < 10:
        return False, "minutes_too_low"
    return True, ""

def load_players(path):
    panel = {}
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["sport"].strip().lower(), row["player_name"].strip(), row["team"].strip())
            panel[key] = {
                "sport": row["sport"].strip().lower(),
                "player_name": row["player_name"],
                "team": row["team"],
                "minutes_proj": float(row["minutes_proj"]) if row["minutes_proj"] else 0.0,
                "usage_adj": float(row["usage_adj"]) if row["usage_adj"] else 1.0,
                "shots_per90": float(row["shots_per90"]) if row["shots_per90"] else None,
                "sog_rate": float(row["sog_rate"]) if row["sog_rate"] else None,
                "xg_per90": float(row["xg_per90"]) if row["xg_per90"] else None,
                "passes_per90": float(row["passes_per90"]) if row["passes_per90"] else None,
                "shots_per36": float(row["shots_per36"]) if row["shots_per36"] else None,
                "oncourt_usage": float(row["oncourt_usage"]) if row["oncourt_usage"] else None,
                "injury_status": row["injury_status"].strip().lower(),
                "lineup_status": row["lineup_status"].strip().lower(),
                "mil_manager_tempo": float(row["mil_manager_tempo"]) if row["mil_manager_tempo"] else 0.50,
                "mil_press_intensity": float(row["mil_press_intensity"]) if row["mil_press_intensity"] else 0.50,
                "mil_subs_aggressiveness": float(row["mil_subs_aggressiveness"]) if row["mil_subs_aggressiveness"] else 0.50,
            }
    return panel

def main(players_csv, legs_csv):
    players = load_players(players_csv)
    out = []
    dropped = []
    with open(legs_csv, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sport = row["sport"].strip().lower()
            player_key = (sport, row["player"].strip(), row["team"].strip())
            player = players.get(player_key)
            if not player:
                dropped.append({"leg_id": row["leg_id"], "reason": "player_not_found"})
                continue

            market = row["market"].strip().lower()
            line = float(row["line"])
            A = int(row["american_odds"])
            minutes_override = row.get("minutes_override")
            minutes = float(minutes_override) if minutes_override else float(player["minutes_proj"])
            tempo_adj = float(row["tempo_adj"]) if row.get("tempo_adj") else (0.95 + 0.2*(player["mil_manager_tempo"]-0.5))
            injury_guard = row.get("injury_guard","True").lower() != "false"
            lineup_guard = row.get("lineup_guard","True").lower() != "false"

            leg = {"injury_guard": injury_guard, "lineup_guard": lineup_guard, "minutes_override": minutes_override}
            ok, reason = guard_ok(player, leg, sport)
            if not ok:
                dropped.append({"leg_id": row["leg_id"], "reason": reason})
                continue

            usage_adj = player["usage_adj"] or 1.0

            lam = None
            if sport == "soccer":
                if market == "shots":
                    lam = (player["shots_per90"] or 0.0) * (minutes/90.0) * usage_adj * tempo_adj
                elif market == "sog":
                    sog_rate = player["sog_rate"] if player["sog_rate"] is not None else 0.35
                    lam = (player["shots_per90"] or 0.0) * sog_rate * (minutes/90.0) * usage_adj * tempo_adj
                else:
                    dropped.append({"leg_id": row["leg_id"], "reason": "unsupported_market"}); continue
            elif sport == "nba":
                if market == "shots":
                    lam = (player["shots_per36"] or 0.0) * (minutes/36.0) * usage_adj * tempo_adj
                elif market == "sog":
                    dropped.append({"leg_id": row["leg_id"], "reason": "nba_sog_not_supported"}); continue
                else:
                    dropped.append({"leg_id": row["leg_id"], "reason": "unsupported_market"}); continue
            else:
                dropped.append({"leg_id": row["leg_id"], "reason": "unsupported_sport"}); continue

            p_over = 1.0 - sum(math.exp(-lam)*(lam**i)/math.factorial(i) for i in range(0, int(math.floor(line))+1))

            fair_dec = 1.0 / max(1e-6, p_over)
            fair_amer = round((fair_dec-1.0)*100) if fair_dec >= 2.0 else round(-100.0/(fair_dec-1.0))
            p_raw = (A/(A+100.0)) if A>0 else (100.0/(abs(A)+100.0))
            p_vigless = max(0.01, min(0.99, p_raw * (1 - 0.045)))
            vle = p_over - p_vigless
            tag = "Underpriced" if vle >= 0.04 else ("Overpriced" if vle <= -0.04 else "Fair")
            EV100 = p_over*100.0*(american_to_decimal(A)-1.0) - (1.0 - p_over)*100.0

            out.append({
                "leg_id": row["leg_id"],
                "sport": sport,
                "player": row["player"],
                "team": row["team"],
                "market": market,
                "line": line,
                "minutes": round(minutes,1),
                "lambda": round(lam,3),
                "p_model": round(p_over,4),
                "fair_decimal": round(fair_dec,2),
                "fair_american": int(fair_amer),
                "book_american": A,
                "p_vigless": round(p_vigless,4),
                "vle": round(vle,4),
                "vle_tag": tag,
                "EV_$100": round(EV100,2),
                "tempo_adj": round(tempo_adj,3),
                "guards": {"injury": injury_guard, "lineup": lineup_guard},
                "ts": datetime.datetime.utcnow().isoformat()+"Z"
            })

    out_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "priced_legs.json"), "w", encoding="utf-8") as jf:
        json.dump(out, jf, indent=2)
    with open(os.path.join(out_dir, "priced_legs.csv"), "w", encoding="utf-8", newline="") as cf:
        w = csv.DictWriter(cf, fieldnames=list(out[0].keys()) if out else ["empty"])
        w.writeheader()
        for r in out: w.writerow(r)

    with open(os.path.join(out_dir, "dropped_legs.json"), "w", encoding="utf-8") as df:
        json.dump(dropped, df, indent=2)

    print(json.dumps({"priced_count": len(out), "dropped": dropped[:10]}, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/price_props.py <players_csv> <legs_csv>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
