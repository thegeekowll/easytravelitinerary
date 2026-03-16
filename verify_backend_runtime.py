import sys
import os
from uuid import UUID

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "backend")
sys.path.append(backend_dir)

from app.db.session import SessionLocal
from app.services.auth_service import AuthService
from app.schemas.user import UserWithPermissions
from app.models.user import User

def verify_runtime():
    db = SessionLocal()
    try:
        email = "test_agent_rev@example.com"
        print(f"Fetching user {email}...")
        
        # 1. Fetch User directly
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print("User not found!")
            return

        print(f"User ID: {user.id}")
        
        # 2. Check ORM permissions
        print(f"ORM Permissions count: {len(user.permissions)}")
        for p in user.permissions:
            print(f" - {p.name}")
            
        # 3. Attempt Pydantic Serialization (This mimics the API response)
        print("\nAttempting Pydantic Serialization...")
        try:
            user_pydantic = UserWithPermissions.model_validate(user)
            data = user_pydantic.model_dump()
            print("Serialization SUCCESS")
            print(f"Serialized Permissions: {len(data['permissions'])}")
            for p in data['permissions']:
                print(f" - {p['name']}")
                
        except Exception as e:
            print(f"Serialization FAILED: {e}")

    finally:
        db.close()

if __name__ == "__main__":
    verify_runtime()
