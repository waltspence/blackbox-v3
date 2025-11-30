import logging
from typing import Tuple, List
from .schema import GameData

logger = logging.getLogger("BlackBox.GameStory")

class GameStoryEngine:
    """
    Domain II: Narrative & Contextual Adjustments.
    
    REFACTOR NOTE:
    To avoid double-counting, this engine now strictly uses configuration constants.
    It applies adjustments to the HOME team's probability.
    """
    
    def __init__(self):
        # Configuration - these could be loaded from a JSON/YAML file
        self.RIVALRY_VARIANCE_DAMPENER = 0.95  # Rivalries are harder to predict
        self.REST_ADVANTAGE_BONUS = 0.02       # 2% prob boost for significant rest advantage
        self.MOTIVATION_PLAYOFF_BOOST = 0.03   # 3% boost for home team in playoffs
        self.WEATHER_TOTAL_PENALTY = -3.0      # Points deducted from total for bad weather

    def analyze(self, game: GameData, current_prob: float) -> Tuple[float, float, List[str]]:
        """
        Applies narrative adjustments to the fundamental probability.

        Args:
            game (GameData): The game context.
            current_prob (float): The Domain I (Fundamental) Home Win Probability.

        Returns:
            Tuple[float, float, List[str]]: 
                - New Home Win Prob
                - Confidence Modifier (0.0 - 1.0)
                - List of applied flags/reasons
        """
        adj_prob = current_prob
        confidence = 1.0
        flags = []

        # 1. Rest Discrepancy Logic
        # If one team has >3 days rest advantage
        rest_diff = game.home_team.days_rest - game.away_team.days_rest
        if rest_diff > 3:
            adj_prob += self.REST_ADVANTAGE_BONUS
            flags.append(f"Home Rest Advantage (+{rest_diff} days)")
        elif rest_diff < -3:
            adj_prob -= self.REST_ADVANTAGE_BONUS
            flags.append(f"Away Rest Advantage ({rest_diff} days)")

        # 2. Rivalry Games
        # Rivalries often defy logic, reducing confidence in the fundamental model
        if game.is_rivalry:
            confidence *= self.RIVALRY_VARIANCE_DAMPENER
            flags.append("Rivalry Game (Confidence Dampened)")

        # 3. Injury Impact (Simplified for example)
        # Note: Ideally, power ratings in Domain I already account for 'key' players.
        # Domain II should only account for 'breaking news' or 'morale' impact of injuries.
        home_injuries = len(game.home_team.injuries)
        away_injuries = len(game.away_team.injuries)
        
        # Simple heuristic: heavily injured teams are less predictable
        if home_injuries + away_injuries > 4:
            confidence *= 0.90
            flags.append("High Injury Count (Uncertainty)")

        # Clamp result to ensure sanity
        adj_prob = max(0.01, min(0.99, adj_prob))

        return adj_prob, confidence, flags

    def get_weather_impact(self, game: GameData) -> float:
        """Returns impact on the TOTAL (Over/Under) score."""
        if game.weather_condition in ["Snow", "Heavy Rain", "High Wind"]:
            return self.WEATHER_TOTAL_PENALTY
        return 0.0
