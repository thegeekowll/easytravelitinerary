
import os
import sys
from sqlalchemy import text
from app.db.session import SessionLocal

def add_column():
    db = SessionLocal()
    try:
        print("Checking if column exists...")
        result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='itinerary_days' AND column_name='meals_included'"))
        if result.fetchone():
            print("Column 'meals_included' already exists.")
        else:
            print("Adding column 'meals_included'...")
            db.execute(text("ALTER TABLE itinerary_days ADD COLUMN meals_included VARCHAR(255)"))
            db.commit()
            print("Column added successfully.")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_column()
