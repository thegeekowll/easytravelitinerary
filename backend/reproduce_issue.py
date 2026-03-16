
import sys
from pathlib import Path
from uuid import uuid4
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.services.itinerary_service import itinerary_service
from app.schemas.itinerary import ItineraryCreateCustom, ItineraryDayCreate
from app.models.base_tour import TourType

def reproduce_issue():
    db = SessionLocal()
    try:
        # Get a tour type (or create one if missing, though we expect it might fail if strictly enforced)
        tour_type = db.query(TourType).first()
        if not tour_type:
            print("No tour types found! Cannot proceed with reproduction properly without at least one tour type.")
            # For reproduction of the *attribute* error, we might need a dummy ID even if it doesn't exist in DB
            # but FK constraints might bite us. Let's try to create one or use a dummy UUID if we can't find one.
            tour_type_id = uuid4()
        else:
            tour_type_id = tour_type.id

        admin_user_id = uuid4() # In a real test we'd need a real user, but let's see where it fails. 
        # Actually, for ItineraryService to assign to user, we might need real users if there are FK checks.
        # But usually service logic runs before DB flush? No, it flushes.
        # So we probably need a real user.
        
        from app.models.user import User, UserRoleEnum
        user = db.query(User).first()
        if not user:
            print("No user found. Creating dummy user for test.")
            user = User(email=f"test{uuid4()}@example.com", hashed_password="pw", full_name="Test", role=UserRoleEnum.ADMIN)
            db.add(user)
            db.commit()
        
        admin_user_id = user.id

        print(f"Using Tour Type ID: {tour_type_id}")
        print(f"Using User ID: {admin_user_id}")

        # Construct payload causing the issue
        # The issue is that ItineraryService.create_custom_itinerary accesses .title on these objects
        # But our schema ItineraryDayCreate has .day_title, not .title
        
        days = [
            ItineraryDayCreate(
                day_number=1,
                day_title="Test Day 1",
                description="Test Description",
                itinerary_id=uuid4(), # Dummy, service overwrites
                destination_ids=[],
                accommodation_id=None # mimic frontend sending null
            )
        ]
        
        tour_data = ItineraryCreateCustom(
            tour_title="Test Custom Itinerary",
            client_name="Test Client",
            client_email="test@client.com",
            departure_date=date.today(),
            return_date=date.today(),
            tour_type_id=tour_type_id,
            days=days
        )
        
        print("Attempting to create custom itinerary...")
        try:
            itinerary_service.create_custom_itinerary(
                tour_data=tour_data,
                days=days,
                travelers=[],
                departure_date=date.today(),
                assigned_to_user_id=admin_user_id,
                created_by_user_id=admin_user_id,
                db=db
            )
            print("SUCCESS: Itinerary created (Unexpected if bug exists)")
        except AttributeError as e:
            print(f"CAUGHT EXPECTED ERROR: {e}")
            if "'ItineraryDayCreate' object has no attribute 'title'" in str(e):
                print(">> CONFIRMED: Bug reproduced successfully.")
            else:
                print(">> WARNING: AttributeError caught but message differs.")
        except Exception as e:
            print(f"CAUGHT UNEXPECTED ERROR: {type(e).__name__}: {e}")
            # If it's the FK error for tour type, that's fine, we want to see the attribute error first ideally.
            # But the attribute error happens inside the loop processing days, which happens AFTER itinerary creation/flush?
            # Let's check service code order.
            # Itinerary is created and flushed FIRST.
            # Then loop over days.
            # So if Tour Type is missing, we'll get FK error first.
            if "ForeignKeyViolation" in str(e) or "tour_type" in str(e):
                print(">> Failed at DB constraint step (probably missing tour type).")

    finally:
        db.close()

if __name__ == "__main__":
    reproduce_issue()
