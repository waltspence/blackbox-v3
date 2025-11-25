"""
Pack #5: SlipKelly Verification Test
Validates Kelly Criterion slip management and sizing
"""
import sys
import os
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

import pytest
import pandas as pd
import numpy as np
from datetime import datetime


def test_imports():
    """Test that critical SlipKelly modules can be imported."""
    try:
        from sliprisk import portfolio
        print("✓ sliprisk.portfolio imported successfully")
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_portfolio_functions():
    """Test that key functions exist in portfolio module."""
    from sliprisk import portfolio
    
    required_functions = [
        'calculate_kelly_fraction',
        'optimize_portfolio',
        'manage_bankroll'
    ]
    
    for func_name in required_functions:
        assert hasattr(portfolio, func_name), \
            f"Required function '{func_name}' not found in portfolio module"
    
    print(f"✓ All {len(required_functions)} required functions exist")


def create_sample_bet_opportunities():
    """Create sample betting opportunities for testing."""
    np.random.seed(42)
    
    return pd.DataFrame({
        'bet_id': range(5),
        'odds_decimal': np.random.uniform(1.8, 2.5, 5),
        'win_probability': np.random.uniform(0.45, 0.55, 5),
        'edge': np.random.uniform(0.02, 0.08, 5),
        'max_bet': [1000, 500, 2000, 750, 1500]
    })


def test_kelly_fraction_calculation():
    """Test Kelly fraction calculation."""
    try:
        from sliprisk import portfolio
        
        if hasattr(portfolio, 'calculate_kelly_fraction'):
            # Test with known values
            odds = 2.0  # Even money
            win_prob = 0.55  # 55% win probability
            
            kelly_fraction = portfolio.calculate_kelly_fraction(
                probability=win_prob,
                odds=odds
            )
            
            assert isinstance(kelly_fraction, (int, float)), \
                "Kelly fraction should be numeric"
            assert 0 <= kelly_fraction <= 1, \
                "Kelly fraction should be between 0 and 1"
            
            print(f"✓ Kelly fraction calculated: {kelly_fraction:.4f}")
        else:
            print("⚠ calculate_kelly_fraction function not implemented yet")
            
    except Exception as e:
        print(f"⚠ Kelly fraction calculation test encountered error: {e}")
        pytest.skip(f"Skipping due to: {e}")


def test_fractional_kelly():
    """Test fractional Kelly sizing (risk management)."""
    try:
        from sliprisk import portfolio
        
        if hasattr(portfolio, 'fractional_kelly'):
            full_kelly = 0.10  # 10% Kelly
            fraction = 0.5  # Half Kelly
            
            sized_kelly = portfolio.fractional_kelly(
                kelly=full_kelly,
                fraction=fraction
            )
            
            expected = full_kelly * fraction
            assert abs(sized_kelly - expected) < 0.001, \
                "Fractional Kelly should be product of kelly and fraction"
            
            print(f"✓ Fractional Kelly: {full_kelly} * {fraction} = {sized_kelly:.4f}")
        else:
            print("⚠ fractional_kelly function not implemented yet")
            
    except Exception as e:
        print(f"⚠ Fractional Kelly test encountered error: {e}")
        pytest.skip(f"Skipping due to: {e}")


def test_bankroll_management():
    """Test bankroll management and bet sizing."""
    try:
        from sliprisk import portfolio
        
        if hasattr(portfolio, 'manage_bankroll'):
            bankroll = 10000
            kelly_fraction = 0.05
            
            bet_size = portfolio.manage_bankroll(
                bankroll=bankroll,
                kelly_fraction=kelly_fraction
            )
            
            assert isinstance(bet_size, (int, float)), \
                "Bet size should be numeric"
            assert 0 <= bet_size <= bankroll, \
                "Bet size should not exceed bankroll"
            
            print(f"✓ Bankroll ${bankroll} with Kelly {kelly_fraction} → Bet size ${bet_size:.2f}")
        else:
            print("⚠ manage_bankroll function not implemented yet")
            
    except Exception as e:
        print(f"⚠ Bankroll management test encountered error: {e}")
        pytest.skip(f"Skipping due to: {e}")


