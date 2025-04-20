from flask import Blueprint, jsonify, request, redirect, url_for
from src.controllers import game_controller
from flask_login import current_user, login_required

game_bp = Blueprint('game', __name__)

# Custom authentication check for API routes
def api_login_required(view_func):
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        return view_func(*args, **kwargs)
    decorated_view.__name__ = view_func.__name__
    return decorated_view

# Game routes
@game_bp.route('/start-game', methods=['POST'])
@api_login_required
def start_game():
    return game_controller.start_game()

@game_bp.route('/games/<int:game_id>', methods=['GET'])
@api_login_required
def get_game(game_id):
    return game_controller.get_game(game_id)

@game_bp.route('/games/<int:game_id>/move', methods=['POST'])
@api_login_required
def make_move(game_id):
    try:
        return game_controller.make_move(game_id)
    except Exception as e:
        print(f"[ERROR] Exception in make_move route: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@game_bp.route('/games/<int:game_id>/resign', methods=['POST'])
@api_login_required
def resign_game(game_id):
    return game_controller.resign_game(game_id)

@game_bp.route('/games/<int:game_id>/draw', methods=['POST'])
@api_login_required
def offer_draw(game_id):
    return game_controller.offer_draw(game_id)

@game_bp.route('/games/<int:game_id>/moves', methods=['GET'])
@api_login_required
def get_game_moves(game_id):
    return game_controller.get_game_moves(game_id)

@game_bp.route('/active-games', methods=['GET'])
@api_login_required
def get_active_games():
    return game_controller.get_active_games()

@game_bp.route('/game-history', methods=['GET'])
@api_login_required
def get_game_history():
    return game_controller.get_game_history()

@game_bp.route('/available-players', methods=['GET'])
@api_login_required
def get_available_players():
    return game_controller.get_available_players()

# Game queue routes
@game_bp.route('/queue/join', methods=['POST'])
@api_login_required
def join_game_queue():
    return game_controller.join_game_queue()

@game_bp.route('/queue/status', methods=['GET'])
@api_login_required
def check_queue_status():
    return game_controller.check_queue_status()

@game_bp.route('/queue/leave', methods=['POST'])
@api_login_required
def leave_game_queue():
    return game_controller.leave_game_queue() 