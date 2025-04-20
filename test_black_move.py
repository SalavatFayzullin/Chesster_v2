import requests
import json
from bs4 import BeautifulSoup

# Game ID to test - we're using the game we created earlier
game_id = 1

# Start a session to maintain cookies
session = requests.Session()

# First, get the login page to get the CSRF token if any
login_page = session.get("http://127.0.0.1:5000/login")
print("Login page status:", login_page.status_code)

# Parse the login page to extract any hidden fields or CSRF token
soup = BeautifulSoup(login_page.text, 'html.parser')
hidden_inputs = {}
for hidden_input in soup.find_all('input', type='hidden'):
    if hidden_input.get('name'):
        hidden_inputs[hidden_input.get('name')] = hidden_input.get('value', '')

# Login with the web form - we'll login as the black player (tester) this time
login_data = {
    "username": "tester",    # Login as black player
    "password": "testing123" # Using the tester password
}
# Add any hidden fields found
login_data.update(hidden_inputs)

# Submit the login form
login_response = session.post("http://127.0.0.1:5000/login", data=login_data, allow_redirects=True)
print("Login response status:", login_response.status_code)
print("Login response URL:", login_response.url)

# Check if login was successful by checking the redirect URL
if "profile" in login_response.url:
    print("Login successful - redirected to profile")
else:
    print("Login failed - not redirected to profile")
    exit(1)  # Exit with error code

# Check if the game exists and get current state
get_game_response = session.get(f"http://127.0.0.1:5000/api/games/{game_id}")
print("Get game response status:", get_game_response.status_code)

try:
    game_data = json.loads(get_game_response.text)
    print("Game data:", json.dumps(game_data, indent=2))
    
    # Check if it's our turn (black player responds to white's move)
    if game_data.get('game', {}).get('current_turn') == 'black':
        print("It is our turn to move (black)")
    else:
        print("It is not our turn to move")
        exit(1)
except json.JSONDecodeError:
    print("Game response is not valid JSON:", get_game_response.text[:200])
    exit(1)

# Make a move request - Sicilian defense (black pawn e7 to e5)
move_data = {
    "from_square": "e7",  # Black pawn
    "to_square": "e5",    # Move forward two squares
    "promotion": None     # No promotion
}

move_response = session.post(f"http://127.0.0.1:5000/api/games/{game_id}/move", 
                            json=move_data)

print("Move response status code:", move_response.status_code)
try:
    response_json = json.loads(move_response.text)
    print("Move response content:", json.dumps(response_json, indent=2))
    
    if move_response.status_code == 200:
        print("Move was successful!")
    else:
        print(f"Move failed with status {move_response.status_code}")
except json.JSONDecodeError:
    print("Response isn't JSON. First 200 chars:", move_response.text[:200])

# Check game state after move
get_game_response = session.get(f"http://127.0.0.1:5000/api/games/{game_id}")
print("Game state after move:")
try:
    game_data = json.loads(get_game_response.text)
    print(json.dumps(game_data, indent=2))
except json.JSONDecodeError:
    print("Game response is not valid JSON:", get_game_response.text[:200]) 