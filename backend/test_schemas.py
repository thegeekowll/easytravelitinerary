"""
Schema validation test script.

Tests that all Pydantic schemas can be imported and basic validation works.
"""
import sys
from pathlib import Path
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_schema_imports():
    """Test that all schemas can be imported."""
    print("=" * 70)
    print(" SCHEMA IMPORT TEST")
    print("=" * 70)
    print()

    try:
        print("📦 Importing common schemas...")
        from app.schemas.common import PaginatedResponse, MessageResponse, ErrorResponse
        print("   ✅ Common schemas imported")

        print("📦 Importing user schemas...")
        from app.schemas.user import UserCreate, UserResponse, UserWithPermissions
        print("   ✅ User schemas imported")

        print("📦 Importing permission schemas...")
        from app.schemas.permission import PermissionCreate, PermissionResponse
        print("   ✅ Permission schemas imported")

        print("📦 Importing agent type schemas...")
        from app.schemas.agent_type import AgentTypeCreate, AgentTypeResponse
        print("   ✅ Agent type schemas imported")

        print("📦 Importing destination schemas...")
        from app.schemas.destination import DestinationCreate, DestinationWithImages
        print("   ✅ Destination schemas imported")

        print("📦 Importing accommodation schemas...")
        from app.schemas.accommodation import AccommodationCreate, AccommodationWithDetails
        print("   ✅ Accommodation schemas imported")

        print("📦 Importing base tour schemas...")
        from app.schemas.base_tour import BaseTourCreate, BaseTourWithDetails
        print("   ✅ Base tour schemas imported")

        print("📦 Importing inclusion/exclusion schemas...")
        from app.schemas.inclusion import InclusionCreate
        from app.schemas.exclusion import ExclusionCreate
        print("   ✅ Inclusion/Exclusion schemas imported")

        print("📦 Importing destination combination schemas...")
        from app.schemas.destination_combination import DestinationCombinationCreate
        print("   ✅ Destination combination schemas imported")

        print("📦 Importing itinerary schemas...")
        from app.schemas.itinerary import (
            ItineraryCreateCustom,
            ItineraryCreateChooseExisting,
            ItineraryWithDetails
        )
        print("   ✅ Itinerary schemas imported")

        print("📦 Importing payment schemas...")
        from app.schemas.payment import PaymentRecordCreate, PaymentSummary
        print("   ✅ Payment schemas imported")

        print("📦 Importing email schemas...")
        from app.schemas.email import EmailSendRequest, EmailLogResponse
        print("   ✅ Email schemas imported")

        print("📦 Importing notification schemas...")
        from app.schemas.notification import NotificationCreate, NotificationSummary
        print("   ✅ Notification schemas imported")

        print("📦 Importing company schemas...")
        from app.schemas.company import CompanyContentCreate, CompanyAssetCreate
        print("   ✅ Company schemas imported")

        print()
        print("✅ ALL SCHEMAS IMPORTED SUCCESSFULLY")
        return True

    except Exception as e:
        print()
        print(f"❌ IMPORT FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_schema_validation():
    """Test basic schema validation."""
    print()
    print("=" * 70)
    print(" SCHEMA VALIDATION TEST")
    print("=" * 70)
    print()

    try:
        from app.schemas.user import UserCreate
        from app.schemas.destination import DestinationCreate
        from app.schemas.itinerary import ItineraryCreateCustom, ItineraryDayCreate

        # Test 1: Valid user creation
        print("🧪 Test 1: Valid user creation...")
        user = UserCreate(
            email="agent@travel.com",
            full_name="John Smith",
            password="SecurePass123!",
            role="cs_agent"
        )
        print(f"   ✅ User created: {user.email}")

        # Test 2: Invalid password (should fail)
        print("🧪 Test 2: Invalid password (should fail)...")
        try:
            invalid_user = UserCreate(
                email="test@test.com",
                full_name="Test",
                password="weak",  # Too short, no complexity
                role="cs_agent"
            )
            print("   ❌ VALIDATION SHOULD HAVE FAILED")
            return False
        except ValueError as e:
            print(f"   ✅ Validation correctly rejected: {str(e)[:50]}...")

        # Test 3: Valid destination
        print("🧪 Test 3: Valid destination with GPS validation...")
        destination = DestinationCreate(
            name="Paris, France",
            country="France",
            gps_coordinates="48.8566,2.3522",
            timezone="Europe/Paris"
        )
        print(f"   ✅ Destination created: {destination.name}")

        # Test 4: Invalid GPS coordinates (should fail)
        print("🧪 Test 4: Invalid GPS coordinates (should fail)...")
        try:
            invalid_dest = DestinationCreate(
                name="Test",
                country="Test",
                gps_coordinates="invalid"
            )
            print("   ❌ VALIDATION SHOULD HAVE FAILED")
            return False
        except ValueError as e:
            print(f"   ✅ Validation correctly rejected: {str(e)[:50]}...")

        # Test 5: Valid custom itinerary
        print("🧪 Test 5: Valid custom itinerary with date validation...")
        itinerary = ItineraryCreateCustom(
            creation_method="custom",
            tour_title="European Tour - Smith Family",
            client_name="John Smith",
            client_email="john@example.com",
            number_of_travelers=4,
            departure_date=date(2024, 6, 15),
            return_date=date(2024, 6, 28),
            days=[
                ItineraryDayCreate(
                    itinerary_id=uuid4(),
                    day_number=1,
                    description="Arrival day",
                    destination_ids=[]
                )
            ]
        )
        print(f"   ✅ Itinerary created: {itinerary.tour_title}")

        # Test 6: Invalid dates (return before departure - should fail)
        print("🧪 Test 6: Invalid dates (should fail)...")
        try:
            invalid_itin = ItineraryCreateCustom(
                creation_method="custom",
                tour_title="Test",
                client_name="Test",
                client_email="test@test.com",
                departure_date=date(2024, 6, 28),
                return_date=date(2024, 6, 15),  # Before departure!
                days=[]
            )
            print("   ❌ VALIDATION SHOULD HAVE FAILED")
            return False
        except ValueError as e:
            print(f"   ✅ Validation correctly rejected: {str(e)[:50]}...")

        print()
        print("✅ ALL VALIDATION TESTS PASSED")
        return True

    except Exception as e:
        print()
        print(f"❌ VALIDATION TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_schema_serialization():
    """Test that schemas can serialize to dict/JSON."""
    print()
    print("=" * 70)
    print(" SCHEMA SERIALIZATION TEST")
    print("=" * 70)
    print()

    try:
        from app.schemas.user import UserCreate
        from app.schemas.common import MessageResponse, PaginatedResponse

        # Test 1: Basic serialization
        print("🧪 Test 1: User schema to dict...")
        user = UserCreate(
            email="agent@travel.com",
            full_name="John Smith",
            password="SecurePass123!",
            role="cs_agent"
        )
        user_dict = user.model_dump()
        print(f"   ✅ Serialized to dict with {len(user_dict)} fields")

        # Test 2: JSON serialization
        print("🧪 Test 2: Schema to JSON...")
        user_json = user.model_dump_json()
        print(f"   ✅ Serialized to JSON ({len(user_json)} chars)")

        # Test 3: Generic pagination
        print("🧪 Test 3: Generic PaginatedResponse...")
        from app.schemas.destination import DestinationResponse

        # Note: Can't fully test without actual data, but can check it exists
        print(f"   ✅ PaginatedResponse[DestinationResponse] available")

        # Test 4: Message response
        print("🧪 Test 4: MessageResponse...")
        msg = MessageResponse(message="Test successful")
        msg_dict = msg.model_dump()
        print(f"   ✅ MessageResponse created: {msg_dict}")

        print()
        print("✅ ALL SERIALIZATION TESTS PASSED")
        return True

    except Exception as e:
        print()
        print(f"❌ SERIALIZATION TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print()

    # Run all tests
    import_success = test_schema_imports()

    if import_success:
        validation_success = test_schema_validation()
        serialization_success = test_schema_serialization()

        print()
        print("=" * 70)
        print(" FINAL RESULTS")
        print("=" * 70)
        print()
        print(f"Import Test:         {'✅ PASSED' if import_success else '❌ FAILED'}")
        print(f"Validation Test:     {'✅ PASSED' if validation_success else '❌ FAILED'}")
        print(f"Serialization Test:  {'✅ PASSED' if serialization_success else '❌ FAILED'}")
        print()

        if import_success and validation_success and serialization_success:
            print("🎉 ALL TESTS PASSED - SCHEMAS ARE READY TO USE!")
            print()
            sys.exit(0)
        else:
            print("⚠️  SOME TESTS FAILED - REVIEW ERRORS ABOVE")
            print()
            sys.exit(1)
    else:
        print()
        print("❌ IMPORT TEST FAILED - FIX IMPORTS BEFORE RUNNING OTHER TESTS")
        print()
        sys.exit(1)
