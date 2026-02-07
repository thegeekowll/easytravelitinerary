"""
Authentication System Test Script.

Tests the complete authentication flow including:
- Default admin creation
- Login
- Token validation
- User management

Run this script after starting the server to test authentication.
"""
import requests
import json
from typing import Dict, Optional

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_success(message: str):
    """Print success message in green."""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_error(message: str):
    """Print error message in red."""
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def print_info(message: str):
    """Print info message in blue."""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")


def print_warning(message: str):
    """Print warning message in yellow."""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def test_server_running() -> bool:
    """Test if server is running."""
    print("\n" + "=" * 70)
    print(" TEST 1: Server Health Check")
    print("=" * 70)

    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_success("Server is running")
            print_info(f"Response: {response.json()}")
            return True
        else:
            print_error(f"Server returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Could not connect to server: {e}")
        print_warning("Make sure the server is running: uvicorn app.main:app --reload")
        return False


def test_database_connection() -> bool:
    """Test database connection."""
    print("\n" + "=" * 70)
    print(" TEST 2: Database Connection")
    print("=" * 70)

    try:
        response = requests.get(f"{BASE_URL}/db-check")
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "connected":
                print_success("Database is connected")
                print_info(f"Statistics: {data.get('statistics', {})}")
                return True
            else:
                print_error(f"Database connection failed: {data.get('error')}")
                return False
        else:
            print_error(f"Database check returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Database check failed: {e}")
        return False


def test_admin_login() -> Optional[Dict]:
    """Test login with default admin credentials."""
    print("\n" + "=" * 70)
    print(" TEST 3: Admin Login")
    print("=" * 70)

    try:
        # Login credentials
        login_data = {
            "username": "admin@travelagency.com",
            "password": "Admin123!"
        }

        print_info("Attempting login with default admin credentials...")
        response = requests.post(
            f"{API_URL}/auth/login",
            data=login_data
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Login successful")
            print_info(f"User: {data.get('user', {}).get('email')}")
            print_info(f"Role: {data.get('user', {}).get('role')}")
            print_info(f"Token: {data.get('access_token')[:50]}...")
            return data
        else:
            print_error(f"Login failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Login request failed: {e}")
        return None


def test_get_current_user(token: str) -> bool:
    """Test getting current user profile."""
    print("\n" + "=" * 70)
    print(" TEST 4: Get Current User Profile")
    print("=" * 70)

    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/auth/me", headers=headers)

        if response.status_code == 200:
            data = response.json()
            print_success("Retrieved current user profile")
            print_info(f"Email: {data.get('email')}")
            print_info(f"Full Name: {data.get('full_name')}")
            print_info(f"Role: {data.get('role')}")
            print_info(f"Permissions: {len(data.get('permissions', []))} permissions")
            return True
        else:
            print_error(f"Failed to get profile: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False


def test_create_user(token: str) -> Optional[str]:
    """Test creating a new user."""
    print("\n" + "=" * 70)
    print(" TEST 5: Create CS Agent User")
    print("=" * 70)

    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        user_data = {
            "email": "testagent@travelagency.com",
            "full_name": "Test Agent",
            "password": "TestAgent123!",
            "role": "cs_agent",
            "is_active": True
        }

        print_info("Creating new CS agent user...")
        response = requests.post(
            f"{API_URL}/users",
            headers=headers,
            json=user_data
        )

        if response.status_code == 200:
            data = response.json()
            print_success("User created successfully")
            print_info(f"Email: {data.get('email')}")
            print_info(f"Role: {data.get('role')}")
            print_info(f"User ID: {data.get('id')}")
            return data.get('id')
        else:
            print_error(f"Failed to create user: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Request failed: {e}")
        return None


def test_list_users(token: str) -> bool:
    """Test listing users."""
    print("\n" + "=" * 70)
    print(" TEST 6: List All Users")
    print("=" * 70)

    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/users", headers=headers)

        if response.status_code == 200:
            data = response.json()
            print_success("Retrieved user list")
            print_info(f"Total users: {data.get('total', 0)}")
            print_info(f"Users on this page: {len(data.get('items', []))}")
            return True
        else:
            print_error(f"Failed to list users: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False


def test_agent_login() -> bool:
    """Test login with newly created agent."""
    print("\n" + "=" * 70)
    print(" TEST 7: Agent Login")
    print("=" * 70)

    try:
        login_data = {
            "username": "testagent@travelagency.com",
            "password": "TestAgent123!"
        }

        print_info("Attempting login with test agent credentials...")
        response = requests.post(
            f"{API_URL}/auth/login",
            data=login_data
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Agent login successful")
            print_info(f"User: {data.get('user', {}).get('email')}")
            print_info(f"Role: {data.get('user', {}).get('role')}")
            return True
        else:
            print_error(f"Agent login failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print(" AUTHENTICATION SYSTEM TEST SUITE")
    print("=" * 70)
    print()

    # Test 1: Server running
    if not test_server_running():
        print_error("\nServer not running. Exiting tests.")
        return

    # Test 2: Database connection
    if not test_database_connection():
        print_error("\nDatabase not connected. Exiting tests.")
        return

    # Test 3: Admin login
    auth_data = test_admin_login()
    if not auth_data:
        print_error("\nAdmin login failed. Exiting tests.")
        return

    token = auth_data.get('access_token')

    # Test 4: Get current user
    test_get_current_user(token)

    # Test 5: Create user
    user_id = test_create_user(token)

    # Test 6: List users
    test_list_users(token)

    # Test 7: Agent login
    if user_id:
        test_agent_login()

    # Final summary
    print("\n" + "=" * 70)
    print(" TEST SUMMARY")
    print("=" * 70)
    print_success("All core authentication tests completed")
    print()
    print("Next steps:")
    print("  1. Change the default admin password")
    print("  2. Test user management endpoints (update, delete, permissions)")
    print("  3. Test token refresh endpoint")
    print("  4. Implement password reset flow")
    print()


if __name__ == "__main__":
    main()
