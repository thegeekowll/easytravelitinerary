import sys
import os
from sqlalchemy import create_engine, text

# Set env vars to match docker-compose if needed, or assume localhost port
DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/travel_agency"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        itinerary_id = 'ef90ac1b-39af-425d-8d1e-39d56bc236c0'
        
        print(f"--- Checking Itinerary: {itinerary_id} ---")
        result = connection.execute(text("SELECT id, tour_title FROM itineraries WHERE id = :id"), {"id": itinerary_id})
        itinerary = result.fetchone()
        
        if not itinerary:
            print("❌ Itinerary NOT FOUND in database!")
        else:
            print(f"✅ Itinerary Found: {itinerary.tour_title}")
            
            print("\n--- Checking Images ---")
            images_result = connection.execute(text("SELECT * FROM itinerary_images WHERE itinerary_id = :id"), {"id": itinerary_id})
            images = images_result.fetchall()
            
            if not images:
                print("❌ No images found in 'itinerary_images' table for this ID.")
            else:
                print(f"✅ Found {len(images)} images:")
                for img in images:
                    print(f"   - ID: {img.id}, URL: {img.image_url}, Caption: {img.caption}")

except Exception as e:
    print(f"Error: {e}")
