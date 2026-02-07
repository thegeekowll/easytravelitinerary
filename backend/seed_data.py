"""
Seed database with initial data for development and testing.

Run: python seed_data.py
"""
import asyncio
from datetime import date, timedelta, datetime
from decimal import Decimal
import uuid

from app.db.session import SessionLocal
from app.models.user import User, UserRoleEnum
from app.models.destination import Destination
from app.models.accommodation import Accommodation, AccommodationType
from app.models.base_tour import BaseTour, BaseTourDay, TourType
from app.models.destination_combination import DestinationCombination
from app.models.company import CompanyContent
from app.models.itinerary import Itinerary, ItineraryDay, ItineraryStatusEnum, CreationMethodEnum, Traveler
from app.models.permission import Permission, PermissionNames, PermissionCategories
from app.core.security import get_password_hash



def seed_permissions(db):
    """Seed permissions."""
    print("\n🔐 Seeding permissions...")
    default_permissions = [
        # Accommodation
        {"name": PermissionNames.VIEW_ACCOMMODATIONS, "description": "View accommodations", "category": PermissionCategories.ACCOMMODATION},
        {"name": PermissionNames.ADD_ACCOMMODATION, "description": "Add new accommodations", "category": PermissionCategories.ACCOMMODATION},
        {"name": PermissionNames.EDIT_ACCOMMODATION, "description": "Edit existing accommodations", "category": PermissionCategories.ACCOMMODATION},
        {"name": PermissionNames.DELETE_ACCOMMODATION, "description": "Delete accommodations", "category": PermissionCategories.ACCOMMODATION},
        
        # Destination
        {"name": PermissionNames.VIEW_DESTINATIONS, "description": "View destinations", "category": PermissionCategories.DESTINATION},
        {"name": PermissionNames.ADD_DESTINATION, "description": "Add new destinations", "category": PermissionCategories.DESTINATION},
        {"name": PermissionNames.EDIT_DESTINATION, "description": "Edit existing destinations", "category": PermissionCategories.DESTINATION},
        {"name": PermissionNames.DELETE_DESTINATION, "description": "Delete destinations", "category": PermissionCategories.DESTINATION},
        
        # Base Tours
        {"name": PermissionNames.VIEW_TOUR_PACKAGES, "description": "View base tours", "category": PermissionCategories.TOUR_PACKAGE},
        {"name": PermissionNames.ADD_TOUR_PACKAGE, "description": "Add new base tours", "category": PermissionCategories.TOUR_PACKAGE},
        {"name": PermissionNames.EDIT_TOUR_PACKAGE, "description": "Edit existing base tours", "category": PermissionCategories.TOUR_PACKAGE},
        {"name": PermissionNames.DELETE_TOUR_PACKAGE, "description": "Delete base tours", "category": PermissionCategories.TOUR_PACKAGE},
        
        # 2D Table
        {"name": PermissionNames.VIEW_2D_TABLE, "description": "View 2D Matrix", "category": PermissionCategories.TWO_D_TABLE},
        {"name": PermissionNames.EDIT_2D_TABLE, "description": "Edit 2D Matrix", "category": PermissionCategories.TWO_D_TABLE},
        
        # Analytics
        {"name": PermissionNames.VIEW_ANALYTICS, "description": "View analytics dashboard", "category": PermissionCategories.ANALYTICS},
        {"name": PermissionNames.VIEW_ANALYTICS_REVENUE, "description": "View revenue in analytics", "category": PermissionCategories.ANALYTICS},
        {"name": PermissionNames.EXPORT_ANALYTICS, "description": "Export analytics reports", "category": PermissionCategories.ANALYTICS},
        
        # Settings (System)
        {"name": PermissionNames.MANAGE_AGENT_TYPES, "description": "Manage Settings & Configurations", "category": PermissionCategories.SYSTEM},
    ]

    added_count = 0
    for perm_data in default_permissions:
        # Check if exists by name
        existing = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        
        if not existing:
            new_perm = Permission(
                name=perm_data["name"],
                description=perm_data["description"],
                category=perm_data["category"]
            )
            db.add(new_perm)
            added_count += 1
            print(f"✅ Created permission: {perm_data['name']}")
    
    db.commit()
    print(f"✅ Permissions seeded successfully ({added_count} new)")


