import http.client
import json
import urllib.parse
import sys

def fetch_permissions_from_vps():
    HOST = "168.231.124.213"
    PORT = 80
    
    print("Logging in to VPS...", flush=True)
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    body = urllib.parse.urlencode({"username": "admin@travelagency.com", "password": "Admin123!"})
    
    conn.request("POST", "/api/v1/auth/login", body=body, headers=headers)
    resp = conn.getresponse()
    if resp.status != 200:
        print("Login failed!", resp.status, resp.read().decode())
        return
        
    data = json.loads(resp.read().decode())
    token = data["access_token"]
    
    print("Fetching permissions...")
    headers = {"Authorization": f"Bearer {token}"}
    conn.request("GET", "/api/v1/permissions", headers=headers)
    resp = conn.getresponse()
    print("Permissions status:", resp.status)
    print("Response:", resp.read().decode())
    
fetch_permissions_from_vps()
