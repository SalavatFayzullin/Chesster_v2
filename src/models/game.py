from datetime import datetime
from src.models.user import db
import chess  # Updated import name
import json

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
            if promotion:
                move = chess.Move.from_uci(f"{from_square}{to_square}{promotion}")
            else:
                move = chess.Move.from_uci(f"{from_square}{to_square}")
        except ValueError:
            return False, "Invalid move format"
        
        # Check if the move is legal
        if move not in board.legal_moves:
            return False, "Illegal move"
        
        # Make the move
        board.push(move)
        
        # Update game state
        self.board_state = board.fen()
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        
        # Create move record
        chess_move = ChessMove(
            game_id=self.id,
            player_id=self.white_player_id if self.current_turn == 'black' else self.black_player_id,
            from_square=from_square,
            to_square=to_square,
            promotion=promotion,
            move_notation=board.san(move)
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
            'last_move': None if not self.moves else self.moves[-1].to_dict()
        }
        
        if self.winner_id:
            state['winner'] = self.winner.username
        
        return state


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