import http.client
import json
import urllib.parse

HOST = "localhost"
PORT = 8000
API_BASE = "/api/v1"

def request(method, path, body=None, headers=None):
    if headers is None:
        headers = {}
    
    conn = http.client.HTTPConnection(HOST, PORT)
    headers["Content-Type"] = "application/json"
    
    json_body = json.dumps(body) if body else None
    
    try:
        conn.request(method, f"{API_BASE}{path}", body=json_body, headers=headers)
        response = conn.getresponse()
        data = response.read().decode()
        
        try:
            json_data = json.loads(data)
        except:
            json_data = data
            
        return response.status, json_data, response.getheader("Authorization")
    except Exception as e:
        print(f"Request failed: {e}")
        return 500, str(e), None
    finally:
        conn.close()

def request_encoded(method, path, body=None, headers=None):
    if headers is None:
        headers = {}
    
    conn = http.client.HTTPConnection(HOST, PORT)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    
    encoded_body = urllib.parse.urlencode(body) if body else None
    
    try:
        conn.request(method, f"{API_BASE}{path}", body=encoded_body, headers=headers)
        response = conn.getresponse()
        data = response.read().decode()
        
        try:
            json_data = json.loads(data)
        except:
            json_data = data
            
        return response.status, json_data, response.getheader("Authorization")
    except Exception as e:
        print(f"Request failed: {e}")
        return 500, str(e), None
    finally:
        conn.close()

def test_permission_flow():
    print("1. Logging in as Admin...")
    login_data = {"username": "admin@travelagency.com", "password": "Admin123!"}
    status, data, _ = request_encoded("POST", "/auth/login", body=login_data)
    
    if status != 200:
        print(f"Admin login failed: {status} {data}")
        return
    
    admin_token = data["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("✅ Admin logged in.")

    print("\n2. Fetching Permissions...")
    status, permissions, _ = request("GET", "/users/admin@travelagency.com/permissions", headers=admin_headers) # Wrong endpoint, checking permissions table directly isn't exposed usually?
    # Wait, seed_data said permissions table. Is there an endpoint to list all permissions?
    # I saw apiClient.getPermissions() calling /permissions. Let's try that.
    status, permissions, _ = request("GET", "/permissions", headers=admin_headers)
    
    if status != 200:
        print(f"Failed to fetch permissions: {status} {data}")
        # Try to find /permissions endpoint in backend code?
        # Assuming it exists based on seed_data saying seeded.
        return

    revenue_perm = next((p for p in permissions if p["name"] == "view_analytics_revenue"), None)
    if not revenue_perm:
        print("❌ 'view_analytics_revenue' permission NOT FOUND!")
        return
    print(f"✅ Found permission: {revenue_perm['name']} ({revenue_perm['id']})")

    print("\n3. Creating/Updating Test Agent...")
    agent_email = "test_agent_rev@example.com"
    agent_password = "Password123!"
    
    status, users_resp, _ = request("GET", "/users", headers=admin_headers)
    users = users_resp["items"]
    agent = next((u for u in users if u["email"] == agent_email), None)
    
    if agent:
        agent_id = agent["id"]
        print(f"Agent exists ({agent_id}). Updating permissions...")
        update_data = {"permission_ids": [revenue_perm["id"]]}
        status, _, _ = request("PATCH", f"/users/{agent_id}", body=update_data, headers=admin_headers)
        if status != 200:
            print(f"Update failed: {status}")
            return
    else:
        print("Creating new agent...")
        create_data = {
            "email": agent_email,
            "full_name": "Test Agent Revenue",
            "password": agent_password,
            "role": "cs_agent",
            "permission_ids": [revenue_perm["id"]]
        }
        status, resp, _ = request("POST", "/users", body=create_data, headers=admin_headers)
        if status != 200:
            print(f"Create user failed: {status} {resp}")
            return
        agent_id = resp["id"]

    print("✅ Agent ready.")

    print("\n4. Logging in as Agent...")
    agent_login = {"username": agent_email, "password": agent_password}
    status, login_json, _ = request_encoded("POST", "/auth/login", body=agent_login)
    
    if status != 200:
        print(f"Agent login failed: {status} {login_json}")
        return
    
    user_data = login_json["user"]
    if "permissions" not in user_data:
        print("❌ 'permissions' field MISSING in Login response!")
    else:
        perms = user_data["permissions"]
        print(f"Login Permissions Count: {len(perms)}")
        has_perm = any(p["name"] == "view_analytics_revenue" for p in perms)
        if has_perm:
            print("✅ Login response contains 'view_analytics_revenue'")
        else:
            print("❌ Login response permissions do NOT contain 'view_analytics_revenue'")

    print("\n5. Checking /auth/me...")
    agent_token = login_json["access_token"]
    agent_headers = {"Authorization": f"Bearer {agent_token}"}
    
    status, me_json, _ = request("GET", "/auth/me", headers=agent_headers)
    if status != 200:
        print(f"Me request failed: {status}")
        return
        
    if "permissions" not in me_json:
        print("❌ 'permissions' field MISSING in /me response!")
    else:
        perms = me_json["permissions"]
        print(f"/me Permissions Count: {len(perms)}")
        has_perm = any(p["name"] == "view_analytics_revenue" for p in perms)
        if has_perm:
            print("✅ /me response contains 'view_analytics_revenue'")
        else:
            print("❌ /me response permissions do NOT contain 'view_analytics_revenue'")

if __name__ == "__main__":
    test_permission_flow()
