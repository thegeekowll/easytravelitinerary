import sys
import os

# Add the current directory to sys.path so we can import app modules
sys.path.append(os.getcwd())

print("Verifying backend imports (Attempt 2)...")

try:
    print("Importing app.services.azure_blob_service (Patched)...")
    import app.services.azure_blob_service
    print("SUCCESS: app.services.azure_blob_service imported.")
except Exception as e:
    print(f"FAILURE: Could not import app.services.azure_blob_service. Error: {e}")
    import traceback
    traceback.print_exc()

try:
    print("Importing app.models.itinerary...")
    import app.models.itinerary
    print("SUCCESS: app.models.itinerary imported.")
except Exception as e:
    print(f"FAILURE: Could not import app.models.itinerary. Error: {e}")
    import traceback
    traceback.print_exc()

try:
    print("Importing app.api.v1.endpoints.itineraries...")
    import app.api.v1.endpoints.itineraries
    print("SUCCESS: app.api.v1.endpoints.itineraries imported.")
except Exception as e:
    print(f"FAILURE: Could not import app.api.v1.endpoints.itineraries. Error: {e}")
    import traceback
    traceback.print_exc()

try:
    print("Importing app.db.base...")
    import app.db.base
    print("SUCCESS: app.db.base imported.")
except Exception as e:
    print(f"FAILURE: Could not import app.db.base. Error: {e}")
    import traceback
    traceback.print_exc()

print("Verification complete.")
