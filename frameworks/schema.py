from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime

class TeamData(BaseModel):
    name: str
    power_rating: float
    injuries: List[str] = Field(default_factory=list)
    days_rest: int
    is_home: bool

class GameData(BaseModel):
    """
    Standardized input for the prediction engine.
    Decouples the logic from the specific API response format.
    """
    game_id: str
    sport: str
    commence_time: datetime
    home_team: TeamData
    away_team: TeamData
    
    # Contextual flags for Domain II
    is_rivalry: bool = False
    is_playoff: bool = False
    neutral_site: bool = False
    weather_condition: Optional[str] = None # e.g., "Snow", "Rain", "Dome"

class PredictionResult(BaseModel):
    """
    Standardized output from the prediction engine.
    """
    game_id: str
    home_win_prob: float
    away_win_prob: float
    fair_spread: float
    fair_total: float
    confidence_score: float
    
    # Traceability: How did we get here?
    domain_1_raw: float  # Fundamental
    domain_2_adj: float  # Narrative adjustment
    domain_3_var: float  # Variance adjustment
    
    flags: List[str] = Field(default_factory=list) # e.g., ["High Wind Penalty", "Rivalry Boost"]
