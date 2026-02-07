import requests
import sys

API_URL = "http://localhost:8000/api/v1"
EMAIL = "admin@travelagency.com"
PASSWORD = "Admin123!"

def test_flow():
    with open("test_output.txt", "w") as f:
        # 1. Login
        f.write(f"Logging in as {EMAIL}...\n")
        try:
            resp = requests.post(f"{API_URL}/auth/login", data={"username": EMAIL, "password": PASSWORD})
            if resp.status_code != 200:
                f.write(f"Login failed: {resp.status_code} - {resp.text}\n")
                sys.exit(1)
            
            token = resp.json()["access_token"]
            f.write("Login successful. Token acquired.\n")
            
            # 2. Get Itineraries
            f.write("Fetching itineraries...\n")
            headers = {"Authorization": f"Bearer {token}"}
            resp = requests.get(f"{API_URL}/itineraries", headers=headers)
            
            if resp.status_code == 200:
                data = resp.json()
                f.write(f"Success! Found {len(data)} itineraries.\n")
                f.write(str(data) + "\n")
            else:
                f.write(f"Failed to fetch itineraries: {resp.status_code} - {resp.text}\n")
                sys.exit(1)
                
        except Exception as e:
            f.write(f"Error: {e}\n")
            sys.exit(1)

if __name__ == "__main__":
    test_flow()
