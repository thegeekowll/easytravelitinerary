
import sys
import os
from uuid import uuid4

# Add backend to path
sys.path.append('/app')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.destination import Destination
from app.models.destination_combination import DestinationCombination
from app.db.base import Base

# Setup DB connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def seed_matrix():
    print("Fetching destinations...")
    destinations = db.query(Destination).all()
    print(f"Found {len(destinations)} destinations.")
    
    cnt = 0
    # Create content for every pair
    for d1 in destinations:
        for d2 in destinations:
            # Check if exists
            exists = db.query(DestinationCombination).filter(
                DestinationCombination.destination_1_id == d1.id,
                DestinationCombination.destination_2_id == d2.id
            ).first()
            
            if exists:
                continue
                
            is_diagonal = (d1.id == d2.id)
            
            if is_diagonal:
                desc = f"Explore {d1.name}. Enjoy the local sights and sounds of this beautiful location."
                act = f"City tour of {d1.name}, Visit local market, Sunset view."
                # Diagonal stores dest2 as None in logic? 
                # Wait, service says: if dest_2_id is None, it is diagonal.
                # But the model allows destination_2_id to be stored.
                # Let's follow the service convention: Diagonal -> destination_2_id = NULL
                
                # Check if diagonal exists (dest_2 is None)
                diag_exists = db.query(DestinationCombination).filter(
                    DestinationCombination.destination_1_id == d1.id,
                    DestinationCombination.destination_2_id == None
                ).first()
                
                if not diag_exists:
                    combo = DestinationCombination(
                        destination_1_id=d1.id,
                        destination_2_id=None,
                        description_content=desc,
                        activity_content=act
                    )
                    db.add(combo)
                    cnt += 1

            else:
                # Directional Pair A->B
                desc = f"Transfer from {d1.name} to {d2.name}. The journey offers scenic views."
                act = f"Stop for lunch on the way to {d2.name}. Photo opportunities."
                
                combo = DestinationCombination(
                    destination_1_id=d1.id,
                    destination_2_id=d2.id,
                    description_content=desc,
                    activity_content=act
                )
                db.add(combo)
                cnt += 1
                
    db.commit()
    print(f"Successfully created {cnt} new matrix entries.")

if __name__ == "__main__":
    seed_matrix()
