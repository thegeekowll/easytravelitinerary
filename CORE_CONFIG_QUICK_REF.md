# Core Configuration Quick Reference

## Backend Quick Reference

### Database Session
```python
from app.db.session import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

@router.get("/items")
def get_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

### Authentication
```python
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)

# Hash password
hashed = get_password_hash("password")

# Verify password
is_valid = verify_password("password", hashed)

# Create token
token = create_access_token(user_id)

# Protected endpoint
@router.get("/me")
def read_me(user = Depends(get_current_user)):
    return user
```

### Authorization
```python
from app.core.security import RoleChecker, PermissionChecker, Roles, Permissions

# Require admin role
@router.get("/admin")
def admin_only(user = Depends(RoleChecker([Roles.ADMIN]))):
    return {"access": "granted"}

# Require permission
@router.post("/itineraries")
def create_itinerary(
    user = Depends(PermissionChecker([Permissions.ITINERARY_CREATE]))
):
    return itinerary
```

### Dependencies
```python
from app.api.v1.deps import (
    PaginationParams,
    CommonQueryParams,
    require_admin,
    create_paginated_response,
)

# Pagination
@router.get("/items")
def list_items(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    items = db.query(Item).offset(pagination.skip).limit(pagination.limit).all()
    total = db.query(Item).count()
    return create_paginated_response(items, total, pagination.page, pagination.page_size)

# Combined query params
@router.get("/search")
def search_items(common: CommonQueryParams = Depends()):
    # common.page, common.page_size, common.skip, common.limit
    # common.sort_by, common.sort_order, common.q
    pass
```

### Exceptions
```python
from app.core.exceptions import (
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
)

# Raise exceptions
raise NotFoundException("Item not found")
raise UnauthorizedException("Invalid credentials")
raise ForbiddenException("Permission denied")
```

### Logging
```python
from app.utils.logger import logger

logger.info("User logged in")
logger.error("Failed to process request")
logger.warning("Deprecated endpoint used")
```

### Constants
```python
from app.utils.constants import (
    RoleEnum,
    ItineraryStatusEnum,
    Permissions,
)

# Use enums
if user.role == RoleEnum.ADMIN:
    pass

if itinerary.status == ItineraryStatusEnum.CONFIRMED:
    pass

# Check permissions
if Permissions.ITINERARY_CREATE in user_permissions:
    pass
```

## Frontend Quick Reference

### API Client
```typescript
import { api } from '@/lib/api/client';

// GET request
const users = await api.get<User[]>('/users');

// POST request
const user = await api.post<User>('/users', {
  name: 'John',
  email: 'john@example.com'
});

// PUT request
await api.put(`/users/${id}`, updateData);

// DELETE request
await api.delete(`/users/${id}`);

// Upload file
const formData = new FormData();
formData.append('file', file);
await api.upload('/upload', formData);

// Download file
await api.download('/reports/monthly.pdf', 'report.pdf');
```

### Authentication
```tsx
import { useAuth } from '@/lib/hooks/useAuth';

function MyComponent() {
  const { user, login, logout, isAuthenticated, isLoading } = useAuth();

  const handleLogin = async () => {
    await login({
      email: 'user@example.com',
      password: 'password'
    });
  };

  if (isLoading) return <div>Loading...</div>;
  if (!isAuthenticated) return <div>Please login</div>;

  return <div>Welcome, {user.first_name}!</div>;
}
```

### Authorization Hooks
```tsx
import { useUser, usePermissions, useRoles } from '@/lib/hooks/useAuth';

function MyComponent() {
  // User hook
  const { user, isAdmin, isCSAgent } = useUser();

  // Permissions hook
  const { can, canAll } = usePermissions();

  // Roles hook
  const { is, isAny } = useRoles();

  return (
    <div>
      {isAdmin && <AdminPanel />}
      {can('itinerary:create') && <CreateButton />}
      {isAny(['admin', 'cs_agent']) && <Dashboard />}
    </div>
  );
}
```

### Protected Routes
```tsx
import {
  ProtectedRoute,
  AdminRoute,
  CSAgentRoute,
} from '@/lib/auth/AuthContext';

// Any authenticated user
<ProtectedRoute>
  <MyPage />
</ProtectedRoute>

// Admin only
<AdminRoute>
  <AdminDashboard />
</AdminRoute>

// CS Agent or Admin
<CSAgentRoute>
  <ItineraryBuilder />
</CSAgentRoute>

// Specific role
<ProtectedRoute requiredRole="admin">
  <Settings />
</ProtectedRoute>

// Multiple roles
<ProtectedRoute requiredRoles={['admin', 'cs_agent']}>
  <Dashboard />
</ProtectedRoute>

// Permission-based
<ProtectedRoute requiredPermission="itinerary:create">
  <CreateItinerary />
</ProtectedRoute>

// Multiple permissions
<ProtectedRoute
  requiredPermissions={['itinerary:create', 'itinerary:send_email']}
>
  <AdvancedItinerary />
</ProtectedRoute>
```

### Auth Provider Setup
```tsx
// app/layout.tsx
import { AuthProvider } from '@/lib/auth/AuthContext';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

## Common Patterns

### Backend: Protected Endpoint with Pagination
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.v1.deps import PaginationParams, require_cs_agent, create_paginated_response

router = APIRouter()

@router.get("/itineraries")
def list_itineraries(
    pagination: PaginationParams = Depends(),
    user = Depends(require_cs_agent),
    db: Session = Depends(get_db)
):
    query = db.query(Itinerary)
    total = query.count()
    itineraries = query.offset(pagination.skip).limit(pagination.limit).all()
    return create_paginated_response(itineraries, total, pagination.page, pagination.page_size)
```

### Frontend: Fetching Data with Auth
```tsx
import { useAuth } from '@/lib/hooks/useAuth';
import { api } from '@/lib/api/client';
import { useQuery } from '@tanstack/react-query';

function ItineraryList() {
  const { isAuthenticated } = useAuth();

  const { data, isLoading, error } = useQuery({
    queryKey: ['itineraries'],
    queryFn: () => api.get('/itineraries'),
    enabled: isAuthenticated,
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading itineraries</div>;

  return (
    <div>
      {data.data.map(itinerary => (
        <div key={itinerary.id}>{itinerary.name}</div>
      ))}
    </div>
  );
}
```

### Backend: Creating Resource with Validation
```python
from app.core.exceptions import ValidationException, ConflictException
from app.utils.logger import logger

@router.post("/users")
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    # Check if user exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise ConflictException(f"User with email {user_data.email} already exists")

    # Validate password
    is_valid, error = validate_password_strength(user_data.password)
    if not is_valid:
        raise ValidationException(error)

    # Create user
    user = User(**user_data.dict())
    user.password = get_password_hash(user_data.password)
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"User created: {user.email}")
    return user
```

## Token Management

### Backend: Token Endpoints
```python
@router.post("/auth/login")
def login(credentials: LoginCredentials, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise InvalidCredentialsException()

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return {
        "user": user,
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    }

@router.post("/auth/refresh")
def refresh_token(refresh_token: str):
    payload = verify_token(refresh_token, "refresh")
    user_id = payload.get("sub")

    new_access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token
    }
```

### Frontend: Auto Token Refresh
```typescript
// Already handled automatically by API client
// Tokens are stored in localStorage
// Automatically refreshed on 401 response
// Failed requests are queued and retried

// Manual token management if needed
import { tokenManager } from '@/lib/api/client';

// Get tokens
const accessToken = tokenManager.getAccessToken();
const refreshToken = tokenManager.getRefreshToken();

// Set tokens
tokenManager.setTokens(accessToken, refreshToken);

// Clear tokens
tokenManager.removeTokens();
```

## Error Handling

### Backend: Centralized Error Handling
```python
from app.core.exceptions import NotFoundException
from app.utils.logger import logger

@router.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        logger.warning(f"Item {item_id} not found")
        raise NotFoundException(f"Item with ID {item_id} not found")
    return item
```

### Frontend: Automatic Error Display
```typescript
// Errors are automatically displayed as toast notifications
// No need for try-catch in most cases

// But you can still catch errors if needed
try {
  await api.post('/items', data);
  toast.success('Item created successfully');
} catch (error) {
  // Error already shown by API client
  // Add custom handling here if needed
  console.error('Failed to create item:', error);
}
```

## Environment Variables

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/travel_agency

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)
```bash
# API
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## Quick Tips

1. **Always use dependencies** - Don't manually check auth in endpoints
2. **Use typed responses** - Define Pydantic schemas for all responses
3. **Log important events** - Use logger for debugging and auditing
4. **Handle errors gracefully** - Use custom exceptions with clear messages
5. **Validate input** - Use Pydantic for request validation
6. **Use pagination** - Always paginate list endpoints
7. **Cache when possible** - Use Redis for frequently accessed data
8. **Type everything** - Use TypeScript types on frontend
9. **Use React Query** - For data fetching and caching
10. **Test your code** - Write tests for critical functionality
