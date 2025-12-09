"""BlackBox v3.1 Pipeline - 7-Phase Workflow Orchestrator

Executes the complete Saturday ticket generation workflow:
Phase 1-2: Monthly Context Overlay
Phase 3: Match Protocol v1.0 Application  
Phase 4: Hybrid Ticket Construction
Phase 5: Contrarian Analysis Engine
Phase 6: Tier Ranking & Constitution Enforcement
Phase 7: Output Generation
"""

from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass

from core.constitution import BlackBoxConstitution, BetType
from analysis.monthly_context import MonthlyContextAnalyzer
from analysis.contrarian import ContrarianEngine, ContrarianGrade


@dataclass
class MatchData:
    """Minimal match data structure for pipeline testing."""
    home_team: str
    away_team: str
    league: str
    kickoff: str
    

@dataclass
class BetProposal:
    """Proposed bet before Constitution enforcement."""
    match: MatchData
    bet_type: BetType
    selection: str
    confidence: float
    reasoning: str
    

@dataclass
class FinalBet:
    """Validated bet after Constitution + Contrarian + Tier assignment."""
    match: MatchData
    bet_type: BetType
    selection: str
    confidence: float
    reasoning: str
    contrarian_grade: ContrarianGrade
    tier: int
    label: str  # "The Buffer", "The Safety", "The Anchor"
    

