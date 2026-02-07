
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.db.session import SessionLocal
from app.models.base_tour import TourType

def seed_tour_types():
    db = SessionLocal()
    try:
        tour_types = [
            "Wildlife",
            "Safari",
            "Family",
            "Honeymoon",
            "Private",
            "Group",
            "Cultural"
        ]

        print("Seeding Tour Types...")
        for name in tour_types:
            existing = db.query(TourType).filter(TourType.name == name).first()
            if not existing:
                print(f"Creating: {name}")
                new_type = TourType(name=name, description=f"{name} tour packages")
                db.add(new_type)
            else:
                print(f"Skipping (already exists): {name}")

        db.commit()
        print("Done!")

    except Exception as e:
        print(f"Error seeding tour types: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_tour_types()
