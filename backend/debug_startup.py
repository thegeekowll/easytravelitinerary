
import sys
import os
import traceback

# Add current directory to path
sys.path.append(os.getcwd())

print("Starting debug imports...")

try:
    print("Importing users...")
    from app.api.v1.endpoints import users
    print("Success: users")

    print("Importing auth...")
    from app.api.v1.endpoints import auth
    print("Success: auth")

    print("Importing itineraries...")
    from app.api.v1.endpoints import itineraries
    print("Success: itineraries")

    print("Importing base_tours...")
    from app.api.v1.endpoints import base_tours
    print("Success: base_tours")

    print("Importing destinations...")
    from app.api.v1.endpoints import destinations
    print("Success: destinations")

    print("Importing accommodations...")
    from app.api.v1.endpoints import accommodations
    print("Success: accommodations")

    print("Importing content...")
    from app.api.v1.endpoints import content
    print("Success: content")
    
    print("Importing dashboard...")
    from app.api.v1.endpoints import dashboard
    print("Success: dashboard")
    
    print("Importing destination_combinations...")
    from app.api.v1.endpoints import destination_combinations
    print("Success: destination_combinations")
    
    print("Importing media...")
    from app.api.v1.endpoints import media
    print("Success: media")

    print("Importing notifications...")
    from app.api.v1.endpoints import notifications
    print("Success: notifications")
    
    print("Importing public...")
    from app.api.v1.endpoints import public
    print("Success: public")

except Exception:
    traceback.print_exc()
