import asyncio
import os
import sys

# Add backend dir to pythonpath
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app.db.session import SessionLocal
from app.api.v1.endpoints.permissions import seed_permissions

async def main():
    db = SessionLocal()
    try:
        class DummyUser: pass
        result = await seed_permissions(db, DummyUser())
        print(f"Seed result: {result}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
