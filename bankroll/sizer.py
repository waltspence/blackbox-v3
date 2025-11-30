import logging
from decimal import Decimal, ROUND_DOWN
from typing import Optional

# Configure logging
logger = logging.getLogger("BlackBox.Bankroll")

class KellySizer:
    """
    Calculates bet sizing based on the Kelly Criterion with strict safety rails.
    
    Principles:
    1. Safety First: Defaults to fractional Kelly (0.25x) to reduce variance.
    2. Hard Caps: Never recommends more than a fixed % of bankroll (default 5%).
    3. No Negative EV: If edge is <= 0, stake is 0.
    """

    def __init__(self, kelly_fraction: float = 0.25, max_bankroll_pct: float = 0.05):
        """
        Args:
            kelly_fraction (float): The multiplier for the Kelly calculation (e.g., 0.25 for Quarter Kelly).
            max_bankroll_pct (float): The hard cap for a single bet as a percentage of total bankroll (0.05 = 5%).
        """
        self.kelly_fraction = kelly_fraction
        self.max_bankroll_pct = max_bankroll_pct

    def calculate_stake(self, 
                        win_prob: float, 
                        decimal_odds: float, 
                        bankroll: float, 
                        confidence_score: float = 1.0) -> float:
        """
        Calculates the optimal wager amount.

        Args:
            win_prob (float): The modeled probability of winning (0.0 to 1.0).
            decimal_odds (float): The decimal odds offered by the bookmaker (e.g., 1.91).
            bankroll (float): Current available bankroll.
            confidence_score (float): A domain-specific multiplier (0.0 to 1.0) to dampen low-confidence bets.

        Returns:
            float: The dollar amount to wager.
        """
        if bankroll <= 0:
            logger.warning("Bankroll is 0 or negative. Cannot wager.")
            return 0.0
        
        if win_prob <= 0 or win_prob >= 1:
            logger.error(f"Invalid probability: {win_prob}. Must be between 0 and 1.")
            return 0.0

        if decimal_odds <= 1:
            logger.error(f"Invalid odds: {decimal_odds}. Must be > 1.")
            return 0.0

        # Kelly Formula: f* = (bp - q) / b
        # where b = decimal_odds - 1 (net fractional odds)
        # p = win_prob
        # q = 1 - win_prob
        
        b = decimal_odds - 1
        p = win_prob
        q = 1 - p
        
        full_kelly_pct = (b * p - q) / b

        # 1. Negative EV Check
        if full_kelly_pct <= 0:
            logger.info(f"Negative EV detected (Kelly: {full_kelly_pct:.4f}). Recommendation: No Bet.")
            return 0.0

        # 2. Apply Fractional Multiplier & Confidence
        adjusted_kelly_pct = full_kelly_pct * self.kelly_fraction * confidence_score

        # 3. Apply Hard Cap
        final_pct = min(adjusted_kelly_pct, self.max_bankroll_pct)

        # 4. Calculate Absolute Stake
        stake_amount = bankroll * final_pct

        # Round down to 2 decimal places for currency safety
        stake_amount = float(Decimal(stake_amount).quantize(Decimal("0.01"), rounding=ROUND_DOWN))

        logger.info(f"Sizing: Edge={(full_kelly_pct*b):.2%} | Raw Kelly={full_kelly_pct:.2%} | Final Stake=${stake_amount} ({final_pct:.2%})")
        
        return stake_amount
