scripts/backtest_dry_run.pyimport sys
import os
import random
import csv
import logging
from datetime import datetime

# Ensure we can import from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frameworks.three_domain import PredictionEngine
from bankroll.sizer import KellySizer
from services.mock_data import MockDataFetcher
from frameworks.schema import GameData, TeamData

# Setup Logging to Console
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("BlackBox.Backtest")

def run_simulation():
    print("--- STARTING BLACKBOX v3 DRY RUN ---")
    
    # 1. Initialize Core Components
    engine = PredictionEngine()
    sizer = KellySizer(kelly_fraction=0.25, max_bankroll_pct=0.05)
    mock_source = MockDataFetcher()
    
    # Simulation Parameters
    STARTING_BANKROLL = 1000.00
    SIMULATION_COUNT = 50
    results = []

    # 2. Get Base Templates
    base_games = mock_source.fetch_schedule("NFL")
    base_odds = mock_source.fetch_current_odds("mock_game_001") # Use generic odds for base

    print(f"Loaded {len(base_games)} base templates. Generating {SIMULATION_COUNT} scenarios...")

    # 3. Procedural Generation Loop
    for i in range(SIMULATION_COUNT):
        # Pick a random template and mutate it slightly to create variance
        template = random.choice(base_games)
        
        # Mutation: Randomize power ratings slightly to test edge cases
        h_rating_var = random.uniform(-15, 15)
        a_rating_var = random.uniform(-15, 15)
        
        sim_game = GameData(
            game_id=f"sim_{i:03d}",
            sport=template.sport,
            commence_time=template.commence_time,
            home_team=TeamData(
                name=template.home_team.name, 
                power_rating=template.home_team.power_rating + h_rating_var,
                days_rest=template.home_team.days_rest,
                is_home=True
            ),
            away_team=TeamData(
                name=template.away_team.name, 
                power_rating=template.away_team.power_rating + a_rating_var,
                days_rest=template.away_team.days_rest,
                is_home=False
            ),
            is_rivalry=template.is_rivalry,
            weather_condition=template.weather_condition
        )

        # Mutation: Randomize Odds slightly (1.10 to 3.50)
        home_odds = round(random.uniform(1.10, 3.50), 2)
        
        # --- EXECUTE PIPELINE ---
        
        # A. Predict
        pred_result = engine.predict(sim_game)
        
        # B. Size
        stake = sizer.calculate_stake(
            win_prob=pred_result.home_win_prob,
            decimal_odds=home_odds,
            bankroll=STARTING_BANKROLL,
            confidence_score=pred_result.confidence_score
        )

        # C. Calculate Expected Value (EV)
        # EV = (Prob * (Odds - 1)) - (1 - Prob)
        ev_pct = (pred_result.home_win_prob * (home_odds - 1)) - (1 - pred_result.home_win_prob)

        # D. Record Result
        results.append({
            "id": sim_game.game_id,
            "matchup": f"{sim_game.home_team.name} vs {sim_game.away_team.name}",
            "home_rating": round(sim_game.home_team.power_rating, 1),
            "away_rating": round(sim_game.away_team.power_rating, 1),
            "odds": home_odds,
            "model_prob": f"{pred_result.home_win_prob:.1%}",
            "fair_spread": pred_result.fair_spread,
            "ev_roi": f"{ev_pct:.1%}",
            "stake_amt": stake,
            "stake_pct": f"{(stake/STARTING_BANKROLL):.1%}",
            "flags": "|".join(pred_result.flags) if pred_result.flags else "Clean"
        })

    # 4. Output & Verification
    csv_file = "backtest_results.csv"
    keys = results[0].keys()
    
    with open(csv_file, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(results)

    print(f"\n--- SIMULATION COMPLETE ---")
    print(f"Results saved to {csv_file}")
    
    # 5. Safety Checks (The Gatekeeper)
    max_stake = max(r['stake_amt'] for r in results)
    min_stake = min(r['stake_amt'] for r in results)
    
    print(f"Max Stake: ${max_stake} (Limit: ${STARTING_BANKROLL * 0.05})")
    print(f"Min Stake: ${min_stake}")

    if max_stake > (STARTING_BANKROLL * 0.05):
        logger.error("❌ CRITICAL FAIL: Hard Cap Breached!")
        sys.exit(1)
    
    if min_stake < 0:
        logger.error("❌ CRITICAL FAIL: Negative Stake Suggested!")
        sys.exit(1)

    print("✅ SAFETY CHECKS PASSED: Ready for Phase A Integration.")

if __name__ == "__main__":
    run_simulation()
