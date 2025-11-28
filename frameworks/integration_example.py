"""Integration Example: Wiring GameStory into Three-Domain Pipeline
--------------------------------------------------------------
Demonstrates safe application of adjustments using clamp()
to prevent probability breakage.
"""

from game_story import build_game_context, get_domain_adjustments, clamp

def mock_domain_i_engine(match_data):
    """Mock engine returning a raw win probability."""
    # Suppose Domain I says Home Win is 60%
    return 0.60

def run_pipeline_demo():
    # 1. Incoming Data (Knockout Scenario)
    match_data = {
        'competition': {'name': 'UCL', 'phase': 'Knockout', 'leg': 2},
        'home_team': {
            'incentive': 'neutral',
            'aggregate_gap': -2.0,  # Down by 2 goals!
            'form_w5': 'WWDWW'
        },
        'away_team': {'form_w5': 'DDLDW'}
    }

    print("--- Pipeline Start ---")

    # 2. Build Context (Layer 0)
    ctx = build_game_context(match_data)
    adjs = get_domain_adjustments(ctx)

    print(f"Narrative: {ctx.narrative}")
    print(f"Adjustments: {adjs}")

    # 3. Domain I: Skill (Base Probability)
    base_prob = mock_domain_i_engine(match_data)

    # 4. Apply Adjustment SAFELY
    # We apply the skill adjustment (delta) to the base probability.
    # Then we CLAMP the result so it never hits 0.0 or 1.0.
    skill_delta = adjs['domain_i_adjustment']
    final_prob = clamp(base_prob + skill_delta, 0.01, 0.99)

    print(f"Base Prob: {base_prob:.2f}")
    print(f"Skill Adj: {skill_delta:+.2f}")
    print(f"Final Prob: {final_prob:.2f}")

    # 5. Domain III: Variance Injection
    # If we are running a Monte Carlo sim, we widen the distribution
    base_sigma = 1.2
    variance_boost = adjs['domain_iii_variance_boost']
    final_sigma = base_sigma + variance_boost

    print(f"Simulation Sigma: {final_sigma:.2f} (Boost: +{variance_boost:.2f})")

    if 'chasing_game_script' in adjs['risk_flags']:
        print("ALERT: High Volatility! Reduce bet sizing.")

if __name__ == "__main__":
    run_pipeline_demo()