def seed_users(db):
    """Seed users."""
    print("\n📝 Seeding users...")

    # Check if admin exists
    admin = db.query(User).filter(User.email == "admin@travelagency.com").first()
    if not admin:
        admin = User(
            email="admin@travelagency.com",
            full_name="System Administrator",
            hashed_password=get_password_hash("Admin123!"),
            role=UserRoleEnum.ADMIN,
            is_active=True,
            phone_number="+1-555-0100"
        )
        db.add(admin)
        print("✅ Created admin user: admin@travelagency.com / Admin123!")
    else:
        print("ℹ️  Admin user already exists")

    # Create CS agents
    agents_data = [
        {
            "email": "sarah.johnson@travelagency.com",
            "name": "Sarah Johnson",
            "password": "Agent123!",
            "phone": "+1-555-0101"
        },
        {
            "email": "mike.williams@travelagency.com",
            "name": "Mike Williams",
            "password": "Agent123!",
            "phone": "+1-555-0102"
        },
        {
            "email": "emily.davis@travelagency.com",
            "name": "Emily Davis",
            "password": "Agent123!",
            "phone": "+1-555-0103"
        }
    ]

    for agent_data in agents_data:
        agent = db.query(User).filter(User.email == agent_data["email"]).first()
        if not agent:
            agent = User(
                email=agent_data["email"],
                full_name=agent_data["name"],
                hashed_password=get_password_hash(agent_data["password"]),
                role=UserRoleEnum.CS_AGENT,
                is_active=True,
                phone_number=agent_data["phone"]
            )
            db.add(agent)
            print(f"✅ Created agent: {agent_data['email']} / {agent_data['password']}")

    db.commit()
    print(f"✅ Users seeded successfully")


def seed_destinations(db):
    """Seed destinations."""
    print("\n🌍 Seeding destinations...")

    destinations_data = [
        {
            "name": "Serengeti National Park",
            "description": "The Serengeti is a vast ecosystem in east-central Africa. It spans 12,000 square miles and is renowned for its annual migration of over 1.5 million wildebeest and 250,000 zebra.",
            "region": "Northern Tanzania",
            "country": "Tanzania",
            "tags": ["Great Migration", "Big Five wildlife", "Hot air balloon safaris", "Maasai cultural experiences"],
            "best_time_to_visit": "June to October (dry season)",
            "activities": ["Game drives", "Hot air ballooning", "Walking safaris", "Photography"]
        },
        {
            "name": "Ngorongoro Crater",
            "description": "A UNESCO World Heritage Site, the Ngorongoro Crater is the world's largest inactive volcanic caldera. It's home to an estimated 25,000 large animals.",
            "region": "Northern Tanzania",
            "country": "Tanzania",
            "tags": ["World's largest volcanic caldera", "High concentration of wildlife", "Black rhinos", "Maasai villages"],
            "best_time_to_visit": "Year-round",
            "activities": ["Crater floor game drives", "Bird watching", "Cultural tours"]
        },
        {
            "name": "Zanzibar",
            "description": "The Zanzibar Archipelago, located in the Indian Ocean 15 miles off the coast of Tanzania, is a breathtaking spot to escape to. Famous for its spice plantations and pristine beaches.",
            "region": "Off the coast of Tanzania",
            "country": "Tanzania",
            "tags": ["Stone Town UNESCO site", "Pristine beaches", "Spice plantations", "Dhow sailing"],
            "best_time_to_visit": "June to October",
            "activities": ["Beach relaxation", "Snorkeling", "Spice tours", "Stone Town exploration"]
        },
        {
            "name": "Tarangire National Park",
            "description": "Known for its large elephant population and iconic baobab trees, Tarangire offers a more intimate safari experience than the Serengeti.",
            "region": "Northern Tanzania",
            "country": "Tanzania",
            "tags": ["Large elephant herds", "Ancient baobab trees", "Tarangire River wildlife", "Tree-climbing lions"],
            "best_time_to_visit": "June to October",
            "activities": ["Game drives", "Walking safaris", "Night drives", "Bird watching"]
        },
        {
            "name": "Lake Manyara National Park",
            "description": "A compact game-viewing circuit and a groundwater forest that supports a rich diversity of primates and birds. Famous for tree-climbing lions.",
            "region": "Northern Tanzania",
            "country": "Tanzania",
            "tags": ["Tree-climbing lions", "Flamingos on the lake", "Groundwater forest", "Hot springs"],
            "best_time_to_visit": "June to October",
            "activities": ["Game drives", "Canoeing", "Bird watching", "Forest walks"]
        }
    ]

    for dest_data in destinations_data:
        destination = db.query(Destination).filter(Destination.name == dest_data["name"]).first()
        if not destination:
            destination = Destination(**dest_data)
            db.add(destination)
            print(f"✅ Created destination: {dest_data['name']}")

    db.commit()
    print(f"✅ Destinations seeded successfully")

    return db.query(Destination).all()


