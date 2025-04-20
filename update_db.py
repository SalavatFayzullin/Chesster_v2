from flask import Flask
from src.models.user import db
import os
from sqlalchemy import text
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chesster.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def column_exists(table, column):
    """Check if a column exists in a table"""
    try:
        result = db.session.execute(text(f"SELECT {column} FROM {table} LIMIT 1"))
        return True
    except Exception:
        return False

with app.app_context():
    # Add new columns to the game table
    try:
        # Check and add turn_time_limit column
        if not column_exists('game', 'turn_time_limit'):
            print("Adding turn_time_limit column to game table...")
            db.session.execute(text('ALTER TABLE game ADD COLUMN turn_time_limit INTEGER DEFAULT 60'))
        else:
            print("turn_time_limit column already exists.")
        
        # Check and add last_move_time column
        if not column_exists('game', 'last_move_time'):
            print("Adding last_move_time column to game table...")
            db.session.execute(text('ALTER TABLE game ADD COLUMN last_move_time DATETIME'))
            
            # Update all existing games to set last_move_time to their start_time
            print("Updating existing games with default last_move_time...")
            db.session.execute(text("UPDATE game SET last_move_time = start_time"))
        else:
            print("last_move_time column already exists.")
        
        # Commit the changes
        db.session.commit()
        
        print("Database update completed successfully!")
    except Exception as e:
        print(f"Error updating database: {str(e)}")
        db.session.rollback()
        raise 