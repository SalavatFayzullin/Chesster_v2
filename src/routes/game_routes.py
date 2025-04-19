from flask import Blueprint
from src.controllers import game_controller

game_bp = Blueprint('game', __name__)

# Game routes
game_bp.route('/start-game', methods=['POST'])(game_controller.start_game)
game_bp.route('/games/<int:game_id>', methods=['GET'])(game_controller.get_game)
game_bp.route('/games/<int:game_id>/move', methods=['POST'])(game_controller.make_move)
game_bp.route('/games/<int:game_id>/resign', methods=['POST'])(game_controller.resign_game)
game_bp.route('/games/<int:game_id>/draw', methods=['POST'])(game_controller.offer_draw)
game_bp.route('/games/<int:game_id>/moves', methods=['GET'])(game_controller.get_game_moves)
game_bp.route('/active-games', methods=['GET'])(game_controller.get_active_games)
game_bp.route('/game-history', methods=['GET'])(game_controller.get_game_history)
game_bp.route('/available-players', methods=['GET'])(game_controller.get_available_players)

# Game queue routes
game_bp.route('/queue/join', methods=['POST'])(game_controller.join_game_queue)
game_bp.route('/queue/status', methods=['GET'])(game_controller.check_queue_status)
game_bp.route('/queue/leave', methods=['POST'])(game_controller.leave_game_queue) 