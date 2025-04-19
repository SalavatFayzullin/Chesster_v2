from flask import request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from src.models.user import User, db
import re

def register():
    """Register a new user"""
    if current_user.is_authenticated:
        return jsonify({"error": "Already logged in"}), 400
    
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    
    # Validation
    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400
    
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400
    
    # Validate username format
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return jsonify({"error": "Username must be 3-20 characters and contain only letters, numbers, and underscores"}), 400
    
    # Validate email format
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({"error": "Invalid email format"}), 400
    
    # Check if user exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400
    
    # Create user
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"message": "Registration successful"}), 201

def login():
    """Login a user"""
    if current_user.is_authenticated:
        return jsonify({"error": "Already logged in"}), 400
    
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        login_user(user)
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "elo_rating": user.elo_rating,
                "battles_won": user.battles_won,
                "battles_lost": user.battles_lost
            }
        }), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

@login_required
def logout():
    """Logout the current user"""
    logout_user()
    return jsonify({"message": "Logout successful"}), 200

@login_required
def get_current_user():
    """Get the current user's details"""
    return jsonify({
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "elo_rating": current_user.elo_rating,
            "battles_won": current_user.battles_won,
            "battles_lost": current_user.battles_lost
        }
    }), 200 