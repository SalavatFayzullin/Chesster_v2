from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    battles_won = db.Column(db.Integer, default=0)
    battles_lost = db.Column(db.Integer, default=0)
    elo_rating = db.Column(db.Integer, default=1200)  # Chess ELO rating
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_rating(self, opponent_rating, result):
        # Simple ELO rating update
        # result: 1 = win, 0.5 = draw, 0 = loss
        k_factor = 32  # K-factor for rating calculation
        expected_score = 1 / (1 + 10 ** ((opponent_rating - self.elo_rating) / 400))
        new_rating = self.elo_rating + k_factor * (result - expected_score)
        self.elo_rating = int(new_rating)
        return self.elo_rating 