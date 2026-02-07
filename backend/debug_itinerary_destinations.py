import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Hardcoded connection string for local execution
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/travel_agency"

def check_itinerary_destinations(itinerary_id):
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print(f"Checking itinerary: {itinerary_id}")
        
        # 1. Check if itinerary exists
        result = db.execute(text("SELECT id, tour_title FROM itineraries WHERE id = :id"), {"id": itinerary_id}).fetchone()
        if not result:
            print("Itinerary not found!")
            return
        print(f"Found Itinerary: {result[1]}")
        
        # 2. Get Days
        days = db.execute(text("SELECT id, day_number FROM itinerary_days WHERE itinerary_id = :id ORDER BY day_number"), {"id": itinerary_id}).fetchall()
        print(f"Found {len(days)} days.")
        
        # 3. For each day, check destinations
        for day in days:
            day_id = day[0]
            day_num = day[1]
            
            dests = db.execute(text("""
                SELECT d.name 
                FROM itinerary_day_destinations idd
                JOIN destinations d ON idd.destination_id = d.id
                WHERE idd.itinerary_day_id = :day_id
            """), {"day_id": day_id}).fetchall()
            
            print(f"Day {day_num} has {len(dests)} destinations: {[d[0] for d in dests]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_itinerary_destinations("f5f25ef0-fab3-45fb-a6d7-6bf7f59eb129")
