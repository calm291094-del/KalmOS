# test_endpoint.py - Para verificar que el endpoint existe
import requests

try:
    r = requests.get('http://localhost:8080/api/browser/bookmarks')
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")