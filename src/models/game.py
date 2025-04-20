from datetime import datetime
from src.models.user import db
import chess  # Updated import name
import json
import random

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    white_player_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    black_player_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    winner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    board_state = db.Column(db.Text, default=chess.Board().fen())  # FEN notation
    status = db.Column(db.String(20), default='active')  # active, checkmate, stalemate, draw, resigned
    current_turn = db.Column(db.String(5), default='white')  # white or black
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    turn_time_limit = db.Column(db.Integer, default=3)  # Default time limit of 60 seconds per turn
    last_move_time = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of the last move
    
    # Relationships
    white_player = db.relationship('User', foreign_keys=[white_player_id])
    black_player = db.relationship('User', foreign_keys=[black_player_id])
    winner = db.relationship('User', foreign_keys=[winner_id])
    moves = db.relationship('ChessMove', backref='game', lazy=True, cascade="all, delete-orphan")
    
    def get_board(self):
        """Return a chess.Board object representing the current state"""
        return chess.Board(self.board_state)
    
    def is_player_turn(self, user_id):
        """Check if it's the given user's turn"""
        if self.current_turn == 'white' and user_id == self.white_player_id:
            return True
        if self.current_turn == 'black' and user_id == self.black_player_id:
            return True
        return False
    
    def is_player_in_game(self, user_id):
        """Check if the user is a player in this game"""
        return user_id in (self.white_player_id, self.black_player_id)
    
    def make_move(self, from_square, to_square, promotion=None):
        """Make a move on the board and update the game state"""
        board = self.get_board()
        
        # Create the move object
        try:
            if promotion and promotion.strip():
                move = chess.Move.from_uci(f"{from_square}{to_square}{promotion}")
            else:
                move = chess.Move.from_uci(f"{from_square}{to_square}")
        except ValueError:
            return False, "Invalid move format"
        
        # Check if the move is legal
        if move not in board.legal_moves:
            return False, "Illegal move"
        
        # Store the move before pushing it for notation
        try:
            san_notation = board.san(move)
        except Exception as e:
            return False, f"Error calculating move notation: {str(e)}"
        
        # Store the current player's ID before changing the turn
        current_player_id = self.white_player_id if self.current_turn == 'white' else self.black_player_id
        
        # Make the move
        board.push(move)
        
        # Update game state
        self.board_state = board.fen()
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        self.last_move_time = datetime.utcnow()  # Update the timestamp of the last move
        
        # Create move record with the correct player ID (the one who made the move)
        chess_move = ChessMove(
            game_id=self.id,
            player_id=current_player_id,
            from_square=from_square,
            to_square=to_square,
            promotion=promotion,
            move_notation=san_notation
        )
        db.session.add(chess_move)
        
        # Check for game ending conditions
        if board.is_checkmate():
            self.status = 'checkmate'
            self.winner_id = self.black_player_id if self.current_turn == 'black' else self.white_player_id
            self.end_time = datetime.utcnow()
        elif board.is_stalemate():
            self.status = 'stalemate'
            self.end_time = datetime.utcnow()
        elif board.is_insufficient_material():
            self.status = 'draw'
            self.end_time = datetime.utcnow()
        
        return True, None
    
    def resign(self, user_id):
        """Player resigns the game"""
        if not self.is_player_in_game(user_id):
            return False, "You are not a player in this game"
        
        if self.status != 'active':
            return False, "Game is already over"
        
        self.status = 'resigned'
        self.winner_id = self.black_player_id if user_id == self.white_player_id else self.white_player_id
        self.end_time = datetime.utcnow()
        return True, None
    
    def get_game_state(self):
        """Return a dictionary with the current game state"""
        board = self.get_board()
        
        state = {
            'id': self.id,
            'white_player': self.white_player.username,
            'black_player': self.black_player.username,
            'board': self.board_state,
            'current_turn': self.current_turn,
            'status': self.status,
            'is_check': board.is_check(),
            'legal_moves': [move.uci() for move in board.legal_moves],
            'piece_map': {str(sq): str(piece) for sq, piece in board.piece_map().items()},
            'last_move': None if not self.moves else self.moves[-1].to_dict(),
            'turn_time_limit': self.turn_time_limit,
            'time_remaining': self.get_time_remaining()
        }
        
        if self.winner_id:
            state['winner'] = self.winner.username
        
        return state
        
    def get_time_remaining(self):
        """Get the remaining time for the current turn in seconds"""
        if self.status != 'active':
            return 0
            
        elapsed = (datetime.utcnow() - self.last_move_time).total_seconds()
        remaining = max(0, self.turn_time_limit - int(elapsed))
        return remaining
        
    def check_time_limit(self):
        """Check if the time limit for the current turn has expired and make a random move if necessary"""
        if self.status != 'active':
            return False
            
        if self.get_time_remaining() > 0:
            return False
            
        # Time limit exceeded, make a random move
        return self.make_random_move()
        
    def make_random_move(self):
        """Make a random legal move and return whether it was successful"""
        board = self.get_board()
        
        # Get all legal moves
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return False
            
        # Select a random move
        random_move = random.choice(legal_moves)
        
        # Convert move to uci format
        from_square = chess.square_name(random_move.from_square)
        to_square = chess.square_name(random_move.to_square)
        promotion = random_move.promotion_char() if random_move.promotion else None
        
        # Make the move
        success, _ = self.make_move(from_square, to_square, promotion)
        
        if success:
            # Create a note that this was a random move due to time expiration
            note = "Random move due to time limit expiration"
            # Update the last move's note if it exists
            if self.moves:
                last_move = self.moves[-1]
                last_move.move_notation += f" ({note})"
                
        return success


class ChessMove(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    from_square = db.Column(db.String(2), nullable=False)  # e.g., "e2"
    to_square = db.Column(db.String(2), nullable=False)    # e.g., "e4"
    promotion = db.Column(db.String(1), nullable=True)     # piece type for pawn promotion
    move_notation = db.Column(db.String(10), nullable=False)  # Standard algebraic notation
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    player = db.relationship('User', foreign_keys=[player_id])
    
    def to_dict(self):
        """Return a dictionary representation of the move"""
        return {
            'id': self.id,
            'game_id': self.game_id,
            'player': self.player.username,
            'from_square': self.from_square,
            'to_square': self.to_square,
            'promotion': self.promotion,
            'move_notation': self.move_notation,
            'timestamp': self.timestamp.isoformat()
        } 