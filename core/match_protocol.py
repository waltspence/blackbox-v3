from typing import Dict, Optional

class MatchProtocol:
    """
    The Diagnostic Engine (Phase 3).
    Determines the Tactical Profile (Type A/B/C/D) based on Phase 2 Context.
    """

    def diagnose_match(self, match_data: Dict, home_ctx: Dict, away_ctx: Dict) -> Dict:
        """
        The standardized entry point for Phase 3.
        """
        # 1. Extract Core Metrics
        home_gpg = home_ctx.get('avg_goals_for', 1.5)
        away_gpg = away_ctx.get('avg_goals_for', 1.5)
        home_conceded = home_ctx.get('avg_goals_against', 1.0)
        away_conceded = away_ctx.get('avg_goals_against', 1.0)
        
        # 2. Extract Narrative Flags
        is_derby = match_data.get('is_derby', False)
        is_cup_final = match_data.get('stage') == 'Final'
        
        # 3. RUN THE DIAGNOSTIC TREES
        
        # TREE 1: The "Crisis" Check (Overrides everything)
        if home_ctx.get('is_leaking') or away_ctx.get('is_leaking'):
            # If a team is leaking 2+ goals/game, it forces chaos
            return {"type": "TYPE_A", "reason": "Crisis Team Detected (Leaking Goals)"}

        # TREE 2: The "Suppression" Check
        # Elite Defense + Low Momentum = Grind
        if home_conceded < 0.8 and away_conceded < 0.8:
            return {"type": "TYPE_C", "reason": "Mutual Suppression (Elite Defenses)"}
            
        if is_cup_final or (is_derby and home_ctx['momentum_score'] < 0):
             return {"type": "TYPE_C", "reason": "High Stakes / Fear Factor"}

        # TREE 3: The "Track Meet" Check
        # Both teams hot on offense
        if home_ctx.get('is_hot') and away_ctx.get('is_hot'):
            return {"type": "TYPE_A", "reason": "Both Teams in God Mode"}

        # TREE 4: The "Control" Check (Mismatch)
        # Home is good, Away is bad but not leaking catastrophe yet
        if home_ctx['momentum_score'] > 2 and away_ctx['momentum_score'] < 0:
            return {"type": "TYPE_B", "reason": "Home Control / One-Way Traffic"}

        # TREE 5: The "Mid-Off" (Default)
        return {"type": "TYPE_D", "reason": "Standard Variance / No Strong Signal"}
