"""BlackBox v3: Settlement Script
------------------------------
Cron Job: Checks for completed matches, grades pending bets,
and updates user bankrolls atomically.

Usage: python scripts/settle_bets.py
"""

import sys
import os
import requests
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.db import (
    init_db,
    get_pending_bets,
    mark_bet_settled,
    update_user_stats
)
from services.entity_mapper import get_canonical_id

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SettlementBot")

load_dotenv()
ODDS_API_KEY = os.getenv('ODDS_API_KEY')

def fetch_completed_scores():
    """
    Fetches completed match scores from The Odds API (or your specific provider).
    Returns a normalized list of results.
    """
    if not ODDS_API_KEY:
        logger.error("ODDS_API_KEY missing in environment.")
        return []
    
    # Example endpoint: EPL scores for last 3 days
    # Adjust sport/league key as needed
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/scores/?daysFrom=3&apiKey={ODDS_API_KEY}"
    
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        
        results = []
        for match in data:
            if match.get('completed', False):
                scores = match.get('scores', [])
                
                # Normalize scores (Provider specific logic)
                home_score = next((s['score'] for s in scores if s['name'] == match['home_team']), 0)
                away_score = next((s['score'] for s in scores if s['name'] == match['away_team']), 0)
                
                results.append({
                    'home_team': match['home_team'],
                    'away_team': match['away_team'],
                    'home_score': int(home_score),
                    'away_score': int(away_score),
                    'commence_time': match['commence_time']
                })
        
        return results
    except Exception as e:
        logger.error(f"API Fetch Error: {e}")
        return []

def determine_winner(home_score, away_score):
    if home_score > away_score:
        return "HOME"
    if away_score > home_score:
        return "AWAY"
    return "DRAW"

def run_settlement():
    logger.info("Starting settlement process...")
    init_db()
    
    # 1. Get Pending Bets
    pending_bets = get_pending_bets()
    if not pending_bets:
        logger.info("No pending bets found.")
        return
    
    logger.info(f"Found {len(pending_bets)} pending bets.")
    
    # 2. Get Real-World Results
    recent_results = fetch_completed_scores()
    if not recent_results:
        logger.info("No completed matches found in API window.")
        return
    
    # 3. Create Lookup Map (using Canonical IDs to match DB)
    # Key: "HOME_ID vs AWAY_ID" -> Result
    results_map = {}
    for res in recent_results:
        h_id = get_canonical_id(res['home_team'])
        a_id = get_canonical_id(res['away_team'])
        key = f"{h_id} vs {a_id}"
        results_map[key] = {
            'winner': determine_winner(res['home_score'], res['away_score']),
            'score': f"{res['home_score']}-{res['away_score']}"
        }
    
    # 4. Grade Bets
    processed_count = 0
    for bet in pending_bets:
        match_sig = bet.get('match_signature')
        if match_sig in results_map:
            outcome = results_map[match_sig]
            winning_selection = outcome['winner']
            
            payout = 0.0
            result_status = "LOSS"
            profit = -float(bet['stake'])
            
            # Check Selection
            user_pick = bet['selection'].upper()
            if "HOME" in user_pick:
                user_pick = "HOME"
            elif "AWAY" in user_pick:
                user_pick = "AWAY"
            elif "DRAW" in user_pick:
                user_pick = "DRAW"
            
            if user_pick == winning_selection:
                result_status = "WIN"
                payout = float(bet['stake']) * float(bet['odds'])
                profit = payout - float(bet['stake'])
            
            logger.info(f"Settling Bet {bet['id']}: {result_status} ({outcome['score']})")
            
            # Atomic Updates
            mark_bet_settled(bet['id'], result_status, payout, outcome['score'])
            update_user_stats(bet['user_id'], profit, result_status == "WIN")
            processed_count += 1
    
    logger.info(f"Settlement Complete. Processed {processed_count} bets.")

if __name__ == "__main__":
    run_settlement()
