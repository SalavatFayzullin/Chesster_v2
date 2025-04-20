import requests
from bs4 import BeautifulSoup

# Create a session to maintain cookies
session = requests.Session()

# First, get the register page to get any CSRF token
register_page = session.get("http://127.0.0.1:5000/register")
print("Register page status:", register_page.status_code)

# Parse the register page to extract any hidden fields
soup = BeautifulSoup(register_page.text, 'html.parser')
hidden_inputs = {}
for hidden_input in soup.find_all('input', type='hidden'):
    if hidden_input.get('name'):
        hidden_inputs[hidden_input.get('name')] = hidden_input.get('value', '')

# Registration data
register_data = {
    "username": "opponent",
    "email": "opponent@example.com",
    "password": "testing123",
    "confirm_password": "testing123"
}
# Add any hidden fields
register_data.update(hidden_inputs)

# Submit the registration form
register_response = session.post("http://127.0.0.1:5000/register", 
                               data=register_data, 
                               allow_redirects=True)

print("Register response status:", register_response.status_code)
print("Register response URL:", register_response.url)

# Check the response
if "login" in register_response.url:
    print("Registration successful - redirected to login")
elif "register" in register_response.url:
    print("Registration failed - stayed on register page")
    if "already exists" in register_response.text:
        print("  User already exists. Try with a different username/email.")
    else:
        print("  Unknown registration error. Check response content.")
else:
    print("Unexpected redirect or response.")

print("\nNow try to login with the new user")

# Get login page
login_page = session.get("http://127.0.0.1:5000/login")
print("Login page status:", login_page.status_code)

# Parse for hidden inputs
soup = BeautifulSoup(login_page.text, 'html.parser')
hidden_inputs = {}
for hidden_input in soup.find_all('input', type='hidden'):
    if hidden_input.get('name'):
        hidden_inputs[hidden_input.get('name')] = hidden_input.get('value', '')

# Login data
login_data = {
    "username": "opponent",
    "password": "testing123"
}
login_data.update(hidden_inputs)

# Submit login
login_response = session.post("http://127.0.0.1:5000/login", 
                             data=login_data, 
                             allow_redirects=True)

print("Login response status:", login_response.status_code)
print("Login response URL:", login_response.url)

# Check if logged in
if "profile" in login_response.url:
    print("Login successful - redirected to profile")
else:
    print("Login failed - not redirected to profile") 