def seed_accommodation_types(db):
    """Seed accommodation types."""
    print("\n🏨 Seeding accommodation types...")

    types_data = [
        {
            "name": "Lodge",
            "description": "Safari lodges typically built in or near national parks, offering comfort and wildlife viewing"
        },
        {
            "name": "Resort",
            "description": "Beach or luxury resorts with comprehensive facilities and amenities"
        },
        {
            "name": "Hotel",
            "description": "City or town hotels with standard hospitality services"
        },
        {
            "name": "Tented Camp",
            "description": "Luxury tented camps offering an authentic safari experience with modern comforts"
        },
        {
            "name": "Guesthouse",
            "description": "Smaller, more intimate accommodations often family-run"
        }
    ]

    for type_data in types_data:
        acc_type = db.query(AccommodationType).filter(AccommodationType.name == type_data["name"]).first()
        if not acc_type:
            acc_type = AccommodationType(**type_data)
            db.add(acc_type)
            print(f"✅ Created accommodation type: {type_data['name']}")

    db.commit()
    print(f"✅ Accommodation types seeded successfully")

    return db.query(AccommodationType).all()


def seed_accommodations(db, destinations, accommodation_types):
    """Seed accommodations."""
    print("\n🏨 Seeding accommodations...")

    # Map destination names to IDs
    dest_map = {dest.name: dest.id for dest in destinations}

    # Map accommodation type names to IDs
    type_map = {acc_type.name: acc_type.id for acc_type in accommodation_types}

    accommodations_data = [
        {
            "name": "Four Seasons Safari Lodge Serengeti",
            "location_destination_id": dest_map.get("Serengeti National Park"),
            "type_id": type_map.get("Lodge"),
            "star_rating": 5,
            "description": "Perched on a ridge overlooking a waterhole, this luxury safari lodge offers panoramic views of the Serengeti.",
            "amenities": ["Pool", "Spa", "Restaurant", "Bar", "WiFi", "Game drives"],
            "room_types": [
                {"type": "Superior Room", "capacity": 2, "features": ["King bed", "Private balcony", "En-suite bathroom"]},
                {"type": "Safari Suite", "capacity": 3, "features": ["King bed", "Living area", "Private deck", "Outdoor shower"]},
                {"type": "Family Suite", "capacity": 4, "features": ["2 bedrooms", "Living area", "2 bathrooms"]}
            ],
            "meal_plans": ["Full Board", "All Inclusive"],
            "contact_info": {"email": "info@fourseasons-serengeti.com", "phone": "+255-123-456-789"}
        },
        {
            "name": "Serengeti Serena Safari Lodge",
            "location_destination_id": dest_map.get("Serengeti National Park"),
            "type_id": type_map.get("Lodge"),
            "star_rating": 4,
            "description": "Built into the hillside overlooking the Serengeti plains, featuring traditional Maasai design.",
            "amenities": ["Pool", "Restaurant", "Bar", "WiFi"],
            "room_types": [
                {"type": "Standard Room", "capacity": 2, "features": ["Twin or double bed", "En-suite bathroom"]},
                {"type": "Superior Room", "capacity": 2, "features": ["King bed", "Sitting area", "Better view"]}
            ],
            "meal_plans": ["Half Board", "Full Board"],
            "contact_info": {"email": "reservations@serena.co.tz", "phone": "+255-234-567-890"}
        },
        {
            "name": "Ngorongoro Crater Lodge",
            "location_destination_id": dest_map.get("Ngorongoro Crater"),
            "type_id": type_map.get("Lodge"),
            "star_rating": 5,
            "description": "Perched on the rim of the crater, this lodge combines luxury with breathtaking views.",
            "amenities": ["Butler service", "Spa", "Restaurant", "Bar", "WiFi"],
            "room_types": [
                {"type": "Crater Suite", "capacity": 2, "features": ["King bed", "Butler service", "Floor-to-ceiling windows", "Fireplace"]}
            ],
            "meal_plans": ["Full Board"],
            "contact_info": {"email": "info@ngorongorolodge.com", "phone": "+255-345-678-901"}
        },
        {
            "name": "Zuri Zanzibar",
            "location_destination_id": dest_map.get("Zanzibar"),
            "type_id": type_map.get("Resort"),
            "star_rating": 5,
            "description": "A stunning beachfront resort on Zanzibar's northwest coast with pristine white sand beaches.",
            "amenities": ["Beach access", "Pool", "Spa", "Multiple restaurants", "Water sports", "WiFi"],
            "room_types": [
                {"type": "Ocean View Room", "capacity": 2, "features": ["King bed", "Ocean view", "Private terrace"]},
                {"type": "Beach Villa", "capacity": 3, "features": ["King bed", "Direct beach access", "Plunge pool"]},
                {"type": "Family Villa", "capacity": 4, "features": ["2 bedrooms", "Living area", "Private pool"]}
            ],
            "meal_plans": ["Bed & Breakfast", "Half Board", "All Inclusive"],
            "contact_info": {"email": "info@zurizanzibar.com", "phone": "+255-456-789-012"}
        },
        {
            "name": "Tarangire Sopa Lodge",
            "location_destination_id": dest_map.get("Tarangire National Park"),
            "type_id": type_map.get("Lodge"),
            "star_rating": 4,
            "description": "Located on a ridge with sweeping views of Tarangire National Park.",
            "amenities": ["Pool", "Restaurant", "Bar", "WiFi"],
            "room_types": [
                {"type": "Standard Room", "capacity": 2, "features": ["Twin or double bed", "En-suite bathroom"]},
                {"type": "Superior Room", "capacity": 2, "features": ["King bed", "Larger room", "Better views"]}
            ],
            "meal_plans": ["Full Board"],
            "contact_info": {"email": "reservations@sopalodges.com", "phone": "+255-567-890-123"}
        },
        {
            "name": "Lake Manyara Serena Safari Lodge",
            "location_destination_id": dest_map.get("Lake Manyara National Park"),
            "type_id": type_map.get("Lodge"),
            "star_rating": 4,
            "description": "Perched on the edge of the Great Rift Valley with views of Lake Manyara.",
            "amenities": ["Pool", "Restaurant", "Bar", "WiFi"],
            "room_types": [
                {"type": "Standard Room", "capacity": 2, "features": ["Twin or double bed", "En-suite bathroom"]},
                {"type": "Superior Room", "capacity": 2, "features": ["King bed", "Sitting area", "Valley views"]}
            ],
            "meal_plans": ["Half Board", "Full Board"],
            "contact_info": {"email": "manyara@serena.co.tz", "phone": "+255-678-901-234"}
        }
    ]

    for acc_data in accommodations_data:
        accommodation = db.query(Accommodation).filter(Accommodation.name == acc_data["name"]).first()
        if not accommodation:
            accommodation = Accommodation(**acc_data)
            db.add(accommodation)
            print(f"✅ Created accommodation: {acc_data['name']}")

    db.commit()
    print(f"✅ Accommodations seeded successfully")
    return db.query(Accommodation).all()


