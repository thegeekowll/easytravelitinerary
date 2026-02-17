
import sys
import os
from pathlib import Path

# Add the current directory to sys.path so that 'app' module can be found
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.models.user import User, UserRoleEnum
from app.core.security import get_password_hash

def create_superuser():
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.email == "admin@example.com").first()
        if user:
            print("Admin user already exists")
            return

        print("Creating admin user...")
        # Note: adjust fields based on User model definition if needed
        user = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            role=UserRoleEnum.ADMIN,
            is_active=True
        )
        session.add(user)
        session.commit()
        print("Admin user created successfully")
        print("Email: admin@example.com")
        print("Password: admin123")
    except Exception as e:
        print(f"Error creating user: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    create_superuser()
