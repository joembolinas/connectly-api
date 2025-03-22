import requests
import base64
import json

base_url = 'http://127.0.0.1:8000'
username = 'joem-admin'
password = 'Admin@123456'

print("=== AUTHENTICATION TESTS ===\n")

# Test 1: Basic Authentication
auth_string = f"{username}:{password}"
encoded_auth = base64.b64encode(auth_string.encode()).decode()
headers = {'Authorization': f'Basic {encoded_auth}'}

response = requests.get(f'{base_url}/api/posts/users/', headers=headers)
print(f"Basic Authentication: {response.status_code}")
print(f"Response: {response.text[:100]}...\n")

# Test 2: Token Authentication (first get token)
try:
    token_response = requests.post(
        f'{base_url}/api/token-auth/',
        json={'username': username, 'password': password}
    )
    token = token_response.json().get('token')
    
    if (token):
        token_headers = {'Authorization': f'Token {token}'}
        response = requests.get(f'{base_url}/api/posts/users/', headers=token_headers)
        print(f"Token Authentication: {response.status_code}")
        print(f"Response: {response.text[:100]}...\n")
    else:
        print(f"Token Authentication: Failed to obtain token")
        print(f"Response: {token_response.text}\n")
except Exception as e:
    print(f"Token Authentication: Error - {str(e)}\n")

# Test 3: Session Authentication
session = requests.Session()
login_url = f'{base_url}/admin/login/'

# Get CSRF token
response = session.get(login_url)
if 'csrftoken' in session.cookies:
    csrftoken = session.cookies['csrftoken']
    login_data = {
        'username': username,
        'password': password,
        'csrfmiddlewaretoken': csrftoken,
        'next': '/admin/'
    }
    
    response = session.post(login_url, data=login_data, headers={'Referer': login_url})
    print(f"Session Authentication: {response.status_code}")
    
    # Now try to access protected endpoint with session
    response = session.get(f'{base_url}/api/posts/users/')
    print(f"Session Access: {response.status_code}")
    print(f"Response: {response.text[:100]}...\n")
else:
    print("Session Authentication: Failed to get CSRF token\n")

print("=== AUTHENTICATION TESTS COMPLETE ===")