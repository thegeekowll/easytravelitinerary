# Testing Checklist

## Pre-Testing Setup

- [ ] PostgreSQL database running
- [ ] Database initialized (`python app/db/init_db.py`)
- [ ] Server running (`uvicorn app.main:app --reload`)
- [ ] Access http://localhost:8000/docs
- [ ] Login as admin (admin@travelagency.com / Admin123!)
- [ ] Copy access token
- [ ] Click "Authorize" in Swagger UI and paste token

---

## 1. Destinations Testing

- [ ] **GET /destinations** - List all destinations (should be empty initially)
- [ ] **POST /destinations** - Create "Paris" destination
  ```json
  {
    "name": "Paris",
    "country": "France",
    "region": "Île-de-France",
    "description": "The City of Light",
    "best_time_to_visit": "April to June",
    "average_temp_celsius": 12.5,
    "highlights": ["Eiffel Tower", "Louvre", "Notre-Dame"],
    "activities": ["Sightseeing", "Museums", "Dining"]
  }
  ```
- [ ] **POST /destinations** - Create "London" destination
- [ ] **POST /destinations** - Create "Rome" destination
- [ ] **GET /destinations** - Verify 3 destinations listed
- [ ] **GET /destinations?search=paris** - Test search
- [ ] **GET /destinations?country=France** - Test filter
- [ ] **GET /destinations/{id}** - Get Paris details
- [ ] **POST /destinations/{id}/images** - Upload 2 images for Paris
- [ ] **PATCH /destinations/{id}** - Update Paris description
- [ ] **GET /destinations/export/csv** - Download CSV export
- [ ] **POST /destinations/bulk-import** - Upload CSV (create sample first)
- [ ] **DELETE /destinations/images/{id}** - Delete one image
- [ ] **DELETE /destinations/{id}** - Delete Rome (admin only)

---

## 2. Accommodations Testing

- [ ] **GET /accommodations/types** - List types (should be empty)
- [ ] **POST /accommodations/types** - Create "Luxury Hotel"
  ```json
  {
    "name": "Luxury Hotel",
    "description": "5-star hotels with premium amenities"
  }
  ```
- [ ] **POST /accommodations/types** - Create "Boutique Hotel"
- [ ] **POST /accommodations/types** - Create "Resort"
- [ ] **GET /accommodations/types** - Verify 3 types
- [ ] **GET /accommodations** - List accommodations (empty initially)
- [ ] **POST /accommodations** - Create "Hotel Ritz Paris"
  ```json
  {
    "name": "Hotel Ritz Paris",
    "accommodation_type_id": "{luxury-hotel-uuid}",
    "destination_id": "{paris-uuid}",
    "location": "15 Place Vendôme",
    "star_rating": 5,
    "description": "Iconic luxury hotel",
    "amenities": ["Spa", "Fine Dining", "Concierge"],
    "contact_email": "info@ritzparis.com",
    "contact_phone": "+33 1 43 16 30 30"
  }
  ```
- [ ] **POST /accommodations** - Create "Shangri-La Hotel Paris"
- [ ] **GET /accommodations** - Verify 2 accommodations
- [ ] **GET /accommodations?destination_id={paris}** - Filter by destination
- [ ] **GET /accommodations?star_rating=5** - Filter by rating
- [ ] **GET /accommodations/{id}** - Get Ritz details
- [ ] **POST /accommodations/{id}/images** - Upload images
- [ ] **PATCH /accommodations/{id}** - Update description
- [ ] **DELETE /accommodations/images/{id}** - Delete one image
- [ ] **DELETE /accommodations/{id}** - Delete Shangri-La

---

## 3. Base Tours Testing

- [ ] **GET /base-tours/types** - List tour types (empty)
- [ ] **POST /base-tours/types** - Create "Cultural Tour"
  ```json
  {
    "name": "Cultural Tour",
    "description": "Explore art, history, and culture"
  }
  ```
- [ ] **POST /base-tours/types** - Create "Adventure Tour"
- [ ] **GET /base-tours/types** - Verify 2 types
- [ ] **GET /base-tours** - List tours (empty)
- [ ] **POST /base-tours** - Create "Paris Explorer"
  ```json
  {
    "title": "Paris Explorer",
    "tour_type_id": "{cultural-tour-uuid}",
    "duration_days": 5,
    "description": "Discover the best of Paris",
    "highlights": ["Eiffel Tower", "Louvre", "Seine Cruise"],
    "difficulty_level": "Easy",
    "is_active": true
  }
  ```
