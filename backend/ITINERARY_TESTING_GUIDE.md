# Itinerary System Testing Guide

Quick reference for testing the 2D table and itinerary creation system.

---

## 🚀 Quick Start Testing Flow

### Prerequisites

1. Server running: `uvicorn app.main:app --reload`
2. Open Swagger UI: http://localhost:8000/docs
3. Login as admin and authorize
4. Have at least 3 destinations created
5. Have at least 1 base tour created

---

## Part 1: Test 2D Destination Table

### Step 1: Create Diagonal (Single Destination)

**Endpoint:** `POST /destination-combinations`

```json
{
  "destination_1_id": "{your-serengeti-uuid}",
  "destination_2_id": null,
  "description_content": "Spend the day exploring the vast Serengeti plains, home to the Great Migration. Witness thousands of wildebeest and zebras crossing the grasslands.",
  "activity_content": "Morning game drive through the central Serengeti. Afternoon visit to a kopje for panoramic views. Evening sundowner watching predators hunt."
}
```

✅ **Expected:** Combination created successfully

### Step 2: Create Pair Combination

```json
{
  "destination_1_id": "{serengeti-uuid}",
  "destination_2_id": "{ngorongoro-uuid}",
  "description_content": "Journey from the endless plains of Serengeti to the breathtaking Ngorongoro Crater. Experience diverse ecosystems and wildlife in a single day.",
  "activity_content": "Morning game drive in Serengeti. Scenic drive to Ngorongoro. Afternoon crater rim walk with spectacular views."
}
```

✅ **Expected:** Combination created

### Step 3: Test Symmetry

**Endpoint:** `GET /destination-combinations/search`

```
?destination_1_id={serengeti-uuid}&destination_2_id={ngorongoro-uuid}
```

✅ **Expected:** Returns the combination

Now reverse the order:

```
?destination_1_id={ngorongoro-uuid}&destination_2_id={serengeti-uuid}
```

✅ **Expected:** Returns THE SAME combination (this is symmetry!)

### Step 4: Test Auto-Fill (Single Destination)

**Endpoint:** `POST /destination-combinations/auto-fill`

```json
{
  "destination_ids": ["{serengeti-uuid}"]
}
```

✅ **Expected Response:**
```json
{
  "type": "single",
  "description": "Spend the day exploring...",
  "activity": "Morning game drive...",
  "suggestions": []
}
```

### Step 5: Test Auto-Fill (Two Destinations)

```json
{
  "destination_ids": [
    "{serengeti-uuid}",
    "{ngorongoro-uuid}"
  ]
}
```

✅ **Expected Response:**
```json
{
  "type": "pair",
  "description": "Journey from the endless plains...",
  "activity": "Morning game drive in Serengeti...",
  "suggestions": []
}
```

### Step 6: Create More Combinations

Create combinations for:
- Ngorongoro × Tarangire
- Serengeti × Tarangire
- Tarangire (diagonal)

This will enable testing 3+ destinations.

### Step 7: Test Auto-Fill (3+ Destinations)

```json
{
  "destination_ids": [
    "{serengeti-uuid}",
    "{ngorongoro-uuid}",
    "{tarangire-uuid}"
  ]
}
```

✅ **Expected Response:**
```json
{
  "type": "multiple",
  "description": null,
  "activity": null,
  "suggestions": [
    {
      "pair_name": "Serengeti × Ngorongoro",
      "destination_1_id": "...",
      "destination_2_id": "...",
      "description": "Journey from the endless plains...",
      "activity": "Morning game drive..."
    },
    {
      "pair_name": "Ngorongoro × Tarangire",
      "destination_1_id": "...",
      "destination_2_id": "...",
      "description": "...",
      "activity": "..."
    },
    {
      "pair_name": "Serengeti × Tarangire",
      "destination_1_id": "...",
      "destination_2_id": "...",
      "description": "...",
      "activity": "..."
    }
  ]
}
```

✅ **This is the dropdown scenario!** Agent would choose one of these suggestions.

---

## Part 2: Test Itinerary Creation

### Method A: Choose Existing Base Tour

**Endpoint:** `POST /itineraries/create-from-base`

**Preparation:**
1. Make sure you have a base tour with days
2. Note the base_tour_id

**Test:**

```json
{
  "base_tour_id": "{your-base-tour-uuid}",
  "departure_date": "2026-06-15",
  "travelers": [
    {
      "full_name": "John Smith",
      "email": "john.smith@example.com",
      "phone": "+1-555-0100",
      "date_of_birth": "1985-03-20",
      "nationality": "United States",
      "passport_number": "AB1234567",
      "is_primary_contact": true
    },
    {
      "full_name": "Jane Smith",
      "email": "jane.smith@example.com",
      "phone": "+1-555-0101",
      "date_of_birth": "1987-07-15",
      "nationality": "United States",
      "passport_number": "AB7654321",
      "is_primary_contact": false
    }
  ]
}
```

