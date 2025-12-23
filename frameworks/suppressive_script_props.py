"""Blackbox v3: Suppressive Script Prop Betting Module
===========================================================

Detects defensive/suppressive game scripts and generates draw prop signals
for time intervals: 10', 20', 40', 60' minutes.

Suppressive scripts occur when:
- Underdog teams employ low-block defensive tactics
- Teams "park the bus" to protect a deficit or secure a point
- Motivation suggests conservative play (dead rubber, avoiding defeat)
"""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from .schema import GameData

logger = logging.getLogger("BlackBox.SuppressiveScript")


@dataclass
class DrawPropSignal:
    """Signal for a specific draw prop bet."""
    minute_mark: int  # 10, 20, 40, or 60
    probability: float  # Estimated probability of draw at this time
    confidence: float  # 0.0 - 1.0 confidence in signal
    edge: float  # Estimated edge vs market (if known)
    reasons: List[str]  # Why this signal was generated


@dataclass
class SuppressiveScriptAnalysis:
    """Complete analysis of suppressive script likelihood."""
    is_suppressive: bool
    suppression_score: float  # 0.0 - 1.0, higher = more likely
    suppressing_team: str  # 'home', 'away', or 'both'
    draw_props: List[DrawPropSignal]
    tactical_flags: List[str]


