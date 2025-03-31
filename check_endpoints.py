import requests
import sys

base_url = "http://127.0.0.1:8000"

# Define endpoints with their appropriate HTTP methods
endpoints = [
    {"url": "/swagger/", "method": "GET"},
    {"url": "/redoc/", "method": "GET"},
    {"url": "/api/auth/token/", "method": "POST", "data": {"username": "testuser", "password": "testpassword"}},
    {"url": "/api/auth/jwt/", "method": "POST", "data": {"username": "testuser", "password": "testpassword"}},
    {"url": "/api-auth/login/", "method": "GET"}
]

print("Checking API endpoints...\n")

for endpoint in endpoints:
    url = f"{base_url}{endpoint['url']}"
    method = endpoint["method"]
    data = endpoint.get("data", {})
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        status = response.status_code
        if status in [200, 400, 401]:  # 400/401 are expected with wrong credentials
            result = "✅ Available"
        else:
            result = f"❌ Error: Status {status}"
    except requests.exceptions.ConnectionError:
        result = "❌ Connection Error"
    
    print(f"{endpoint['url'].ljust(30)} [{method}] {result}")

print("\nIf you see connection errors, make sure your Django server is running.")
print("Run: python manage.py runserver")