# Chesster - Full-Featured Chess Battle Game

A Flask web application featuring user authentication and a full-featured chess game with ELO ratings and game history.

## Features

- User registration and authentication
- Personal profile page with chess statistics and ELO rating
- Challenge other players to real chess games
- Complete chess game implementation with legal move validation
- Game history and move tracking
- RESTful API for game management
- Beautiful chess-themed UI design
- Responsive layout for desktop and mobile devices

## Installation

1. Clone this repository:
```
git clone <repository-url>
cd Chesster_V2
```

2. Create a virtual environment and activate it:
```
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask development server:
```
python app.py
```

2. Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

## How to Play

1. Register for a new account or log in if you already have one
2. From your profile page, click "Start a New Battle"
3. Choose an opponent from the list of available players
4. In the chess board, make your moves by selecting pieces and valid destinations
5. The game automatically enforces rules, detects checkmate, stalemate, and other end conditions
6. Your ELO rating and statistics will be updated after each game

## API Documentation

Chesster provides a comprehensive API for managing chess games:

### Authentication API
- `POST /api/auth/register` - Create a new user account
- `POST /api/auth/login` - Log in to an existing account
- `POST /api/auth/logout` - Log out the current user
- `GET /api/auth/me` - Get current user details

### Chess Game API
- `POST /api/chess/start-game` - Start a new chess game
- `GET /api/chess/games/:game_id` - Get details of a specific game
- `POST /api/chess/games/:game_id/move` - Make a move in a chess game
- `POST /api/chess/games/:game_id/resign` - Resign from a chess game
- `POST /api/chess/games/:game_id/draw` - Offer a draw in a chess game
- `GET /api/chess/games/:game_id/moves` - Get all moves for a specific game
- `GET /api/chess/active-games` - Get all active games for the current user
- `GET /api/chess/game-history` - Get completed games for the current user
- `GET /api/chess/available-players` - Get list of players available for a new game

See `src/utils/api_docs.py` for more detailed API documentation.

## Security Features

- Server-side game state management to prevent cheating
- Legal move validation using python-chess library
- Authentication required for all game actions
- Players can only access games they are participating in
- ELO rating system for fair player matchmaking

## Project Structure

```
Chesster_V2/
├── app/
│   ├── static/       # CSS, JS, and image files
│   └── templates/    # HTML templates
├── src/
│   ├── controllers/  # Backend controllers for handling requests
│   ├── models/       # Database models
│   ├── routes/       # API route definitions
│   ├── services/     # Business logic services
│   └── utils/        # Helper functions and utilities
├── app.py            # Application entry point
├── chesster.db       # SQLite database
└── requirements.txt  # Project dependencies
```

## Technologies Used

- Flask - Python web framework
- Flask-Login - User session management
- Flask-SQLAlchemy - Database ORM
- SQLite - Database
- python-chess - Chess logic and move validation
- HTML/CSS - Frontend styling with chess theme

## Development

To contribute to the development:

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 