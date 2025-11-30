from .schema import GameData, PredictionResult
from .game_story import GameStoryEngine
import math

class PredictionEngine:
    """
    The Core "Glass Box" Orchestrator.
    
    Pipelines:
    1. FairLine (Domain I): Calculates raw skill-based probability.
    2. GameStory (Domain II): Adjusts for narrative context.
    3. Variance (Domain III): Calculates confidence intervals (not fully impl here, represented by score).
    """

    def __init__(self):
        self.story_engine = GameStoryEngine()

    def _calculate_fundamental_prob(self, home_rating: float, away_rating: float, is_neutral: bool) -> float:
        """
        Domain I: FairLine.
        Uses a standard logistic function based on ELO/Power Rating difference.
        """
        HFA = 2.5 if not is_neutral else 0.0  # Standard Home Field Advantage points
        
        # Example: 1 point of rating diff = ~2.5% win prob shift (simplified)
        # In reality, this would be a sophisticated regression model.
        point_spread = (away_rating - home_rating) - HFA
        
        # Convert spread to win probability (Standard conversion heuristic)
        # Z-score approximation
        if point_spread == 0:
            return 0.50
        
        # Simple spread-to-prob conversion for demo
        # -3.0 spread => ~60% win prob
        prob = 0.50 - (point_spread * 0.03) 
        return max(0.01, min(0.99, prob))

    def predict(self, game: GameData) -> PredictionResult:
        # --- Domain I: Fundamentals ---
        raw_prob = self._calculate_fundamental_prob(
            game.home_team.power_rating, 
            game.away_team.power_rating,
            game.neutral_site
        )

        # --- Domain II: Narrative ---
        adj_prob, confidence, flags = self.story_engine.analyze(game, raw_prob)

        # --- Domain III: Variance/Construction ---
        # Calculate fair spread based on the adjusted probability
        # Reverse engineering the spread from the new probability
        fair_spread = (0.50 - adj_prob) / 0.03
        
        # Calculate Total (Base total assumed 45 for demo, adjusted by weather)
        base_total = 45.0 # This would come from offensive/defensive ratings in a real model
        weather_adj = self.story_engine.get_weather_impact(game)
        fair_total = base_total + weather_adj
        if weather_adj != 0:
            flags.append(f"Weather Adjustment ({weather_adj})")

        return PredictionResult(
            game_id=game.game_id,
            home_win_prob=round(adj_prob, 4),
            away_win_prob=round(1.0 - adj_prob, 4),
            fair_spread=round(fair_spread, 2),
            fair_total=fair_total,
            confidence_score=confidence,
            domain_1_raw=round(raw_prob, 4),
            domain_2_adj=round(adj_prob, 4),
            domain_3_var=0.0, # Placeholder for variance simulation result
            flags=flags
        )
