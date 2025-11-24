#!/usr/bin/env python3
"""
Three-Domain Pipeline - Master Orchestrator

This script demonstrates the complete BlackBox v3 three-domain betting framework:
- Domain I (Entity vs Entity): Pure competitive skill baseline from fairline_v3
- Domain II (Entity vs Environment): Environmental context adjustments
- Domain III (Entity vs Self): Variance and uncertainty overlay

The pipeline integrates all three domains with market psychology analysis
to produce final betting recommendations with domain-aware Kelly sizing.
"""

import sys
from typing import Dict, Optional
from datetime import datetime

# Import three-domain engines
try:
    from core.fairline_v3 import FairLineV3
    from core.context_engine import ContextEngine
    from core.variance_overlay import VarianceOverlay
    from engines.crowdlens_v3 import CrowdLensV3
except ImportError:
    print("Warning: Import paths adjusted for standalone execution")
    pass


def run_three_domain_analysis(
    home_team: str,
    away_team: str,
    home_xg: float,
    away_xg: float,
    tactical_edge: float,
    travel_km: int,
    home_rest_days: int,
    away_rest_days: int,
    home_fixture_count: int,
    away_fixture_count: int,
    recent_xg: float,
    seasonal_xg: float,
    pressure_share: float,
    sample_size: int,
    market_odds: float,
    verbose: bool = True
) -> Dict:
    """
    Execute complete three-domain betting analysis pipeline.
    
    Args:
        home_team: Home team name
        away_team: Away team name
        home_xg: Home team expected goals per 90
        away_xg: Away team expected goals per 90
        tactical_edge: Tactical matchup advantage (-1.0 to 1.0)
        travel_km: Distance away team traveled
        home_rest_days: Days rest for home team
        away_rest_days: Days rest for away team
        home_fixture_count: Fixture congestion for home (last 30 days)
        away_fixture_count: Fixture congestion for away (last 30 days)
        recent_xg: Recent xG performance (last 5 games)
        seasonal_xg: Season average xG
        pressure_share: High-pressure possession share
        sample_size: Number of games in sample
        market_odds: Closing market odds (decimal)
        verbose: Print detailed analysis output
    
    Returns:
        Dictionary containing:
        - domain_i: Pure skill baseline (Entity vs Entity)
        - domain_ii: Environmental adjustments (Entity vs Environment)
        - domain_iii: Variance bands (Entity vs Self)
        - market_psychology: Market inefficiency analysis
        - final_edge: Recommended betting edge
        - kelly_fraction: Suggested Kelly stake size
        - recommendation: Action recommendation
    """
    results = {}
    
    # ========================================
    # DOMAIN I: Entity vs Entity (Pure Skill)
    # ========================================
    if verbose:
        print("\n" + "="*60)
        print("DOMAIN I: ENTITY VS ENTITY (Pure Competitive Skill)")
        print("="*60)
    
    fairline = FairLineV3()
    domain_i = fairline.compute_baseline(
        home_xg=home_xg,
        away_xg=away_xg,
        tactical_edge=tactical_edge
    )
    
    results["domain_i"] = domain_i
    
    if verbose:
        print(f"\nMatch: {home_team} vs {away_team}")
        print(f"Home xG/90: {home_xg:.2f}")
        print(f"Away xG/90: {away_xg:.2f}")
        print(f"Tactical Edge: {tactical_edge:+.2f}")
        print(f"\nDomain I Baseline Win Probability: {domain_i['win_prob']:.3f}")
        print(f"Fair Odds: {domain_i['fair_odds']:.2f}")
    
    # ========================================
    # DOMAIN II: Entity vs Environment
    # ========================================
    if verbose:
        print("\n" + "="*60)
        print("DOMAIN II: ENTITY VS ENVIRONMENT (Contextual Adjustments)")
        print("="*60)
    
    context_engine = ContextEngine()
    domain_ii = context_engine.apply_context(
        baseline_prob=domain_i["win_prob"],
        travel_km=travel_km,
        rest_days_home=home_rest_days,
        rest_days_away=away_rest_days,
        fixture_congestion_home=home_fixture_count,
        fixture_congestion_away=away_fixture_count
    )
    
    results["domain_ii"] = domain_ii
    
    if verbose:
        print(f"\nTravel Distance: {travel_km}km")
        print(f"Rest Days: Home={home_rest_days}, Away={away_rest_days}")
        print(f"Fixture Congestion: Home={home_fixture_count}, Away={away_fixture_count}")
        print(f"\nContextual Adjustment: {domain_ii['context_adjustment']:+.4f}")
        print(f"Adjusted Win Probability: {domain_ii['adjusted_prob']:.3f}")
    
    # ========================================
    # DOMAIN III: Entity vs Self (Variance)
    # ========================================
    if verbose:
        print("\n" + "="*60)
        print("DOMAIN III: ENTITY VS SELF (Variance & Uncertainty)")
        print("="*60)
    
    variance_overlay = VarianceOverlay()
    domain_iii = variance_overlay.apply_variance(
        point_estimate=domain_ii["adjusted_prob"],
        recent_xg=recent_xg,
        seasonal_xg=seasonal_xg,
        pressure_share=pressure_share,
        sample_size=sample_size
    )
    
    results["domain_iii"] = domain_iii
    
    if verbose:
        print(f"\nForm Volatility: {domain_iii['form_volatility']:.4f}")
        print(f"Process Volatility: {domain_iii['process_volatility']:.4f}")
        print(f"Sample Uncertainty: {domain_iii['sample_uncertainty']:.4f}")
        print(f"\nConfidence Interval: [{domain_iii['lower_bound']:.3f}, {domain_iii['upper_bound']:.3f}]")
        print(f"Point Estimate: {domain_iii['point_estimate']:.3f}")
    
    # ========================================
    # MARKET PSYCHOLOGY ANALYSIS
    # ========================================
    if verbose:
        print("\n" + "="*60)
        print("MARKET PSYCHOLOGY: Crowd Inefficiency Detection")
        print("="*60)
    
    crowdlens = CrowdLensV3()
    market_analysis = crowdlens.analyze_market(
        domain_i_prob=domain_i["win_prob"],
        domain_ii_prob=domain_ii["adjusted_prob"],
        domain_iii_prob=domain_iii["point_estimate"],
        market_odds=market_odds
    )
    
    results["market_psychology"] = market_analysis
    
    if verbose:
        market_prob = 1.0 / market_odds
        print(f"\nMarket Odds: {market_odds:.2f} (Implied Prob: {market_prob:.3f})")
        print(f"Model Fair Value: {domain_iii['point_estimate']:.3f}")
        print(f"Edge: {market_analysis['edge']:.4f} ({market_analysis['edge']*100:+.2f}%)")
        print(f"Primary Bias: {market_analysis['primary_bias']}")
    
    # ========================================
    # FINAL RECOMMENDATION
    # ========================================
    if verbose:
        print("\n" + "="*60)
        print("FINAL BETTING RECOMMENDATION")
        print("="*60)
    
    # Calculate Kelly fraction based on edge and confidence
    edge = market_analysis["edge"]
    confidence_width = domain_iii["upper_bound"] - domain_iii["lower_bound"]
    confidence_adjustment = max(0.5, 1.0 - confidence_width)  # Reduce stake with wider CI
    
    kelly_fraction = 0.0
    recommendation = "PASS"
    
    if edge > 0.03:  # Minimum 3% edge required
        # Full Kelly: edge / odds
        full_kelly = edge / (market_odds - 1.0)
        # Fractional Kelly with confidence adjustment
        kelly_fraction = full_kelly * 0.25 * confidence_adjustment  # Quarter Kelly with CI adjustment
        recommendation = "BET" if kelly_fraction > 0.01 else "SMALL_BET"
    elif edge < -0.03:
        recommendation = "AVOID"
    
    results["final_edge"] = edge
    results["kelly_fraction"] = kelly_fraction
    results["recommendation"] = recommendation
    
    if verbose:
        print(f"\nEdge: {edge:+.4f} ({edge*100:+.2f}%)")
        print(f"Kelly Fraction: {kelly_fraction:.4f} ({kelly_fraction*100:.2f}% of bankroll)")
        print(f"Recommendation: {recommendation}")
        print("\n" + "="*60)
    
    return results


if __name__ == "__main__":
    # Real-world example: Arsenal vs Bayern Munich (UCL 2024)
    print("\n" + "#"*60)
    print("# BlackBox v3 Three-Domain Pipeline")
    print("# Arsenal vs Bayern Munich - UEFA Champions League")
    print("#"*60)
    
    analysis = run_three_domain_analysis(
        home_team="Arsenal",
        away_team="Bayern Munich",
        # Domain I: Pure skill metrics
        home_xg=1.8,
        away_xg=2.1,
        tactical_edge=-0.15,  # Bayern slight tactical edge
        # Domain II: Environmental context
        travel_km=950,
        home_rest_days=7,
        away_rest_days=3,
        home_fixture_count=3,
        away_fixture_count=1,
        # Domain III: Variance factors
        recent_xg=2.1,  # Recent form above season average
        seasonal_xg=1.8,
        pressure_share=0.25,
        sample_size=12,
        # Market data
        market_odds=2.50,  # Arsenal closing at +150 (2.50 decimal)
        verbose=True
    )
    
    print("\n" + "#"*60)
    print("# Analysis Complete")
    print("#"*60)