✅ **Expected:**
- Itinerary created with status "draft"
- `unique_code` generated (8 chars)
- `creation_method` = "choose_existing"
- All days copied from base tour
- `return_date` calculated automatically
- Days have `day_date` set

**Verify:**
```
GET /itineraries/{itinerary-id}
```

Check:
- ✅ All days present
- ✅ Each day has destinations
- ✅ `is_description_custom` = false (came from base tour)
- ✅ Travelers created
- ✅ Unique code present

---

### Method B: Edit Existing Base Tour

**Endpoint:** `POST /itineraries/create-from-edited`

**Scenario:** Start with base tour but customize days

```json
{
  "base_tour_id": "{your-base-tour-uuid}",
  "title": "Custom Safari Experience",
  "description": "A tailored safari adventure",
  "departure_date": "2026-07-01",
  "days": [
    {
      "day_number": 1,
      "title": "Arrival & Serengeti",
      "destination_ids": ["{serengeti-uuid}"],
      "accommodation_ids": ["{accommodation-uuid}"],
      "meals_included": "Dinner"
    },
    {
      "day_number": 2,
      "title": "Serengeti to Ngorongoro",
      "destination_ids": [
        "{serengeti-uuid}",
        "{ngorongoro-uuid}"
      ],
      "accommodation_ids": ["{accommodation-uuid}"],
      "meals_included": "All meals",
      "description": "Custom description that overrides auto-fill",
      "activities": "Custom activities"
    },
    {
      "day_number": 3,
      "title": "Three Park Day",
      "destination_ids": [
        "{serengeti-uuid}",
        "{ngorongoro-uuid}",
        "{tarangire-uuid}"
      ],
      "accommodation_ids": ["{accommodation-uuid}"],
      "meals_included": "All meals"
    }
  ],
  "travelers": [
    {
      "full_name": "Sarah Johnson",
      "email": "sarah@example.com",
      "phone": "+1-555-0200",
      "date_of_birth": "1990-05-10",
      "nationality": "Canada",
      "passport_number": "CD9876543",
      "is_primary_contact": true
    }
  ]
}
```

✅ **Expected:**
- Custom title applied
- Day 1: Auto-filled from Serengeti diagonal
  - `is_description_custom` = false
  - `is_activity_custom` = false
- Day 2: Custom content used (no auto-fill)
  - `is_description_custom` = true
  - `is_activity_custom` = true
- Day 3: NOT auto-filled (3+ destinations)
  - Description/activity will be empty
  - Agent needs to choose from suggestions manually

**Verify Day 3:**

Since Day 3 has 3 destinations and no provided content, check what suggestions would be:

```
POST /destination-combinations/auto-fill
{
  "destination_ids": [
    "{serengeti-uuid}",
    "{ngorongoro-uuid}",
    "{tarangire-uuid}"
  ]
}
```

You should see 3 suggestions. Agent would pick one and update the itinerary.

---

### Method C: Build Custom Itinerary

**Endpoint:** `POST /itineraries/create-custom`

**Scenario:** Build from scratch with no base tour

```json
{
  "title": "Fully Custom Tanzania Adventure",
  "tour_type_id": "{your-tour-type-uuid}",
  "description": "A completely customized journey",
  "departure_date": "2026-08-01",
  "days": [
    {
      "day_number": 1,
      "title": "Welcome to Tanzania",
      "destination_ids": ["{serengeti-uuid}"],
      "accommodation_ids": ["{accommodation-uuid}"],
      "meals_included": "Dinner"
    },
    {
      "day_number": 2,
      "title": "Safari Day",
      "destination_ids": [
        "{serengeti-uuid}",
        "{ngorongoro-uuid}"
      ],
      "accommodation_ids": ["{accommodation-uuid}"],
      "meals_included": "All meals"
    }
  ],
  "travelers": [
    {
      "full_name": "Michael Chen",
      "email": "michael@example.com",
      "phone": "+1-555-0300",
      "date_of_birth": "1982-11-25",
      "nationality": "Singapore",
      "passport_number": "EF1357924",
      "is_primary_contact": true
    }
  ],
  "inclusion_ids": [
    "{inclusion-uuid-1}",
    "{inclusion-uuid-2}"
  ],
  "exclusion_ids": [
    "{exclusion-uuid-1}"
  ]
}
```

✅ **Expected:**
- No base_tour_id
- `creation_method` = "custom"
- Days auto-filled from 2D table
- Custom inclusions/exclusions set

---

## Part 3: Test Update & Permissions

### Test 1: Update Itinerary Before Tour Starts

```
GET /itineraries/{id}
```

Copy the itinerary, then:

```
PATCH /itineraries/{id}
{
  "description": "Updated description"
}
```