def seed_tour_types(db):
    """Seed tour types."""
    print("\n🔍 Seeding tour types...")
    
    types = ["Small Group Safari", "Private Safari", "Beach Holiday", "Cultural Tour"]
    
    for t_name in types:
        t_type = db.query(TourType).filter(TourType.name == t_name).first()
        if not t_type:
            t_type = TourType(name=t_name, description=f"{t_name} Description")
            db.add(t_type)
            print(f"✅ Created tour type: {t_name}")
            
    db.commit()
    print(f"✅ Tour types seeded successfully")
    return db.query(TourType).all()

def seed_base_tours(db, destinations, accommodations, tour_types):
    """Seed base tours."""
    print("\n🗺️  Seeding base tours...")

    # Get specific destinations
    serengeti = next((d for d in destinations if d.name == "Serengeti National Park"), None)
    ngorongoro = next((d for d in destinations if d.name == "Ngorongoro Crater"), None)
    zanzibar = next((d for d in destinations if d.name == "Zanzibar"), None)
    tarangire = next((d for d in destinations if d.name == "Tarangire National Park"), None)
    
    # Get tour type
    small_group = next((t for t in tour_types if t.name == "Small Group Safari"), tour_types[0])

    if not serengeti or not ngorongoro or not tarangire:
        print("❌ Skipping base tours: Missing required destinations")
        return

    base_tours_data = [
        {
            "tour_name": "Classic Tanzania Safari",
            "tour_code": "CTS7",
            "tour_type_id": small_group.id,
            "number_of_days": 7,
            "number_of_nights": 6,
            "hero_image_url": "https://example.com/safari.jpg",
            "default_pricing": 3500.00,
            "best_time_to_travel": "June to October",
            "is_active": True
        }
    ]

    created_tours = []
    for tour_data in base_tours_data:
        tour = db.query(BaseTour).filter(BaseTour.tour_code == tour_data["tour_code"]).first()
        if not tour:
            tour = BaseTour(**tour_data)
            db.add(tour)
            print(f"✅ Created base tour: {tour_data['tour_name']}")
            created_tours.append(tour)
        else:
            created_tours.append(tour)

    db.commit()
    print(f"✅ Base tours seeded successfully")
    return created_tours