class BlackBoxPipeline:
    """7-Phase Saturday Workflow Orchestrator."""
    
    def __init__(self):
        self.constitution = BlackBoxConstitution()
        self.monthly_analyzer = MonthlyContextAnalyzer()
        self.contrarian_engine = ContrarianEngine()
        
    def execute_match_workflow(self, matches: List[MatchData]) -> Dict[str, Any]:
        """Run complete 7-phase workflow on Saturday fixtures."""
        narrative = []
        narrative.append("=" * 60)
        narrative.append("🎯 BLACKBOX SATURDAY WORKFLOW - 7 PHASES")
        narrative.append("=" * 60)
        narrative.append("")
        
        # PHASE 1-2: Monthly Context Overlay
        narrative.append("📊 PHASE 1-2: MONTHLY CONTEXT OVERLAY")
        monthly_context = {}
        for match in matches:
            home_ctx = self.monthly_analyzer.get_december_form(match.home_team)
            away_ctx = self.monthly_analyzer.get_december_form(match.away_team)
            monthly_context[f"{match.home_team} vs {match.away_team}"] = {
                'home': home_ctx,
                'away': away_ctx
            }
            narrative.append(f"  ✓ {match.home_team}: {home_ctx}")
            narrative.append(f"  ✓ {match.away_team}: {away_ctx}")
        narrative.append("")
        
        # PHASE 3: Match Protocol v1.0 Application
        narrative.append("🔍 PHASE 3: MATCH PROTOCOL v1.0 APPLICATION")
        narrative.append("  [Diagnostic tree execution - to be integrated with core/match_protocol.py]")
        match_types = self._run_protocol_tree(matches)
        narrative.append("")
        
        # PHASE 4: Hybrid Ticket Construction
        narrative.append("🎟️ PHASE 4: HYBRID TICKET CONSTRUCTION")
        bet_proposals = self._get_authorized_bets(matches, match_types, monthly_context)
        narrative.append(f"  Generated {len(bet_proposals)} initial bet proposals")
        narrative.append("")
        
        # PHASE 5: Contrarian Analysis Engine
        narrative.append("⚡ PHASE 5: CONTRARIAN ANALYSIS ENGINE")
        graded_bets = []
        for prop in bet_proposals:
            grade = self.contrarian_engine.grade_bet(
                bet_type=prop.bet_type,
                selection=prop.selection,
                confidence=prop.confidence,
                public_heavy=True,
                sharp_fade=True
            )
            graded_bets.append((prop, grade))
            narrative.append(f"  {prop.selection}: {grade.letter_grade} (Sharp:{grade.sharp_alignment}/10, Trap:{grade.public_trap_score}/10)")
        narrative.append("")
        
        # PHASE 6: Constitution Enforcement + Tier Ranking
        narrative.append("⚖️ PHASE 6: CONSTITUTION ENFORCEMENT + TIER RANKING")
        final_bets = []
        for prop, grade in graded_bets:
            is_valid, reason = self.constitution.check_bet(
                bet_type=prop.bet_type,
                match_context={
                    'home_team': prop.match.home_team,
                    'away_team': prop.match.away_team,
                    'match_type': 'Type A',
                    'is_crisis': False
                },
                parlay_leg_count=3
            )
            
            if not is_valid:
                narrative.append(f"  ❌ BLOCKED: {prop.selection} - {reason}")
                continue
                
            tier = self._assign_tier(grade, prop.confidence)
            label = self._assign_label(tier, len(final_bets))
            
            final_bet = FinalBet(
                match=prop.match,
                bet_type=prop.bet_type,
                selection=prop.selection,
                confidence=prop.confidence,
                reasoning=prop.reasoning,
                contrarian_grade=grade,
                tier=tier,
                label=label
            )
            final_bets.append(final_bet)
            narrative.append(f"  ✅ Tier {tier}: {prop.selection} [{label}]")
        narrative.append("")
        
        # PHASE 7: Output Generation
        narrative.append("📋 PHASE 7: OUTPUT GENERATION")
        output = self._generate_output(final_bets, narrative)
        
        return output
        
    def _run_protocol_tree(self, matches: List[MatchData]) -> Dict[str, str]:
        """Phase 3: Run Match Protocol v1.0 diagnostic tree."""
        return {f"{m.home_team} vs {m.away_team}": "Type A" for m in matches}
        
    def _get_authorized_bets(self, matches: List[MatchData], 
                            match_types: Dict[str, str],
                            monthly_context: Dict[str, Any]) -> List[BetProposal]:
        """Phase 4: Build hybrid ticket with Safety + Anchor structure."""
        proposals = []
        for match in matches[:3]:
            proposals.append(BetProposal(
                match=match,
                bet_type=BetType.UNDER,
                selection=f"{match.home_team} vs {match.away_team} Under 2.5",
                confidence=8.5,
                reasoning="Mock reasoning - low xG expected"
            ))
        return proposals
        
    def _assign_tier(self, grade: ContrarianGrade, confidence: float) -> int:
        """Assign tier based on contrarian grade and confidence."""
        if grade.letter_grade == 'A' and confidence >= 9.5:
            return 1
        elif grade.letter_grade in ['A', 'B'] and confidence >= 8.0:
            return 2
        else:
            return 3
            
    def _assign_label(self, tier: int, position: int) -> str:
        """Assign Buffer/Safety/Anchor label."""
        if tier == 1 and position == 0:
            return "The Buffer"
        elif tier == 2:
            return "The Safety"
        else:
            return "The Anchor"
            
    def _generate_output(self, final_bets: List[FinalBet], narrative: List[str]) -> Dict[str, Any]:
        """Phase 7: Generate final output with rankings and ticket structure."""
        sorted_bets = sorted(final_bets, key=lambda b: (b.tier, -b.confidence))
        
        master_list = []
        for bet in sorted_bets:
            master_list.append({
                'tier': bet.tier,
                'label': bet.label,
                'selection': bet.selection,
                'confidence': bet.confidence,
                'grade': bet.contrarian_grade.letter_grade,
                'reasoning': bet.reasoning
            })
            
        ticket_structure = {
            'legs': [b['selection'] for b in master_list[:3]],
            'estimated_odds': '+250',
            'structure': '2 Safety + 1 Anchor'
        }
        
        narrative.append("")
        narrative.append("✅ WORKFLOW COMPLETE")
        narrative.append(f"   {len(final_bets)} bets passed all checks")
        narrative.append("=" * 60)
        
        return {
            'master_list': master_list,
            'ticket_structure': ticket_structure,
            'narrative': '\n'.join(narrative),
            'timestamp': datetime.now().isoformat()
        }


if __name__ == "__main__":
    pipeline = BlackBoxPipeline()
    
    saturday_matches = [
        MatchData("Arsenal", "Manchester United", "EPL", "12:30 EST"),
        MatchData("Sheffield Utd", "Norwich", "Championship", "15:00 EST"),
        MatchData("Torino", "AC Milan", "Serie A", "14:00 EST"),
    ]
    
    result = pipeline.execute_match_workflow(saturday_matches)
    print(result['narrative'])
    print("\n📊 MASTER LIST:")
    for bet in result['master_list']:
        print(f"  Tier {bet['tier']} [{bet['label']}]: {bet['selection']} - Grade {bet['grade']}")
    print(f"\n🎟️ RECOMMENDED TICKET: {result['ticket_structure']}")