- [ ] **POST /base-tours** - Create "Paris Adventure"
- [ ] **GET /base-tours** - Verify 2 tours
- [ ] **GET /base-tours?tour_type_id={cultural}** - Filter by type
- [ ] **GET /base-tours?min_days=3&max_days=7** - Filter by duration
- [ ] **GET /base-tours/{id}** - Get Paris Explorer details
- [ ] **POST /base-tours/{id}/images** - Upload images
- [ ] **POST /base-tours/{id}/duplicate?new_title=Paris Explorer Premium** - Clone tour
- [ ] **PATCH /base-tours/{id}** - Update description
- [ ] **DELETE /base-tours/{id}** - Delete Paris Adventure

---

## 4. Content Testing

### Inclusions

- [ ] **GET /content/inclusions** - List inclusions (empty)
- [ ] **POST /content/inclusions** - Create "Airport Transfers"
  ```json
  {
    "title": "Airport Transfers",
    "description": "Round-trip airport transfers included"
  }
  ```
- [ ] **POST /content/inclusions** - Create "Hotel Accommodation"
- [ ] **POST /content/inclusions** - Create "Daily Breakfast"
- [ ] **POST /content/inclusions** - Create "Tour Guide"
- [ ] **GET /content/inclusions** - Verify 4 inclusions
- [ ] **PATCH /content/inclusions/{id}** - Update description
- [ ] **DELETE /content/inclusions/{id}** - Delete one

### Exclusions

- [ ] **GET /content/exclusions** - List exclusions (empty)
- [ ] **POST /content/exclusions** - Create "International Flights"
  ```json
  {
    "title": "International Flights",
    "description": "International airfare not included"
  }
  ```
- [ ] **POST /content/exclusions** - Create "Travel Insurance"
- [ ] **POST /content/exclusions** - Create "Personal Expenses"
- [ ] **GET /content/exclusions** - Verify 3 exclusions
- [ ] **PATCH /content/exclusions/{id}** - Update description
- [ ] **DELETE /content/exclusions/{id}** - Delete one

### Company Content

- [ ] **GET /content/company** - Get company content (may be empty)
- [ ] **POST /content/company/logo** - Upload company logo (PNG/JPG)
- [ ] **GET /content/company** - Verify logo URL
- [ ] **GET /content/company/awards** - List awards (empty)
- [ ] **POST /content/company/awards** - Upload award badge 1
- [ ] **POST /content/company/awards** - Upload award badge 2
- [ ] **GET /content/company/awards** - Verify 2 awards
- [ ] **DELETE /content/company/awards/{id}** - Delete one award
- [ ] **GET /content/company/templates** - Get all templates
- [ ] **PATCH /content/company/templates/email_template** - Update email template
  ```json
  {
    "content": "Dear {customer_name},\n\nThank you for choosing our services..."
  }
  ```
- [ ] **PATCH /content/company/templates/intro_letter_template** - Update intro
- [ ] **GET /content/company/templates** - Verify updates

---

## 5. Media Testing

- [ ] **POST /media/upload?container=test&folder=docs** - Upload single PDF
- [ ] **POST /media/upload?container=test&folder=images** - Upload single image
- [ ] **POST /media/upload-multiple?container=test&folder=batch** - Upload 3 images at once
- [ ] **GET /media/list?container=test&folder=docs** - List docs folder
- [ ] **GET /media/list?container=test&folder=images** - List images folder
- [ ] **GET /media/list?container=test&folder=batch** - List batch folder
- [ ] **DELETE /media?file_url={url}** - Delete one file
- [ ] **GET /media/list?container=test&folder=batch** - Verify deletion

---

## 6. CSV Import Testing

### Create Sample CSV Files

**destinations.csv:**
```csv
name,country,region,description,best_time_to_visit,average_temp_celsius,highlights,activities
Barcelona,Spain,Catalonia,Vibrant coastal city,May to October,15.5,"Sagrada Familia,Park Güell,La Rambla","Beach,Architecture,Nightlife"
Amsterdam,Netherlands,North Holland,City of canals,April to September,10.2,"Van Gogh Museum,Anne Frank House,Canal Cruise","Museums,Cycling,Cafes"
```