class SuppressiveScriptEngine:
    """
    Analyzes match context to identify suppressive/defensive scripts.
    Generates draw prop signals at key time intervals.
    """

    def __init__(self):
        # Configuration thresholds
        self.POWER_RATING_THRESHOLD = 0.15  # Min gap for underdog suppression
        self.POSITION_GAP_THRESHOLD = 8  # League position difference
        
        # Base probabilities for draw at each time mark (calibrated from historical data)
        self.BASE_DRAW_PROBS = {
            10: 0.65,  # 65% of matches are drawn at 10'
            20: 0.52,  # 52% at 20'
            40: 0.38,  # 38% at 40' (halftime)
            60: 0.28   # 28% at 60'
        }
        
        # Suppressive script multipliers (increases draw probability)
        self.SUPPRESSION_MULTIPLIERS = {
            'underdog_defensive': 1.15,  # +15% to base prob
            'dead_rubber': 1.10,
            'away_conservative': 1.12,
            'low_scoring_history': 1.08,
            'weather_defensive': 1.06
        }

    def analyze(self, game: GameData, domain_i_prob: float) -> SuppressiveScriptAnalysis:
        """
        Main analysis function.
        
        Args:
            game: GameData with team info, standings, tactics
            domain_i_prob: Home win probability from fundamental model
            
        Returns:
            SuppressiveScriptAnalysis with draw prop signals
        """
        # Calculate suppression likelihood
        suppression_score, suppressing_team, flags = self._detect_suppression(game, domain_i_prob)
        
        is_suppressive = suppression_score >= 0.50  # Threshold for signal generation
        
        draw_props = []
        if is_suppressive:
            # Generate signals for each time interval
            draw_props = self._generate_draw_prop_signals(
                game, suppression_score, suppressing_team, flags
            )
            
        logger.info(
            f"Suppression Analysis: Score={suppression_score:.2f}, "
            f"Team={suppressing_team}, Signals={len(draw_props)}"
        )
        
        return SuppressiveScriptAnalysis(
            is_suppressive=is_suppressive,
            suppression_score=suppression_score,
            suppressing_team=suppressing_team,
            draw_props=draw_props,
            tactical_flags=flags
        )

    def _detect_suppression(self, game: GameData, home_prob: float) -> Tuple[float, str, List[str]]:
        """
        Calculates suppression score based on tactical/motivational factors.
        
        Returns:
            (suppression_score, suppressing_team, tactical_flags)
        """
        score = 0.0
        flags = []
        suppressing = 'none'
        
        # 1. POWER IMBALANCE DETECTION
        # When underdog faces favorite, likely to employ defensive tactics
        if home_prob < (0.50 - self.POWER_RATING_THRESHOLD):
            # Away team is favorite, home may park bus
            score += 0.25
            suppressing = 'home'
            flags.append('home_underdog_defensive')
            
        elif home_prob > (0.50 + self.POWER_RATING_THRESHOLD):
            # Home team is strong favorite, away may sit deep
            score += 0.30  # Away suppression is more common
            suppressing = 'away'
            flags.append('away_underdog_defensive')
        
        # 2. LEAGUE POSITION GAP
        position_gap = abs(game.home_team.league_position - game.away_team.league_position)
        if position_gap >= self.POSITION_GAP_THRESHOLD:
            score += 0.15
            flags.append(f'major_position_gap_{position_gap}')
        
        # 3. MOTIVATION FACTORS
        # Dead rubber games = low intensity, fewer goals, more draws
        home_motive = getattr(game.home_team, 'motivation', 'neutral')
        away_motive = getattr(game.away_team, 'motivation', 'neutral')
        
        if home_motive == 'dead_rubber' and away_motive == 'dead_rubber':
            score += 0.20
            flags.append('both_teams_dead_rubber')
            suppressing = 'both'
            
        elif away_motive in ['survival', 'avoid_defeat']:
            score += 0.18
            flags.append('away_survival_mode')
            if suppressing == 'none':
                suppressing = 'away'
        
        # 4. AWAY TEAM DEFENSIVE TENDENCY
        # Away teams naturally more conservative
        if suppressing == 'away':
            score += 0.10
            flags.append('away_natural_defensiveness')
        
        # 5. HISTORICAL LOW-SCORING MATCHES
        # If both teams have low xG history, expect conservative play
        home_avg_goals = getattr(game.home_team, 'avg_goals_scored', 1.5)
        away_avg_goals = getattr(game.away_team, 'avg_goals_scored', 1.5)
        
        if home_avg_goals < 1.2 and away_avg_goals < 1.2:
            score += 0.12
            flags.append('both_low_scoring_teams')
        
        # 6. WEATHER CONDITIONS
        # Bad weather encourages conservative play
        weather = getattr(game, 'weather_condition', 'Clear')
        if weather in ['Heavy Rain', 'Snow', 'High Wind']:
            score += 0.08
            flags.append(f'defensive_weather_{weather}')
        
        # Clamp score to [0.0, 1.0]
        score = min(1.0, score)
        
        return score, suppressing, flags

    def _generate_draw_prop_signals(
        self, 
        game: GameData, 
        suppression_score: float,
        suppressing_team: str,
        flags: List[str]
    ) -> List[DrawPropSignal]:
        """
        Generate draw prop bet signals for time intervals: 10, 20, 40, 60.
        
        Logic:
        - Earlier time marks (10', 20') have higher base draw probability
        - Suppression score amplifies these probabilities
        - Confidence decreases as time progresses (more variance)
        """
        signals = []
        
        for minute in [10, 20, 40, 60]:
            base_prob = self.BASE_DRAW_PROBS[minute]
            
            # Apply suppression multiplier
            # Higher suppression = more likely to stay 0-0 longer
            multiplier = 1.0 + (suppression_score * 0.20)  # Up to +20%
            
            adjusted_prob = min(0.95, base_prob * multiplier)
            
            # Confidence calculation
            # Early time marks = higher confidence
            # Suppression score also boosts confidence
            time_confidence_factor = {
                10: 0.85,
                20: 0.75,
                40: 0.65,
                60: 0.50
            }[minute]
            
            confidence = time_confidence_factor * (0.7 + suppression_score * 0.3)
            confidence = min(0.95, confidence)
            
            # Edge estimation (vs typical market pricing)
            # Assume market typically prices draw @ X mins around base_prob - 5%
            # Our edge is the difference between our estimate and market
            estimated_market_prob = base_prob * 0.95  # Market slightly underprices early draws
            edge = adjusted_prob - estimated_market_prob
            
            # Only generate signal if:
            # 1. Adjusted probability is meaningfully higher than base
            # 2. We estimate positive edge
            if adjusted_prob > (base_prob + 0.03) and edge > 0.02:
                signal = DrawPropSignal(
                    minute_mark=minute,
                    probability=adjusted_prob,
                    confidence=confidence,
                    edge=edge,
                    reasons=self._build_signal_reasons(
                        minute, suppression_score, suppressing_team, flags
                    )
                )
                signals.append(signal)
                
                logger.debug(
                    f"Draw@{minute}': P={adjusted_prob:.3f}, "
                    f"Conf={confidence:.2f}, Edge={edge:.3f}"
                )
        
        return signals

    def _build_signal_reasons(self, minute: int, suppression_score: float,
                             suppressing_team: str, flags: List[str]) -> List[str]:
        """
        Build human-readable reasons for the signal.
        """
        reasons = [
            f"Suppression Score: {suppression_score:.2f}/1.00",
            f"Suppressing Team: {suppressing_team}",
            f"Time Interval: {minute}' (Early match phase)"
        ]
        
        # Add specific tactical reasons
        key_flags = [
            'away_underdog_defensive',
            'home_underdog_defensive', 
            'both_teams_dead_rubber',
            'away_survival_mode',
            'both_low_scoring_teams'
        ]
        
        for flag in flags:
            if any(kf in flag for kf in key_flags):
                reasons.append(flag.replace('_', ' ').title())
        
        return reasons

    def get_recommendations(self, analysis: SuppressiveScriptAnalysis,
                          min_confidence: float = 0.60) -> List[Dict]:
        """
        Returns actionable betting recommendations.
        
        Args:
            analysis: SuppressiveScriptAnalysis result
            min_confidence: Minimum confidence threshold for recommendations
            
        Returns:
            List of bet recommendation dicts
        """
        recommendations = []
        
        if not analysis.is_suppressive:
            return recommendations
        
        for prop in analysis.draw_props:
            if prop.confidence >= min_confidence and prop.edge > 0.02:
                rec = {
                    'market': f'Draw at {prop.minute_mark} minutes',
                    'selection': 'YES',
                    'probability': prop.probability,
                    'confidence': prop.confidence,
                    'estimated_edge': prop.edge,
                    'stake_suggestion': self._calculate_kelly_stake(prop.edge, prop.probability),
                    'reasoning': ' | '.join(prop.reasons[:3])  # Top 3 reasons
                }
                recommendations.append(rec)
        
        return recommendations

    def _calculate_kelly_stake(self, edge: float, probability: float,
                              kelly_fraction: float = 0.25) -> float:
        """
        Calculate fractional Kelly stake.
        
        Args:
            edge: Estimated edge vs market
            probability: Our estimated probability
            kelly_fraction: Fraction of Kelly to use (0.25 = quarter Kelly)
            
        Returns:
            Recommended stake as fraction of bankroll (0.0 - 1.0)
        """
        if edge <= 0 or probability <= 0:
            return 0.0
        
        # Simplified Kelly: (edge / odds) = stake_fraction
        # More conservative: use fractional Kelly
        kelly_pct = edge * kelly_fraction
        
        # Cap at 5% of bankroll for safety
        return min(0.05, max(0.0, kelly_pct))
