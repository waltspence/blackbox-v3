#!/usr/bin/env python3
"""
Context Engine: Domain II Adjuster
===================================
Applies environmental modifiers to Domain I baseline.

Author: BlackBox v3
Date: 2025-11-24
"""

from typing import Dict


class ContextEngine:
    """
    Domain II: Entity vs. Environment
    Adjusts baseline probability for contextual forces.
    """
    
    def __init__(self):
        self.modifiers = {
            "travel_threshold_km": 800,
            "rest_penalty_per_day": 0.02,
            "motivation_multiplier": 0.15,
            "fatigue_threshold_games": 3
        }
    
    def apply_context(self, domain_i_output: Dict, context_data: Dict) -> Dict:
        """
        Apply Domain II environmental modifiers.
        
        Args:
            domain_i_output: Output from FairLine v3
            context_data: {
                "travel_km": float,
                "rest_days_home": int,
                "rest_days_away": int,
                "games_last_7_days_home": int,
                "games_last_7_days_away": int,
                "stakes_differential": float (-1 to 1, positive = home needs it more),
                "venue_factor": float (1.0 = neutral, >1.0 = home advantage)
            }
        
        Returns:
            {
                "adjusted_prob": float,
                "domain_ii_delta": float,  # Total adjustment
                "context_factors": dict
            }
        """
        base_prob = domain_i_output["base_prob"]
        adjustments = {}
        
        # Factor 1: Travel fatigue
        travel_km = context_data.get("travel_km", 0)
        if travel_km > self.modifiers["travel_threshold_km"]:
            travel_penalty = -0.05 * (travel_km / 1000)
            adjustments["travel_fatigue"] = travel_penalty
        
        # Factor 2: Rest differential
        rest_home = context_data.get("rest_days_home", 7)
        rest_away = context_data.get("rest_days_away", 7)
        rest_diff = rest_home - rest_away
        if abs(rest_diff) > 2:
            rest_adjustment = rest_diff * self.modifiers["rest_penalty_per_day"]
            adjustments["rest_differential"] = rest_adjustment
        
        # Factor 3: Schedule density (fixture congestion)
        games_home = context_data.get("games_last_7_days_home", 1)
        games_away = context_data.get("games_last_7_days_away", 1)
        if games_home > self.modifiers["fatigue_threshold_games"]:
            fatigue_penalty = -0.04 * (games_home - 2)
            adjustments["schedule_density_home"] = fatigue_penalty
        if games_away > self.modifiers["fatigue_threshold_games"]:
            fatigue_boost = 0.04 * (games_away - 2)
            adjustments["schedule_density_away"] = fatigue_boost
        
        # Factor 4: Motivation asymmetry
        stakes = context_data.get("stakes_differential", 0)
        if abs(stakes) > 0.2:
            motivation_adjustment = stakes * self.modifiers["motivation_multiplier"]
            adjustments["motivation_asymmetry"] = motivation_adjustment
        
        # Factor 5: Venue impact
        venue = context_data.get("venue_factor", 1.0)
        if venue != 1.0:
            venue_adjustment = (venue - 1.0) * 0.10
            adjustments["venue_impact"] = venue_adjustment
        
        # Apply all adjustments
        total_delta = sum(adjustments.values())
        adjusted_prob = max(0.05, min(0.95, base_prob + total_delta))
        
        return {
            "adjusted_prob": round(adjusted_prob, 3),
            "domain_ii_delta": round(total_delta, 3),
            "context_factors": {k: round(v, 3) for k, v in adjustments.items()},
            "domain": "II"
        }


if __name__ == "__main__":
    import sys
    sys.path.append('.')
    from fairline_v3 import FairLineV3
    
    # Arsenal vs Bayern example
    fairline = FairLineV3()
    domain_i = fairline.compute_baseline({
        "xg_home": 1.8,
        "xg_away": 2.1,
        "tactical_mismatch": -0.15,
        "h2h_advantage": 0.05,
        "manager_chess_rating": 0.60
    })
    
    context_engine = ContextEngine()
    domain_ii = context_engine.apply_context(
        domain_i_output=domain_i,
        context_data={
            "travel_km": 950,  # Bayern traveling from Munich
            "rest_days_home": 7,
            "rest_days_away": 3,  # Bayern played midweek
            "games_last_7_days_home": 1,
            "games_last_7_days_away": 3,  # Bayern congested
            "stakes_differential": 0.3,  # Arsenal needs CL spot
            "venue_factor": 1.08  # Emirates advantage
        }
    )
    
    print("=== Context Engine: Domain II Adjustments ===")
    print(f"Domain I baseline: {domain_i['base_prob']:.1%}")
    print(f"Domain II adjusted: {domain_ii['adjusted_prob']:.1%}")
    print(f"Total delta: {domain_ii['domain_ii_delta']:+.1%}")
    print("\nContext factors:")
    for factor, value in domain_ii['context_factors'].items():
        print(f"  {factor}: {value:+.3f}")