**accommodations.csv:** (Use actual UUIDs from your database)
```csv
name,accommodation_type_id,destination_id,location,star_rating,description,amenities,contact_email,contact_phone
Hotel Arts Barcelona,{luxury-uuid},{barcelona-uuid},Carrer de la Marina,5,Beachfront luxury hotel,"Spa,Pool,Beach Access",info@hotelbcn.com,+34 93 221 1000
```

### Test Imports

- [ ] **POST /destinations/bulk-import** - Upload destinations.csv
  - Verify success count
  - Check for any errors
  - Verify destinations created
- [ ] Try importing same CSV again - Should get "already exists" errors
- [ ] Create accommodations.csv with real UUIDs
- [ ] Import would be via custom endpoint (or use destinations pattern)

---

## 7. Permission Testing

### Create CS Agent User

- [ ] **POST /users** - Create CS agent
  ```json
  {
    "email": "agent@test.com",
    "full_name": "Test Agent",
    "password": "Agent123!",
    "role": "cs_agent"
  }
  ```
- [ ] **POST /auth/login** - Login as agent
- [ ] Copy agent token

### Test Agent Permissions (use agent token)

- [ ] **GET /destinations** - Should work (read access)
- [ ] **POST /destinations** - Should fail (no create_destination permission)
- [ ] **PATCH /destinations/{id}** - Should fail (no edit_destination permission)
- [ ] **DELETE /destinations/{id}** - Should fail (not admin)

### Grant Permissions to Agent

- [ ] **POST /users/{agent-id}/permissions/add** - Add "create_destination"
  ```json
  {
    "permission_names": ["create_destination", "edit_destination"]
  }
  ```
- [ ] **POST /destinations** (as agent) - Should now work
- [ ] **PATCH /destinations/{id}** (as agent) - Should now work
- [ ] **DELETE /destinations/{id}** (as agent) - Should still fail (admin only)

---

## 8. Pagination Testing

- [ ] Create 25 destinations
- [ ] **GET /destinations?page=1&page_size=10** - First page
  - Verify: `total=25, page=1, page_size=10, total_pages=3, has_next=true, has_prev=false`
  - Verify: 10 items returned
- [ ] **GET /destinations?page=2&page_size=10** - Second page
  - Verify: `page=2, has_next=true, has_prev=true`
- [ ] **GET /destinations?page=3&page_size=10** - Last page
  - Verify: `page=3, has_next=false, has_prev=true`
  - Verify: 5 items returned

---

## 9. Error Handling Testing

- [ ] **POST /destinations** with invalid data - Verify 422 validation error
- [ ] **GET /destinations/{invalid-uuid}** - Verify 404 error
- [ ] **POST /destinations** with duplicate name - Verify 400 error
- [ ] **DELETE /destinations/{id}** without auth - Verify 401 error
- [ ] **DELETE /destinations/{id}** as agent - Verify 403 forbidden error
- [ ] **POST /accommodations** with non-existent destination_id - Verify error

---

## 10. Image Upload Testing

- [ ] Upload JPG image - Should work
- [ ] Upload PNG image - Should work
- [ ] Upload PDF (if allowed) - Test
- [ ] Upload very large file - Test size limits
- [ ] Upload file with special characters in name - Test
- [ ] Upload same file twice - Should create unique names
- [ ] Verify images accessible via returned URLs

---

## Testing Complete Checklist

- [ ] All destinations endpoints tested
- [ ] All accommodations endpoints tested
- [ ] All base tours endpoints tested
- [ ] All content endpoints tested
- [ ] All media endpoints tested
- [ ] CSV imports tested
- [ ] Permission system tested
- [ ] Pagination tested
- [ ] Error handling tested
- [ ] Image uploads tested

---

## Issues Found

Document any issues discovered during testing:

1. **Issue:** [Description]
   - **Steps to Reproduce:** [Steps]
   - **Expected:** [Expected behavior]
   - **Actual:** [Actual behavior]
   - **Status:** [Fixed / Pending]

---

## Next Steps After Testing

1. Create base tour days management endpoints
2. Create itinerary management system (main feature)
3. Add payment tracking
4. Add email/notification system
5. Add analytics endpoints
