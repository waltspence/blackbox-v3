#!/usr/bin/env python3
"""
Domain-Aware Kelly Criterion Stake Sizing

Implements fractional Kelly criterion with Domain III confidence interval adjustments.
Follows Gemini's recommendation for production-ready risk management.

Key features:
- Fractional Kelly (Kelly/2 or Kelly/4) for bankroll preservation
- Domain III CI width adjustment for uncertainty
- Maximum stake caps for safety
- Minimum edge thresholds
"""

from typing import Dict, Optional
import math


class DomainAwareKelly:
    """
    Kelly Criterion calculator with domain-aware adjustments.
    
    Implements:
    - Full Kelly: f* = (bp - q) / b
    - Fractional Kelly: f = f* * fraction
    - Domain III CI adjustment: f_adj = f * confidence_factor
    
    Where:
    - b = odds - 1 (decimal odds minus 1)
    - p = win probability (from Domain III point estimate)
    - q = 1 - p (loss probability)
    - CI width = domain_iii['upper_bound'] - domain_iii['lower_bound']
    """
    
    def __init__(
        self,
        kelly_fraction: float = 0.25,  # Quarter Kelly (conservative)
        max_stake: float = 0.05,  # 5% bankroll maximum
        min_edge: float = 0.03,  # 3% minimum edge required
        ci_penalty: bool = True  # Apply Domain III CI width penalty
    ):
        """
        Initialize Kelly calculator.
        
        Args:
            kelly_fraction: Fractional Kelly multiplier (0.25 = Kelly/4, 0.5 = Kelly/2)
            max_stake: Maximum stake as fraction of bankroll
            min_edge: Minimum edge required to bet
            ci_penalty: Apply confidence interval width adjustment
        """
        self.kelly_fraction = kelly_fraction
        self.max_stake = max_stake
        self.min_edge = min_edge
        self.ci_penalty = ci_penalty
    
    def calculate_stake(
        self,
        edge: float,
        odds: float,
        domain_iii: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate optimal stake size with domain-aware adjustments.
        
        Args:
            edge: Expected edge (model_prob - market_prob)
            odds: Market odds (decimal format)
            domain_iii: Domain III variance data with CI bounds
        
        Returns:
            Dictionary with:
            - full_kelly: Full Kelly fraction
            - fractional_kelly: Adjusted Kelly fraction
            - confidence_factor: CI width adjustment factor
            - final_stake: Recommended stake (fraction of bankroll)
            - recommendation: BET/SMALL_BET/PASS/AVOID
            - domain: "III" (Entity vs Self - confidence-aware sizing)
        """
        # Check minimum edge threshold
        if edge < self.min_edge:
            return {
                "full_kelly": 0.0,
                "fractional_kelly": 0.0,
                "confidence_factor": 0.0,
                "final_stake": 0.0,
                "recommendation": "PASS" if edge > 0 else "AVOID",
                "domain": "III",
                "reason": f"Edge {edge:.4f} below minimum {self.min_edge}"
            }
        
        # Calculate model probability from edge and market odds
        market_prob = 1.0 / odds
        model_prob = market_prob + edge
        
        # Full Kelly formula: f* = (bp - q) / b
        b = odds - 1.0  # Decimal odds minus 1
        p = model_prob
        q = 1.0 - p
        
        # Full Kelly fraction
        full_kelly = (b * p - q) / b
        
        # Apply fractional Kelly for bankroll preservation
        fractional_kelly = full_kelly * self.kelly_fraction
        
        # Domain III: Confidence interval adjustment
        confidence_factor = 1.0
        if self.ci_penalty and domain_iii:
            ci_width = domain_iii.get('upper_bound', p) - domain_iii.get('lower_bound', p)
            # Wider CI = lower confidence = smaller stake
            # Typical CI width: 0.05-0.15
            # Factor range: 0.5 (wide) to 1.0 (narrow)
            confidence_factor = max(0.5, 1.0 - (ci_width * 2.0))
        
        # Apply confidence adjustment
        final_stake = fractional_kelly * confidence_factor
        
        # Apply maximum stake cap
        final_stake = min(final_stake, self.max_stake)
        
        # Determine recommendation
        if final_stake >= 0.02:  # 2% or more
            recommendation = "BET"
        elif final_stake >= 0.005:  # 0.5% to 2%
            recommendation = "SMALL_BET"
        else:
            recommendation = "PASS"
        
        return {
            "full_kelly": full_kelly,
            "fractional_kelly": fractional_kelly,
            "confidence_factor": confidence_factor,
            "final_stake": final_stake,
            "recommendation": recommendation,
            "domain": "III",
            "edge": edge,
            "odds": odds,
            "ci_width": domain_iii.get('upper_bound', 0) - domain_iii.get('lower_bound', 0) if domain_iii else 0
        }
    
    def format_stake(self, stake_result: Dict, bankroll: Optional[float] = None) -> str:
        """
        Format stake result for display.
        
        Args:
            stake_result: Result from calculate_stake()
            bankroll: Optional bankroll size for unit calculation
        
        Returns:
            Formatted string
        """
        lines = []
        lines.append(f"Edge: {stake_result['edge']:+.4f} ({stake_result['edge']*100:+.2f}%)")
        lines.append(f"Full Kelly: {stake_result['full_kelly']:.4f} ({stake_result['full_kelly']*100:.2f}%)")
        lines.append(f"Fractional Kelly: {stake_result['fractional_kelly']:.4f}")
        lines.append(f"CI Confidence Factor: {stake_result['confidence_factor']:.3f}")
        lines.append(f"Final Stake: {stake_result['final_stake']:.4f} ({stake_result['final_stake']*100:.2f}%)")
        
        if bankroll:
            units = stake_result['final_stake'] * bankroll
            lines.append(f"Units: ${units:.2f}")
        
        lines.append(f"Recommendation: {stake_result['recommendation']}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Example: Arsenal vs Bayern with 5% edge but wide CI
    print("\n" + "="*60)
    print("Domain-Aware Kelly Criterion Example")
    print("="*60)
    
    kelly = DomainAwareKelly(
        kelly_fraction=0.25,  # Quarter Kelly
        max_stake=0.05,  # 5% max
        min_edge=0.03,  # 3% min edge
        ci_penalty=True
    )
    
    # Scenario 1: Strong edge, narrow CI (high confidence)
    domain_iii_narrow = {
        'point_estimate': 0.45,
        'lower_bound': 0.42,
        'upper_bound': 0.48,  # CI width = 0.06 (narrow)
    }
    
    result1 = kelly.calculate_stake(
        edge=0.05,  # 5% edge
        odds=2.50,
        domain_iii=domain_iii_narrow
    )
    
    print("\nScenario 1: Strong edge + Narrow CI (High Confidence)")
    print(kelly.format_stake(result1, bankroll=10000))
    
    # Scenario 2: Strong edge, wide CI (lower confidence)
    domain_iii_wide = {
        'point_estimate': 0.45,
        'lower_bound': 0.38,
        'upper_bound': 0.52,  # CI width = 0.14 (wide)
    }
    
    result2 = kelly.calculate_stake(
        edge=0.05,  # Same 5% edge
        odds=2.50,
        domain_iii=domain_iii_wide
    )
    
    print("\nScenario 2: Strong edge + Wide CI (Lower Confidence)")
    print(kelly.format_stake(result2, bankroll=10000))
    
    print("\n" + "="*60)
    print("Note: Scenario 2 has smaller stake due to CI width penalty")
    print("="*60 + "\n")
