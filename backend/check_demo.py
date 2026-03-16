
from app.db.session import SessionLocal
from app.models.itinerary import Itinerary

db = SessionLocal()
itinerary = db.query(Itinerary).filter(Itinerary.unique_code == "DEMO12345678").first()

if itinerary:
    print(f"FOUND: Itinerary {itinerary.unique_code} exists (ID: {itinerary.id})")
else:
    print("NOT FOUND: Demo itinerary does not exist")
db.close()
