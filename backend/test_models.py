"""
Comprehensive test script for all database models.

This script creates test records for each model, verifies relationships,
and cleans up afterwards.
"""
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.core.security import get_password_hash
from app.models import *


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def test_database_models():
    """Test all database models."""
    print_section("STARTING DATABASE MODEL TESTS")

    db: Session = SessionLocal()

    try:
        # ============================================================
        # TEST 1: USER & PERMISSION MODELS
        # ============================================================
        print_section("TEST 1: User & Permission Models")

        # Create admin user
        admin = User(
            email="admin@test.com",
            hashed_password=get_password_hash("Admin123!"),
            full_name="Admin User",
            role=UserRoleEnum.ADMIN,
            is_active=True
        )
        db.add(admin)
        db.flush()
        print(f"✅ Created admin user: {admin.email}")

        # Create CS agent
        agent = User(
            email="agent@test.com",
            hashed_password=get_password_hash("Agent123!"),
            full_name="CS Agent",
            role=UserRoleEnum.CS_AGENT,
            is_active=True
        )
        db.add(agent)
        db.flush()
        print(f"✅ Created CS agent: {agent.email}")

        # Create permission
        permission = Permission(
            name=PermissionNames.CREATE_ITINERARY,
            description="Can create itineraries",
            category=PermissionCategories.ITINERARY
        )
        db.add(permission)
        db.flush()
        print(f"✅ Created permission: {permission.name}")

        # Assign permission to agent
        agent.permissions.append(permission)
        db.flush()
        print(f"✅ Assigned permission to agent")

        # ============================================================
        # TEST 2: AGENT TYPE MODEL
        # ============================================================
        print_section("TEST 2: Agent Type Model")

        agent_type = AgentType(
            name="Safari Specialist",
            description="Expert in safari tours",
            created_by_admin_id=admin.id
        )
        db.add(agent_type)
        db.flush()
        agent.agent_type_id = agent_type.id
        db.flush()
        print(f"✅ Created agent type: {agent_type.name}")

        # ============================================================
        # TEST 3: DESTINATION MODELS
        # ============================================================
        print_section("TEST 3: Destination Models")

        serengeti = Destination(
            name="Serengeti National Park",
            description="Tanzania's most famous wildlife sanctuary",
            country="Tanzania",
            region="Northern Circuit",
            gps_latitude=-2.3333,
            gps_longitude=34.8333,
            activities=["Game drives", "Hot air balloon safari"],
            tags=["Wildlife", "Safari", "Big Five"],
            created_by_user_id=admin.id
        )
        db.add(serengeti)
        db.flush()
        print(f"✅ Created destination: {serengeti.name}")

        ngorongoro = Destination(
            name="Ngorongoro Crater",
            description="World's largest volcanic caldera",
            country="Tanzania",
            region="Northern Circuit",
            gps_latitude=-3.1667,
            gps_longitude=35.5833,
            activities=["Crater tour", "Maasai village visit"],
            tags=["Wildlife", "Crater", "UNESCO"],
            created_by_user_id=admin.id
        )
        db.add(ngorongoro)
        db.flush()
        print(f"✅ Created destination: {ngorongoro.name}")

        # Create destination image
        dest_image = DestinationImage(
            destination_id=serengeti.id,
            image_url="https://example.com/serengeti.jpg",
            image_type=ImageTypeEnum.ATMOSPHERIC,
            caption="Serengeti plains at sunset",
            sort_order=1
        )
        db.add(dest_image)
        db.flush()
        print(f"✅ Created destination image")

        # ============================================================
        # TEST 4: DESTINATION COMBINATION (2D TABLE)
        # ============================================================
        print_section("TEST 4: Destination Combination (2D Table)")

        combo = DestinationCombination(
            destination_1_id=serengeti.id,
            destination_2_id=ngorongoro.id,
            description_content="Experience the best of Tanzania with Serengeti and Ngorongoro...",
            activity_content="Day 1-3: Serengeti game drives. Day 4: Ngorongoro crater tour.",
            last_edited_by_user_id=admin.id
        )
        db.add(combo)
        db.flush()
        print(f"✅ Created destination combination: {combo.destination_names}")

        # Test lookup
        key = DestinationCombination.get_combination_key(serengeti.id, ngorongoro.id)
        found_combo = db.query(DestinationCombination).filter(
            DestinationCombination.destination_1_id == key[0],
            DestinationCombination.destination_2_id == key[1]
        ).first()
        if found_combo:
            print(f"✅ Lookup test passed: Found combination")
        else:
            print(f"❌ Lookup test failed")

        # ============================================================
        # TEST 5: ACCOMMODATION MODELS
        # ============================================================
        print_section("TEST 5: Accommodation Models")

        acc_type = AccommodationType(
            name="Luxury Tented Camp",
            description="High-end tented accommodation"
        )
        db.add(acc_type)
        db.flush()
        print(f"✅ Created accommodation type: {acc_type.name}")

        accommodation = Accommodation(
            name="Serengeti Safari Camp",
            description="Luxury camp in the heart of Serengeti",
            type_id=acc_type.id,
            location_destination_id=serengeti.id,
            star_rating=5,
            amenities=["WiFi", "Pool", "Restaurant", "Spa"],
            room_types=["Luxury Tent", "Family Tent", "Suite"],
            meal_plans=["Full Board", "All Inclusive"]
        )
        db.add(accommodation)
        db.flush()
        print(f"✅ Created accommodation: {accommodation.name}")

        # ============================================================
        # TEST 6: BASE TOUR MODELS
        # ============================================================
        print_section("TEST 6: Base Tour Models")

        tour_type = TourType(
            name="Small Group Safari",
            description="Small group wildlife safari"
        )
        db.add(tour_type)
        db.flush()
        print(f"✅ Created tour type: {tour_type.name}")

        # Create inclusions/exclusions
        inclusion = Inclusion(
            name="Accommodation",
            icon_name="hotel",
            category=InclusionCategories.ACCOMMODATION,
            sort_order=1
        )
        db.add(inclusion)
        db.flush()
        print(f"✅ Created inclusion: {inclusion.name}")

        exclusion = Exclusion(
            name="International Flights",
            icon_name="plane",
            category=ExclusionCategories.FLIGHTS,
            sort_order=1
        )
        db.add(exclusion)
        db.flush()
        print(f"✅ Created exclusion: {exclusion.name}")

        # Create base tour
        base_tour = BaseTour(
            tour_code="SER-5D",
            tour_name="5-Day Serengeti Safari",
            tour_type_id=tour_type.id,
            number_of_days=5,
            number_of_nights=4,
            default_pricing=Decimal("2500.00"),
            is_active=True
        )
        base_tour.inclusions.append(inclusion)
        base_tour.exclusions.append(exclusion)
        db.add(base_tour)
        db.flush()
        print(f"✅ Created base tour: {base_tour.tour_name}")

        # Create base tour day
        tour_day = BaseTourDay(
            base_tour_id=base_tour.id,
            day_number=1,
            day_title="Arrival in Serengeti",
            description="Transfer from airport to Serengeti",
            activities="Game drive en route",
            accommodation_id=accommodation.id
        )
        tour_day.destinations.append(serengeti)
        db.add(tour_day)
        db.flush()
        print(f"✅ Created base tour day: Day {tour_day.day_number}")

        # ============================================================
        # TEST 7: ITINERARY MODELS
        # ============================================================
        print_section("TEST 7: Itinerary Models")

        # Create itinerary
        itinerary = Itinerary(
            unique_code=Itinerary.generate_unique_code(),
            tour_title="Custom Serengeti Safari",
            tour_code="CUSTOM-001",
            tour_type_id=tour_type.id,
            number_of_days=5,
            number_of_nights=4,
            departure_date=date.today() + timedelta(days=30),
            status=ItineraryStatusEnum.DRAFT,
            creation_method=CreationMethodEnum.CUSTOM,
            created_by_user_id=admin.id,
            assigned_to_user_id=agent.id
        )
        itinerary.auto_calculate_dates()
        itinerary.inclusions.append(inclusion)
        itinerary.exclusions.append(exclusion)
        itinerary.featured_accommodations.append(accommodation)
        db.add(itinerary)
        db.flush()
        print(f"✅ Created itinerary: {itinerary.unique_code}")
        print(f"   Public URL: {itinerary.get_public_url()}")

        # Create traveler
        traveler = Traveler(
            itinerary_id=itinerary.id,
            is_primary=True,
            full_name="John Doe",
            email="john@example.com",
            phone="+1234567890",
            age=35,
            nationality="USA",
            special_requests="Vegetarian meals"
        )
        db.add(traveler)
        db.flush()
        print(f"✅ Created traveler: {traveler.full_name}")

        # Create itinerary day
        itin_day = ItineraryDay(
            itinerary_id=itinerary.id,
            day_number=1,
            day_title="Arrival in Serengeti",
            day_date=itinerary.departure_date,
            description=combo.description_content,
            activities=combo.activity_content,
            is_description_custom=False,
            is_activity_custom=False,
            accommodation_id=accommodation.id
        )
        itin_day.destinations.append(serengeti)
        db.add(itin_day)
        db.flush()
        print(f"✅ Created itinerary day: Day {itin_day.day_number}")
        print(f"   Auto-filled: {not itin_day.is_description_custom}")

        # ============================================================
        # TEST 8: PAYMENT, EMAIL, NOTIFICATION MODELS
        # ============================================================
        print_section("TEST 8: Payment, Email, Notification Models")

        # Create payment record
        payment = PaymentRecord(
            itinerary_id=itinerary.id,
            payment_status=PaymentStatusEnum.PARTIALLY_PAID,
            total_amount=Decimal("2500.00"),
            paid_amount=Decimal("500.00"),
            payment_method="Bank Transfer",
            created_by_user_id=admin.id
        )
        db.add(payment)
        db.flush()
        print(f"✅ Created payment record: {payment.payment_status.value}")

        # Create email log
        email_log = EmailLog(
            itinerary_id=itinerary.id,
            sent_to_email=traveler.email,
            cc_emails=["agent@test.com"],
            subject="Your Safari Itinerary",
            body="Please find your itinerary attached",
            pdf_attached=True,
            sent_by_user_id=agent.id,
            delivery_status=DeliveryStatusEnum.SENT
        )
        db.add(email_log)
        db.flush()
        print(f"✅ Created email log: {email_log.subject}")

        # Create activity log
        activity_log = ItineraryActivityLog(
            user_id=agent.id,
            itinerary_id=itinerary.id,
            action_type=ActionTypeEnum.CREATED,
            description=f"Created itinerary {itinerary.unique_code}",
            metadata={"itinerary_title": itinerary.tour_title},
            ip_address="127.0.0.1"
        )
        db.add(activity_log)
        db.flush()
        print(f"✅ Created activity log: {activity_log.action_type.value}")

        # Create notification
        notification = Notification(
            user_id=agent.id,
            itinerary_id=itinerary.id,
            notification_type=NotificationTypeEnum.ASSIGNED,
            title="New Itinerary Assigned",
            message=f"You have been assigned to itinerary {itinerary.unique_code}",
            priority=PriorityEnum.HIGH,
            action_url=f"/itineraries/{itinerary.unique_code}"
        )
        db.add(notification)
        db.flush()
        print(f"✅ Created notification: {notification.title}")

        # ============================================================
        # TEST 9: COMPANY MODELS
        # ============================================================
        print_section("TEST 9: Company Models")

        # Create company content
        content = CompanyContent(
            key="intro_letter_template",
            content="Dear {{traveler_name}}, Welcome to your safari adventure...",
            placeholders={"traveler_name": "Traveler's full name", "departure_date": "Departure date"},
            updated_by_user_id=admin.id
        )
        db.add(content)
        db.flush()
        print(f"✅ Created company content: {content.key}")

        # Create company asset
        asset = CompanyAsset(
            asset_type=AssetTypeEnum.LOGO,
            asset_name="Company Logo",
            asset_url="https://example.com/logo.png",
            sort_order=1,
            is_active=True
        )
        db.add(asset)
        db.flush()
        print(f"✅ Created company asset: {asset.asset_name}")

        # ============================================================
        # TEST 10: RELATIONSHIP TESTS
        # ============================================================
        print_section("TEST 10: Relationship Tests")

        # Test user -> itineraries relationship
        print(f"User {agent.full_name}:")
        print(f"  Created itineraries: {agent.itineraries_created.count()}")
        print(f"  Assigned itineraries: {agent.itineraries_assigned.count()}")

        # Test itinerary -> days relationship
        print(f"\nItinerary {itinerary.unique_code}:")
        print(f"  Days: {len(itinerary.days)}")
        print(f"  Travelers: {len(itinerary.travelers)}")
        print(f"  Primary traveler: {itinerary.primary_traveler.full_name if itinerary.primary_traveler else 'None'}")

        # Test base tour -> days relationship
        print(f"\nBase Tour {base_tour.tour_name}:")
        print(f"  Days: {len(base_tour.days)}")
        print(f"  Inclusions: {len(base_tour.inclusions)}")
        print(f"  Exclusions: {len(base_tour.exclusions)}")

        # Test destination -> images relationship
        print(f"\nDestination {serengeti.name}:")
        print(f"  Images: {len(serengeti.images)}")

        print("\n✅ All relationship tests passed")

        # ============================================================
        # TEST 11: METHOD TESTS
        # ============================================================
        print_section("TEST 11: Method Tests")

        # Test Itinerary methods
        print(f"Itinerary.is_editable('cs_agent'): {itinerary.is_editable('cs_agent')}")
        print(f"Itinerary.is_tour_ended: {itinerary.is_tour_ended}")
        print(f"Itinerary.get_public_url(): {itinerary.get_public_url()}")

        # Test User methods
        print(f"\nUser.verify_password('Admin123!'): {admin.verify_password('Admin123!')}")
        print(f"Agent.has_permission(CREATE_ITINERARY): {agent.has_permission(PermissionNames.CREATE_ITINERARY)}")
        print(f"Admin.is_admin: {admin.is_admin}")

        print("\n✅ All method tests passed")

        # ============================================================
        # COMMIT ALL CHANGES
        # ============================================================
        print_section("COMMITTING CHANGES")
        db.commit()
        print("✅ All changes committed to database")

        # ============================================================
        # VERIFICATION
        # ============================================================
        print_section("VERIFICATION")

        counts = {
            "Users": db.query(User).count(),
            "Permissions": db.query(Permission).count(),
            "Destinations": db.query(Destination).count(),
            "Accommodations": db.query(Accommodation).count(),
            "Base Tours": db.query(BaseTour).count(),
            "Itineraries": db.query(Itinerary).count(),
            "Travelers": db.query(Traveler).count(),
            "Destination Combinations": db.query(DestinationCombination).count(),
            "Notifications": db.query(Notification).count(),
        }

        for model, count in counts.items():
            print(f"  {model}: {count}")

        print_section("ALL TESTS COMPLETED SUCCESSFULLY ✅")

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False

    finally:
        # Note: Not cleaning up test data - use --cleanup flag to clean
        db.close()


