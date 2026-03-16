import sys
import os
import uuid
from datetime import datetime

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "backend")
sys.path.append(backend_dir)

from app.schemas.user import UserWithPermissions
from app.models.user import User, UserRoleEnum
from app.models.permission import Permission

def test_serialization():
    print("Testing UserWithPermissions serialization...")

    # Mock Permission
    perm1 = Permission(
        id=uuid.uuid4(),
        name="view_analytics_revenue",
        description="View revenue",
        category="analytics"
    )
    
    # Mock User
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed",
        role=UserRoleEnum.CS_AGENT,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        permissions=[perm1] # direct assignment for mock
    )

    try:
        # Attempt validation/serialization
        user_schema = UserWithPermissions.model_validate(user)
        
        # Dump to dict
        result = user_schema.model_dump()
        
        print("\n--- Result ---")
        print(f"Email: {result.get('email')}")
        print(f"Role: {result.get('role')}")
        print(f"Permissions: {result.get('permissions')}")
        
        if result.get('permissions') and len(result['permissions']) > 0:
            print(f"\nSUCCESS: Found {len(result['permissions'])} permission(s).")
            print(f"First permission: {result['permissions'][0]}")
        else:
            print("\nFAILURE: Permissions list is empty or missing.")

    except Exception as e:
        print(f"\nERROR during validation: {e}")

if __name__ == "__main__":
    test_serialization()
