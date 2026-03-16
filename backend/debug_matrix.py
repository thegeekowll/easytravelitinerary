import requests
import sys
import json

BASE_URL = "http://localhost:8000/api/v1"

def debug_matrix():
    # 1. Login
    print("Logging in...")
    login_data = {
        "username": "admin@travelagency.com",
        "password": "Admin123!"
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        sys.exit(1)
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")

    # 2. Call Matrix Grid Endpoint
    print("Fetching matrix grid...")
    response = requests.get(f"{BASE_URL}/destination-combinations/grid", headers=headers)
    
    if response.status_code == 200:
        print("Success!")
        data = response.json()
        print(f"Rows: {len(data['row_destinations'])}")
        print(f"Cols: {len(data['col_destinations'])}")
        print(f"Combinations: {len(data['combinations'])}")
    else:
        print(f"Failed grid: {response.status_code}")
        print(response.text)

    # 3. Call List Endpoint
    print("\nFetching list...")
    response = requests.get(f"{BASE_URL}/destination-combinations", headers=headers)
    if response.status_code == 200:
        print(f"List success! Items: {response.json()['total']}")
    else:
        print(f"List failed: {response.status_code}")
        print(response.text)

    # 4. Call Auto-fill Endpoint (Fail case)
    print("\nTesting auto-fill (empty)...")
    try:
        response = requests.post(f"{BASE_URL}/destination-combinations/auto-fill", json={"destination_ids": []}, headers=headers)
        print(f"Auto-fill status: {response.status_code}")
    except Exception as e:
         print(f"Auto-fill error: {e}")

if __name__ == "__main__":
    debug_matrix()
