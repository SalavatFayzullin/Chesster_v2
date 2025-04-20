from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
import os
from datetime import datetime
import threading
import time

# Import models
from src.models.user import User, db
from src.models.game import Game, ChessMove

# Import routes
from src.routes.auth_routes import auth_bp
from src.routes.game_routes import game_bp

# Import services
from src.services.game_service import GameService

# Initialize Flask app
app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='app/static')
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chesster.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Initialize database
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(game_bp, url_prefix='/api')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Web routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate form
        if not username or not email or not password:
            flash('All fields are required')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('profile'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/battle', methods=['GET', 'POST'])
@login_required
def battle():
    if request.method == 'POST':
        opponent_username = request.form.get('opponent')
        opponent = User.query.filter_by(username=opponent_username).first()
        
        if not opponent:
            flash('User not found')
            return redirect(url_for('battle'))
        
        if opponent.id == current_user.id:
            flash('You cannot battle yourself')
            return redirect(url_for('battle'))
        
        # Create a new game using our service
        game = GameService.create_game(current_user.id, opponent.id)
        
        return redirect(url_for('game', game_id=game.id))
    
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('battle.html', users=users)

@app.route('/game/<int:game_id>')
@login_required
def game(game_id):
    game = Game.query.get_or_404(game_id)
    
    if not game.is_player_in_game(current_user.id):
        flash('You are not authorized to view this game')
        return redirect(url_for('profile'))
    
    return render_template('game.html', game=game)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# API error handler
@app.errorhandler(Exception)
def handle_exception(e):
    # Pass through HTTP errors
    if hasattr(e, 'code') and isinstance(e.code, int) and 400 <= e.code < 600:
        return e
    
    # Log the full error with traceback
    import traceback
    app.logger.error(f"Unhandled exception: {str(e)}")
    app.logger.error(traceback.format_exc())
    
    # Return JSON response for API routes
    if request.path.startswith('/api/'):
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    
    # Return HTML response for web routes
    return render_template('500.html'), 500

@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())
    app.logger.debug('Path: %s', request.path)
    app.logger.debug('Method: %s', request.method)
    app.logger.debug('User authenticated: %s', current_user.is_authenticated if hasattr(current_user, 'is_authenticated') else False)

# Background timer checker
def timer_checker():
    """Background thread to check for expired timers"""
    print("Starting timer checker thread")
    with app.app_context():
        while True:
            try:
                # Check for expired timers
                games_with_random_moves = GameService.check_expired_timers()
                if games_with_random_moves:
                    print(f"Made random moves for {len(games_with_random_moves)} games with expired timers")
            except Exception as e:
                print(f"Error in timer checker: {str(e)}")
            
            # Sleep for 1 second
            time.sleep(1)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Print registered routes for debugging
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.rule} - Methods: {rule.methods}")
    
    # Start the timer checker thread
    timer_thread = threading.Thread(target=timer_checker)
    timer_thread.daemon = True  # This ensures the thread will exit when the main program exits
    timer_thread.start()
    
    app.run(debug=True)