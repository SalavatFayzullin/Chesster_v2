from flask import request, jsonify
from flask_login import current_user
from src.models.user import User, db
from src.models.game import Game, ChessMove
from src.services.game_service import GameService

def start_game():
    """Start a new chess game"""
    data = request.get_json()
    opponent_id = data.get('opponent_id')
    
    if not opponent_id:
        return jsonify({"error": "Opponent ID is required"}), 400
    
    # Validate opponent exists
    opponent = User.query.get(opponent_id)
    if not opponent:
        return jsonify({"error": "Opponent not found"}), 404
    
    # Prevent playing against yourself
    if opponent.id == current_user.id:
        return jsonify({"error": "You cannot play against yourself"}), 400
    
    # Create game
    game = GameService.create_game(current_user.id, opponent.id)
    
    return jsonify({
        "message": "Game started successfully",
        "game": {
            "id": game.id,
            "white_player": game.white_player.username,
            "black_player": game.black_player.username,
            "your_color": "white" if game.white_player_id == current_user.id else "black"
        }
    }), 201

def get_game(game_id):
    """Get details of a specific game"""
    game = GameService.get_game(game_id)
    
    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    # Check if user is a player in this game
    if not game.is_player_in_game(current_user.id):
        return jsonify({"error": "You are not authorized to view this game"}), 403
    
    return jsonify({"game": game.get_game_state()}), 200

def make_move(game_id):
    """Make a move in a chess game"""
    # Return error if user is not authenticated
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
        
    # Log request data for debugging
    print(f"[DEBUG] Request headers: {request.headers}")
    print(f"[DEBUG] Request method: {request.method}")
    print(f"[DEBUG] Content type: {request.content_type}")
    print(f"[DEBUG] Raw request data: {request.get_data(as_text=True)}")
    
    try:
        data = request.get_json(force=True)
    except Exception as e:
        print(f"[ERROR] JSON parsing error: {str(e)}")
        return jsonify({"error": f"Invalid JSON format: {str(e)}"}), 400
    
    if not data:
        print("[ERROR] Empty data after parsing JSON")
        return jsonify({"error": "Empty data received"}), 400
        
    print(f"[DEBUG] Parsed JSON data: {data}")
        
    try:
        from_square = data.get('from_square')
        to_square = data.get('to_square')
        promotion = data.get('promotion')  # Optional
    except Exception as e:
        print(f"[ERROR] Error accessing data fields: {str(e)}")
        return jsonify({"error": f"Error accessing move data: {str(e)}"}), 400
    
    print(f"[DEBUG] Move data - from: {from_square}, to: {to_square}, promotion: {promotion}")
    
    # Validate input
    if not from_square or not to_square:
        return jsonify({"error": "From and to squares are required"}), 400
    
    # Validate square format (e.g., "e2", "e4")
    if not (len(from_square) == 2 and len(to_square) == 2):
        return jsonify({"error": "Invalid square format"}), 400
    
    # If promotion is empty string, set it to None
    if promotion == "":
        promotion = None
    
    # Make the move
    success, result = GameService.make_move(
        game_id, current_user.id, from_square, to_square, promotion
    )
    
    if not success:
        return jsonify({"error": result}), 400
    
    return jsonify({"game": result}), 200

def resign_game(game_id):
    """Resign from a chess game"""
    success, result = GameService.resign_game(game_id, current_user.id)
    
    if not success:
        return jsonify({"error": result}), 400
    
    return jsonify({"message": result}), 200

def offer_draw(game_id):
    """Offer a draw in a chess game"""
    success, result = GameService.offer_draw(game_id, current_user.id)
    
    if not success:
        return jsonify({"error": result}), 400
    
    return jsonify({"message": result}), 200

def get_active_games():
    """Get all active games for the current user"""
    games = GameService.get_active_games_for_user(current_user.id)
    
    return jsonify({
        "games": [
            {
                "id": game.id,
                "white_player": game.white_player.username,
                "black_player": game.black_player.username,
                "your_color": "white" if game.white_player_id == current_user.id else "black",
                "current_turn": game.current_turn,
                "start_time": game.start_time.isoformat()
            }
            for game in games
        ]
    }), 200

def get_game_history():
    """Get completed games for the current user"""
    games = GameService.get_completed_games_for_user(current_user.id)
    
    return jsonify({
        "games": [
            {
                "id": game.id,
                "white_player": game.white_player.username,
                "black_player": game.black_player.username,
                "winner": game.winner.username if game.winner else None,
                "result": "win" if game.winner_id == current_user.id else "loss" if game.winner_id else "draw",
                "status": game.status,
                "start_time": game.start_time.isoformat(),
                "end_time": game.end_time.isoformat() if game.end_time else None
            }
            for game in games
        ]
    }), 200