def seed_destination_combinations(db, destinations):
    """Seed destination combinations."""
    print("\n🔗 Seeding destination combinations...")

    # Get destinations
    serengeti = next((d for d in destinations if d.name == "Serengeti National Park"), None)
    ngorongoro = next((d for d in destinations if d.name == "Ngorongoro Crater"), None)
    zanzibar = next((d for d in destinations if d.name == "Zanzibar"), None)
    tarangire = next((d for d in destinations if d.name == "Tarangire National Park"), None)

    if not (serengeti and ngorongoro and zanzibar and tarangire):
        return

    combinations_data = [
        {
            "destination_1_id": serengeti.id,
            "destination_2_id": None,  # Diagonal
            "description_content": "Full day game drives in Serengeti National Park, home to the Great Migration and abundant wildlife.",
            "activity_content": "Morning and afternoon game drives tracking the Big Five"
        },
        {
            "destination_1_id": serengeti.id,
            "destination_2_id": ngorongoro.id,
            "description_content": "Transfer from Serengeti to Ngorongoro Crater with game viewing en route.",
            "activity_content": "Scenic drive through the highlands with wildlife viewing"
        },
        # Add simpler keys for finding duplicates if necessary, but just rely on IDs
    ]

    for combo_data in combinations_data:
        # Check if combination exists (simplified check)
        combo = db.query(DestinationCombination).filter(
            DestinationCombination.destination_1_id == combo_data["destination_1_id"],
            DestinationCombination.destination_2_id == combo_data["destination_2_id"]
        ).first()

        if not combo:
            combo = DestinationCombination(**combo_data)
            db.add(combo)
            print(f"✅ Created combination")

    db.commit()
    print(f"✅ Destination combinations seeded successfully")


