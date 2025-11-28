import unittest
import sys
import os

# Ensure we can import the module if running from tests dir
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game_story import build_game_context, get_domain_adjustments

class TestGameStory(unittest.TestCase):

    def setUp(self):
        # Base template for match data
        self.base_match = {
            'competition': {'name': 'Premier League', 'phase': 'League'},
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
        """Test 1: Normal match, minimal adjustments expected."""
        ctx = build_game_context(self.base_match)
        adjs = get_domain_adjustments(ctx)
        
        # Expect minimal variance boost
        self.assertEqual(adjs['domain_iii_variance_boost'], 0.0)
        
        # Home has better form (WDLWW > LLWLD), expectation is positive domain_i adjustment (favoring home)
        self.assertGreater(adjs['domain_i_adjustment'], 0.0)
        
        # Check narrative generation
        self.assertIn("Home: qualified", ctx.narrative)

    def test_derby_game(self):
        """Test 2: Derby match, expect variance boost."""
        data = self.base_match.copy()
        data['meta']['is_derby'] = True
        
        ctx = build_game_context(data)
        adjs = get_domain_adjustments(ctx)
        
        self.assertTrue(ctx.is_derby)
        self.assertGreater(ctx.derby_intensity_boost, 0.0)
        self.assertGreater(adjs['domain_iii_variance_boost'], 0.05)
        self.assertIn('high_intensity', adjs['risk_flags'])

    def test_must_win_plus_injuries(self):
        """Test 3: Must win but injured. High variance, negative skill shift."""
        # Use deepcopy if nested dicts become complex, but shallow copy of top level suffices here
        # provided we replace the sub-dictionaries we edit.
        import copy
        data = copy.deepcopy(self.base_match)
        
        # Home team desperate but battered
        data['home_team']['incentive'] = 'must_win'
        data['home_team']['injuries'] = ['Kane', 'Son', 'Romero'] # 3 key injuries
        data['home_team']['form_w5'] = 'LLLLL' # Terrible confidence
        
        # Away team strong
        data['away_team']['form_w5'] = 'WWWWW'
        
        ctx = build_game_context(data)
        adjs = get_domain_adjustments(ctx)
        
        # Domain I should be negative (Away favored due to Home injuries/bad form)
        # Even though they "must win", their skill is depleted.
        self.assertLess(adjs['domain_i_adjustment'], -0.05)
        
        # Variance should be high due to desperation (must_win status)
        self.assertIn('home_desperation', adjs['risk_flags'])
        self.assertGreater(adjs['domain_iii_variance_boost'], 0.0)

if __name__ == '__main__':
    unittest.main()
