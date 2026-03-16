"""
Database initialization script.

This script creates all database tables and verifies they were created successfully.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from app.db.session import engine, Base, SessionLocal
from app.core.config import settings

# Import all models to register them with Base
# Import all models to register them with Base
from app.db.base import *
from app.models.accommodation import AccommodationLevel, AccommodationType
from app.api.v1.endpoints.permissions import seed_permissions
import asyncio


def create_tables():
    """Create all database tables."""
    print("=" * 70)
    print(" DATABASE INITIALIZATION")
    print("=" * 70)
    print()

    print(f"📊 Database: {settings.POSTGRES_DB}")
    print(f"🖥️  Server: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}")
    print(f"👤 User: {settings.POSTGRES_USER}")
    print()

    try:
        # Test connection
        print("🔌 Testing database connection...")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        print()

        # Create all tables
        print("🏗️  Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Table creation complete")
        print()

        # Seed Accommodation Levels
        print("🌱 Seeding initial data...")
        with SessionLocal() as session:
            levels = [
                "Basic", "Comfort", "Comfort Plus", "Luxury", "Luxury Plus"
            ]
            for level_name in levels:
                existing = session.query(AccommodationLevel).filter_by(name=level_name).first()
                if not existing:
                    session.add(AccommodationLevel(name=level_name, description=f"{level_name} accommodation tier"))
                    print(f"   - Created level: {level_name}")
            
            # Seed Accommodation Types
            types = [
                "Hotel", "Resort", "Lodge", "Camp", "Guesthouse", "Villa"
            ]
            for type_name in types:
                existing = session.query(AccommodationType).filter_by(name=type_name).first()
                if not existing:
                    session.add(AccommodationType(name=type_name, description=f"{type_name} accommodation"))
                    print(f"   - Created type: {type_name}")

            session.commit()
            
            print("🔑 Seeding permissions...")
            class DummyUser: pass
            
            # Run the async permission seeder synchronously in this wrapper
            async def run_seed():
                result = await seed_permissions(session, DummyUser())
                print(f"   - Permissions seeded: {result}")
            asyncio.run(run_seed())
            
        print("✅ Seeding complete")
        print()

        # Verify tables were created
        print("🔍 Verifying tables...")
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"\n📋 Found {len(tables)} tables:")
        print("-" * 70)

        # Expected tables
        expected_tables = [
            # Phase 2.1
            "users",
            "permissions",
            "user_permissions",
            "agent_types",
            "destinations",
            "destination_images",
            "destination_combinations",
            "accommodation_types",
            "accommodation_levels",
            "accommodations",
            "accommodation_images",
            "tour_types",
            "base_tours",
            "base_tour_days",
            "base_tour_images",
            "base_tour_inclusions",
            "base_tour_exclusions",
            "base_tour_day_destinations",
            "inclusions",
            "exclusions",
            "activity_logs",
            # Phase 2.2
            "itineraries",
            "itinerary_days",
            "travelers",
            "itinerary_day_destinations",
            "itinerary_featured_accommodations",
            "itinerary_inclusions",
            "itinerary_exclusions",
            "payment_records",
            "email_logs",
            "itinerary_activity_logs",
            "notifications",
            "company_content",
            "company_assets",
        ]

        # Check each expected table
        missing_tables = []
        for table in sorted(expected_tables):
            if table in tables:
                print(f"  ✅ {table}")
            else:
                print(f"  ❌ {table} (MISSING)")
                missing_tables.append(table)

        print("-" * 70)
        print()

        if missing_tables:
            print(f"⚠️  Warning: {len(missing_tables)} expected tables are missing:")
            for table in missing_tables:
                print(f"   - {table}")
            print()
            return False

        # Count total tables
        extra_tables = set(tables) - set(expected_tables)
        if extra_tables:
            print(f"ℹ️  Found {len(extra_tables)} additional tables:")
            for table in sorted(extra_tables):
                print(f"   - {table}")
            print()

        print("=" * 70)
        print("✅ DATABASE INITIALIZATION SUCCESSFUL")
        print("=" * 70)
        print()
        print(f"Total tables: {len(tables)}")
        print(f"Expected tables: {len(expected_tables)}")
        print(f"All required tables: {'✅ Present' if not missing_tables else '❌ Missing'}")
        print()

        return True

    except Exception as e:
        print()
        print("=" * 70)
        print("❌ DATABASE INITIALIZATION FAILED")
        print("=" * 70)
        print()
        print(f"Error: {str(e)}")
        print()
        print("Troubleshooting:")
        print("  1. Make sure PostgreSQL is running")
        print("  2. Check database credentials in .env file")
        print(f"  3. Verify database '{settings.POSTGRES_DB}' exists")
        print("  4. Check network connectivity to database server")
        print()
        return False


def drop_all_tables():
    """Drop all tables (use with caution!)."""
    print("⚠️  WARNING: This will drop ALL tables!")
    response = input("Type 'yes' to confirm: ")

    if response.lower() == 'yes':
        print("🗑️  Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped")
    else:
        print("❌ Cancelled")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Initialize database')
    parser.add_argument(
        '--drop',
        action='store_true',
        help='Drop all tables before creating (destructive!)'
    )

    args = parser.parse_args()

    if args.drop:
        drop_all_tables()
        print()

    success = create_tables()
    sys.exit(0 if success else 1)
