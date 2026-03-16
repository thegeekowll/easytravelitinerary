
import os
import sys
from sqlalchemy import text
from app.db.session import SessionLocal

def add_columns():
    db = SessionLocal()
    try:
        print("Migrating itineraries table...")
        
        # Add tour_type_id if not exists (it might exist but let's check)
        # Actually existing Itinerary model had tour_type_id since before, but confirm.
        # It was non-nullable before, now nullable. Modification might be needed.
        
        # Add accommodation_level_id
        try:
            db.execute(text("ALTER TABLE itineraries ADD COLUMN accommodation_level_id UUID REFERENCES accommodation_levels(id) ON DELETE SET NULL"))
            print("Added accommodation_level_id")
        except Exception as e:
            print(f"Skipping accommodation_level_id: {e}")
            db.rollback()

        # Add difficulty_level
        try:
            db.execute(text("ALTER TABLE itineraries ADD COLUMN difficulty_level VARCHAR(50)"))
            print("Added difficulty_level")
        except Exception as e:
             print(f"Skipping difficulty_level: {e}")
             db.rollback()

        # Add description
        try:
            db.execute(text("ALTER TABLE itineraries ADD COLUMN description TEXT"))
            print("Added description")
        except Exception as e:
             print(f"Skipping description: {e}")
             db.rollback()

        # Add highlights
        try:
            db.execute(text("ALTER TABLE itineraries ADD COLUMN highlights TEXT"))
            print("Added highlights")
        except Exception as e:
             print(f"Skipping highlights: {e}")
             db.rollback()

        # Make tour_type_id nullable if it was not
        try:
             db.execute(text("ALTER TABLE itineraries ALTER COLUMN tour_type_id DROP NOT NULL"))
             print("Made tour_type_id nullable")
        except Exception as e:
             print(f"Skipping tour_type_id modification: {e}")
             db.rollback()

        db.commit()
        print("Migration complete.")
            
    except Exception as e:
        print(f"Global Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_columns()
