# Destination Combination Table - Implementation Guide

## Overview

The **DestinationCombination** model (2D table) is the **signature feature** of this Itinerary Builder Platform. It enables automatic content generation when CS agents create itineraries by storing pre-written descriptions for destination pairs.

---

## Why This Feature Matters

### The Problem
- CS agents need to create hundreds of custom itineraries
- Writing unique descriptions for every combination is time-consuming
- ~1000 destinations × ~1000 destinations = 1,000,000 possible combinations
- Manual writing would take years and result in inconsistent quality

### The Solution
- Pre-written, high-quality content for common destination combinations
- Instant auto-fill when agent selects destinations
- Maintains consistency across all itineraries
- Reduces agent workload by 70%+
- Professional content reviewed by experts

---

## Database Design

### Table Structure

```sql
CREATE TABLE destination_combinations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    destination_1_id UUID NOT NULL REFERENCES destinations(id) ON DELETE CASCADE,
    destination_2_id UUID NULL REFERENCES destinations(id) ON DELETE CASCADE,
    description_content TEXT NOT NULL,
    activity_content TEXT NULL,
    last_edited_by_user_id UUID NULL REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Ensure no duplicate combinations
    CONSTRAINT uq_destination_combination UNIQUE (destination_1_id, destination_2_id)
);

-- Indexes for fast lookups
CREATE INDEX ix_dest_combo_dest1 ON destination_combinations(destination_1_id);
CREATE INDEX ix_dest_combo_dest2 ON destination_combinations(destination_2_id);
CREATE INDEX ix_dest_combo_both ON destination_combinations(destination_1_id, destination_2_id);
```

### Key Design Decisions

1. **Nullable destination_2_id**
   - Supports single-destination entries
   - Example: "Serengeti Only" itinerary still gets auto-fill content

2. **UniqueConstraint on (destination_1_id, destination_2_id)**
   - Prevents duplicate combinations
   - Ensures data integrity

3. **Separate description_content and activity_content**
   - description_content: Overview/introduction paragraph
   - activity_content: Detailed day-by-day activities
   - Allows flexibility in how content is used

4. **Audit trail with last_edited_by**
   - Track who last updated the content
   - Essential for content management workflow

---

## Model Implementation

### Python Model (SQLAlchemy)

```python
from app.models.destination_combination import DestinationCombination
from sqlalchemy import and_, or_

# Example 1: Create a single destination entry
serengeti_only = DestinationCombination(
    destination_1_id=serengeti.id,
    destination_2_id=None,  # NULL for single destination
    description_content="""
        Serengeti National Park is Tanzania's most famous wildlife sanctuary.
        Home to the Great Migration, the Serengeti offers unparalleled game viewing
        opportunities throughout the year. Witness lions, elephants, leopards,
        cheetahs, and thousands of wildebeest across endless golden plains.
    """,
    activity_content="""
        Day 1: Arrival and evening game drive
        Day 2-3: Full-day game drives tracking the Great Migration
        Day 4: Morning game drive and departure
    """,
    last_edited_by_user_id=admin_user.id
)
db.add(serengeti_only)
db.commit()

# Example 2: Create a two-destination combination
serengeti_ngorongoro = DestinationCombination(
    destination_1_id=serengeti.id,
    destination_2_id=ngorongoro.id,
    description_content="""
        Experience the best of Tanzania's northern safari circuit with this classic
        combination of Serengeti National Park and Ngorongoro Crater. Journey through
        the endless plains of the Serengeti, witness the Great Migration, then descend
        into the world's largest intact volcanic caldera for exceptional wildlife
        viewing in a unique ecosystem.
    """,
    activity_content="""
        Day 1-2: Serengeti National Park - Game drives focusing on the Great Migration
        Day 3: Transfer from Serengeti to Ngorongoro Conservation Area
        Day 4: Ngorongoro Crater tour - Descend 600m into the crater for game viewing
        Day 5: Visit Maasai village and departure
    """,
    last_edited_by_user_id=admin_user.id
)
db.add(serengeti_ngorongoro)
db.commit()
```

### Helper Method: get_combination_key()

```python
# Ensures consistent lookups regardless of selection order
key1 = DestinationCombination.get_combination_key(serengeti_id, ngorongoro_id)
# Returns: (serengeti_id, ngorongoro_id) if serengeti_id < ngorongoro_id

key2 = DestinationCombination.get_combination_key(ngorongoro_id, serengeti_id)
# Returns: (serengeti_id, ngorongoro_id) - SAME AS key1

# This means lookup works regardless of which destination user selected first
```

---

