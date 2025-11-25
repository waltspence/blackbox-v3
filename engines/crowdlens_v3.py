#!/usr/bin/env python3
"""
CrowdLens v3 - Domain-Specific Market Psychology

Philosophy:
Market inefficiencies manifest differently across the Three Domains:

- Domain I (skill): Crowd underestimates fundamental talent differentials
- Domain II (context): Crowd overreacts to recent contextual events
- Domain III (variance): Crowd exhibits recency bias and hot-hand fallacy

This engine detects domain-specific market mispricing by comparing
our three-domain true probability against the closing line.
"""

import math
from typing import Dict, Optional


class CrowdLensV3:
    """
    Domain-aware market psychology analyzer.
    
    Identifies value by detecting domain-specific crowd biases.
    """
    
    def __init__(self):
        # Domain-specific bias weights
        self.domain_bias_weights = {
            "I": 0.40,   # Skill domain: moderate crowd error
            "II": 0.60,  # Context domain: high crowd overreaction
            "III": 0.80  # Variance domain: extreme recency bias
        }
    
    def analyze_market(
        self,
        true_prob: float,
        market_prob: float,
        domain: str,
        variance_data: Optional[Dict] = None
    ) -> Dict:
        """
        Detect market mispricing relative to domain-aware true probability.
        
        Args:
            true_prob: Our three-domain computed probability
            market_prob: Implied probability from closing line
            domain: Dominant domain classification ("I", "II", or "III")
            variance_data: Optional variance metadata (for Domain III analysis)
        
        Returns:
            Dict with edge, confidence, and psychological factors
        """
        # Raw edge (true prob - market prob)
        raw_edge = true_prob - market_prob
        
        # Domain-specific bias weight
        bias_weight = self.domain_bias_weights.get(domain, 0.50)
        
        # Adjusted edge accounting for domain-specific crowd behavior
        # Higher bias weight = more confidence in our edge
        adjusted_edge = raw_edge * (1 + bias_weight * 0.5)
        
        # Detect specific psychological factors
        psych_factors = self._identify_psychological_factors(
            raw_edge, domain, variance_data
        )
        
        # Edge confidence (higher for domains where crowd is more biased)
        confidence = self._compute_confidence(adjusted_edge, domain, psych_factors)
        
        # Kelly fraction recommendation
        kelly_fraction = self._compute_kelly(adjusted_edge, confidence)
        
        return {
            "domain": domain,
            "true_prob": round(true_prob, 4),
            "market_prob": round(market_prob, 4),
            "raw_edge": round(raw_edge, 4),
            "adjusted_edge": round(adjusted_edge, 4),
            "confidence": confidence,
            "kelly_fraction": round(kelly_fraction, 4),
            "psychological_factors": psych_factors,
            "recommendation": self._generate_recommendation(adjusted_edge, confidence)
        }
    
    def _identify_psychological_factors(
        self,
        edge: float,
        domain: str,
        variance_data: Optional[Dict]
    ) -> Dict:
        """
        Identify domain-specific psychological biases.
        """
        factors = {}
        
        if domain == "I":
            # Skill domain: look for talent undervaluation
            if edge > 0.05:
                factors["skill_undervaluation"] = True
                factors["reason"] = "Crowd underestimates fundamental skill gap"
        
        elif domain == "II":
            # Context domain: look for overreaction to recent context
            if abs(edge) > 0.08:
                factors["contextual_overreaction"] = True
                factors["reason"] = "Crowd overreacts to travel/rest/schedule"
        
        elif domain == "III":
            # Variance domain: look for recency bias
            if variance_data and variance_data.get("recent_form_z", 0) > 1.0:
                if edge < -0.10:  # Market overvalues hot team
                    factors["recency_bias"] = True
                    factors["hot_hand_fallacy"] = True
                    factors["reason"] = "Crowd overvalues recent variance streak"
        
        return factors
    
    def _compute_confidence(self, edge: float, domain: str, psych_factors: Dict) -> str:
        """
        Compute confidence level in our edge.
        """
        bias_weight = self.domain_bias_weights[domain]
        
        # Higher bias weight + identified psych factors = higher confidence
        confidence_score = abs(edge) * bias_weight
        
        if psych_factors:
            confidence_score *= 1.3  # 30% boost if we identified specific bias
        
        if confidence_score > 0.08:
            return "high"
        elif confidence_score > 0.04:
            return "medium"
        else:
            return "low"
    
    def _compute_kelly(self, edge: float, confidence: str) -> float:
        """
        Compute Kelly criterion fraction based on edge and confidence.
        """
        # Simplified Kelly: f = edge (assuming fair odds)
        base_kelly = abs(edge)
        
        # Adjust for confidence
        if confidence == "high":
            return base_kelly * 1.0  # Full Kelly
        elif confidence == "medium":
            return base_kelly * 0.5  # Half Kelly
        else:
            return base_kelly * 0.25  # Quarter Kelly
    
    def _generate_recommendation(self, edge: float, confidence: str) -> str:
        """
        Generate action recommendation.
        """
        if abs(edge) < 0.03:
            return "PASS - Insufficient edge"
        elif confidence == "low":
            return "PASS - Low confidence"
        elif edge > 0:
            return f"BET - {confidence.upper()} confidence edge"
        else:
            return "PASS - Negative edge"


if __name__ == "__main__":
    # Arsenal vs Bayern example
    # True prob from Domain I+II+III: 0.455
    # Market closing line: Arsenal +150 (0.40 implied)
    
    crowdlens = CrowdLensV3()
    
    result = crowdlens.analyze_market(
        true_prob=0.455,     # From our three-domain pipeline
        market_prob=0.400,   # From +150 closing line
        domain="II",         # Dominant domain (context adjustments)
        variance_data={
            "recent_form_z": 0.8  # Arsenal slightly above seasonal avg
        }
    )
    
    print("==== CrowdLens v3: Market Psychology Analysis ====")
    print(f"True probability: {result['true_prob']:.3f}")
    print(f"Market probability: {result['market_prob']:.3f}")
    print(f"Raw edge: {result['raw_edge']:+.3f}")
    print(f"Adjusted edge (domain-aware): {result['adjusted_edge']:+.3f}")
    print(f"Confidence: {result['confidence']}")
    print(f"Kelly fraction: {result['kelly_fraction']:.3f}")
    print(f"\nPsychological factors: {result['psychological_factors']}")
    print(f"\n✓ Recommendation: {result['recommendation']}")
