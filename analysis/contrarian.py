# analysis/contrarian.py
from dataclasses import dataclass
from typing import Dict, Tuple

@dataclass
class ContrarianGrade:
    score: float  # 0-10
    grade: str  # A/B/C/D
    verdict: str

class ContrarianEngine:
    """
    Phase 5 Engine: Detects Public Traps and Calculates Sharp Alignment.
    """
    
    def analyze_prop(self, odds: int, ticket_pct: int, money_pct: int) -> ContrarianGrade:
        trap_score = self._detect_public_trap(odds, ticket_pct)
        sharp_score = self._sharp_alignment(ticket_pct, money_pct)
        final_score = (trap_score * 0.4) + (sharp_score * 0.6)
        return self._assign_grade(final_score)
    
    def _detect_public_trap(self, odds: int, ticket_pct: int) -> float:
        """
        Detects if a bet is a 'Public Trap'.
        High Ticket % on a 'bad' line (e.g., -170 BTTS) = High Trap Score.
        """
        is_square_odds = -190 <= odds <= -130  # The "Sucker Range"
        is_heavy_public = ticket_pct > 75
        
        if is_square_odds and is_heavy_public:
            return 10.0  # MAXIMUM TRAP WARNING
        elif is_heavy_public:
            return 7.0
        return 2.0
    
    def _sharp_alignment(self, ticket_pct: int, money_pct: int) -> float:
        """
        Calculates alignment with sharp money.
        Money % significantly higher than Ticket % = Sharp Action.
        """
        differential = money_pct - ticket_pct
        
        if differential > 15:
            return 10.0  # Massive Sharp Buy Signal
        elif differential > 5:
            return 7.5
        elif differential < -10:
            return 0.0  # Pros are fading this
        return 5.0
    
    def _assign_grade(self, score: float) -> ContrarianGrade:
        if score >= 9.0:
            return ContrarianGrade(score, "A", "💎 CONTRARIAN GOLD")
        if score >= 7.5:
            return ContrarianGrade(score, "B", "✅ SHARP ALIGNED")
        if score >= 5.0:
            return ContrarianGrade(score, "C", "⚠️ PUBLIC LEAN")
        return ContrarianGrade(score, "D", "⛔ SQUARE TRAP")
