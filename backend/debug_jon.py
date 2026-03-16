import sys
import os

# Add /app to pythonpath to find app modules
sys.path.append('/app')

from app.db.session import SessionLocal
from app.models.itinerary import Itinerary, Traveler
from sqlalchemy import text

def debug_jon():
    db = SessionLocal()
    try:
        print("Searching for 'jonjon'...")
        # Case insensitive search
        t = db.query(Traveler).filter(Traveler.full_name.ilike('%jon%')).first()
        
        if t:
            print(f"FOUND TRAVELER: {t.full_name}")
            print(f"  ID: {t.id}")
            print(f"  Is Primary: {t.is_primary}")
            print(f"  Age: {t.age}")
            print(f"  Nationality: {t.nationality}")
            print(f"  Itinerary ID: {t.itinerary_id}")
            
            i = db.query(Itinerary).filter(Itinerary.id == t.itinerary_id).first()
            if i:
                print(f"LINKED ITINERARY FOUND")
                print(f"  Client Name: '{i.client_name}'")
                print(f"  Client Email: '{i.client_email}'")
                print(f"  Client Phone: '{i.client_phone}'")
                print(f"  Traveler Count: {i.number_of_travelers}")
            else:
                print("  ! No linked itinerary found")
                
            # FIX IT IF BROKEN
            if not t.is_primary or i.client_name in ['Guest', 'Unknown Client'] or not i.client_name:
                print("\nDETECTED BROKEN LEGACY DATA. ATTEMPTING FIX...")
                
                # Fix Traveler
                t.is_primary = True
                print(f"  -> Set {t.full_name} as PRIMARY")
                
                # Fix Itinerary
                if i:
                    i.client_name = t.full_name
                    i.client_email = t.email or i.client_email
                    i.client_phone = t.phone or i.client_phone
                    print(f"  -> Updated Itinerary Client Details to match {t.full_name}")
                
                db.commit()
                print("FIX APPLIED SUCCESSFULLY.")
                
        else:
            print("No traveler found matching 'jon'")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_jon()