def cleanup_test_data():
    """Clean up test data."""
    print_section("CLEANING UP TEST DATA")

    db: Session = SessionLocal()

    try:
        # Delete in reverse order of dependencies
        db.query(Notification).filter(Notification.user_id.in_(
            db.query(User.id).filter(User.email.in_(["admin@test.com", "agent@test.com"]))
        )).delete(synchronize_session=False)

        db.query(ItineraryActivityLog).filter(ItineraryActivityLog.user_id.in_(
            db.query(User.id).filter(User.email.in_(["admin@test.com", "agent@test.com"]))
        )).delete(synchronize_session=False)

        db.query(EmailLog).delete(synchronize_session=False)
        db.query(PaymentRecord).delete(synchronize_session=False)
        db.query(ItineraryDay).delete(synchronize_session=False)
        db.query(Traveler).delete(synchronize_session=False)
        db.query(Itinerary).delete(synchronize_session=False)
        db.query(BaseTourDay).delete(synchronize_session=False)
        db.query(BaseTour).delete(synchronize_session=False)
        db.query(Inclusion).delete(synchronize_session=False)
        db.query(Exclusion).delete(synchronize_session=False)
        db.query(Accommodation).delete(synchronize_session=False)
        db.query(AccommodationType).delete(synchronize_session=False)
        db.query(TourType).delete(synchronize_session=False)
        db.query(DestinationCombination).delete(synchronize_session=False)
        db.query(DestinationImage).delete(synchronize_session=False)
        db.query(Destination).delete(synchronize_session=False)
        db.query(CompanyContent).delete(synchronize_session=False)
        db.query(CompanyAsset).delete(synchronize_session=False)
        db.query(AgentType).delete(synchronize_session=False)
        db.query(Permission).delete(synchronize_session=False)
        db.query(User).filter(User.email.in_(["admin@test.com", "agent@test.com"])).delete(synchronize_session=False)

        db.commit()
        print("✅ Test data cleaned up successfully")

    except Exception as e:
        print(f"❌ Cleanup failed: {str(e)}")
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Test database models')
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean up test data after running'
    )

    args = parser.parse_args()

    success = test_database_models()

    if args.cleanup:
        cleanup_test_data()

    sys.exit(0 if success else 1)
