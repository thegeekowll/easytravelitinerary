from sqlalchemy import create_engine, text
import os

# Use the connection string from docker-compose or environment
# Defaulting to localhost for running from host machine if port mapped, 
# but inside container (which I might be able to run via run_command exec) it needs internal host.
# I'll try running it via docker exec.

DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/travel_agency"

def debug_db():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("--- Company Assets ---")
        result = conn.execute(text("SELECT id, asset_type, asset_name, asset_url FROM company_assets"))
        rows = result.fetchall()
        if not rows:
            print("No assets found.")
        for row in rows:
            print(f"ID: {row[0]}, Type: '{row[1]}', Name: '{row[2]}', URL: '{row[3]}'")

if __name__ == "__main__":
    debug_db()
