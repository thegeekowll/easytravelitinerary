
import logging
from app.db.session import SessionLocal
from app.models.base_tour import TourType
from app.models.accommodation import AccommodationLevel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_data():
    db = SessionLocal()
    try:
        # Seed Tour Types
        if db.query(TourType).count() == 0:
            logger.info("Seeding Tour Types...")
            types = [
                "Safari", "Beach Holiday", "Cultural Tour", 
                "Adventure", "City Break", "Honeymoon", "Trekking"
            ]
            for t_name in types:
                db.add(TourType(name=t_name))
            db.commit()
            logger.info("Tour Types seeded.")
        else:
            logger.info("Tour Types already exist.")

        # Seed Accommodation Levels
        if db.query(AccommodationLevel).count() == 0:
            logger.info("Seeding Accommodation Levels...")
            levels = [
                "Budget", "Standard", "Comfort", 
                "Mid-Range", "Luxury", "Ultra-Luxury"
            ]
            for l_name in levels:
                db.add(AccommodationLevel(name=l_name))
            db.commit()
            logger.info("Accommodation Levels seeded.")
        else:
            logger.info("Accommodation Levels already exist.")

    except Exception as e:
        logger.error(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
