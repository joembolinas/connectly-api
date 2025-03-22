import requests

# Try basic API access
response = requests.get('http://127.0.0.1:8000/api/')
print(f"API Root: {response.status_code}")
print(response.text)

# Try accessing the posts endpoint
response = requests.get('http://127.0.0.1:8000/api/posts/posts/')
print(f"\nPosts endpoint: {response.status_code}")
print(response.text)

# Check what URLs are available
response = requests.get('http://127.0.0.1:8000/')
print(f"\nRoot URL: {response.status_code}")