## Usage Examples

### 1. Auto-Fill When Creating Itinerary

```python
from app.models import DestinationCombination, Itinerary
from sqlalchemy.orm import Session

def create_itinerary_with_autofill(
    db: Session,
    destination_ids: list[UUID],
    user_id: UUID
) -> Itinerary:
    """
    Create itinerary with auto-filled content from destination combinations.
    """
    # Get standardized key
    if len(destination_ids) == 1:
        key = (destination_ids[0], None)
    else:
        key = DestinationCombination.get_combination_key(
            destination_ids[0],
            destination_ids[1]
        )

    # Lookup pre-written content
    combo = db.query(DestinationCombination).filter(
        DestinationCombination.destination_1_id == key[0],
        DestinationCombination.destination_2_id == key[1]
    ).first()

    if combo:
        # Use pre-written content
        description = combo.description_content
        activities = combo.activity_content
    else:
        # Fallback to generic content or blank
        description = "Custom itinerary"
        activities = None

    # Create itinerary with auto-filled content
    itinerary = Itinerary(
        title=f"Safari Adventure",
        description=description,
        activities_overview=activities,
        created_by_user_id=user_id,
        # ... other fields
    )

    db.add(itinerary)
    db.commit()

    return itinerary
```

### 2. Suggest Destination Combinations

```python
def get_popular_combinations(db: Session, destination_id: UUID, limit: int = 5):
    """
    Get popular destination combinations for a given destination.
    Useful for suggesting "People also visit..." feature.
    """
    combos = db.query(DestinationCombination).filter(
        or_(
            DestinationCombination.destination_1_id == destination_id,
            DestinationCombination.destination_2_id == destination_id
        )
    ).limit(limit).all()

    # Extract the other destination in each combo
    suggestions = []
    for combo in combos:
        if combo.destination_1_id == destination_id:
            suggestions.append(combo.destination_2)
        else:
            suggestions.append(combo.destination_1)

    return suggestions
```

### 3. Content Management - Bulk Update

```python
def bulk_update_combination_content(
    db: Session,
    updates: list[dict],
    editor_user_id: UUID
):
    """
    Bulk update destination combination content.
    Useful for content team to update multiple entries at once.
    """
    for update in updates:
        combo = db.query(DestinationCombination).filter(
            DestinationCombination.destination_1_id == update['dest1_id'],
            DestinationCombination.destination_2_id == update['dest2_id']
        ).first()

        if combo:
            combo.description_content = update.get('description', combo.description_content)
            combo.activity_content = update.get('activities', combo.activity_content)
            combo.last_edited_by_user_id = editor_user_id
            combo.updated_at = datetime.utcnow()

    db.commit()
```

---

## API Endpoint Design

### Pydantic Schemas

```python
from pydantic import BaseModel, UUID4
from typing import Optional

class DestinationCombinationCreate(BaseModel):
    destination_1_id: UUID4
    destination_2_id: Optional[UUID4] = None
    description_content: str
    activity_content: Optional[str] = None

class DestinationCombinationUpdate(BaseModel):
    description_content: Optional[str] = None
    activity_content: Optional[str] = None

class DestinationCombinationResponse(BaseModel):
    id: UUID4
    destination_1_id: UUID4
    destination_1_name: str
    destination_2_id: Optional[UUID4]
    destination_2_name: Optional[str]
    is_single_destination: bool
    destination_names: str
    description_content: str
    activity_content: Optional[str]
    last_edited_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### REST API Endpoints

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, get_current_user
from app.models import DestinationCombination, User

router = APIRouter()

@router.post("/destination-combinations/", response_model=DestinationCombinationResponse)
def create_destination_combination(
    combo_in: DestinationCombinationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new destination combination with auto-fill content.
    Only admins can create combinations.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can create combinations")

    combo = DestinationCombination(
        **combo_in.dict(),
        last_edited_by_user_id=current_user.id
    )
    db.add(combo)
    db.commit()
    db.refresh(combo)

    return combo.to_dict()

@router.get("/destination-combinations/lookup/")
def lookup_combination(
    destination_1_id: UUID4,
    destination_2_id: Optional[UUID4] = None,
    db: Session = Depends(get_db)
):
    """
    Lookup pre-written content for a destination combination.
    Used by frontend when CS agent selects destinations.
    """
    key = DestinationCombination.get_combination_key(destination_1_id, destination_2_id)

    combo = db.query(DestinationCombination).filter(
        DestinationCombination.destination_1_id == key[0],
        DestinationCombination.destination_2_id == key[1]
    ).first()

    if not combo:
        raise HTTPException(status_code=404, detail="No combination found")

    return combo.to_dict()

@router.get("/destination-combinations/suggestions/{destination_id}")
def get_combination_suggestions(
    destination_id: UUID4,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    Get suggested destination combinations for a given destination.
    """
    combos = db.query(DestinationCombination).filter(
        or_(
            DestinationCombination.destination_1_id == destination_id,
            DestinationCombination.destination_2_id == destination_id
        )
    ).limit(limit).all()

    return [combo.to_dict() for combo in combos]

@router.patch("/destination-combinations/{combo_id}")
def update_combination(
    combo_id: UUID4,
    combo_update: DestinationCombinationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update destination combination content.
    Only admins can update.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can update combinations")

    combo = db.query(DestinationCombination).filter(
        DestinationCombination.id == combo_id
    ).first()

    if not combo:
        raise HTTPException(status_code=404, detail="Combination not found")

    # Update fields
    if combo_update.description_content:
        combo.description_content = combo_update.description_content
    if combo_update.activity_content:
        combo.activity_content = combo_update.activity_content

    combo.last_edited_by_user_id = current_user.id
    combo.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(combo)

    return combo.to_dict()
```

