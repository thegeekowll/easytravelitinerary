import sys
import os

# Add the parent directory to sys.path to allow importing app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "backend")
sys.path.append(backend_dir)

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.permission import Permission

def debug_specific_user():
    db = SessionLocal()
    try:
        email = "test_agent_rev@example.com"
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            print(f"FOUND USER: {user.email}")
            print(f"Role: {user.role}")
            
            # Use sql to query user_permissions table directly
            from sqlalchemy import text
            result = db.execute(text(
                "SELECT p.name, p.id FROM permissions p "
                "JOIN user_permissions up ON p.id = up.permission_id "
                "WHERE up.user_id = :uid"
            ), {"uid": user.id}).fetchall()
            
            print(f"Direct SQL Permission Count: {len(result)}")
            for row in result:
                print(f" - {row[0]} ({row[1]})")
                
            # Check ORM relationship
            print(f"ORM Permission Count: {len(user.permissions)}")
            for p in user.permissions:
                print(f" - {p.name}")
        else:
            print(f"User {email} NOT FOUND.")
            
            # List all users
            all_users = db.query(User.email).all()
            print("Available users:", [u[0] for u in all_users])

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_specific_user()
