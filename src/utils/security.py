from functools import wraps
from flask import jsonify, request
from flask_login import current_user

def admin_required(f):
    """
    Decorator to require admin privileges for a route
    Example use: @admin_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In a real application, you would check for admin role
        # This is just a placeholder implementation
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            return jsonify({"error": "Admin privileges required"}), 403
        return f(*args, **kwargs)
    return decorated_function

def validate_game_access(game, user_id):
    """
    Validate that a user has access to a game
    Returns (success, error_message)
    """
    if not game:
        return False, "Game not found"
    
    if not game.is_player_in_game(user_id):
        return False, "You are not authorized to access this game"
    
    return True, None

def validate_move(from_square, to_square):
    """
    Validate chess move format
    Returns (is_valid, error_message)
    """
    # Check format like "e2" or "a7"
    if not (len(from_square) == 2 and len(to_square) == 2):
        return False, "Invalid square format"
    
    file_chars = "abcdefgh"
    rank_chars = "12345678"
    
    if (from_square[0] not in file_chars or from_square[1] not in rank_chars or 
        to_square[0] not in file_chars or to_square[1] not in rank_chars):
        return False, "Invalid square notation"
    
    return True, None 