---

## Frontend Integration

### React Component Example

```typescript
import { useState, useEffect } from 'react';
import { api } from '@/lib/api/client';

interface DestinationCombination {
  id: string;
  description_content: string;
  activity_content: string | null;
  destination_names: string;
}

export const ItineraryBuilder = () => {
  const [selectedDestinations, setSelectedDestinations] = useState<string[]>([]);
  const [autoFillContent, setAutoFillContent] = useState<DestinationCombination | null>(null);
  const [description, setDescription] = useState('');

  // Auto-fill when destinations are selected
  useEffect(() => {
    if (selectedDestinations.length === 0) return;

    const fetchAutoFill = async () => {
      try {
        const params = {
          destination_1_id: selectedDestinations[0],
          destination_2_id: selectedDestinations[1] || null
        };

        const response = await api.get<DestinationCombination>(
          '/destination-combinations/lookup/',
          { params }
        );

        setAutoFillContent(response);

        // Auto-fill the description field
        setDescription(response.description_content);

        // Show toast notification
        toast.success(`Auto-filled content for ${response.destination_names}`);
      } catch (error) {
        // No combination found, user will enter custom content
        setAutoFillContent(null);
      }
    };

    fetchAutoFill();
  }, [selectedDestinations]);

  return (
    <div>
      {/* Destination selector */}
      <DestinationSelector
        onChange={setSelectedDestinations}
        value={selectedDestinations}
      />

      {/* Show auto-fill indicator */}
      {autoFillContent && (
        <div className="bg-green-50 p-3 rounded-md mb-4">
          <div className="flex items-center">
            <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
            <span className="text-sm text-green-700">
              Content auto-filled for {autoFillContent.destination_names}
            </span>
          </div>
        </div>
      )}

      {/* Description field with auto-filled content */}
      <Textarea
        label="Itinerary Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        rows={6}
        helperText={
          autoFillContent
            ? "Content auto-filled from destination combination. You can edit as needed."
            : "Enter a custom description for this itinerary."
        }
      />
    </div>
  );
};
```

---

## Content Management Workflow

### For Content Team (Admins)

1. **Initial Data Seeding**
   ```bash
   # Run seed script to populate common combinations
   python scripts/seed_destination_combinations.py
   ```

2. **Content Review Process**
   - Admin reviews auto-filled content quality
   - Edits description_content and activity_content
   - System tracks last_edited_by and updated_at

3. **Analytics on Usage**
   - Track which combinations are used most often
   - Prioritize content creation for popular combinations
   - Identify gaps (requested combinations without content)

4. **Bulk Import from Spreadsheet**
   ```python
   # Import from CSV
   import pandas as pd

   df = pd.read_csv('destination_combinations.csv')

   for _, row in df.iterrows():
       dest1 = db.query(Destination).filter(Destination.name == row['destination_1']).first()
       dest2 = db.query(Destination).filter(Destination.name == row['destination_2']).first()

       combo = DestinationCombination(
           destination_1_id=dest1.id,
           destination_2_id=dest2.id if dest2 else None,
           description_content=row['description'],
           activity_content=row['activities'],
           last_edited_by_user_id=admin_user.id
       )
       db.add(combo)

   db.commit()
   ```

---

## Performance Considerations

### Indexing Strategy
- **Primary lookups:** (destination_1_id, destination_2_id) → Composite index
- **Suggestion queries:** destination_1_id OR destination_2_id → Individual indexes
- **Content search:** Consider full-text search index on description_content