def get_available_players():
    """Get list of players available for a new game"""
    users = User.query.filter(User.id != current_user.id).all()
    
    return jsonify({
        "players": [
            {
                "id": user.id,
                "username": user.username,
                "elo_rating": user.elo_rating
            }
            for user in users
        ]
    }), 200

def get_game_moves(game_id):
    """Get all moves for a specific game"""
    game = GameService.get_game(game_id)
    
    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    # Check if user is a player in this game
    if not game.is_player_in_game(current_user.id):
        return jsonify({"error": "You are not authorized to view this game"}), 403
    
    moves = ChessMove.query.filter_by(game_id=game_id).order_by(ChessMove.timestamp).all()
    
    return jsonify({
        "moves": [move.to_dict() for move in moves]
    }), 200

def join_game_queue():
    """Join the game queue or get matched immediately"""
    in_queue, opponent_id = GameService.join_game_queue(current_user.id)
    
    if in_queue:
        # User was added to queue
        return jsonify({
            "status": "queued",
            "message": "You've been added to the game queue"
        }), 200
    elif opponent_id:
        # Immediate match found
        game = GameService.create_game(current_user.id, opponent_id)
        
        return jsonify({
            "status": "matched",
            "message": "You've been matched with an opponent",
            "game": {
                "id": game.id,
                "white_player": game.white_player.username,
                "black_player": game.black_player.username,
                "your_color": "white" if game.white_player_id == current_user.id else "black"
            }
        }), 200
    else:
        # User is already in queue
        return jsonify({
            "status": "already_queued",
            "message": "You are already in the game queue"
        }), 200

def check_queue_status():
    """Check for a match while in queue (long polling)"""
    try:
        matched, opponent_id = GameService.check_for_match(current_user.id)
        
        if matched and opponent_id:
            # Check if a game with this opponent already exists
            from src.models.game import Game  # Import Game model here to ensure it's available
            
            recent_game = Game.query.filter(
                (((Game.white_player_id == current_user.id) & (Game.black_player_id == opponent_id)) |
                 ((Game.white_player_id == opponent_id) & (Game.black_player_id == current_user.id))) &
                (Game.status == 'active')
            ).order_by(Game.start_time.desc()).first()
            
            if recent_game:
                # Game already exists, return it
                return jsonify({
                    "status": "matched",
                    "message": "You've been matched with an opponent",
                    "game": {
                        "id": recent_game.id,
                        "white_player": recent_game.white_player.username,
                        "black_player": recent_game.black_player.username,
                        "your_color": "white" if recent_game.white_player_id == current_user.id else "black"
                    }
                }), 200
            
            # Create a new game with the opponent if we're the second player
            # The first player will find this game in their next poll
            from src.models.game_queue import GameQueue
            
            user_entry = GameQueue.query.filter_by(user_id=current_user.id).first()
            opponent_entry = GameQueue.query.filter_by(user_id=opponent_id).first()
            
            if user_entry and opponent_entry and user_entry.joined_at > opponent_entry.joined_at:
                # This user joined second, create the game
                game = GameService.create_game(current_user.id, opponent_id)
                
                # Don't remove users from queue yet - they'll be removed after redirection
                # We'll only create the game but keep them in queue until they navigate to game page
                
                return jsonify({
                    "status": "matched",
                    "message": "You've been matched with an opponent",
                    "game": {
                        "id": game.id,
                        "white_player": game.white_player.username,
                        "black_player": game.black_player.username,
                        "your_color": "white" if game.white_player_id == current_user.id else "black"
                    }
                }), 200
            
            # Only report that we found a match but wait for other player to create game
            return jsonify({
                "status": "matching",
                "message": "Found a potential opponent, waiting for confirmation..."
            }), 200
        
        # Still in queue, no match yet
        return jsonify({
            "status": "waiting",
            "message": "Still waiting for an opponent..."
        }), 200
        
    except Exception as e:
        # Log the error
        app.logger.error(f"Error checking queue status: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "An error occurred while checking queue status"
        }), 500

def leave_game_queue():
    """Leave the game queue"""
    success = GameService.leave_game_queue(current_user.id)
    
    # Always return success, regardless of whether the user was in the queue or not
    return jsonify({
        "status": "success",
        "message": "You've been removed from the game queue"
    }), 200 