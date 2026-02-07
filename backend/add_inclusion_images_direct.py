from sqlalchemy import create_engine, text

# Hardcoded connection string for local execution against Docker mapped port
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/travel_agency"

def add_image_url_columns():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # Add image_url to inclusions
            try:
                print("Checking inclusions table...")
                check_query = text("SELECT column_name FROM information_schema.columns WHERE table_name='inclusions' AND column_name='image_url'")
                if conn.execute(check_query).fetchone():
                    print("Column 'image_url' already exists in 'inclusions'.")
                else:
                    conn.execute(text("ALTER TABLE inclusions ADD COLUMN image_url VARCHAR"))
                    print("Added image_url to inclusions table")
                    conn.commit()
            except Exception as e:
                print(f"Error adding to inclusions: {e}")
                conn.rollback()

            # Add image_url to exclusions
            try:
                print("Checking exclusions table...")
                check_query = text("SELECT column_name FROM information_schema.columns WHERE table_name='exclusions' AND column_name='image_url'")
                if conn.execute(check_query).fetchone():
                    print("Column 'image_url' already exists in 'exclusions'.")
                else:
                    conn.execute(text("ALTER TABLE exclusions ADD COLUMN image_url VARCHAR"))
                    print("Added image_url to exclusions table")
                    conn.commit()
            except Exception as e:
                print(f"Error adding to exclusions: {e}")
                conn.rollback()
                
    except Exception as e:
        print(f"Failed to connect or execute: {e}")

if __name__ == "__main__":
    add_image_url_columns()
