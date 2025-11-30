services/mock_data.pyfrom typing import List, Dict
from datetime import datetime, timedelta
from .interfaces import IDataFetcher
from frameworks.schema import GameData, TeamData

class MockDataFetcher(IDataFetcher):
    """
    Provides deterministic data for unit tests and backtesting.
    No network calls.
    """
    
    def fetch_schedule(self, sport: str) -> List[GameData]:
        # Return 2 control games: 
        # 1. A heavy favorite (Home)
        # 2. A close match (Rivalry)
        
        now = datetime.utcnow()
        
        game1 = GameData(
            game_id="mock_game_001",
            sport="NFL",
            commence_time=now + timedelta(hours=2),
            home_team=TeamData(name="Chiefs", power_rating=90.0, days_rest=10, is_home=True),
            away_team=TeamData(name="Raiders", power_rating=80.0, days_rest=6, is_home=False),
            is_rivalry=True,
            weather_condition="Clear"
        )
        
        game2 = GameData(
            game_id="mock_game_002",
            sport="NFL",
            commence_time=now + timedelta(hours=5),
            home_team=TeamData(name="Bills", power_rating=88.0, days_rest=7, is_home=True),
            away_team=TeamData(name="Dolphins", power_rating=88.0, days_rest=7, is_home=False),
            weather_condition="Snow"
        )
        
        return [game1, game2]

    def fetch_current_odds(self, game_id: str) -> Dict[str, float]:
        if game_id == "mock_game_001":
            # Chiefs favored
            return {"home_odds": 1.40, "away_odds": 3.00}
        elif game_id == "mock_game_002":
            # Coin flip
            return {"home_odds": 1.91, "away_odds": 1.91}
        return {}
