# src/core/match_protocol.py
from typing import Dict, Optional

class MatchProtocol:
    """
    The Diagnostic Engine (Phase 3).
    Determines the Tactical Profile (Type A/B/C/D) based on Phase 2 Context.
    """

    def diagnose_match(self, match_data: Dict, home_ctx: Dict, away_ctx: Dict) -> Dict:
        """
        The standardized entry point for Phase 3.
        Diagnoses the tactical shape of the match using the 30-day context.
        """
        # 1. Extract Core Monthly Metrics (Phase 2 Data)
        home_gpg = home_ctx.get('avg_goals_for', 1.5)
        away_gpg = away_ctx.get('avg_goals_for', 1.5)
        home_conceded = home_ctx.get('avg_goals_against', 1.0)
        away_conceded = away_ctx.get('avg_goals_against', 1.0)
        
        # 2. Extract Narrative Flags
        is_derby = match_data.get('is_derby', False)
        stage = match_data.get('stage', 'Group')
        
        # 3. DIAGNOSTIC TREES
        
        # TREE 1: The "Crisis" Check (Overrides everything)
        # If a team is leaking 2+ goals/game, the game defaults to Chaos (Type A)
        if home_ctx.get('is_leaking') or away_ctx.get('is_leaking'):
            return {"type": "TYPE_A", "reason": "CRISIS DETECTED: Leaking Defense Forces Chaos"}

        # TREE 2: The "Suppression" Check
        # Elite Defense (Conceding <0.8) + Low Momentum = Type C (Grind)
        if home_conceded < 0.8 and away_conceded < 0.8:
            return {"type": "TYPE_C", "reason": "Mutual Suppression (Elite Defenses)"}
            
        # Fear Factor: Derbies or Finals with low momentum often freeze
        if (is_derby or stage == 'Final') and home_ctx.get('momentum_score', 0) < 1:
             return {"type": "TYPE_C", "reason": "High Stakes Suppression"}

        # TREE 3: The "Track Meet" Check (God Mode)
        # Both teams scoring 2.0+ or flagged as "Hot"
        if home_ctx.get('is_hot') and away_ctx.get('is_hot'):
            return {"type": "TYPE_A", "reason": "God Mode Clash (Track Meet)"}

        # TREE 4: The "Control" Check (Mismatch)
        # Home is dominant, Away is bad but not leaking catastrophe
        if home_ctx.get('momentum_score', 0) > 2 and away_ctx.get('momentum_score', 0) < 0:
            return {"type": "TYPE_B", "reason": "Home Control / One-Way Traffic"}

        # TREE 5: The "Mid-Off" (Default)
        return {"type": "TYPE_D", "reason": "Standard Variance / No Strong Signal"}
