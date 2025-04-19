from datetime import datetime
from src.models.user import db
from flask_login import current_user

class GameQueue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='queue_entry', uselist=False)
    
    @staticmethod
    def find_match():
        """
        Find a match for the current user
        Returns the first user in queue who is not the current user
        """
        return GameQueue.query.filter(GameQueue.user_id != current_user.id).order_by(GameQueue.joined_at).first()
    
    @staticmethod
    def get_queue_position(user_id):
        """Get the position of a user in the queue"""
        user_entry = GameQueue.query.filter_by(user_id=user_id).first()
        if not user_entry:
            return None
        
        try:    
            position = GameQueue.query.filter(GameQueue.joined_at <= user_entry.joined_at).count()
            return position
        except Exception as e:
            # If there's any error, return a safe default
            print(f"Error getting queue position: {str(e)}")
            return 1 