✅ **Expected:** Update succeeds (tour hasn't started)

### Test 2: Update After Tour Ends (Should Fail)

Create an itinerary with `departure_date` in the past:

```json
{
  "base_tour_id": "{uuid}",
  "departure_date": "2024-01-01",  // Past date
  "travelers": [...]
}
```

Now try to update it:

```
PATCH /itineraries/{id}
{
  "description": "Updated"
}
```

✅ **Expected:** 403 Forbidden (tour has ended, edit locked)

### Test 3: Admin Can Always Edit

Use admin token:

```
PATCH /itineraries/{id}
{
  "description": "Admin override"
}
```

✅ **Expected:** Update succeeds (admins bypass edit lock)

### Test 4: Enable Edit After Tour

```
PATCH /itineraries/{id}
{
  "can_edit_after_tour": true
}
```

Now try updating again with agent token:

✅ **Expected:** Update succeeds (edit lock disabled)

---

## Part 4: Test Additional Features

### Duplicate Itinerary

```
POST /itineraries/{id}/duplicate?new_departure_date=2026-09-01
```

✅ **Expected:**
- New itinerary created
- New `unique_code`
- All days copied
- New dates calculated
- Travelers reset to "[To be updated]" (privacy)
- Status = "draft"

### Assign to Agent (Admin Only)

```
PATCH /itineraries/{id}/assign
{
  "assigned_to_user_id": "{agent-uuid}"
}
```

✅ **Expected:** Itinerary reassigned

### Mark Complete

```
PATCH /itineraries/{id}/complete?mark_complete=true
```

✅ **Expected:** Status = "completed"

```
PATCH /itineraries/{id}/complete?mark_complete=false
```

✅ **Expected:** Status = "confirmed"

### Soft Delete

```
DELETE /itineraries/{id}
```

✅ **Expected:** Status = "cancelled" (not hard deleted)

---

## Part 5: Test Listing & Filtering

### List My Itineraries

```
GET /itineraries?page=1&page_size=20
```

✅ **Expected:** User's created itineraries

### Filter by Status

```
GET /itineraries?status_filter=draft
```

✅ **Expected:** Only draft itineraries

### Filter by Date Range

```
GET /itineraries?departure_date_from=2026-06-01&departure_date_to=2026-12-31
```

✅ **Expected:** Itineraries in date range

### Search

```
GET /itineraries?search=Safari
```

✅ **Expected:** Itineraries with "Safari" in title

### Assigned to Me

```
GET /itineraries/assigned-to-me
```

✅ **Expected:** Itineraries assigned to current user

### All Itineraries (Admin)

```
GET /itineraries/all
```

✅ **Expected:** All itineraries in system

---

## 🧪 Complete Test Checklist

### 2D Table Tests
- [ ] Create diagonal combination (single destination)
- [ ] Create pair combination
- [ ] Test symmetry (reversed order)
- [ ] Auto-fill with 1 destination
- [ ] Auto-fill with 2 destinations
- [ ] Auto-fill with 3+ destinations (suggestions)
- [ ] Update combination
- [ ] Delete combination
- [ ] List combinations
- [ ] Get grid data

### Itinerary Creation Tests
- [ ] Method A: Create from base tour
- [ ] Method B: Create from edited tour
- [ ] Method C: Create custom itinerary
- [ ] Verify auto-fill worked
- [ ] Verify custom flags set correctly
- [ ] Verify dates calculated correctly
- [ ] Verify unique code generated

### Permission Tests
- [ ] Update before tour starts (should work)
- [ ] Update after tour ends (should fail)
- [ ] Admin can always edit
- [ ] Enable can_edit_after_tour flag
- [ ] Update with flag enabled (should work)

### Additional Feature Tests
- [ ] Duplicate itinerary
- [ ] Assign to different agent
- [ ] Mark complete/incomplete
- [ ] Soft delete

### Listing Tests
- [ ] List my itineraries
- [ ] List assigned itineraries
- [ ] List all (admin)
- [ ] Filter by status
- [ ] Filter by date range
- [ ] Search by title
- [ ] Pagination works

---

## 🚨 Common Issues & Solutions

**Issue:** Auto-fill returns null
**Solution:** Make sure destination combinations exist in 2D table

**Issue:** 403 Forbidden when updating
**Solution:** Check if tour has ended and can_edit_after_tour is false

**Issue:** Duplicate throws error
**Solution:** Ensure original itinerary has all required data

**Issue:** 3+ destinations not showing suggestions
**Solution:** Verify combinations exist for all pairs

**Issue:** Dates look wrong
**Solution:** Check departure_date format and duration_days

---

## ✅ Success Criteria

All tests pass if:
- ✅ 2D table lookups work with symmetry
- ✅ Auto-fill works for 1-2 destinations
- ✅ Suggestions shown for 3+ destinations
- ✅ All three creation methods work
- ✅ Dates calculated correctly
- ✅ Unique codes generated
- ✅ Edit permissions enforced
- ✅ All CRUD operations work
- ✅ Filtering and pagination work

---

**Ready for production testing!** 🎉
