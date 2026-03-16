
import sys
import os
from datetime import datetime
import uuid

# Add current directory to path
sys.path.append(os.getcwd())

from app.models.company import CompanyAsset, CompanyContent, AssetTypeEnum
from app.schemas.company import CompanyAssetResponse, CompanyContentResponse

def test_asset_serialization():
    print("Testing CompanyAsset serialization...")
    try:
        # Simulate DB Object
        asset = CompanyAsset(
            id=uuid.uuid4(),
            asset_type=AssetTypeEnum.LOGO,
            asset_name="Test Logo",
            asset_url="http://example.com/logo.png",
            sort_order=1,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Serialize
        serialized = CompanyAssetResponse.model_validate(asset)
        print("✅ CompanyAsset serialized successfully:", serialized.model_dump())
    except Exception as e:
        print("❌ CompanyAsset serialization FAILED:", e)

def test_content_serialization():
    print("\nTesting CompanyContent serialization...")
    try:
        # Simulate DB Object
        content = CompanyContent(
            id=uuid.uuid4(),
            key="intro_letter",
            content="Hello world",
            placeholders={"name": "Traveler"},
            updated_by_user_id=uuid.uuid4(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Serialize
        serialized = CompanyContentResponse.model_validate(content)
        print("✅ CompanyContent serialized successfully:", serialized.model_dump())
    except Exception as e:
        print("❌ CompanyContent serialization FAILED:", e)

if __name__ == "__main__":
    test_asset_serialization()
    test_content_serialization()
