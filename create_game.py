import requests
import json
from bs4 import BeautifulSoup

# Start a session to maintain cookies
session = requests.Session()

# First, log in
login_page = session.get("http://127.0.0.1:5000/login")
soup = BeautifulSoup(login_page.text, 'html.parser')
hidden_inputs = {}
for hidden_input in soup.find_all('input', type='hidden'):
    if hidden_input.get('name'):
        hidden_inputs[hidden_input.get('name')] = hidden_input.get('value', '')

login_data = {
    "username": "tester",
    "password": "testing123"
}
login_data.update(hidden_inputs)

login_response = session.post("http://127.0.0.1:5000/login", data=login_data, allow_redirects=True)
print("Login response status:", login_response.status_code)
print("Login response URL:", login_response.url)

if "profile" not in login_response.url:
    print("Login failed - cannot proceed")
    exit(1)

print("Login successful")

# Check for available players
players_response = session.get("http://127.0.0.1:5000/api/available-players")
print("Available players response status:", players_response.status_code)

try:
    players_data = json.loads(players_response.text)
    print("Available players:", json.dumps(players_data, indent=2))
    
    if players_data.get('players') and len(players_data['players']) > 0:
        # Use the first available player
        opponent_id = players_data['players'][0]['id']
        print(f"Selected opponent with ID: {opponent_id}")
        
        # Create a game
        game_data = {
            "opponent_id": opponent_id
        }
        
        create_game_response = session.post("http://127.0.0.1:5000/api/start-game", 
                                          json=game_data)
        print("Create game response status:", create_game_response.status_code)
        
        try:
            game_result = json.loads(create_game_response.text)
            print("Game created:", json.dumps(game_result, indent=2))
            
            if game_result.get('game') and game_result['game'].get('id'):
                game_id = game_result['game']['id']
                print(f"Created game with ID: {game_id}")
            else:
                print("No game ID returned")
        except json.JSONDecodeError:
            print("Create game response is not valid JSON:", create_game_response.text[:200])
    else:
        print("No available players found. Need to create another user.")
except json.JSONDecodeError:
    print("Available players response is not valid JSON:", players_response.text[:200]) 