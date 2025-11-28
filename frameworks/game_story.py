"""
BlackBox v3: Game Story Module
------------------------------
Responsible for the 'Pre-Betting Context Layer'.
Captures narrative, motivation, availability, and rivalry factors 
to adjust Domain I (Skill), Domain II (Environment), and Domain III (Variance).
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class GameContext:
    """
    Data Transfer Object capturing the narrative state of a match.
    """
    competition: str
    phase: str
    leg: Optional[int]
    aggregate_score: Optional[str]
    
    home_position: int
    home_points_gap: float
    away_position: int
    away_points_gap: float
    
    home_incentive: str  # must_win | qualified | dead_rubber | look_ahead
    away_incentive: str
    
    home_injuries: List[str]
    away_injuries: List[str]
    home_rotation_risk: float  # 0.0 to 1.0
    away_rotation_risk: float
    
    home_form_w5: str  # e.g. "WWLDW"
    away_form_w5: str
    home_confidence: float  # 0.0 to 1.0
    away_confidence: float
    
    is_derby: bool
    derby_intensity_boost: float  # 0.0 to 0.1, added to variance
    
    narrative: str = "" # 2-3 sentence summary populated after init

def _calculate_confidence(form_string: str) -> float:
    """
    Converts 5-game form string (W/D/L) into 0-1 confidence float.
    Weights: W=3, D=1, L=0. Max score = 15.
    """
    if not form_string:
        return 0.5
    
    score = 0
    points_map = {'W': 3, 'D': 1, 'L': 0}
    
    for char in form_string.upper():
        score += points_map.get(char, 0)
        
    # Normalize 0-15 scale to 0-1
    return min(max(score / 15.0, 0.0), 1.0)

def _generate_narrative(ctx: GameContext) -> str:
    """Synthesizes context into a brief narrative string."""
    derby_text = "DERBY MATCH. " if ctx.is_derby else ""
    stakes_text = f"Home: {ctx.home_incentive}, Away: {ctx.away_incentive}."
    
    injury_text = ""
    if len(ctx.home_injuries) > 2 or len(ctx.away_injuries) > 2:
        injury_text = " Significant squad depletion detected."
    
    return f"{derby_text}{stakes_text} Home Conf: {ctx.home_confidence:.2f}.{injury_text}"

def build_game_context(match_data: Dict[str, Any]) -> GameContext:
    """
    Parse match metadata and return GameContext.
    
    Args:
        match_data: Raw dictionary containing competition, standings, 
                    team_news, and form data.
    """
    # Extract sub-dictionaries with safe defaults
    comp = match_data.get('competition', {})
    home = match_data.get('home_team', {})
    away = match_data.get('away_team', {})
    meta = match_data.get('meta', {})

    # Calculate confidence based on form
    h_form = home.get('form_w5', 'DDDDD')
    a_form = away.get('form_w5', 'DDDDD')
    
    h_conf = _calculate_confidence(h_form)
    a_conf = _calculate_confidence(a_form)

    # Determine Derby Status
    is_derby = meta.get('is_derby', False)
    derby_boost = 0.08 if is_derby else 0.0

    context = GameContext(
        competition=comp.get('name', 'Unknown'),
        phase=comp.get('phase', 'League'),
        leg=comp.get('leg'),
        aggregate_score=comp.get('aggregate'),
        
        home_position=home.get('position', 0),
        home_points_gap=home.get('points_gap', 0.0),
        away_position=away.get('position', 0),
        away_points_gap=away.get('points_gap', 0.0),
        
        home_incentive=home.get('incentive', 'neutral'),
        away_incentive=away.get('incentive', 'neutral'),
        
        home_injuries=home.get('injuries', []),
        away_injuries=away.get('injuries', []),
        home_rotation_risk=home.get('rotation_risk', 0.0),
        away_rotation_risk=away.get('rotation_risk', 0.0),
        
        home_form_w5=h_form,
        away_form_w5=a_form,
        home_confidence=h_conf,
        away_confidence=a_conf,
        
        is_derby=is_derby,
        derby_intensity_boost=derby_boost,
        narrative=""
    )
    
    # Populate the narrative field
    context.narrative = _generate_narrative(context)
    return context

def get_domain_adjustments(context: GameContext) -> Dict[str, Any]:
    """
    Translates narrative context into mathematical adjustments 
    for the Three-Domain Pipeline.
    
    Returns:
        Dict with adjustment floats and risk flags.
    """
    adjustments = {
        'domain_i_adjustment': 0.0,      # Skill/Power tweak
        'domain_ii_adjustment': 0.0,     # Environment/Tempo tweak
        'domain_iii_variance_boost': 0.0, # Volatility/Sigma tweak
        'risk_flags': []
    }
    
    # --- Domain I: Skill Adjustments (Injuries & Confidence) ---
    # Penalize for injuries (simplified heuristic)
    # Note: In production, weight this by player xG contribution (xG/xA)
    h_injury_pen = len(context.home_injuries) * 0.02
    a_injury_pen = len(context.away_injuries) * 0.02
    
    # Confidence impact (high confidence boosts skill slightly)
    # Center around 0.5 (neutral form)
    h_conf_boost = (context.home_confidence - 0.5) * 0.03
    a_conf_boost = (context.away_confidence - 0.5) * 0.03

    # Net skill adjustment (Positive favors Home, Negative favors Away)
    adjustments['domain_i_adjustment'] = (h_conf_boost - h_injury_pen) - (a_conf_boost - a_injury_pen)

    # --- Domain II: Environment (Tempo/Intensity) ---
    # Derbies usually imply higher tempo or tighter checking
    if context.is_derby:
        adjustments['domain_ii_adjustment'] += 0.05
        adjustments['risk_flags'].append('high_intensity')

    # Dead rubbers often lead to open, low-defense games
    if context.home_incentive == 'dead_rubber' and context.away_incentive == 'dead_rubber':
        adjustments['domain_ii_adjustment'] -= 0.1  # Looser play
        adjustments['risk_flags'].append('possible_open_game')

    # --- Domain III: Variance/Volatility ---
    # Base variance boost from derby
    adjustments['domain_iii_variance_boost'] += context.derby_intensity_boost
    
    # Must win vs Dead Rubber creates volatility
    if context.home_incentive == 'must_win':
        adjustments['domain_iii_variance_boost'] += 0.02
        adjustments['risk_flags'].append('home_desperation')
        
    # Look ahead spots increase variance (favorite might underperform)
    if 'look_ahead' in [context.home_incentive, context.away_incentive]:
        adjustments['domain_iii_variance_boost'] += 0.04
        adjustments['risk_flags'].append('rotation_risk')

    return adjustments
