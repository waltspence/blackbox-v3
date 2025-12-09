# core/match_protocol.py

import yaml
import logging

class MatchProtocolEngine:
    def __init__(self, config_path='configs/match_protocol.yaml'):
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            self.settings = self.config['protocol_settings']
            self.system_keys = set(self.settings['system_keys'])
            self.logger = logging.getLogger("BlackBox_MatchProtocol")
            self.logger.info("Match Protocol v1.0 Engine Initialized")
        except Exception as e:
            raise RuntimeError(f"Failed to load match protocol config: {e}")

    def run_protocol(self, match_stats, home_lineup, away_lineup):
        """
        Master execution function for the Protocol.
        Returns the final Match Type and the List of Authorized Markets.
        """
        # Phase 1: Diagnosis
        tree_scores = self.diagnose_trees(match_stats)
        
        # Phase 2: Classification
        initial_type = self.classify_match(tree_scores)
        
        # Phase 3: Hardware Check
        final_type, note = self.hardware_check(initial_type, home_lineup, away_lineup)
        
        # Phase 4: Vehicle Selection
        authorized_markets = self.get_authorized_markets(final_type)
        
        return {
            "trees": tree_scores,
            "initial_designation": initial_type,
            "final_designation": final_type,
            "note": note,
            "authorized_markets": authorized_markets
        }

    def diagnose_trees(self, stats):
        """
        PHASE 1: THE DIAGNOSIS
        Calculates the 5 Trees based on ingested stats (normalized 0.0-1.0).
        """
        # NOTE: In production, these would be calculated from raw API data fields
        # (e.g. PPDA, xG, deep_completions).
        # Using basic placeholders that assume 'stats' dict has these pre-normalized values.
        trees = {
            "tempo": stats.get('tempo_rating', 0.5),  # Derived from PPDA / Direct Speed
            "territory": stats.get('field_tilt', 0.5),  # Share of final 3rd possession
            "chaos": stats.get('volatility_index', 0.2),  # Derived from cards/errors
            "creation": stats.get('xg_creation', 0.5),  # xG generated
            "resistance": stats.get('defensive_rating', 0.5)  # xGA prevented
        }
        return trees

    def classify_match(self, trees):
        """
        PHASE 2: THE CLASSIFICATION
        Applies the Flowchart logic to assign a Match Type.
        """
        t = self.settings['thresholds']
        
        # 1. Check Tempo (The Primary Split)
        if trees['tempo'] >= t['high_pace']:
            # High Pace
            if trees['resistance'] < t['high_resistance']:
                return "TYPE_A"  # Track Meet (High Pace + Low/Med Resistance)
            else:
                # High Pace + High Resistance = Heavyweight Clash (Treat as Type A Hybrid)
                return "TYPE_A"
        
        # 2. Low Pace Logic
        else:
            # Check for Siege (Control Grid)
            if trees['territory'] >= t['siege_territory'] and trees['resistance'] >= t['high_resistance']:
                return "TYPE_B"  # Control Grid (Siege)
            
            # Check for Chaos (Chaos Window)
            if trees['chaos'] >= t['chaos_rating']:
                return "TYPE_D"  # Chaos Window (Bad teams/Volatility)
            
            # Default: Mutual Suppression (The Grind)
            return "TYPE_C"

    def hardware_check(self, initial_type, home_lineup, away_lineup):
        """
        PHASE 3: THE HARDWARE CHECK
        Only flips designation if a SYSTEM KEY is missing.
        """
        # Combine lineups
        all_starters = home_lineup + away_lineup
        
        # Identify which system keys are expected but MISSING
        # (Note: In a real implementation, you'd need a list of 'expected' stars for the specific teams playing)
        # For this logic, we assume the 'lineup' passed in contains the CONFIRMED players.
        # We also need to know who SHOULD be there.
        
        # *Simplification for v3*: Pass a list of 'missing_players' from Ingestion.
        # Assuming 'home_lineup' is actually a dict: {'confirmed': [], 'missing_key_players': []}
        missing_keys = []
        if isinstance(home_lineup, dict) and 'missing_key_players' in home_lineup:
            missing_keys.extend(home_lineup['missing_key_players'])
        if isinstance(away_lineup, dict) and 'missing_key_players' in away_lineup:
            missing_keys.extend(away_lineup['missing_key_players'])
        
        # Filter for strictly SYSTEM KEYS defined in yaml
        confirmed_missing_stars = [p for p in missing_keys if p in self.system_keys]
        
        if not confirmed_missing_stars:
            return initial_type, "Verified: No System Keys Missing"
        
        # LOGIC FLIPS
        # 1. Rodri/Controller Missing in Type B -> Flips to Type A/D (Control lost)
        if ("Rodri" in confirmed_missing_stars or "Kevin De Bruyne" in confirmed_missing_stars) and initial_type == "TYPE_B":
            return "TYPE_A", f"Hardware Flip: Controller ({confirmed_missing_stars[0]}) Missing. Siege Broken."
        
        # 2. Alisson/Van Dijk/Star GK/CB Missing -> Increases Volatility (C -> D, or A -> A+)
        defensive_stars = ["Alisson Becker", "Virgil van Dijk", "Thibaut Courtois", "William Saliba"]
        if any(x in confirmed_missing_stars for x in defensive_stars):
            if initial_type == "TYPE_C":
                return "TYPE_D", f"Hardware Flip: Defensive Key ({confirmed_missing_stars[0]}) Missing. Suppression Failed."
        
        return initial_type, f"Verified: Missing {confirmed_missing_stars}, but no Protocol Flip triggered."

    def get_authorized_markets(self, match_type):
        """
        PHASE 4: THE VEHICLE
        Returns the strict list of authorized markets for the designation.
        """
        return self.settings['authorized_markets'].get(match_type, [])

    def build_hybrid_ticket(self, matches_data, max_legs=4):
        """
        PHASE 5: HYBRID TICKET CONSTRUCTION
        Mixes "Safety" buffers (Over/Under goals) with "Structural" locks (BTTS)
        to create tickets with +140 to +400 potential.
        
        Strategy:
        - Safety legs: Over/Under goals (handles most likely outcomes)
        - Structural legs: BTTS on Type A "Track Meet" matches
        - Anchor leg: BTTS on highest probability Type A match
        
        Args:
            matches_data: List of dicts with match info and protocol results
            max_legs: Maximum number of legs in ticket (default 4)
        
        Returns:
            Dict with ticket structure and estimated odds
        """
        safety_legs = []
        structural_legs = []
        
        # Identify legs by category
        for match in matches_data:
            match_type = match.get('final_designation')
            fixture = match.get('fixture')
            
            # Safety Buffer: Over/Under goals for defensive teams
            if match_type in ['TYPE_B', 'TYPE_C']:
                # Arsenal/City (defensive strength) -> Under 3.5
                if any(team in fixture for team in ['Arsenal', 'Man City']):
                    safety_legs.append({
                        'fixture': fixture,
                        'selection': 'Under 3.5 Goals',
                        'logic': 'The Buffer. Defensive strength guarantees low ceiling.'
                    })
                # Sunderland (weak attack) -> Over 1.5
                elif 'Sunderland' in fixture:
                    safety_legs.append({
                        'fixture': fixture,
                        'selection': 'Over 1.5 Goals',
                        'logic': 'The Safety. Covers likely outcomes (2-0 or 1-1).'
                    })
            
            # Structural Lock: BTTS for Type A "Track Meet"
            elif match_type == 'TYPE_A':
                # Track Meet profile: High pace + weak defenses
                if self._is_btts_candidate(match):
                    structural_legs.append({
                        'fixture': fixture,
                        'selection': 'BTTS - YES',
                        'logic': 'The Anchor. Track Meet guarantees both teams score.',
                        'confidence': match.get('btts_confidence', 'High')
                    })
        
        # Build ticket with mix of safety and structural
        ticket = self._construct_ticket(safety_legs, structural_legs, max_legs)
        
        return ticket
    
    def _is_btts_candidate(self, match):
                """
        Determines if a Type A match qualifies for BTTS based on:
        - Chelsea defense is "High Risk" (leaky)
        - Bournemouth at home is relentless (attacking)
        - Both teams have attacking quality (Isak, Salah for Liverpool)
        """
        fixture = match.get('fixture', '')
        trees = match.get('trees', {})
        
        # Track Meet profile criteria
        high_pace = trees.get('tempo', 0) >= 0.7
        low_resistance = trees.get('resistance', 1.0) < 0.5
        both_create = trees.get('creation', 0) >= 0.6
        
        # Specific team patterns from Gemini analysis
        btts_fixtures = [
            ('Chelsea', 'Bournemouth'),  # Chelsea leaky defense + Bournemouth home
            ('Leeds', 'Liverpool'),      # Leeds scoring + Liverpool attack (Isak/Salah)
        ]
        
        # Check if fixture matches BTTS criteria
        for team_a, team_b in btts_fixtures:
            if team_a in fixture and team_b in fixture:
                return True
        
        # General Track Meet with creation
        if high_pace and low_resistance and both_create:
            return True
        
        return False
    
    def _construct_ticket(self, safety_legs, structural_legs, max_legs):
        """
        Constructs final ticket by mixing safety and structural legs.
        
        Rules from Gemini conversation:
        - Use 2 safety legs + 1 anchor leg for 3-legger
        - Use 2 safety + 2 structural for 4-legger
        - Anchor = highest confidence BTTS
        - Estimated odds: +140 to +400 range
        """
        ticket = {'legs': [], 'strategy': 'Hybrid', 'estimated_odds_range': '+140 to +400'}
        
        # Sort structural legs by confidence
        structural_legs.sort(key=lambda x: x.get('confidence', 'Low'), reverse=True)
        
        if max_legs == 3:
            # 3-Leg Hybrid: 2 Safety + 1 Anchor
            ticket['legs'].extend(safety_legs[:2])
            if structural_legs:
                ticket['legs'].append(structural_legs[0])  # Highest confidence BTTS
            ticket['strategy'] = '3-Leg Hybrid (2 Safety + 1 Anchor)'
        
        elif max_legs == 4:
            # 4-Leg Hybrid: 2 Safety + 2 Structural
            ticket['legs'].extend(safety_legs[:2])
            ticket['legs'].extend(structural_legs[:2])
            ticket['strategy'] = '4-Leg Hybrid (2 Safety + 2 Structural)'
        
        return ticket
