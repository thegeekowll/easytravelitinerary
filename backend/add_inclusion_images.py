import sys
import os

# Override DB host for local script execution
os.environ["POSTGRES_SERVER"] = "localhost"

from sqlalchemy import text
from app.db.session import SessionLocal

def add_image_url_columns():
    db = SessionLocal()
    try:
        # Add image_url to inclusions
        try:
            print("Checking inclusions table...")
            # Check if column exists
            check_query = text("SELECT column_name FROM information_schema.columns WHERE table_name='inclusions' AND column_name='image_url'")
            if db.execute(check_query).fetchone():
                print("Column 'image_url' already exists in 'inclusions'.")
            else:
                db.execute(text("ALTER TABLE inclusions ADD COLUMN image_url VARCHAR"))
                db.commit()
                print("Added image_url to inclusions table")
        except Exception as e:
            print(f"Error adding to inclusions: {e}")
            db.rollback()

        # Add image_url to exclusions
        try:
            print("Checking exclusions table...")
            # Check if column exists
            check_query = text("SELECT column_name FROM information_schema.columns WHERE table_name='exclusions' AND column_name='image_url'")
            if db.execute(check_query).fetchone():
                print("Column 'image_url' already exists in 'exclusions'.")
            else:
                db.execute(text("ALTER TABLE exclusions ADD COLUMN image_url VARCHAR"))
                db.commit()
                print("Added image_url to exclusions table")
        except Exception as e:
            print(f"Error adding to exclusions: {e}")
            db.rollback()
            
    finally:
        db.close()

if __name__ == "__main__":
    add_image_url_columns()
