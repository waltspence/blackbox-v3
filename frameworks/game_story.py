"""
BlackBox v3: Game Story Module
------------------------------
Responsible for the 'Pre-Betting Context Layer'.
Captures narrative, motivation, availability, and rivalry factors 
to adjust Domain I (Skill), Domain II (Environment), and Domain III (Variance).
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ValidationError

# --- Pydantic Schemas for Validation ---
class CompetitionModel(BaseModel):
    name: str = "Unknown Competition"
    phase: str = "League"
    leg: Optional[int] = None
    aggregate: Optional[str] = None # e.g. "1-2"

class TeamModel(BaseModel):
    position: int = 0
    points_gap: float = 0.0
    incentive: str = "neutral"
    injuries: List[str] = Field(default_factory=list)
    rotation_risk: float = Field(0.0, ge=0.0, le=1.0)
    form_w5: str = "DDDDD"
    # Added field for precise knockout calcs if available, default to 0
    aggregate_gap: float = 0.0 

class MetaModel(BaseModel):
    is_derby: bool = False

class MatchInputSchema(BaseModel):
    competition: CompetitionModel = Field(default_factory=CompetitionModel)
    home_team: TeamModel = Field(default_factory=TeamModel)
    away_team: TeamModel = Field(default_factory=TeamModel)
    meta: MetaModel = Field(default_factory=MetaModel)

# --- Data Class ---
@dataclass
class GameContext:
    competition: str
    phase: str
    leg: Optional[int]
    aggregate_score: Optional[str]
    
    home_position: int
    home_points_gap: float
    away_position: int
    away_points_gap: float
    
    home_incentive: str  # must_win | qualified | dead_rubber | look_ahead | chasing
    away_incentive: str
    
    home_injuries: List[str]
    away_injuries: List[str]
    home_rotation_risk: float
    away_rotation_risk: float
    
    home_form_w5: str
    away_form_w5: str
    home_confidence: float
    away_confidence: float
    
    is_derby: bool
    derby_intensity_boost: float
    
    narrative: str = ""

# --- Helper Functions ---

def clamp(n: float, minn: float = 0.01, maxn: float = 0.99) -> float:
    """Clamps a value between minn and maxn."""
    return max(min(maxn, n), minn)

def _calculate_confidence(form_string: str) -> float:
    """
    Converts form string (W/D/L) into 0-1 confidence float.
    Dynamically adjusts for short seasons (len < 5).
    """
    if not form_string:
        return 0.5
    
    score = 0
    points_map = {'W': 3, 'D': 1, 'L': 0}
    games_played = len(form_string)
    
    for char in form_string.upper():
        score += points_map.get(char, 0)
    
    # Max possible score is games_played * 3
    max_score = games_played * 3
    if max_score == 0: 
        return 0.5
        
    raw_conf = score / max_score
    return clamp(raw_conf) # Keep within 0.01 - 0.99 safe zone

def _calculate_knockout_urgency(ctx: GameContext) -> None:
    """
    Modifies context in-place if a team is chasing a deficit in Leg 2.
    """
    if ctx.leg == 2:
        # Check Home
        if ctx.home_points_gap < 0: # Reusing points_gap field for agg gap in knockouts
            ctx.home_incentive = 'chasing'
        # Check Away
        if ctx.away_points_gap < 0:
            ctx.away_incentive = 'chasing'

def _generate_narrative(ctx: GameContext) -> str:
    """Synthesizes context into a brief narrative string."""
    derby_text = "DERBY MATCH. " if ctx.is_derby else ""
    stakes_text = f"Home: {ctx.home_incentive}, Away: {ctx.away_incentive}."
    
    injury_text = ""
    if len(ctx.home_injuries) > 2 or len(ctx.away_injuries) > 2:
        injury_text = " Significant squad depletion."
    
    return f"{derby_text}{stakes_text} Home Conf: {ctx.home_confidence:.2f}.{injury_text}"

# --- Main Functions ---

def build_game_context(match_data: Dict[str, Any]) -> GameContext:
    """
    Parse match metadata using Pydantic validation and return GameContext.
    Returns default context if validation fails (prints warning).
    """
    try:
        # Pydantic Validation
        data = MatchInputSchema(**(match_data or {}))
    except ValidationError as e:
        # In production, log this. For now, print and return a safe default.
        print(f"Validation Error in build_game_context: {e}")
        data = MatchInputSchema() # Empty default

    # Confidence Math
    h_conf = _calculate_confidence(data.home_team.form_w5)
    a_conf = _calculate_confidence(data.away_team.form_w5)

    # Derby Logic
    derby_boost = 0.08 if data.meta.is_derby else 0.0

    context = GameContext(
        competition=data.competition.name,
        phase=data.competition.phase,
        leg=data.competition.leg,
        aggregate_score=data.competition.aggregate,
        
        home_position=data.home_team.position,
        home_points_gap=data.home_team.aggregate_gap if data.competition.phase == 'Knockout' else data.home_team.points_gap,
        away_position=data.away_team.position,
        away_points_gap=data.away_team.aggregate_gap if data.competition.phase == 'Knockout' else data.away_team.points_gap,
        
        home_incentive=data.home_team.incentive,
        away_incentive=data.away_team.incentive,
        
        home_injuries=data.home_team.injuries,
        away_injuries=data.away_team.injuries,
        
        home_rotation_risk=clamp(data.home_team.rotation_risk),
        away_rotation_risk=clamp(data.away_team.rotation_risk),
        
        home_form_w5=data.home_team.form_w5,
        away_form_w5=data.away_team.form_w5,
        home_confidence=h_conf,
        away_confidence=a_conf,
        
        is_derby=data.meta.is_derby,
        derby_intensity_boost=derby_boost
    )
    
    # Apply special logic layers
    if data.competition.phase == 'Knockout':
        _calculate_knockout_urgency(context)
        
    context.narrative = _generate_narrative(context)
    return context

def get_domain_adjustments(context: GameContext) -> Dict[str, Any]:
    """
    Translates narrative context into mathematical adjustments.
    """
    adjustments = {
        'domain_i_adjustment': 0.0,      # Skill/Power tweak
        'domain_ii_adjustment': 0.0,     # Environment/Tempo tweak
        'domain_iii_variance_boost': 0.0, # Volatility/Sigma tweak
        'risk_flags': []
    }
    
    # --- Domain I: Skill Adjustments ---
    # Calc raw delta
    h_injury_pen = len(context.home_injuries) * 0.02
    a_injury_pen = len(context.away_injuries) * 0.02
    h_conf_boost = (context.home_confidence - 0.5) * 0.03
    a_conf_boost = (context.away_confidence - 0.5) * 0.03

    raw_skill_adj = (h_conf_boost - h_injury_pen) - (a_conf_boost - a_injury_pen)
    
    # Safety Clamp on the adjustment itself to prevent model breakage
    # We allow negative adjustments, so we clamp magnitude
    adjustments['domain_i_adjustment'] = max(min(raw_skill_adj, 0.15), -0.15)

    # --- Domain II: Environment ---
    if context.is_derby:
        adjustments['domain_ii_adjustment'] += 0.05
        adjustments['risk_flags'].append('high_intensity')

    if context.home_incentive == 'dead_rubber' and context.away_incentive == 'dead_rubber':
        adjustments['domain_ii_adjustment'] -= 0.1
        adjustments['risk_flags'].append('possible_open_game')

    # --- Domain III: Variance/Volatility ---
    var_boost = context.derby_intensity_boost
    
    if context.home_incentive == 'must_win':
        var_boost += 0.02
        adjustments['risk_flags'].append('home_desperation')
        
    if context.home_incentive == 'chasing' or context.away_incentive == 'chasing':
        var_boost += 0.15 # Massive volatility boost for 2nd leg comebacks
        adjustments['risk_flags'].append('chasing_game_script')
        
    if 'look_ahead' in [context.home_incentive, context.away_incentive]:
        var_boost += 0.04
        adjustments['risk_flags'].append('rotation_risk')

    # Clamp Variance Boost (must be positive)
    adjustments['domain_iii_variance_boost'] = clamp(var_boost, 0.0, 0.30)

    return adjustments
