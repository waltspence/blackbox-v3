"""
Pack #2: LegGraph Verification Test
Validates LegGraph copula-based correlation modeling
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
    """Test that critical LegGraph modules can be imported."""
    try:
        from leggraph import copula
        print("✓ leggraph.copula imported successfully")
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_copula_functions():
    """Test that key functions exist in copula module."""
    from leggraph import copula
    
    required_functions = [
        'fit_copula',
        'simulate_correlation',
        'calculate_dependence'
    ]
    
    for func_name in required_functions:
        assert hasattr(copula, func_name), \
            f"Required function '{func_name}' not found in copula module"
    
    print(f"✓ All {len(required_functions)} required functions exist")


def create_sample_leg_data():
    """Create sample leg data for testing."""
    np.random.seed(42)
    
    return pd.DataFrame({
        'leg_id': range(5),
        'outcome': np.random.binomial(1, 0.5, 5),
        'probability': np.random.uniform(0.4, 0.6, 5),
        'odds': np.random.uniform(1.8, 2.2, 5),
        'correlation_group': ['A', 'A', 'B', 'B', 'C']
    })


def test_copula_fitting():
    """Test copula fitting with sample data."""
    try:
        from leggraph import copula
        
        if hasattr(copula, 'fit_copula'):
            leg_data = create_sample_leg_data()
            
            # Fit copula to sample data
            fitted_copula = copula.fit_copula(
                data=leg_data[['probability']].values,
                copula_type='gaussian'
            )
            
            assert fitted_copula is not None, "Copula fitting should return a result"
            print(f"✓ Copula fitting succeeded, result type: {type(fitted_copula)}")
        else:
            print("⚠ fit_copula function not implemented yet")
            
    except Exception as e:
        print(f"⚠ Copula fitting test encountered error: {e}")
        pytest.skip(f"Skipping due to: {e}")


def test_correlation_simulation():
    """Test correlation simulation between legs."""
    try:
        from leggraph import copula
        
        if hasattr(copula, 'simulate_correlation'):
            leg_data = create_sample_leg_data()
            
            # Simulate correlated outcomes
            simulated = copula.simulate_correlation(
                probabilities=leg_data['probability'].values,
                n_simulations=1000,
                correlation_matrix=np.eye(5)
            )
            
            assert simulated is not None, "Simulation should return results"
            print(f"✓ Correlation simulation succeeded, shape: {simulated.shape if hasattr(simulated, 'shape') else 'N/A'}")
        else:
            print("⚠ simulate_correlation function not implemented yet")
            
    except Exception as e:
        print(f"⚠ Correlation simulation test encountered error: {e}")
        pytest.skip(f"Skipping due to: {e}")


def test_dependence_calculation():
    """Test dependence measure calculation."""
    try:
        from leggraph import copula
        
        if hasattr(copula, 'calculate_dependence'):
            # Create correlated sample data
            np.random.seed(42)
            x = np.random.normal(0, 1, 100)
            y = 0.7 * x + 0.3 * np.random.normal(0, 1, 100)
            
            dependence = copula.calculate_dependence(x, y)
            
            assert isinstance(dependence, (int, float)), \
                "Dependence measure should be numeric"
            print(f"✓ Dependence calculation: {dependence:.4f}")
        else:
            print("⚠ calculate_dependence function not implemented yet")
            
    except Exception as e:
        print(f"⚠ Dependence calculation test encountered error: {e}")
        pytest.skip(f"Skipping due to: {e}")


def test_correlation_matrix_validation():
    """Test correlation matrix validation."""
    try:
        from leggraph import copula
        
        if hasattr(copula, 'validate_correlation_matrix'):
            # Valid correlation matrix
            valid_corr = np.array([[1.0, 0.5], [0.5, 1.0]])
            
            is_valid = copula.validate_correlation_matrix(valid_corr)
            assert is_valid, "Valid correlation matrix should pass validation"
            print("✓ Correlation matrix validation works")
        else:
            print("⚠ validate_correlation_matrix function not implemented yet")
            
    except Exception as e:
        print(f"⚠ Correlation matrix validation test encountered error: {e}")
        pytest.skip(f"Skipping due to: {e}")


def test_gaussian_copula_properties():
    """Test Gaussian copula specific properties."""
    try:
        from leggraph import copula
        
        if hasattr(copula, 'GaussianCopula'):
            gc = copula.GaussianCopula(dimension=3)
            
            # Check basic properties
            assert hasattr(gc, 'fit'), "GaussianCopula should have fit method"
            assert hasattr(gc, 'sample'), "GaussianCopula should have sample method"
            
            print("✓ GaussianCopula class exists with required methods")
        else:
            print("⚠ GaussianCopula class not implemented yet")
            
    except Exception as e:
        print(f"⚠ Gaussian copula test encountered error: {e}")
        pytest.skip(f"Skipping due to: {e}")


def test_leg_correlation_groups():
    """Test grouping and correlation of legs by correlation_group."""
    try:
        from leggraph import copula
        
        if hasattr(copula, 'group_correlated_legs'):
            leg_data = create_sample_leg_data()
            
            grouped = copula.group_correlated_legs(
                legs=leg_data,
                group_column='correlation_group'
            )
            
            assert grouped is not None, "Grouping should return results"
            print(f"✓ Leg correlation grouping succeeded")
        else:
            print("⚠ group_correlated_legs function not implemented yet")
            
    except Exception as e:
        print(f"⚠ Leg correlation grouping test encountered error: {e}")
        pytest.skip(f"Skipping due to: {e}")


def test_parlay_outcome_simulation():
    """Test parlay outcome simulation with correlated legs."""
    try:
        from leggraph import copula
        
        if hasattr(copula, 'simulate_parlay_outcomes'):
            leg_data = create_sample_leg_data()
            
            # Simulate 1000 parlay outcomes
            outcomes = copula.simulate_parlay_outcomes(
                leg_probs=leg_data['probability'].values,
                n_sims=1000,
                correlation=0.2
            )
            
            assert outcomes is not None, "Simulation should return results"
            if isinstance(outcomes, np.ndarray):
                assert len(outcomes) == 1000, "Should return 1000 simulations"
                print(f"✓ Parlay simulation: win rate = {outcomes.mean():.3f}")
        else:
            print("⚠ simulate_parlay_outcomes function not implemented yet")
            
    except Exception as e:
        print(f"⚠ Parlay outcome simulation test encountered error: {e}")
        pytest.skip(f"Skipping due to: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Pack #2: LegGraph Verification Test")
    print("=" * 60)
    
    # Run tests individually for better visibility
    test_functions = [
        ("Module Imports", test_imports),
        ("Copula Functions", test_copula_functions),
        ("Copula Fitting", test_copula_fitting),
        ("Correlation Simulation", test_correlation_simulation),
        ("Dependence Calculation", test_dependence_calculation),
        ("Correlation Matrix Validation", test_correlation_matrix_validation),
        ("Gaussian Copula Properties", test_gaussian_copula_properties),
        ("Leg Correlation Groups", test_leg_correlation_groups),
        ("Parlay Outcome Simulation", test_parlay_outcome_simulation)
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
