
import sys
from sqlalchemy import create_engine, text

# Backend runs on 'postgres' host within docker network
DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/travel_agency"

def migrate_db():
    print(f"Connecting to database to update base_tours...")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            
            # Add description
            print("Adding description column...")
            try:
                conn.execute(text("ALTER TABLE base_tours ADD COLUMN description TEXT;"))
                print("Added description.")
            except Exception as e:
                print(f"Skipped description: {e}")

            # Add highlights
            print("Adding highlights column...")
            try:
                conn.execute(text("ALTER TABLE base_tours ADD COLUMN highlights TEXT;"))
                print("Added highlights.")
            except Exception as e:
                print(f"Skipped highlights: {e}")
                
            # Add difficulty_level
            print("Adding difficulty_level column...")
            try:
                conn.execute(text("ALTER TABLE base_tours ADD COLUMN difficulty_level VARCHAR(50);"))
                print("Added difficulty_level.")
            except Exception as e:
                print(f"Skipped difficulty_level: {e}")

            conn.commit()
            print("Migration completed.")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    migrate_db()
