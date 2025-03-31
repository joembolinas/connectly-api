import requests
import json

base_url = "http://127.0.0.1:8000"

# Function to test token authentication
def test_token_auth(username, password):
    print("\n===== Testing Token Authentication =====")
    url = f"{base_url}/api/auth/token/"
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    
    try:
        content = response.json()
        if "token" in content:
            print("Success! Token received.")
            print(f"Token: {content['token']}")
            return content["token"]
        else:
            print("Response content:")
            print(json.dumps(content, indent=2))
    except Exception as e:
        print(f"Failed to parse response: {e}")
        print(f"Response text: {response.text}")
    
    return None

# Function to test JWT authentication
def test_jwt_auth(username, password):
    print("\n===== Testing JWT Authentication =====")
    url = f"{base_url}/api/auth/jwt/"
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    
    try:
        content = response.json()
        if "access" in content:
            print("Success! JWT received.")
            print(f"Access token: {content['access']}")
            return content["access"]
        else:
            print("Response content:")
            print(json.dumps(content, indent=2))
    except Exception as e:
        print(f"Failed to parse response: {e}")
        print(f"Response text: {response.text}")
    
    return None

# Function to test protected endpoint using token
def test_protected_endpoint(token_type, token):
    print(f"\n===== Testing Protected Endpoint with {token_type} =====")
    url = f"{base_url}/api/posts/feed/"
    
    headers = {}
    if token_type == "Token":
        headers["Authorization"] = f"Token {token}"
    elif token_type == "JWT":
        headers["Authorization"] = f"Bearer {token}"
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    try:
        content = response.json()
        print("Response content:")
        print(json.dumps(content, indent=2))
    except Exception as e:
        print(f"Failed to parse response: {e}")
        print(f"Response text: {response.text}")

if __name__ == "__main__":
    # Replace with actual credentials
    username = "joem-admin"
    password = "Admin@123456"
    
    # Test token auth
    token = test_token_auth(username, password)
    
    # Test JWT auth
    jwt = test_jwt_auth(username, password)
    
    # Test protected endpoint with token if received
    if token:
        test_protected_endpoint("Token", token)
    
    # Test protected endpoint with JWT if received
    if jwt:
        test_protected_endpoint("JWT", jwt)