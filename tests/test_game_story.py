import unittest
import sys
import os

# Ensure we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frameworks')))

from game_story import build_game_context, get_domain_adjustments

class TestGameStory(unittest.TestCase):

    def setUp(self):
        self.base_match = {
            'competition': {'name': 'EPL', 'phase': 'League'},
            'meta': {'is_derby': False},
            'home_team': {
                'position': 5, 'points_gap': 3.0, 'incentive': 'qualified',
                'injuries': [], 'rotation_risk': 0.1, 'form_w5': 'WDLWW'
            },
            'away_team': {
                'position': 8, 'points_gap': 10.0, 'incentive': 'dead_rubber',
                'injuries': [], 'rotation_risk': 0.2, 'form_w5': 'LLWLD'
            }
        }

    def test_normal_league_match(self):
        ctx = build_game_context(self.base_match)
        adjs = get_domain_adjustments(ctx)
        self.assertEqual(adjs['domain_iii_variance_boost'], 0.0)
        self.assertGreater(adjs['domain_i_adjustment'], 0.0)

    def test_derby_game(self):
        data = self.base_match.copy()
        data['meta']['is_derby'] = True
        ctx = build_game_context(data)
        adjs = get_domain_adjustments(ctx)
        self.assertTrue(ctx.is_derby)
        self.assertGreater(adjs['domain_iii_variance_boost'], 0.05)
        self.assertIn('high_intensity', adjs['risk_flags'])

    def test_must_win_plus_injuries(self):
        import copy
        data = copy.deepcopy(self.base_match)
        data['home_team']['incentive'] = 'must_win'
        data['home_team']['injuries'] = ['A', 'B', 'C']
        data['home_team']['form_w5'] = 'LLLLL'
        data['away_team']['form_w5'] = 'WWWWW'
        
        ctx = build_game_context(data)
        adjs = get_domain_adjustments(ctx)
        self.assertLess(adjs['domain_i_adjustment'], -0.05)
        self.assertIn('home_desperation', adjs['risk_flags'])

    def test_short_season_form(self):
        """Verify dynamic normalization for short seasons."""
        data = self.base_match.copy()
        # 2 wins in 2 games = 100% confidence
        data['home_team']['form_w5'] = 'WW' 
        ctx = build_game_context(data)
        
        # Should be > 0.95 (approx 0.99 with clamp)
        self.assertGreater(ctx.home_confidence, 0.95)

    def test_empty_data_handling(self):
        """Verify the Pydantic validator handles empty/bad inputs gracefully."""
        # Case 1: None
        ctx = build_game_context(None)
        self.assertEqual(ctx.competition, "Unknown Competition")
        
        # Case 2: Empty Dict
        ctx2 = build_game_context({})
        self.assertEqual(ctx2.competition, "Unknown Competition")
        
        # Case 3: Bad Types (Pydantic will coerce or default)
        bad_data = {'home_team': {'position': "first"}} # String instead of int
        # Note: In strict mode this fails, but build_game_context catches ValidationError
        # and returns default.
        ctx3 = build_game_context(bad_data)
        self.assertIsInstance(ctx3.home_position, int)

    def test_knockout_2leg_tie(self):
        """Test the new Chasing logic."""
        data = self.base_match.copy()
        data['competition']['phase'] = 'Knockout'
        data['competition']['leg'] = 2
        # Home team is down by 1 on aggregate
        data['home_team']['aggregate_gap'] = -1.0 
        
        ctx = build_game_context(data)
        adjs = get_domain_adjustments(ctx)
        
        self.assertEqual(ctx.home_incentive, 'chasing')
        self.assertIn('chasing_game_script', adjs['risk_flags'])
        # Expect huge variance boost (0.15 base + others)
        self.assertGreater(adjs['domain_iii_variance_boost'], 0.14)

    def test_boundary_math(self):
        """Ensure outputs don't exceed clamps."""
        data = self.base_match.copy()
        # Create impossible form score to test clamp
        data['home_team']['form_w5'] = 'WWWWWWWWWW' # 10 wins
        ctx = build_game_context(data)
        
        self.assertLessEqual(ctx.home_confidence, 0.99)
        self.assertGreaterEqual(ctx.home_confidence, 0.01)

if __name__ == '__main__':
    unittest.main()
