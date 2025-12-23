"""Unit tests for Suppressive Script Prop Betting Module"""

import unittest
import sys
import os
from dataclasses import dataclass
from typing import List

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from frameworks.suppressive_script_props import (
    SuppressiveScriptEngine,
    DrawPropSignal,
    SuppressiveScriptAnalysis
)


# Mock GameData for testing
@dataclass
class MockTeam:
    league_position: int
    motivation: str = 'neutral'
    avg_goals_scored: float = 1.5
    
@dataclass  
class MockGameData:
    home_team: MockTeam
    away_team: MockTeam
    weather_condition: str = 'Clear'


class TestSuppressiveScriptEngine(unittest.TestCase):
    
    def setUp(self):
        self.engine = SuppressiveScriptEngine()
        
    def test_underdog_defensive_detection(self):
        """Test detection of away team parking the bus against favorite."""
        game = MockGameData(
            home_team=MockTeam(league_position=2),
            away_team=MockTeam(league_position=18)  # Relegation battle
        )
        
        # Home is heavy favorite (0.70 prob)
        analysis = self.engine.analyze(game, domain_i_prob=0.70)
        
        self.assertTrue(analysis.is_suppressive)
        self.assertEqual(analysis.suppressing_team, 'away')
        self.assertIn('away_underdog_defensive', analysis.tactical_flags)
        self.assertGreater(analysis.suppression_score, 0.40)
        
    def test_home_underdog_defensive(self):
        """Test home team defensive when facing away favorite."""
        game = MockGameData(
            home_team=MockTeam(league_position=17),  # Bottom of table
            away_team=MockTeam(league_position=1)    # League leaders
        )
        
        # Away is heavy favorite (home prob = 0.25)
        analysis = self.engine.analyze(game, domain_i_prob=0.25)
        
        self.assertTrue(analysis.is_suppressive)
        self.assertEqual(analysis.suppressing_team, 'home')
        self.assertIn('home_underdog_defensive', analysis.tactical_flags)
        
    def test_dead_rubber_scenario(self):
        """Test both teams with dead rubber motivation."""
        game = MockGameData(
            home_team=MockTeam(
                league_position=10, 
                motivation='dead_rubber'
            ),
            away_team=MockTeam(
                league_position=11,
                motivation='dead_rubber'
            )
        )
        
        analysis = self.engine.analyze(game, domain_i_prob=0.50)
        
        self.assertTrue(analysis.is_suppressive)
        self.assertEqual(analysis.suppressing_team, 'both')
        self.assertIn('both_teams_dead_rubber', analysis.tactical_flags)
        self.assertGreater(analysis.suppression_score, 0.50)
        
    def test_away_survival_mode(self):
        """Test away team in survival/avoid defeat mode."""
        game = MockGameData(
            home_team=MockTeam(league_position=7),
            away_team=MockTeam(
                league_position=19,  # Relegation zone
                motivation='survival'
            )
        )
        
        analysis = self.engine.analyze(game, domain_i_prob=0.55)
        
        self.assertTrue(analysis.is_suppressive)
        self.assertIn('away_survival_mode', analysis.tactical_flags)
        
    def test_low_scoring_teams(self):
        """Test both teams with low goal scoring history."""
        game = MockGameData(
            home_team=MockTeam(
                league_position=8,
                avg_goals_scored=1.0  # Very low
            ),
            away_team=MockTeam(
                league_position=9,
                avg_goals_scored=1.1  # Very low
            )
        )
        
        analysis = self.engine.analyze(game, domain_i_prob=0.50)
        
        # Should contribute to suppression score
        self.assertIn('both_low_scoring_teams', analysis.tactical_flags)
        
    def test_weather_defensive_play(self):
        """Test bad weather encouraging defensive tactics."""
        game = MockGameData(
            home_team=MockTeam(league_position=2),
            away_team=MockTeam(league_position=15),
            weather_condition='Heavy Rain'
        )
        
        analysis = self.engine.analyze(game, domain_i_prob=0.65)
        
        self.assertIn('defensive_weather_Heavy Rain', analysis.tactical_flags)
        
    def test_draw_prop_signal_generation(self):
        """Test that draw prop signals are generated at correct intervals."""
        game = MockGameData(
            home_team=MockTeam(league_position=3),
            away_team=MockTeam(
                league_position=18,
                motivation='survival'
            )
        )
        
        analysis = self.engine.analyze(game, domain_i_prob=0.70)
        
        # Should generate signals for suppressive script
        self.assertGreater(len(analysis.draw_props), 0)
        
        # Check that signals are for correct time marks
        valid_minutes = {10, 20, 40, 60}
        for prop in analysis.draw_props:
            self.assertIn(prop.minute_mark, valid_minutes)
            self.assertGreater(prop.probability, 0)
            self.assertLessEqual(prop.probability, 1.0)
            self.assertGreater(prop.confidence, 0)
            self.assertLessEqual(prop.confidence, 1.0)
            
    def test_early_time_higher_probability(self):
        """Test that earlier time marks have higher draw probability."""
        game = MockGameData(
            home_team=MockTeam(league_position=1),
            away_team=MockTeam(
                league_position=20,
                motivation='avoid_defeat'
            )
        )
        
        analysis = self.engine.analyze(game, domain_i_prob=0.75)
        
        if len(analysis.draw_props) >= 2:
            # Find 10' and 60' signals
            signal_10 = next((s for s in analysis.draw_props if s.minute_mark == 10), None)
            signal_60 = next((s for s in analysis.draw_props if s.minute_mark == 60), None)
            
            if signal_10 and signal_60:
                # 10' should have higher probability than 60'
                self.assertGreater(signal_10.probability, signal_60.probability)
                # 10' should have higher confidence than 60'
                self.assertGreater(signal_10.confidence, signal_60.confidence)
                
    def test_no_suppression_balanced_game(self):
        """Test that balanced games don't trigger suppression."""
        game = MockGameData(
            home_team=MockTeam(league_position=8),
            away_team=MockTeam(league_position=9)
        )
        
        # Evenly matched (0.50 prob)
        analysis = self.engine.analyze(game, domain_i_prob=0.50)
        
        # Should not be suppressive
        self.assertFalse(analysis.is_suppressive)
        self.assertEqual(len(analysis.draw_props), 0)
        
    def test_position_gap_threshold(self):
        """Test major position gap contributes to suppression."""
        game = MockGameData(
            home_team=MockTeam(league_position=1),
            away_team=MockTeam(league_position=20)  # 19 position gap!
        )
        
        analysis = self.engine.analyze(game, domain_i_prob=0.80)
        
        # Large position gap should contribute
        self.assertTrue(any('position_gap' in flag for flag in analysis.tactical_flags))
        
    def test_recommendations_generation(self):
        """Test actionable bet recommendations are generated."""
        game = MockGameData(
            home_team=MockTeam(league_position=2),
            away_team=MockTeam(
                league_position=19,
                motivation='survival',
                avg_goals_scored=0.9
            )
        )
        
        analysis = self.engine.analyze(game, domain_i_prob=0.75)
        recommendations = self.engine.get_recommendations(analysis, min_confidence=0.60)
        
        # Should have at least one recommendation
        if analysis.is_suppressive:
            self.assertGreater(len(recommendations), 0)
            
            for rec in recommendations:
                self.assertIn('Draw at', rec['market'])
                self.assertEqual(rec['selection'], 'YES')
                self.assertIn('probability', rec)
                self.assertIn('confidence', rec)
                self.assertIn('estimated_edge', rec)
                self.assertIn('stake_suggestion', rec)
                self.assertIn('reasoning', rec)
                
    def test_kelly_stake_calculation(self):
        """Test Kelly stake sizing."""
        # Positive edge should return positive stake
        stake = self.engine._calculate_kelly_stake(edge=0.05, probability=0.65)
        self.assertGreater(stake, 0)
        self.assertLessEqual(stake, 0.05)  # Capped at 5%
        
        # Zero edge should return zero stake
        stake_zero = self.engine._calculate_kelly_stake(edge=0.0, probability=0.50)
        self.assertEqual(stake_zero, 0.0)
        
        # Negative edge should return zero stake
        stake_neg = self.engine._calculate_kelly_stake(edge=-0.02, probability=0.40)
        self.assertEqual(stake_neg, 0.0)
        
    def test_suppression_score_clamping(self):
        """Test that suppression score is clamped to [0, 1]."""
        # Extreme scenario with multiple suppression factors
        game = MockGameData(
            home_team=MockTeam(
                league_position=1,
                avg_goals_scored=2.5
            ),
            away_team=MockTeam(
                league_position=20,
                motivation='survival',
                avg_goals_scored=0.8
            ),
            weather_condition='Snow'
        )
        
        analysis = self.engine.analyze(game, domain_i_prob=0.85)
        
        # Score should be clamped to max 1.0
        self.assertLessEqual(analysis.suppression_score, 1.0)
        self.assertGreaterEqual(analysis.suppression_score, 0.0)


if __name__ == '__main__':
    unittest.main()
