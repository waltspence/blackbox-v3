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
