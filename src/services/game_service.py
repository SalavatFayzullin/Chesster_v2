from src.models.game import Game, ChessMove
from src.models.user import User, db
from src.models.game_queue import GameQueue
import chess
import random
from datetime import datetime

class GameService:
    @staticmethod
    def create_game(player1_id, player2_id):
        """
        Create a new chess game between two players
        Randomly assign white/black color to players
        """
        # Randomly decide who plays white
        players = [player1_id, player2_id]
        random.shuffle(players)
        white_player_id, black_player_id = players
        
        # Create new game
        game = Game(
            white_player_id=white_player_id,
            black_player_id=black_player_id,
            board_state=chess.Board().fen(),
            status='active',
            current_turn='white'
        )
        
        db.session.add(game)
        db.session.commit()
        return game
    
    @staticmethod
    def get_game(game_id):
        """Get a game by ID"""
        return Game.query.get(game_id)
    
    @staticmethod
    def get_active_games_for_user(user_id):
        """Get all active games for a user"""
        return Game.query.filter(
            ((Game.white_player_id == user_id) | (Game.black_player_id == user_id)) &
            (Game.status == 'active')
        ).all()
    
    @staticmethod
    def get_completed_games_for_user(user_id, limit=10):
        """Get completed games for a user"""
        return Game.query.filter(
            ((Game.white_player_id == user_id) | (Game.black_player_id == user_id)) &
            (Game.status != 'active')
        ).order_by(Game.end_time.desc()).limit(limit).all()
    
    @staticmethod
    def make_move(game_id, user_id, from_square, to_square, promotion=None):
        """Make a move in a game"""
        game = Game.query.get(game_id)
        
        if not game:
            return False, "Game not found"
        
        if game.status != 'active':
            return False, "Game is not active"
        
        if not game.is_player_in_game(user_id):
            return False, "You are not a player in this game"
        
        if not game.is_player_turn(user_id):
            return False, "It's not your turn"
        
        success, error = game.make_move(from_square, to_square, promotion)
        if not success:
            return False, error
        
        # If game ended, update player ratings
        if game.status != 'active':
            GameService._update_player_ratings(game)
        
        db.session.commit()
        return True, game.get_game_state()
    
    @staticmethod
    def resign_game(game_id, user_id):
        """Resign from a game"""
        game = Game.query.get(game_id)
        
        if not game:
            return False, "Game not found"
        
        success, error = game.resign(user_id)
        if not success:
            return False, error
        
        # Update player ratings
        GameService._update_player_ratings(game)
        
        db.session.commit()
        return True, "Game resigned successfully"
    
    @staticmethod
    def offer_draw(game_id, user_id):
        """Offer a draw in a game"""
        # In a real implementation, you'd store the draw offer and let the other player accept/reject
        # For simplicity, we'll just check if a draw is possible due to insufficient material
        game = Game.query.get(game_id)
        
        if not game:
            return False, "Game not found"
        
        if game.status != 'active':
            return False, "Game is not active"
        
        if not game.is_player_in_game(user_id):
            return False, "You are not a player in this game"
        
        board = game.get_board()
        if board.is_insufficient_material():
            game.status = 'draw'
            game.end_time = datetime.utcnow()
            game.winner_id = None
            
            # Update player ratings for draw
            GameService._update_player_ratings(game, is_draw=True)
            
            db.session.commit()
            return True, "Draw accepted due to insufficient material"
        
        return False, "Draw offer saved but not automatically accepted"
    
    @staticmethod
    def _update_player_ratings(game, is_draw=False):
        """Update player ratings based on game outcome"""
        white_player = User.query.get(game.white_player_id)
        black_player = User.query.get(game.black_player_id)
        
        if is_draw:
            # Draw: 0.5 points for each player
            white_player.update_rating(black_player.elo_rating, 0.5)
            black_player.update_rating(white_player.elo_rating, 0.5)
        else:
            # Someone won
            if game.winner_id == white_player.id:
                white_player.update_rating(black_player.elo_rating, 1)
                black_player.update_rating(white_player.elo_rating, 0)
                white_player.battles_won += 1
                black_player.battles_lost += 1
            else:
                white_player.update_rating(black_player.elo_rating, 0)
                black_player.update_rating(white_player.elo_rating, 1)
                white_player.battles_lost += 1
                black_player.battles_won += 1
    
    @staticmethod
    def join_game_queue(user_id):
        """
        Add a user to the game queue
        Returns (was_added_to_queue, opponent_id or None)
        """
        # Check if the user is already in queue
        existing_entry = GameQueue.query.filter_by(user_id=user_id).first()
        if existing_entry:
            return False, None
            
        # Check if there's a match already waiting
        match = GameQueue.query.filter(GameQueue.user_id != user_id).order_by(GameQueue.joined_at).first()
        if match:
            # Found a match, create a game
            opponent_id = match.user_id
            
            # Remove the opponent from queue
            db.session.delete(match)
            db.session.commit()
            
            return False, opponent_id
        
        # No match found, add user to queue
        queue_entry = GameQueue(user_id=user_id)
        db.session.add(queue_entry)
        db.session.commit()
        
        return True, None
        
    @staticmethod
    def check_for_match(user_id):
        """
        Check if there's a match for the user
        Returns (matched, opponent_id or None)
        """
        # Check if user is still in queue
        queue_entry = GameQueue.query.filter_by(user_id=user_id).first()
        if not queue_entry:
            # User was matched previously or removed from queue
            # Check if they were recently matched by looking for active games
            from src.models.game import Game  # Ensure Game is imported here
            
            recent_game = Game.query.filter(
                ((Game.white_player_id == user_id) | (Game.black_player_id == user_id)) &
                (Game.status == 'active')
            ).order_by(Game.start_time.desc()).first()
            
            if recent_game:
                # Return the opponent's ID
                opponent_id = recent_game.black_player_id if recent_game.white_player_id == user_id else recent_game.white_player_id
                return True, opponent_id
            
            return False, None
            
        # Check for a match
        match = GameQueue.query.filter(GameQueue.user_id != user_id).order_by(GameQueue.joined_at).first()
        if match:
            # Found a match, but don't create a game here
            # Just mark it as matched so the controller can handle it
            opponent_id = match.user_id
            
            # Ensure one of the players creates the game (the one who joined second)
            # We'll compare timestamps to decide who creates the game
            if queue_entry.joined_at > match.joined_at:
                # This user joined after the opponent, so they should create the game
                # Don't remove from queue yet - just report the match
                return True, opponent_id
            else:
                # This user joined first, let the other player create the game
                # Just report a match was found
                return True, opponent_id
            
        # Still waiting
        return False, None
        
    @staticmethod
    def leave_game_queue(user_id):
        """Remove a user from the game queue"""
        queue_entry = GameQueue.query.filter_by(user_id=user_id).first()
        if queue_entry:
            db.session.delete(queue_entry)
            db.session.commit()
            return True
        return False
        
    @staticmethod
    def get_queue_status(user_id):
        """Get user's queue status and position"""
        queue_entry = GameQueue.query.filter_by(user_id=user_id).first()
        if not queue_entry:
            return False, None
            
        position = GameQueue.get_queue_position(user_id)
        return True, position 