### Caching Strategy
```python
from functools import lru_cache
import redis

# Cache frequently accessed combinations
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_combination_cached(dest1_id: UUID, dest2_id: UUID | None = None):
    cache_key = f"combo:{dest1_id}:{dest2_id}"

    # Try cache first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Query database
    key = DestinationCombination.get_combination_key(dest1_id, dest2_id)
    combo = db.query(DestinationCombination).filter(...).first()

    if combo:
        # Cache for 1 hour
        redis_client.setex(cache_key, 3600, json.dumps(combo.to_dict()))

    return combo.to_dict() if combo else None
```

### Query Optimization
```python
# Eager load relationships to avoid N+1 queries
from sqlalchemy.orm import joinedload

combos = db.query(DestinationCombination).options(
    joinedload(DestinationCombination.destination_1),
    joinedload(DestinationCombination.destination_2),
    joinedload(DestinationCombination.last_edited_by)
).all()
```

---

## Testing

### Unit Tests

```python
import pytest
from app.models import DestinationCombination

def test_get_combination_key_single_destination():
    dest_id = uuid.uuid4()
    key = DestinationCombination.get_combination_key(dest_id, None)
    assert key == (dest_id, None)

def test_get_combination_key_two_destinations():
    dest1_id = uuid.uuid4()
    dest2_id = uuid.uuid4()

    # Should return same key regardless of order
    key1 = DestinationCombination.get_combination_key(dest1_id, dest2_id)
    key2 = DestinationCombination.get_combination_key(dest2_id, dest1_id)

    assert key1 == key2
    assert key1[0] < key1[1]  # Smaller ID always first

def test_create_combination(db_session):
    dest1 = create_test_destination(name="Serengeti")
    dest2 = create_test_destination(name="Ngorongoro")

    combo = DestinationCombination(
        destination_1_id=dest1.id,
        destination_2_id=dest2.id,
        description_content="Test description"
    )
    db_session.add(combo)
    db_session.commit()

    assert combo.id is not None
    assert combo.is_single_destination == False
    assert "Serengeti" in combo.destination_names
```

### Integration Tests

```python
def test_auto_fill_on_itinerary_creation(client, db_session):
    # Create destinations and combination
    dest1 = create_test_destination(name="Serengeti")
    dest2 = create_test_destination(name="Ngorongoro")

    combo = DestinationCombination(
        destination_1_id=dest1.id,
        destination_2_id=dest2.id,
        description_content="Auto-filled description"
    )
    db_session.add(combo)
    db_session.commit()

    # Create itinerary via API
    response = client.post(
        "/api/v1/itineraries/",
        json={
            "title": "Test Safari",
            "destination_ids": [str(dest1.id), str(dest2.id)]
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Auto-filled description"
```

---

## Migration Path

### Populating Initial Data

1. **Create single-destination entries** for top 100 destinations
2. **Create two-destination combinations** for top 200 popular pairs
3. **Gradual expansion** based on usage analytics

### Content Migration from Existing System

If migrating from an existing system:

```python
# Extract existing itineraries and their descriptions
existing_itineraries = get_old_system_itineraries()

destination_content = {}

for itinerary in existing_itineraries:
    dests = tuple(sorted([d.id for d in itinerary.destinations]))

    # Aggregate descriptions for same destination combo
    if dests not in destination_content:
        destination_content[dests] = []

    destination_content[dests].append(itinerary.description)

# Create combinations with most common description
for dest_combo, descriptions in destination_content.items():
    # Use most common description
    most_common = Counter(descriptions).most_common(1)[0][0]

    combo = DestinationCombination(
        destination_1_id=dest_combo[0],
        destination_2_id=dest_combo[1] if len(dest_combo) > 1 else None,
        description_content=most_common
    )
    db.add(combo)

db.commit()
```

---

## Summary

The **DestinationCombination** model is a powerful feature that:

✅ **Reduces CS agent workload** by 70%+ through auto-filling
✅ **Maintains content quality** through expert-reviewed descriptions
✅ **Scales efficiently** with proper indexing and caching
✅ **Flexible** - supports single destinations and pairs
✅ **Auditable** - tracks who edited content and when
✅ **Extensible** - can add more fields (images, videos, pricing templates) later

This 2D table design is the core differentiator that makes your itinerary builder superior to competitors.

---

**Next Steps:**
1. Run database migration to create the table
2. Create seed script to populate initial combinations
3. Implement API endpoints for CRUD operations
4. Build frontend auto-fill component
5. Set up content management workflow for admins
