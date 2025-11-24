#!/usr/bin/env python3
"""
FairLine v3: Pure Domain I Engine
==================================
Computes baseline win probability from pure competitive skill differential.
Assumes neutral environment and mean variance state.

Author: BlackBox v3
Date: 2025-11-24
"""

import math
from typing import Dict, Optional


class FairLineV3:
    """
    Domain I: Entity vs. Entity
    Pure skill-based probability with no environmental or variance adjustments.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {
            "xg_weight": 0.60,
            "tactical_weight": 0.25,
            "h2h_weight": 0.10,
            "manager_weight": 0.05
        }
    
    def compute_baseline(self, match_data: Dict) -> Dict:
        """
        Compute pure Domain I baseline probability.
        
        Args:
            match_data: {
                "xg_home": float,
                "xg_away": float,
                "tactical_mismatch": float (-1 to 1, positive favors home),
                "h2h_advantage": float (-1 to 1),
                "manager_chess_rating": float (0 to 1)
            }
        
        Returns:
            {
                "base_prob": float,  # Win probability
                "confidence": float,  # How reliable is this read
                "components": dict,   # Breakdown by factor
                "assumptions": dict   # What we're assuming
            }
        """
        # Extract inputs
        xg_home = match_data.get("xg_home", 1.5)
        xg_away = match_data.get("xg_away", 1.0)
        tactical = match_data.get("tactical_mismatch", 0.0)
        h2h = match_data.get("h2h_advantage", 0.0)
        manager = match_data.get("manager_chess_rating", 0.5)
        
        # Component 1: xG differential
        xg_diff = xg_home - xg_away
        xg_prob = self._xg_to_prob(xg_diff)
        xg_contribution = xg_prob * self.config["xg_weight"]
        
        # Component 2: Tactical mismatch
        tactical_prob = 0.5 + (tactical * 0.15)  # ±15% swing
        tactical_contribution = tactical_prob * self.config["tactical_weight"]
        
        # Component 3: H2H context
        h2h_prob = 0.5 + (h2h * 0.10)  # ±10% swing
        h2h_contribution = h2h_prob * self.config["h2h_weight"]
        
        # Component 4: Manager chess
        manager_contribution = manager * self.config["manager_weight"]
        
        # Aggregate
        base_prob = (
            xg_contribution + 
            tactical_contribution + 
            h2h_contribution + 
            manager_contribution
        )
        
        # Confidence: Higher when xG differential is large
        confidence = min(0.95, 0.65 + (abs(xg_diff) * 0.10))
        
        return {
            "base_prob": round(base_prob, 3),
            "confidence": round(confidence, 2),
            "components": {
                "xg_differential": round(xg_contribution, 3),
                "tactical_mismatch": round(tactical_contribution, 3),
                "h2h_context": round(h2h_contribution, 3),
                "manager_chess": round(manager_contribution, 3)
            },
            "assumptions": {
                "neutral_environment": True,
                "mean_variance_state": True,
                "full_strength_lineups": True
            },
            "domain": "I"
        }
    
    @staticmethod
    def _xg_to_prob(xg_diff: float) -> float:
        """
        Convert xG differential to win probability using Poisson approximation.
        """
        # Sigmoid transformation
        return 1 / (1 + math.exp(-0.75 * xg_diff))


if __name__ == "__main__":
    # Example: Arsenal vs Bayern (Nov 26, 2025 UCL)
    fairline = FairLineV3()
    
    match = {
        "xg_home": 1.8,  # Arsenal xG
        "xg_away": 2.1,  # Bayern xG
        "tactical_mismatch": -0.15,  # Bayern's press advantage
        "h2h_advantage": 0.05,  # Arsenal slight home H2H edge
        "manager_chess_rating": 0.60  # Kompany > Arteta tactically
    }
    
    result = fairline.compute_baseline(match)
    
    print("=== FairLine v3: Domain I Baseline ===")
    print(f"Arsenal win probability: {result['base_prob']:.1%}")
    print(f"Confidence: {result['confidence']:.1%}")
    print("\nComponent breakdown:")
    for key, val in result['components'].items():
        print(f"  {key}: {val:.3f}")
    print(f"\nAssumptions: {result['assumptions']}")
