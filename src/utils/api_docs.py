"""
Chesster API Documentation
=========================

Authentication API
-----------------

POST /api/auth/register
- Register a new user
- Body: { username, email, password, confirm_password }
- Returns: { message } or { error }

POST /api/auth/login
- Login a user
- Body: { username, password }
- Returns: { message, user: { id, username, email, ... } } or { error }

POST /api/auth/logout
- Logout the current user
- Returns: { message } or { error }

GET /api/auth/me
- Get current user details
- Returns: { user: { id, username, ... } } or { error }

Chess Game API
-------------

POST /api/chess/start-game
- Start a new chess game
- Body: { opponent_id }
- Returns: { message, game: { id, white_player, black_player, your_color } } or { error }

GET /api/chess/games/:game_id
- Get details of a specific game
- Returns: { game: {...} } or { error }

POST /api/chess/games/:game_id/move
- Make a move in a chess game
- Body: { from_square, to_square, promotion?(optional) }
- Returns: { game: {...} } or { error }

POST /api/chess/games/:game_id/resign
- Resign from a chess game
- Returns: { message } or { error }

POST /api/chess/games/:game_id/draw
- Offer a draw in a chess game
- Returns: { message } or { error }

GET /api/chess/games/:game_id/moves
- Get all moves for a specific game
- Returns: { moves: [...] } or { error }

GET /api/chess/active-games
- Get all active games for the current user
- Returns: { games: [...] } or { error }

GET /api/chess/game-history
- Get completed games for the current user
- Returns: { games: [...] } or { error }

GET /api/chess/available-players
- Get list of players available for a new game
- Returns: { players: [...] } or { error }

Security Considerations
----------------------
- All API endpoints except /register and /login require authentication
- Users can only access games they are participating in
- Moves are validated on the backend to prevent cheating
- Only legal chess moves are allowed
- Game state is maintained server-side
- Players can only make moves during their turn
""" 