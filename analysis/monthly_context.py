# analysis/monthly_context.py
from datetime import datetime, timedelta
from typing import Dict, List

class MonthlyContextAnalyzer:
    """
    Analyzes team performance specifically within the current calendar month window.
    Overrides seasonal trends with recent realities.
    """
    
    def __init__(self, current_date: datetime):
        self.current_date = current_date
        self.month_start = current_date.replace(day=1)
    
    def get_monthly_context(self, team_id: str, match_log: List[Dict]) -> Dict:
        """
        Extracts the MANDATORY monthly context metrics.
        """
        # Filter matches for the current month
        monthly_matches = [
            m for m in match_log 
            if m['date'] >= self.month_start and m['date'] <= self.current_date
        ]
        
        # Calculate Monthly Metrics
        goals_scored = sum(m['goals_for'] for m in monthly_matches)
        goals_conceded = sum(m['goals_against'] for m in monthly_matches)
        matches_played = len(monthly_matches)
        
        # Momentum Indicator (Last 3 games, strictly)
        # 1 = Win, 0 = Draw, -1 = Loss
        recent_form = [m['result_code'] for m in monthly_matches[-3:]]
        momentum_score = sum(recent_form)
        
        return {
            "month": self.current_date.strftime("%B"),
            "matches_played": matches_played,
            "goals_scored": goals_scored,
            "goals_conceded": goals_conceded,
            "avg_goals_for": goals_scored / max(1, matches_played),
            "avg_goals_against": goals_conceded / max(1, matches_played),
            "momentum_score": momentum_score,
            "is_hot": goals_scored >= (matches_played * 2.5),  # Scoring 2.5+ per game
            "is_leaking": goals_conceded >= (matches_played * 2.0)  # Conceding 2+ per game
        }
    
    def generate_narrative(self, home_ctx: Dict, away_ctx: Dict) -> str:
        """
        Generates the mandatory text summary for the output.
        """
        return f"""
📅 **{home_ctx['month']} CONTEXT REPORT**:
- **Home Team:** {home_ctx['goals_scored']} goals scored in {home_ctx['matches_played']} games. Momentum: {home_ctx['momentum_score']}.
- **Away Team:** {away_ctx['goals_conceded']} goals conceded. Leaking status: {away_ctx['is_leaking']}.
"""
