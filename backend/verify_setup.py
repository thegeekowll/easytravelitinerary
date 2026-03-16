"""
Setup verification script.

Checks all imports, database connection, tables, and configurations.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def verify_imports():
    """Verify all model imports."""
    print("\n" + "=" * 70)
    print(" VERIFYING IMPORTS")
    print("=" * 70)

    errors = []

    try:
        print("📦 Importing core modules...")
        from app.core.config import settings
        print("  ✅ app.core.config")

        from app.db.session import engine, SessionLocal
        print("  ✅ app.db.session")

        from app.core.security import get_password_hash, verify_password
        print("  ✅ app.core.security")

        print("\n📦 Importing models...")
        from app.models import (
            User, Permission, AgentType, Destination, DestinationCombination,
            Accommodation, BaseTour, Itinerary, PaymentRecord, EmailLog,
            Notification, CompanyContent, CompanyAsset
        )
        print("  ✅ All models imported successfully")

        print("\n✅ All imports successful")
        return True, []

    except ImportError as e:
        error_msg = f"Import error: {str(e)}"
        print(f"\n❌ {error_msg}")
        return False, [error_msg]


def verify_database_connection():
    """Verify database connection."""
    print("\n" + "=" * 70)
    print(" VERIFYING DATABASE CONNECTION")
    print("=" * 70)

    try:
        from app.db.session import engine
        from app.core.config import settings
        from sqlalchemy import text

        print(f"\n📊 Database: {settings.POSTGRES_DB}")
        print(f"🖥️  Server: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}")
        print(f"👤 User: {settings.POSTGRES_USER}")

        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"\n✅ Connected to PostgreSQL")
            print(f"   Version: {version.split(',')[0]}")

        return True, []

    except Exception as e:
        error_msg = f"Database connection error: {str(e)}"
        print(f"\n❌ {error_msg}")
        return False, [error_msg]


def verify_tables():
    """Verify all tables exist."""
    print("\n" + "=" * 70)
    print(" VERIFYING TABLES")
    print("=" * 70)

    try:
        from sqlalchemy import inspect
        from app.db.session import engine

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        expected_tables = [
            "users", "permissions", "user_permissions", "agent_types",
            "destinations", "destination_images", "destination_combinations",
            "accommodations", "accommodation_types", "accommodation_images",
            "base_tours", "base_tour_days", "base_tour_images", "tour_types",
            "inclusions", "exclusions", "base_tour_inclusions", "base_tour_exclusions",
            "itineraries", "itinerary_days", "travelers",
            "payment_records", "email_logs", "itinerary_activity_logs",
            "notifications", "company_content", "company_assets"
        ]

        print(f"\n📋 Expected tables: {len(expected_tables)}")
        print(f"📋 Found tables: {len(tables)}")

        missing = set(expected_tables) - set(tables)
        extra = set(tables) - set(expected_tables)

        if not missing:
            print("\n✅ All expected tables exist")
            return True, []
        else:
            print(f"\n⚠️  Missing {len(missing)} tables:")
            for table in sorted(missing):
                print(f"   - {table}")
            return False, [f"Missing tables: {', '.join(missing)}"]

    except Exception as e:
        error_msg = f"Table verification error: {str(e)}"
        print(f"\n❌ {error_msg}")
        return False, [error_msg]


def verify_config():
    """Verify configuration."""
    print("\n" + "=" * 70)
    print(" VERIFYING CONFIGURATION")
    print("=" * 70)

    try:
        from app.core.config import settings

        checks = {
            "Database URL": settings.DATABASE_URL is not None,
            "Secret Key": len(settings.SECRET_KEY) >= 32,
            "JWT Secret": len(settings.JWT_SECRET_KEY) >= 32,
            "CORS Origins": len(settings.BACKEND_CORS_ORIGINS) > 0,
        }

        optional_checks = {
            "SendGrid API Key": settings.SENDGRID_API_KEY is not None,
            "Azure Storage": settings.AZURE_STORAGE_CONNECTION_STRING is not None,
        }

        print("\n✓ Required Configuration:")
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")

        print("\nℹ️  Optional Configuration:")
        for check, passed in optional_checks.items():
            status = "✅" if passed else "⚠️  Not set"
            print(f"  {status} {check}")

        all_required_passed = all(checks.values())
        return all_required_passed, [] if all_required_passed else ["Required configuration missing"]

    except Exception as e:
        error_msg = f"Configuration verification error: {str(e)}"
        print(f"\n❌ {error_msg}")
        return False, [error_msg]


def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print(" SETUP VERIFICATION")
    print("=" * 70)

    all_errors = []

    # Run all checks
    checks = [
        ("Imports", verify_imports),
        ("Database Connection", verify_database_connection),
        ("Tables", verify_tables),
        ("Configuration", verify_config),
    ]

    results = {}
    for name, check_func in checks:
        success, errors = check_func()
        results[name] = success
        all_errors.extend(errors)

    # Print summary
    print("\n" + "=" * 70)
    print(" SUMMARY")
    print("=" * 70)

    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {name}")

    if all(results.values()):
        print("\n" + "=" * 70)
        print(" ✅ ALL CHECKS PASSED - SETUP COMPLETE!")
        print("=" * 70)
        print("\nYou can now:")
        print("  1. Run database migrations: alembic upgrade head")
        print("  2. Test models: python test_models.py")
        print("  3. Start the application: uvicorn app.main:app --reload")
        print()
        return 0
    else:
        print("\n" + "=" * 70)
        print(" ❌ SOME CHECKS FAILED")
        print("=" * 70)
        print("\nErrors:")
        for error in all_errors:
            print(f"  - {error}")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
