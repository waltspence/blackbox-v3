"""BlkBx Service: Database Interface (Enhanced)
--------------------------------------------
Handles persistence using Google Firestore (NoSQL).
Includes Aggregation Counters, Atomic Updates, and Exposure Checks.
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore
from dataclasses import asdict
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

# Global DB Client
db = None

def init_db(cred_path: str = None):
    """Initialize Firebase Admin SDK."""
    global db
    if db is not None:
        return db
    
    if not cred_path:
        cred_path = os.getenv('FIREBASE_CREDENTIALS_JSON', 'service-account.json')
    
    if not os.path.exists(cred_path):
        # Fallback for environments where JSON is passed as string var
        # (Not implemented here for brevity, assume file exists)
        raise FileNotFoundError(f"Firebase credentials not found at: {cred_path}")
    
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db

# --- WRITE OPERATIONS ---

def save_match_analysis(match_id: str, match_input: Dict[str, Any], game_context: Any, pipeline_results: Dict[str, Any]):
    """Saves match analysis state."""
    if not db:
        init_db()
    
    context_dict = asdict(game_context) if hasattr(game_context, '__dataclass_fields__') else game_context
    
    data = {
        'match_id': match_id,
        'updated_at': firestore.SERVER_TIMESTAMP,
        'input_data': match_input,
        'game_story': context_dict,
        'pipeline_metrics': pipeline_results,
        'status': 'analyzed'
    }
    
    db.collection('matches').document(match_id).set(data, merge=True)

def log_user_bet(user_id: str, match_id: str, selection: str, stake: float, odds: float, match_signature: str):
    """
    Logs a user's bet.
    
    Args:
        match_signature: Helper key for settlement (e.g., 'ARS vs LIV')
    """
    if not db:
        init_db()
    
    bet_id = f"{user_id}_{match_id}_{int(datetime.now().timestamp())}"
    
    bet_data = {
        'user_id': str(user_id),
        'match_id': match_id,
        'match_signature': match_signature,
        'selection': selection,
        'stake': float(stake),
        'odds': float(odds),
        'status': 'pending',
        'placed_at': firestore.SERVER_TIMESTAMP
    }
    
    db.collection('ledger').document(bet_id).set(bet_data)
    return bet_id

def update_user_stats(user_id: str, profit_delta: float, is_win: bool):
    """
    Atomically updates user's aggregate stats to save read costs.
    """
    if not db:
        init_db()
    
    stats_ref = db.collection('users').document(str(user_id))
    
    updates = {
        'total_profit': firestore.Increment(profit_delta),
        'bets_placed': firestore.Increment(1),
        'last_active': firestore.SERVER_TIMESTAMP
    }
    
    if is_win:
        updates['wins'] = firestore.Increment(1)
        updates['current_streak'] = firestore.Increment(1)
    else:
        updates['losses'] = firestore.Increment(1)
        # Reset streak logic would require a read-write transaction,
        # simplified here to just increment losses.
    
    stats_ref.set(updates, merge=True)

def mark_bet_settled(bet_id: str, result: str, payout: float, score_str: str):
    """Updates a bet status to settled."""
    if not db:
        init_db()
    
    db.collection('ledger').document(bet_id).update({
        'status': 'settled',
        'result': result,
        'payout': payout,
        'final_score': score_str,
        'settled_at': firestore.SERVER_TIMESTAMP
    })

# --- READ OPERATIONS ---

def check_exposure(user_id: str, match_id: str) -> bool:
    """Returns True if user already has a pending bet on this match."""
    if not db:
        init_db()
    
    docs = db.collection('ledger')\
        .where('user_id', '==', str(user_id))\
        .where('match_id', '==', match_id)\
        .where('status', '==', 'pending')\
        .limit(1)\
        .stream()
    
    return any(docs)

def get_pending_bets() -> List[Dict]:
    """Fetch all pending bets for settlement."""
    if not db:
        init_db()
    
    # Note: In high volume production, you would paginate this
    docs = db.collection('ledger').where('status', '==', 'pending').stream()
    return [doc.to_dict() | {'id': doc.id} for doc in docs]

def get_recent_signals(limit: int = 5) -> List[Dict]:
    if not db:
        init_db()
    
    docs = db.collection('matches')\
        .where('status', '==', 'analyzed')\
        .order_by('updated_at', direction=firestore.Query.DESCENDING)\
        .limit(limit)\
        .stream()
    
    return [doc.to_dict() for doc in docs]
