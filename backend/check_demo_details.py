
from app.db.session import SessionLocal
from app.models.itinerary import Itinerary

db = SessionLocal()
itinerary = db.query(Itinerary).filter(Itinerary.unique_code == "DEMO12345678").first()

if itinerary:
    print(f"ID: {itinerary.id}")
    print(f"Title: {itinerary.title}")
    print(f"Client Name: {getattr(itinerary, 'client_name', 'MISSING_ATTRIBUTE')}")
    print(f"Duration Days: {getattr(itinerary, 'duration_days', 'MISSING_ATTRIBUTE')}")
    print(f"Primary Traveler: {itinerary.primary_traveler_name if hasattr(itinerary, 'primary_traveler_name') else 'N/A'}")
else:
    print("NOT FOUND")
db.close()
