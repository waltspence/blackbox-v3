# src/workflow/pipeline.py

from typing import Dict, List, Optional
from datetime import datetime
from src.core.constitution import BlackBoxConstitution, BetType
from src.analysis.monthly_context import MonthlyContextAnalyzer
from src.analysis.contrarian import ContrarianEngine
# CRITICAL: Ensure src/core/match_protocol.py exists and has the diagnose_match method
from src.core.match_protocol import MatchProtocol 

# ==============================================================================
# 🔐 AUTHORIZED MARKET MAPPING (Phase 4 Logic)
# Defines strictly which vehicles are allowed for each tactical profile.
# ==============================================================================
AUTHORIZED_MARKETS = {
    "TYPE_A": [BetType.TOTAL_OVER, BetType.BTTS, BetType.SPREAD],
    "TYPE_B": [BetType.MONEYLINE, BetType.SPREAD, BetType.TOTAL_OVER],
    "TYPE_C": [BetType.TOTAL_UNDER, BetType.DOUBLE_CHANCE], # Result bets banned by Constitution later
    "TYPE_D": [BetType.BTTS, BetType.TOTAL_OVER],
    "TYPE_E": [BetType.TOTAL_UNDER, BetType.SPREAD] # Trap games
}

class BlackBoxPipeline:
    """
    The Orchestrator.
    Enforces the strict 7-Phase Workflow for every match analysis.
    """

    def __init__(self):
        self.constitution = BlackBoxConstitution()
        self.monthly_analyzer = MonthlyContextAnalyzer(datetime.now())
        self.contrarian = ContrarianEngine()
        self.match_protocol = MatchProtocol()

    def execute_match_workflow(self, match_data: Dict) -> Dict:
        """
        Executes the full BlackBox v3.1 decision tree.
        Phase 1 (Scan) is assumed complete before calling this.
        """
        fixture_name = match_data.get('fixture', 'Unknown Fixture')
        print(f"🚀 STARTING WORKFLOW FOR: {fixture_name}")

        # =====================================================
        # PHASE 2: MONTHLY CONTEXT (Mandatory)
        # =====================================================
        # Ensure logs exist and extract monthly data
        home_logs = match_data.get('home_logs', [])
        away_logs = match_data.get('away_logs', [])
        
        home_ctx = self.monthly_analyzer.get_monthly_context(match_data['home_id'], home_logs)
        away_ctx = self.monthly_analyzer.get_monthly_context(match_data['away_id'], away_logs)
        
        # Output the mandatory monthly narrative
        narrative = self.monthly_analyzer.generate_narrative(home_ctx, away_ctx)
        print(narrative)

        # =====================================================
        # PHASE 3: PROTOCOL DIAGNOSIS
        # =====================================================
        # Pass monthly context into the protocol for smarter diagnosis
        # NOTE: MatchProtocol.diagnose_match must be updated to accept context
        match_type_result = self.match_protocol.diagnose_match(match_data, home_ctx, away_ctx)
        
        # Handle if result is complex object or string
        match_type = match_type_result.get('type') if isinstance(match_type_result, dict) else match_type_result
        print(f"📍 DIAGNOSIS: {match_type}")

        # =====================================================
        # PHASE 4: TICKET CONSTRUCTION
        # =====================================================
        # Generate potential bets based on the Match Type map
        potential_bets = self._get_authorized_bets(match_type, match_data)
        
        if not potential_bets:
            print("⚠️ NO AUTHORIZED MARKETS FOUND. Skipping match.")
            return None

        # =====================================================
        # PHASE 5: CONTRARIAN CHECK
        # =====================================================
        graded_picks = []
        for bet in potential_bets:
            # Detect traps and sharp action
            grade = self.contrarian.analyze_prop(
                odds=bet['odds'], 
                ticket_pct=bet.get('ticket_pct', 50), 
                money_pct=bet.get('money_pct', 50)
            )
            bet['grade'] = grade
            graded_picks.append(bet)

        # =====================================================
        # PHASE 6: CONSTITUTIONAL REVIEW & TIER RANKING
        # =====================================================
        final_approved_picks = []
        
        for bet in graded_picks:
            # 1. Check Crisis Law (Ban Unders for crisis teams)
            if not self.constitution.check_crisis_law(home_ctx, bet['type']):
                continue
            if not self.constitution.check_crisis_law(away_ctx, bet['type']):
                continue

            # 2. Check Suppression Law (Ban Result bets for Type C)
            if not self.constitution.check_suppression_law(match_type, bet['type']):
                continue

            # 3. Check Parlay Cap (This is typically done at ticket level, but check single bet safety here)
            # (Skipped for single prop analysis)

            # 4. Check Matrix Law (if matrix data exists)
            if 'matrix' in match_data and not self.constitution.check_matrix_law(match_data['matrix'], bet['type']):
                continue
                
            # If passed all laws, add to final list
            final_approved_picks.append(bet)

        # =====================================================
        # PHASE 7: OUTPUT GENERATION
        # =====================================================
        # Sort by Contrarian Grade Score (A > B > C > D)
        sorted_picks = sorted(final_approved_picks, key=lambda x: x['grade'].score, reverse=True)

        output = {
            "fixture": fixture_name,
            "match_type": match_type,
            "monthly_context": {
                "home": home_ctx,
                "away": away_ctx
            },
            "picks": sorted_picks
        }
        
        self._print_verdict(output)
        return output

    def _get_authorized_bets(self, match_type: str, match_data: Dict) -> List[Dict]:
        """
        Generates the raw bet objects based on the AUTHORIZED_MARKETS map.
        Extracts available odds from match_data.
        """
        allowed_types = AUTHORIZED_MARKETS.get(match_type, [])
        generated_bets = []

        # Assumes match_data['markets'] contains standard keys
        markets = match_data.get('markets', {})

        for bet_type in allowed_types:
            
            if bet_type == BetType.MONEYLINE and 'moneyline_home' in markets:
                generated_bets.append({
                    "type": BetType.MONEYLINE,
                    "selection": match_data.get('home_team', 'Home Team'),
                    "odds": markets['moneyline_home'],
                    "ticket_pct": markets.get('ml_ticket_pct', 50),
                    "money_pct": markets.get('ml_money_pct', 50)
                })
            
            elif bet_type == BetType.TOTAL_OVER and 'total_over_2_5' in markets:
                 generated_bets.append({
                    "type": BetType.TOTAL_OVER,
                    "selection": "Over 2.5",
                    "odds": markets['total_over_2_5'],
                    "line": 2.5,
                    "ticket_pct": markets.get('over_ticket_pct', 50),
                    "money_pct": markets.get('over_money_pct', 50)
                })

            elif bet_type == BetType.TOTAL_UNDER and 'total_under_2_5' in markets:
                 generated_bets.append({
                    "type": BetType.TOTAL_UNDER,
                    "selection": "Under 2.5",
                    "odds": markets['total_under_2_5'],
                    "line": 2.5,
                    "ticket_pct": markets.get('under_ticket_pct', 50),
                    "money_pct": markets.get('under_money_pct', 50)
                })
            
            elif bet_type == BetType.BTTS and 'btts_yes' in markets:
                generated_bets.append({
                    "type": BetType.BTTS,
                    "selection": "BTTS - Yes",
                    "odds": markets['btts_yes'],
                    "ticket_pct": markets.get('btts_ticket_pct', 50),
                    "money_pct": markets.get('btts_money_pct', 50)
                })
                
            # Add spread logic here if data available

        return generated_bets

    def _print_verdict(self, output: Dict):
        """
        Helper to visualize the result in the console.
        """
        print(f"\n📋 FINAL VERDICT FOR {output['fixture']}")
        print(f"   Match Type: {output['match_type']}")
        
        if not output['picks']:
            print("   ⛔ NO PLAYABLE BETS FOUND (Constitution Rejected All)")
            return

        print("   ✅ Approved Picks:")
        for pick in output['picks']:
            grade_info = pick['grade']
            print(f"      - {pick['selection']} ({pick['odds']})")
            print(f"        Grade: {grade_info.grade} | Score: {grade_info.score:.1f} | {grade_info.verdict}")
        print("-" * 60)
