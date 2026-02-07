
import sys
from sqlalchemy import create_engine, text

# Hardcoded from docker-compose.yml
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/travel_agency"

# When running inside docker container, host is 'postgres' not 'localhost' if using network, 
# but here we are running 'docker exec' inside the backend container.
# In docker-compose, backend connects to 'postgres' host.
# Let's try the internal one first.
DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/travel_agency"

def migrate_db():
    print(f"Connecting to database...")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # Check if column exists
            print("Checking descriptions column in inclusions...")
            try:
                conn.execute(text("ALTER TABLE inclusions ADD COLUMN description VARCHAR(500);"))
                print("Added description to inclusions.")
            except Exception as e:
                print(f"Inclusions update skipped (might already exist): {e}")
                
            print("Checking descriptions column in exclusions...")
            try:
                conn.execute(text("ALTER TABLE exclusions ADD COLUMN description VARCHAR(500);"))
                print("Added description to exclusions.")
            except Exception as e:
                print(f"Exclusions update skipped (might already exist): {e}")
                
            conn.commit()
            print("Migration completed.")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    migrate_db()