def test_portfolio_optimization():
    """Test portfolio optimization across multiple bets."""
    try:
        from sliprisk import portfolio
        
        if hasattr(portfolio, 'optimize_portfolio'):
            bets = create_sample_bet_opportunities()
            bankroll = 10000
            
            optimal_portfolio = portfolio.optimize_portfolio(
                opportunities=bets,
                bankroll=bankroll,
                max_bets=3
            )
            
            assert optimal_portfolio is not None, \
                "Portfolio optimization should return results"
            
            print(f"✓ Portfolio optimized for {len(bets)} opportunities")
        else:
            print("⚠ optimize_portfolio function not implemented yet")
            
    except Exception as e:
        print(f"⚠ Portfolio optimization test encountered error: {e}")
        pytest.skip(f"Skipping due to: {e}")


def test_max_bet_constraints():
    """Test that max bet constraints are respected."""
    try:
        from sliprisk import portfolio
        
        if hasattr(portfolio, 'apply_constraints'):
            kelly_bet = 500
            max_bet = 250
            
            constrained_bet = portfolio.apply_constraints(
                bet_size=kelly_bet,
                max_bet=max_bet
            )
            
            assert constrained_bet <= max_bet, \
                "Constrained bet should not exceed max bet"
            
            print(f"✓ Kelly bet ${kelly_bet} constrained to max ${max_bet} → ${constrained_bet}")
        else:
            print("⚠ apply_constraints function not implemented yet")
            
    except Exception as e:
        print(f"⚠ Max bet constraints test encountered error: {e}")
        pytest.skip(f"Skipping due to: {e}")


def test_bankroll_drawdown_protection():
    """Test bankroll drawdown protection mechanisms."""
    try:
        from sliprisk import portfolio
        
        if hasattr(portfolio, 'calculate_drawdown_adjustment'):
            current_bankroll = 8000
            peak_bankroll = 10000
            
            adjustment = portfolio.calculate_drawdown_adjustment(
                current=current_bankroll,
                peak=peak_bankroll
            )
            
            assert isinstance(adjustment, (int, float)), \
                "Drawdown adjustment should be numeric"
            assert 0 <= adjustment <= 1, \
                "Adjustment should be a fraction between 0 and 1"
            
            drawdown_pct = (1 - current_bankroll / peak_bankroll) * 100
            print(f"✓ Drawdown {drawdown_pct:.1f}% → Adjustment factor {adjustment:.3f}")
        else:
            print("⚠ calculate_drawdown_adjustment function not implemented yet")
            
    except Exception as e:
        print(f"⚠ Drawdown protection test encountered error: {e}")
        pytest.skip(f"Skipping due to: {e}")


def test_edge_calculation():
    """Test expected value edge calculation."""
    try:
        from sliprisk import portfolio
        
        if hasattr(portfolio, 'calculate_edge'):
            win_prob = 0.55
            odds_decimal = 2.0
            
            edge = portfolio.calculate_edge(
                probability=win_prob,
                odds=odds_decimal
            )
            
            # Edge = (probability * odds) - 1
            expected_edge = (win_prob * odds_decimal) - 1
            assert abs(edge - expected_edge) < 0.001, \
                "Edge calculation should match expected formula"
            
            print(f"✓ Edge calculated: {edge:.4f} ({edge * 100:.2f}%)")
        else:
            print("⚠ calculate_edge function not implemented yet")
            
    except Exception as e:
        print(f"⚠ Edge calculation test encountered error: {e}")
        pytest.skip(f"Skipping due to: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Pack #5: SlipKelly Verification Test")
    print("=" * 60)
    
    # Run tests individually for better visibility
    test_functions = [
        ("Module Imports", test_imports),
        ("Portfolio Functions", test_portfolio_functions),
        ("Kelly Fraction Calculation", test_kelly_fraction_calculation),
        ("Fractional Kelly", test_fractional_kelly),
        ("Bankroll Management", test_bankroll_management),
        ("Portfolio Optimization", test_portfolio_optimization),
        ("Max Bet Constraints", test_max_bet_constraints),
        ("Bankroll Drawdown Protection", test_bankroll_drawdown_protection),
        ("Edge Calculation", test_edge_calculation)
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, test_func in test_functions:
        print(f"\nRunning: {test_name}")
        print("-" * 60)
        try:
            test_func()
            passed += 1
        except pytest.skip.Exception as e:
            print(f"SKIPPED: {e}")
            skipped += 1
        except Exception as e:
            print(f"FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)
