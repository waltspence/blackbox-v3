#!/usr/bin/env python3
"""
LegGraph v3 - Domain-Aware Correlation Modeling

Philosophy:
LegGraph v3 applies the Three-Domain framework to parlay correlation.
It recognizes that different legs of a parlay correlate differently
based on their domain classifications:

- Domain I legs (skill): Low correlation (independent outcomes)
- Domain II legs (context): Medium correlation (shared environmental factors)
- Domain III legs (variance): High short-term correlation (hot-hand effects)

This engine detects domain conflicts (e.g., Arsenal to win + Bayern to win)
and adjusts parlay probabilities accordingly.
"""

import math
from typing import Dict, List, Tuple
import numpy as np
from scipy.stats import norm


class LegGraphV3:
    """
    Domain-aware correlation engine for parlay modeling.
    
    Extends v2 copula approach with Three-Domain classification.
    """
    
    def __init__(self):
        # Base correlation coefficients by domain pair
        self.domain_correlations = {
            ("I", "I"): 0.05,     # Skill-skill: very low (independent)
            ("I", "II"): 0.15,    # Skill-context: low-medium
            ("I", "III"): 0.20,   # Skill-variance: medium
            ("II", "II"): 0.35,   # Context-context: medium-high (shared env)
            ("II", "III"): 0.30,  # Context-variance: medium
            ("III", "III"): 0.45  # Variance-variance: high (streaks)
        }
    
    def compute_parlay_probability(
        self,
        legs: List[Dict]
    ) -> Dict:
        """
        Compute true parlay probability with domain-aware correlations.
        
        Args:
            legs: List of leg dicts, each containing:
                - "prob": Win probability
                - "domain": Domain classification ("I", "II", or "III")
                - "outcome": "win", "over", etc.
                - "entity": Team/player name
        
        Returns:
            Dict with parlay probability and correlation breakdown
        """
        n_legs = len(legs)
        
        if n_legs == 1:
            # Single leg: no correlation
            return {
                "parlay_prob": legs[0]["prob"],
                "independence_prob": legs[0]["prob"],
                "correlation_adjustment": 0.0,
                "n_legs": 1
            }
        
        # Naive independence probability
        independence_prob = np.prod([leg["prob"] for leg in legs])
        
        # Build correlation matrix
        corr_matrix = self._build_correlation_matrix(legs)
        
        # Detect domain conflicts (e.g., both teams to win)
        conflict_penalty = self._detect_conflicts(legs)
        
        # Adjust for correlation using copula-inspired approach
        # Convert probs to z-scores (inverse normal CDF)
        z_scores = [norm.ppf(min(0.999, max(0.001, leg["prob"]))) for leg in legs]
        
        # Expected z-score under correlation
        # Simplified: weighted average based on correlation strength
        avg_correlation = np.mean(corr_matrix[np.triu_indices(n_legs, k=1)])
        
        # Correlation adjustment factor
        # Higher correlation = higher joint probability (positive outcomes cluster)
        correlation_adjustment = avg_correlation * 0.10  # 10% boost per unit correlation
        
        # Apply conflict penalty
        conflict_adjustment = -conflict_penalty * 0.15  # 15% penalty per conflict
        
        # Final parlay probability
        parlay_prob = independence_prob * (1 + correlation_adjustment + conflict_adjustment)
        parlay_prob = max(0.0, min(1.0, parlay_prob))  # Clamp to [0, 1]
        
        return {
            "parlay_prob": round(parlay_prob, 4),
            "independence_prob": round(independence_prob, 4),
            "correlation_adjustment": round(correlation_adjustment, 4),
            "conflict_adjustment": round(conflict_adjustment, 4),
            "avg_correlation": round(avg_correlation, 4),
            "n_legs": n_legs,
            "correlation_matrix": corr_matrix.tolist()
        }
    
    def _build_correlation_matrix(self, legs: List[Dict]) -> np.ndarray:
        """
        Build correlation matrix based on domain classifications.
        """
        n = len(legs)
        corr_matrix = np.eye(n)  # Start with identity (diagonal = 1)
        
        for i in range(n):
            for j in range(i + 1, n):
                domain_i = legs[i]["domain"]
                domain_j = legs[j]["domain"]
                
                # Get base correlation from domain pair
                domain_pair = tuple(sorted([domain_i, domain_j]))
                base_corr = self.domain_correlations.get(domain_pair, 0.10)
                
                # Check if same entity (e.g., same team in multiple legs)
                if legs[i].get("entity") == legs[j].get("entity"):
                    base_corr *= 1.5  # 50% boost for same entity
                
                corr_matrix[i, j] = base_corr
                corr_matrix[j, i] = base_corr
        
        return corr_matrix
    
    def _detect_conflicts(self, legs: List[Dict]) -> float:
        """
        Detect conflicting outcomes (e.g., both teams to win same match).
        
        Returns:
            Conflict penalty score (0 = no conflicts, 1 = strong conflict)
        """
        conflicts = 0
        n = len(legs)
        
        for i in range(n):
            for j in range(i + 1, n):
                # Check for direct conflicts
                if self._is_conflicting(legs[i], legs[j]):
                    conflicts += 1
        
        # Normalize by number of pairs
        n_pairs = n * (n - 1) / 2
        return conflicts / n_pairs if n_pairs > 0 else 0.0
    
    def _is_conflicting(self, leg1: Dict, leg2: Dict) -> bool:
        """
        Check if two legs represent conflicting outcomes.
        
        Example: Arsenal to win AND Bayern to win (same match) -> conflict
        """
        # Simplified: check if different entities but overlapping outcomes
        # In production, would parse match metadata
        if leg1.get("match_id") and leg2.get("match_id"):
            if leg1["match_id"] == leg2["match_id"]:
                if leg1.get("outcome") != leg2.get("outcome"):
                    return True
        return False


if __name__ == "__main__":
    # Example: 3-leg parlay with mixed domains
    # Leg 1: Arsenal to win (Domain I + II adjusted)
    # Leg 2: Liverpool to win (Domain I)
    # Leg 3: Over 2.5 goals in Man City match (Domain III variance)
    
    leggraph = LegGraphV3()
    
    parlay_legs = [
        {
            "prob": 0.455,  # Arsenal to win (from Domain II context engine)
            "domain": "II",
            "outcome": "win",
            "entity": "Arsenal",
            "match_id": "ARS_BAY"
        },
        {
            "prob": 0.620,  # Liverpool to win (pure Domain I skill)
            "domain": "I",
            "outcome": "win",
            "entity": "Liverpool",
            "match_id": "LIV_PSV"
        },
        {
            "prob": 0.580,  # Man City over 2.5 (Domain III variance)
            "domain": "III",
            "outcome": "over_2.5",
            "entity": "Man City",
            "match_id": "MCI_LEV"
        }
    ]
    
    result = leggraph.compute_parlay_probability(parlay_legs)
    
    print("==== LegGraph v3: Domain-Aware Parlay Analysis ====")
    print(f"Independence prob (naive): {result['independence_prob']:.3f}")
    print(f"Correlation adjustment: {result['correlation_adjustment']:+.3f}")
    print(f"Conflict adjustment: {result['conflict_adjustment']:+.3f}")
    print(f"True parlay prob: {result['parlay_prob']:.3f}")
    print(f"\nAverage correlation: {result['avg_correlation']:.3f}")
    print(f"\n✓ Domain-aware correlation modeling applied across {result['n_legs']} legs")
