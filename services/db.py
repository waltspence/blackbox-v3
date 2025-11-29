"""
BlkBx Service: Database Interface
---------------------------------
Handles persistence using Google Firestore (NoSQL).
Stores Matches, Signals, and User Ledgers.
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore
from dataclasses import asdict
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global DB Client
db = None

def init_db(cred_path: str = None):
    """
    Initialize Firebase Admin SDK.
    Looks for FIREBASE_CREDENTIALS_JSON in env if path not provided.
    """
    global db
    if db is not None:
        return db

    # Path to your service-account.json file
    if not cred_path:
        cred_path = os.getenv('FIREBASE_CREDENTIALS_JSON', 'service-account.json')

    if not os.path.exists(cred_path):
        raise FileNotFoundError(f"Firebase credentials not found at: {cred_path}")

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print(f"✅ Firestore connected via {cred_path}")
    return db

# --- WRITE OPERATIONS ---

def save_match_analysis(match_id: str, 
                        match_input: Dict[str, Any], 
                        game_context: Any, 
                        pipeline_results: Dict[str, Any]):
    """
    Saves the complete state of a match analysis.
    
    Args:
        match_id: Unique string (e.g., 'EPL_2025_ARS_LIV')
        match_input: The raw data dict passed to game_story
        game_context: The GameContext dataclass object
        pipeline_results: Output from three_domain_pipeline
    """
    if not db: init_db()
    
    # Convert dataclass to dict
    context_dict = asdict(game_context) if hasattr(game_context, '__dataclass_fields__') else game_context

    data = {
        'match_id': match_id,
        'updated_at': firestore.SERVER_TIMESTAMP,
        'input_data': match_input,
        'game_story': context_dict,
        'pipeline_metrics': pipeline_results,
        'status': 'analyzed'
    }

    # Upsert (Merge=True updates existing fields without deleting others)
    db.collection('matches').document(match_id).set(data, merge=True)
    print(f"💾 Saved analysis for {match_id}")

def log_user_bet(user_id: str, match_id: str, selection: str, stake: float, odds: float):
    """Logs a user's bet into the ledger."""
    if not db: init_db()

    bet_id = f"{user_id}_{match_id}_{int(datetime.now().timestamp())}"
    
    bet_data = {
        'user_id': str(user_id),
        'match_id': match_id,
        'selection': selection,
        'stake': stake,
        'odds': odds,
        'status': 'pending',
        'placed_at': firestore.SERVER_TIMESTAMP
    }
    
    db.collection('ledger').document(bet_id).set(bet_data)
    return bet_id

# --- READ OPERATIONS ---

def get_recent_signals(limit: int = 5) -> List[Dict]:
    """Retrieves the most recently analyzed matches with high value."""
    if not db: init_db()
    
    # Example query: Get analyzed matches sorted by time
    docs = db.collection('matches')\
             .where('status', '==', 'analyzed')\
             .order_by('updated_at', direction=firestore.Query.DESCENDING)\
             .limit(limit)\
             .stream()
             
    return [doc.to_dict() for doc in docs]

def get_user_pending_bets(user_id: str) -> List[Dict]:
    """Fetch pending bets for a specific user."""
    if not db: init_db()
    
    docs = db.collection('ledger')\
             .where('user_id', '==', str(user_id))\
             .where('status', '==', 'pending')\
             .stream()
             
    return [doc.to_dict() for doc in docs]
