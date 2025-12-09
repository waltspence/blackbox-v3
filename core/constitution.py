# src/core/constitution.py
from typing import List, Dict, Optional
from enum import Enum

class BetType(Enum):
    MONEYLINE = "moneyline"
    SPREAD = "spread"
    TOTAL_OVER = "total_over"
    TOTAL_UNDER = "total_under"
    DOUBLE_CHANCE = "double_chance"
    BTTS = "btts"

class BlackBoxConstitution:
    """
    The Supreme Court of the BlackBox.
    Enforces rigid betting laws established in Dec 2025.
    """
    
    @staticmethod
    def check_crisis_law(team_stats: Dict, bet_type: BetType) -> bool:
        """
        LAW 1: THE CRISIS LAW (The Wolves/Liverpool Rule)
        "If a team is in 'Crisis' (Relegation Zone, 0 Wins, or conceded 4+ last game),
        the 'Under' is BANNED."
        """
        is_crisis = (
            team_stats.get("league_position", 1) >= 18 or  # Relegation zone
            team_stats.get("wins_last_5", 0) == 0 or      # Zero wins recently
            team_stats.get("goals_conceded_last_match", 0) >= 4  # Conceded 4+
        )
        
        if is_crisis and bet_type == BetType.TOTAL_UNDER:
            print(f"🚫 CONSTITUTION VIOLATION: Crisis Law. Team {team_stats['name']} is in crisis. UNDER is banned.")
            return False
            
        return True
    
    @staticmethod
    def check_suppression_law(match_type: str, bet_type: BetType) -> bool:
        """
        LAW 2: THE SUPPRESSION LAW (The Arsenal Rule)
        "If a game is designated Type C (Suppression/Grind), the 'Result' is BANNED."
        """
        if match_type == "TYPE_C" and bet_type in [BetType.MONEYLINE, BetType.DOUBLE_CHANCE]:
            print("🚫 CONSTITUTION VIOLATION: Suppression Law. Type C Match detected. RESULT bets are banned. Stick to Unders.")
            return False
            
        return True
    
    @staticmethod
    def check_parlay_cap(legs: List[Dict]) -> bool:
        """
        LAW 3: THE PARLAY CAP LAW (The Dortmund Rule)
        "If a Parlay has 4+ legs, 'Over 2.5 Goals' is BANNED."
        """
        if len(legs) >= 4:
            for leg in legs:
                if leg['bet_type'] == BetType.TOTAL_OVER and leg.get('line', 0) >= 2.5:
                    print("🚫 CONSTITUTION VIOLATION: Parlay Cap. 4+ legs detected. Over 2.5 is forbidden.")
                    return False
                    
        return True
    
    @staticmethod
    def check_matrix_law(matrix_pricing: Dict, bet_type: BetType) -> bool:
        """
        LAW 4: THE MATRIX LAW (The Bookie Rule)
        "If the Correct Score matrix prices 1-1 or 2-1 lower than 1-0 or 2-0,
        you MUST bet BTTS or Over."
        """
        price_1_1 = matrix_pricing.get("1-1", 1000)
        price_1_0 = matrix_pricing.get("1-0", 1000)
        price_2_0 = matrix_pricing.get("2-0", 1000)
        
        is_btts_favored = price_1_1 < price_1_0 and price_1_1 < price_2_0
        
        if is_btts_favored and bet_type in [BetType.TOTAL_UNDER, "win_to_nil"]:
            print("🚫 CONSTITUTION VIOLATION: Matrix Law. Bookies favor 1-1. Under/Win-to-Nil is banned.")
            return False
            
        return True
