import json
import os

MAPPING_FILE = os.path.join(os.path.dirname(__file__), '../data/team_name_mapping.json')
_CACHE = {}

def load_mappings():
    if not _CACHE:
        with open(MAPPING_FILE, 'r') as f:
            data = json.load(f)
        # Invert the map for O(1) lookups
        for canonical, aliases in data['teams'].items():
            _CACHE[canonical] = canonical
            for alias in aliases:
                _CACHE[alias.lower()] = canonical
    return _CACHE

def get_canonical_id(raw_name: str) -> str:
    """Converts API team name to Internal ID. Returns 'UNKNOWN_TEAM' if not found."""
    mapping = load_mappings()
    clean_name = raw_name.strip().lower()
    return mapping.get(clean_name, "UNKNOWN_TEAM")
