print("Python is working!")

try:
    import flask
    print("Flask is installed!")
except ImportError:
    print("Flask is not installed!")

try:
    import flask_login
    print("Flask-Login is installed!")
except ImportError:
    print("Flask-Login is not installed!")

try:
    import flask_sqlalchemy
    print("Flask-SQLAlchemy is installed!")
except ImportError:
    print("Flask-SQLAlchemy is not installed!")

try:
    import python_chess
    print("Python-Chess is installed as python_chess!")
except ImportError:
    print("Python-Chess is not installed as python_chess!")

try:
    import chess
    print("Python-Chess is installed as chess!")
except ImportError:
    print("Python-Chess is not installed as chess!")

import sys
print(f"Python Path: {sys.path}") 