def seed_company_content(db):
    """Seed company content."""
    print("\n🏢 Seeding company content...")

    # Company content uses key-value pairs
    content_data = [
        {
            "key": "company_name",
            "content": "Safari Adventures Tanzania",
            "placeholders": {}
        },
        {
            "key": "email_template",
            "content": "Dear [Traveler Name], check out your tour [Tour Name]",
            "placeholders": {}
        }
    ]

    for item in content_data:
        content = db.query(CompanyContent).filter(CompanyContent.key == item["key"]).first()
        if not content:
            content = CompanyContent(**item)
            db.add(content)
            print(f"✅ Created company content: {item['key']}")

    db.commit()
    print(f"✅ Company content seeded successfully")

def seed_itineraries(db, tour_types, users):
    print("\n📅 Seeding initial itinerary...")
    
    # Needs a tour type
    small_group = tour_types[0]
    # Needs a user
    agent = next((u for u in users if u.role == UserRoleEnum.CS_AGENT), users[0])
    
    # Check if itinerary exists with specific code
    code = "DEMO12345678"
    existing = db.query(Itinerary).filter(Itinerary.unique_code == code).first()
    
    if not existing:
        itinerary = Itinerary(
            unique_code=code,
            tour_title="Unforgettable Tanzania Safari",
            tour_type_id=small_group.id,
            number_of_days=7,
            number_of_nights=6,
            departure_date=date.today() + timedelta(days=30),
            return_date=date.today() + timedelta(days=36),
            status=ItineraryStatusEnum.CONFIRMED,
            created_by_user_id=agent.id,
            assigned_to_user_id=agent.id,
            hero_image_url="https://images.unsplash.com/photo-1516426122078-c23e76319801?auto=format&fit=crop&q=80",
            internal_notes="VIP Client"
        )
        db.add(itinerary)
        db.flush() # get ID
        
        # Add Travelers
        traveler = Traveler(
            itinerary_id=itinerary.id,
            full_name="John Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            is_primary=True,
            age=35
        )
        db.add(traveler)
        
        # Add Days
        day1 = ItineraryDay(
            itinerary_id=itinerary.id,
            day_number=1,
            day_title="Arrival in Arusha",
            day_date=itinerary.departure_date,
            description="Welcome to Tanzania! Arrive at Kilimanjaro Airport.",
            activities="Airport Pickup, Transfer to Hotel"
        )
        db.add(day1)
        
        day2 = ItineraryDay(
             itinerary_id=itinerary.id,
            day_number=2,
            day_title="Tarangire National Park",
            day_date=itinerary.departure_date + timedelta(days=1),
            description="Full day game drive in Tarangire.",
            activities="Game drive, Picnic Lunch"
        )
        db.add(day2)
        
        db.commit()
        print(f"✅ Created Demo Itinerary: {code}")
    else:
        print(f"ℹ️  Demo Itinerary already exists: {code}")


def main():
    """Main seed function."""
    print("=" * 70)
    print(" SEEDING DATABASE")
    print("=" * 70)

    db = SessionLocal()

    try:
        # Seed in order
        seed_permissions(db)
        seed_users(db)
        destinations = seed_destinations(db)
        accommodation_types = seed_accommodation_types(db)
        accommodations = seed_accommodations(db, destinations, accommodation_types)
        
        # Fixed & Enabled
        tour_types = seed_tour_types(db)
        seed_base_tours(db, destinations, accommodations, tour_types)
        seed_destination_combinations(db, destinations)
        seed_company_content(db)

        # Create Itinerary
        users = db.query(User).all()
        seed_itineraries(db, tour_types, users)
        
        print("\n" + "=" * 70)
        print(" ✅ DATABASE SEEDED SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error seeding database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
