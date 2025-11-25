#!/usr/bin/env python3
"""
Variance Overlay v3 - Domain III: Entity vs Self

Philosophy:
Domain III isolates stochastic variance independent of skill (Domain I)
or environment (Domain II). This represents the irreducible uncertainty:
how an entity performs relative to its own expected baseline.

Core variance sources:
1. Mean Reversion Risk: High performers regressing toward true ability
2. Clutch/Choke: Variance in high-pressure moments
3. Hot-Hand/Slump: Short-term streaks unrelated to true talent
4. Sample Size: Smaller samples = higher variance uncertainty

This engine outputs uncertainty bands and confidence flags.
"""

import math
from typing import Dict, Optional
from scipy.stats import norm


class VarianceOverlay:
    """
    Domain III engine: quantifies self-variance (Entity vs Self).
    
    Takes a Domain I + Domain II output and adds uncertainty bands
    based on variance risk unrelated to skill or context.
    """
    
    def __init__(self):
        self.domain = "III"
        self.confidence_thresholds = {
            "high": 0.15,     # < 15% variance: high confidence
            "medium": 0.30,   # 15-30%: medium confidence
            "low": 0.30       # > 30%: low confidence
        }
    
    def apply_variance(
        self,
        domain_ii_output: Dict,
        variance_data: Dict
    ) -> Dict:
        """
        Apply Domain III variance overlay to Domain II output.
        
        Args:
            domain_ii_output: Output from ContextEngine with adjusted probabilities
            variance_data: Dict containing:
                - xg_per90_recent: Recent xG per 90 (regression risk)
                - xg_per90_season: Season avg xG per 90
                - high_pressure_share: Share of high-leverage situations
                - games_played: Sample size for confidence
                - recent_form_z: Z-score of recent form vs season avg
        
        Returns:
            Dict with uncertainty bands and confidence level
        """
        base_prob = domain_ii_output["adjusted_prob"]
        
        # 1. Regression risk: distance from seasonal mean
        regression_risk = self._calculate_regression_risk(
            variance_data["xg_per90_recent"],
            variance_data["xg_per90_season"],
            variance_data["games_played"]
        )
        
        # 2. Clutch variance: high-pressure uncertainty
        clutch_variance = variance_data["high_pressure_share"] * 0.08  # 8% per clutch share
        
        # 3. Form volatility: hot-hand or slump risk
        form_volatility = abs(variance_data["recent_form_z"]) * 0.05  # 5% per z-score
        
        # 4. Sample size uncertainty
        sample_uncertainty = 1.0 / math.sqrt(variance_data["games_played"])
        
        # Total variance (combine all sources)
        total_variance = math.sqrt(
            regression_risk**2 +
            clutch_variance**2 +
            form_volatility**2 +
            sample_uncertainty**2
        )
        
        # Calculate uncertainty bounds (1 std dev)
        lower_bound = max(0.0, base_prob - total_variance)
        upper_bound = min(1.0, base_prob + total_variance)
        
        # Confidence level
        confidence = self._classify_confidence(total_variance)
        
        return {
            "domain": "III",
            "base_prob": base_prob,
            "total_variance": round(total_variance, 4),
            "lower_bound": round(lower_bound, 4),
            "upper_bound": round(upper_bound, 4),
            "confidence": confidence,
            "variance_breakdown": {
                "regression_risk": round(regression_risk, 4),
                "clutch_variance": round(clutch_variance, 4),
                "form_volatility": round(form_volatility, 4),
                "sample_uncertainty": round(sample_uncertainty, 4)
            },
            "domain_ii_context": domain_ii_output.get("context_factors", {})
        }
    
    def _calculate_regression_risk(
        self,
        recent_xg: float,
        season_xg: float,
        games_played: int
    ) -> float:
        """
        Calculate regression-to-mean risk.
        
        Teams/players outperforming their seasonal average are more likely
        to regress. Risk increases with deviation size and decreases with
        larger sample sizes.
        """
        if games_played < 5:
            # Insufficient data - high uncertainty
            return 0.20
        
        # Deviation from season mean
        deviation = abs(recent_xg - season_xg) / season_xg if season_xg > 0 else 0.15
        
        # Adjust for sample size (more games = lower regression risk)
        sample_adjustment = 1.0 / math.sqrt(games_played)
        
        return min(0.30, deviation * sample_adjustment)
    
    def _classify_confidence(self, variance: float) -> str:
        """
        Classify confidence level based on total variance.
        """
        if variance < self.confidence_thresholds["high"]:
            return "high"
        elif variance < self.confidence_thresholds["medium"]:
            return "medium"
        else:
            return "low"


if __name__ == "__main__":
    # Arsenal vs Bayern example with variance
    # Assume we already have Domain II adjusted prob = 0.455
    
    domain_ii_result = {
        "domain": "II",
        "adjusted_prob": 0.455,  # From Context Engine
        "context_factors": {
            "travel_penalty": -0.019,
            "rest_penalty": -0.016
        }
    }
    
    variance_engine = VarianceOverlay()
    domain_iii = variance_engine.apply_variance(
        domain_ii_output=domain_ii_result,
        variance_data={
            "xg_per90_recent": 2.1,      # Arsenal recent form: 2.1 xG/90
            "xg_per90_season": 1.8,      # Season avg: 1.8 xG/90 (overperforming)
            "high_pressure_share": 0.25, # 25% of shots in high-leverage moments
            "games_played": 12,          # 12 recent games sampled
            "recent_form_z": 0.8         # 0.8 std devs above season avg
        }
    )
    
    print("==== Variance Overlay: Domain III Analysis ====")
    print(f"Domain II adjusted prob: {domain_iii['base_prob']:.3f}")
    print(f"\nDomain III Variance Analysis:")
    print(f"  Total variance: {domain_iii['total_variance']:.3f}")
    print(f"  Lower bound (1σ): {domain_iii['lower_bound']:.3f}")
    print(f"  Upper bound (1σ): {domain_iii['upper_bound']:.3f}")
    print(f"  Confidence: {domain_iii['confidence']}")
    print(f"\nVariance Breakdown:")
    for factor, value in domain_iii['variance_breakdown'].items():
        print(f"  {factor}: {value:.3f}")
    print(f"\n✓ True range: [{domain_iii['lower_bound']:.3f}, {domain_iii['upper_bound']:.3f}]")
    print(f"  (Arsenal may be overperforming - regression risk present)")
