# Project Structure

## Complete Directory Tree

```
Itinerary Builder Platform/
│
├── backend/                          # FastAPI Backend Application
│   ├── app/
│   │   ├── __init__.py
│   │   │
│   │   ├── api/                      # API Layer
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── api.py            # API router aggregation
│   │   │       ├── deps.py           # Dependency injection (DB sessions, auth)
│   │   │       └── endpoints/        # API endpoints
│   │   │           ├── __init__.py
│   │   │           ├── auth.py       # Login, register, logout, refresh token
│   │   │           ├── users.py      # User CRUD operations
│   │   │           ├── itineraries.py # Itinerary management
│   │   │           ├── packages.py   # Tour package management
│   │   │           ├── destinations.py # Destination management
│   │   │           ├── accommodations.py # Accommodation management
│   │   │           ├── notifications.py # Notification endpoints
│   │   │           ├── analytics.py  # Analytics endpoints
│   │   │           └── payments.py   # Payment tracking
│   │   │
│   │   ├── core/                     # Core Functionality
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # Settings and configuration
│   │   │   ├── security.py           # Auth, JWT, password hashing
│   │   │   ├── permissions.py        # Permission checking system
│   │   │   └── exceptions.py         # Custom exceptions
│   │   │
│   │   ├── db/                       # Database Configuration
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # Base model and imports
│   │   │   ├── session.py            # Database session management
│   │   │   └── init_db.py            # Initial data loading
│   │   │
│   │   ├── models/                   # SQLAlchemy Models
│   │   │   ├── __init__.py
│   │   │   ├── user.py               # User model
│   │   │   ├── role.py               # Role model
│   │   │   ├── permission.py         # Permission model
│   │   │   ├── itinerary.py          # Itinerary model
│   │   │   ├── itinerary_item.py     # Itinerary daily items
│   │   │   ├── package.py            # Tour package model
│   │   │   ├── destination.py        # Destination model
│   │   │   ├── destination_cross_ref.py # 2D destination mapping
│   │   │   ├── accommodation.py      # Accommodation model
│   │   │   ├── notification.py       # Notification model
│   │   │   ├── analytics.py          # Analytics event model
│   │   │   └── payment.py            # Payment tracking model
│   │   │
│   │   ├── schemas/                  # Pydantic Schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py               # User schemas
│   │   │   ├── auth.py               # Auth schemas (login, token)
│   │   │   ├── itinerary.py          # Itinerary schemas
│   │   │   ├── package.py            # Package schemas
│   │   │   ├── destination.py        # Destination schemas
│   │   │   ├── accommodation.py      # Accommodation schemas
│   │   │   ├── notification.py       # Notification schemas
│   │   │   ├── analytics.py          # Analytics schemas
│   │   │   ├── payment.py            # Payment schemas
│   │   │   └── common.py             # Common schemas (pagination, etc.)
│   │   │
│   │   ├── services/                 # Business Logic Layer
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py       # Authentication logic
│   │   │   ├── user_service.py       # User operations
│   │   │   ├── itinerary_service.py  # Itinerary business logic
│   │   │   ├── package_service.py    # Package operations
│   │   │   ├── destination_service.py # Destination operations
│   │   │   ├── pdf_service.py        # PDF generation
│   │   │   ├── email_service.py      # Email sending (SendGrid)
│   │   │   ├── storage_service.py    # Azure Blob Storage
│   │   │   ├── notification_service.py # Notification management
│   │   │   ├── analytics_service.py  # Analytics processing
│   │   │   ├── celery_app.py         # Celery configuration
│   │   │   └── celery_tasks.py       # Async tasks
│   │   │
│   │   └── utils/                    # Utility Functions
│   │       ├── __init__.py
│   │       ├── date_utils.py         # Date/time helpers
│   │       ├── file_utils.py         # File handling
│   │       ├── validators.py         # Custom validators
│   │       ├── constants.py          # Constants and enums
│   │       └── logger.py             # Logging configuration
│   │
│   ├── alembic/                      # Database Migrations
│   │   ├── versions/                 # Migration versions
│   │   │   └── __init__.py
│   │   ├── env.py                    # Alembic environment
│   │   └── script.py.mako            # Migration template
│   │
│   ├── tests/                        # Tests
│   │   ├── __init__.py
│   │   ├── conftest.py               # Pytest configuration
│   │   ├── unit/                     # Unit tests
│   │   │   ├── __init__.py
│   │   │   ├── test_auth.py
│   │   │   ├── test_itineraries.py
│   │   │   └── test_services.py
│   │   └── integration/              # Integration tests
│   │       ├── __init__.py
│   │       └── test_api.py
│   │
│   ├── main.py                       # FastAPI application entry
│   ├── requirements.txt              # Python dependencies
│   ├── Dockerfile                    # Backend Docker configuration
│   ├── .env.example                  # Environment variables template
│   ├── .gitignore                    # Git ignore rules
│   ├── alembic.ini                   # Alembic configuration
│   └── pytest.ini                    # Pytest configuration
│
├── frontend/                         # Next.js Frontend Application
│   ├── app/                          # App Router Directory
│   │   ├── layout.tsx                # Root layout
│   │   ├── page.tsx                  # Home page
│   │   ├── globals.css               # Global styles
│   │   │
│   │   ├── auth/                     # Authentication Pages
│   │   │   ├── login/
│   │   │   │   └── page.tsx          # Login page
│   │   │   ├── register/
│   │   │   │   └── page.tsx          # Registration page
│   │   │   ├── forgot-password/
│   │   │   │   └── page.tsx          # Forgot password
│   │   │   └── reset-password/
│   │   │       └── page.tsx          # Reset password
│   │   │
│   │   ├── dashboard/                # Protected Dashboard Routes
│   │   │   ├── layout.tsx            # Dashboard layout
│   │   │   ├── page.tsx              # Dashboard home
│   │   │   ├── itineraries/          # Itinerary management
│   │   │   │   ├── page.tsx          # List itineraries
│   │   │   │   ├── new/
│   │   │   │   │   └── page.tsx      # Create itinerary
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx      # View itinerary
│   │   │   │       └── edit/
│   │   │   │           └── page.tsx  # Edit itinerary
│   │   │   ├── packages/             # Package management
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── notifications/        # Notifications
│   │   │   │   └── page.tsx
│   │   │   ├── analytics/            # Analytics
│   │   │   │   └── page.tsx
│   │   │   └── profile/              # User profile
│   │   │       └── page.tsx
│   │   │
│   │   ├── admin/                    # Admin-Only Routes
│   │   │   ├── layout.tsx            # Admin layout
│   │   │   ├── page.tsx              # Admin dashboard
│   │   │   ├── users/                # User management
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── destinations/         # Destination management
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── accommodations/       # Accommodation management
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   └── settings/             # System settings
│   │   │       └── page.tsx
│   │   │
│   │   ├── itinerary/                # Public Itinerary View
│   │   │   └── [id]/
│   │   │       └── page.tsx          # Public itinerary page
│   │   │
│   │   └── api/                      # API Routes (if needed)
│   │       └── health/
│   │           └── route.ts          # Health check
│   │
│   ├── components/                   # React Components
│   │   ├── ui/                       # shadcn/ui Components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   ├── form.tsx
│   │   │   ├── input.tsx
│   │   │   ├── label.tsx
│   │   │   ├── select.tsx
│   │   │   ├── table.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── toast.tsx
│   │   │   └── ... (other shadcn components)
│   │   │
│   │   ├── dashboard/                # Dashboard Components
│   │   │   ├── sidebar.tsx
│   │   │   ├── header.tsx
│   │   │   ├── stats-card.tsx
│   │   │   └── notification-bell.tsx
│   │   │
│   │   ├── itinerary/                # Itinerary Components
│   │   │   ├── itinerary-builder.tsx
│   │   │   ├── itinerary-item-form.tsx
│   │   │   ├── itinerary-preview.tsx
│   │   │   ├── destination-selector.tsx
│   │   │   └── pdf-viewer.tsx
│   │   │
│   │   └── shared/                   # Shared Components
│   │       ├── data-table.tsx
│   │       ├── file-upload.tsx
│   │       ├── date-picker.tsx
│   │       ├── loading-spinner.tsx
│   │       ├── error-boundary.tsx
│   │       └── page-header.tsx
│   │
│   ├── lib/                          # Library Code
│   │   ├── api/                      # API Client
│   │   │   ├── client.ts             # Axios client configuration
│   │   │   ├── auth.ts               # Auth API calls
│   │   │   ├── itineraries.ts        # Itinerary API calls
│   │   │   ├── packages.ts           # Package API calls
│   │   │   ├── destinations.ts       # Destination API calls
│   │   │   ├── notifications.ts      # Notification API calls
│   │   │   └── analytics.ts          # Analytics API calls
│   │   │
│   │   ├── hooks/                    # Custom React Hooks
│   │   │   ├── use-auth.ts           # Authentication hook
│   │   │   ├── use-itinerary.ts      # Itinerary operations
│   │   │   ├── use-toast.ts          # Toast notifications
│   │   │   ├── use-debounce.ts       # Debounce hook
│   │   │   └── use-local-storage.ts  # Local storage hook
│   │   │
│   │   └── utils/                    # Utility Functions
│   │       ├── cn.ts                 # Class name helper
│   │       ├── format.ts             # Formatting functions
│   │       ├── validators.ts         # Form validators
│   │       ├── constants.ts          # Frontend constants
│   │       └── types.ts              # TypeScript types
│   │
│   ├── public/                       # Static Assets
│   │   ├── images/
│   │   │   ├── logo.png
│   │   │   └── default-avatar.png
│   │   ├── fonts/                    # Custom fonts
│   │   └── favicon.ico
│   │
│   ├── styles/                       # Styles
│   │   └── globals.css               # Global CSS with Tailwind
│   │
│   ├── package.json                  # Node dependencies
│   ├── package-lock.json             # Dependency lock file
│   ├── next.config.js                # Next.js configuration
│   ├── tailwind.config.js            # Tailwind configuration
│   ├── tsconfig.json                 # TypeScript configuration
│   ├── postcss.config.js             # PostCSS configuration
│   ├── components.json               # shadcn/ui configuration
│   ├── Dockerfile                    # Frontend Docker configuration
│   ├── .env.local.example            # Environment variables template
│   ├── .gitignore                    # Git ignore rules
│   ├── .eslintrc.json                # ESLint configuration
│   └── .prettierrc                   # Prettier configuration
│
├── shared/                           # Shared Code
│   ├── types/                        # Shared TypeScript types
│   │   ├── index.ts
│   │   ├── user.ts
│   │   ├── itinerary.ts
│   │   └── api.ts
│   │
│   └── constants/                    # Shared constants
│       ├── index.ts
│       ├── roles.ts
│       └── permissions.ts
│
├── docker-compose.yml                # Multi-container Docker setup
├── .env.example                      # Root environment template
├── .gitignore                        # Root git ignore
├── README.md                         # Project documentation
└── PROJECT_STRUCTURE.md              # This file

```

## Key Directories Explained

### Backend (`/backend`)
- **app/api**: REST API endpoints organized by resource
- **app/core**: Core application logic (config, security, permissions)
- **app/db**: Database configuration and session management
- **app/models**: SQLAlchemy ORM models
- **app/schemas**: Pydantic schemas for validation and serialization
- **app/services**: Business logic separated from API layer
- **app/utils**: Helper functions and utilities
- **alembic**: Database migration management
- **tests**: Unit and integration tests

### Frontend (`/frontend`)
- **app**: Next.js 14 App Router structure
  - **auth**: Authentication pages (login, register, password reset)
  - **dashboard**: Protected routes for CS agents and admins
  - **admin**: Admin-only routes
  - **itinerary/[id]**: Public itinerary viewing
- **components**: Reusable React components
  - **ui**: shadcn/ui component library
  - **dashboard**: Dashboard-specific components
  - **itinerary**: Itinerary builder components
  - **shared**: Common components used throughout
- **lib**: Library code
  - **api**: API client with typed endpoints
  - **hooks**: Custom React hooks
  - **utils**: Utility functions and helpers
- **public**: Static assets (images, fonts, etc.)
- **styles**: Global CSS and Tailwind configuration

### Shared (`/shared`)
- **types**: TypeScript type definitions shared between frontend and backend
- **constants**: Constants and enums shared across the application

## Database Tables Overview

### Core Tables
1. **users** - User accounts with authentication
2. **roles** - User roles (Admin, CS Agent, Public)
3. **permissions** - Granular permissions
4. **role_permissions** - Many-to-many role-permission mapping

### Business Tables
5. **tour_packages** - Base tour package templates (~200)
6. **destinations** - Destination database (~1000)
7. **destination_cross_reference** - 2D destination mapping for auto-descriptions
8. **accommodations** - Accommodation database
9. **itineraries** - Customer itineraries
10. **itinerary_items** - Daily itinerary line items
11. **notifications** - User notifications
12. **analytics_events** - Analytics tracking
13. **payment_tracking** - Payment status (no processing)

## API Endpoint Structure

```
/api/v1
├── /auth
│   ├── POST /login
│   ├── POST /register
│   ├── POST /logout
│   ├── POST /refresh
│   └── POST /reset-password
├── /users
│   ├── GET /users
│   ├── GET /users/{id}
│   ├── POST /users
│   ├── PUT /users/{id}
│   └── DELETE /users/{id}
├── /itineraries
│   ├── GET /itineraries
│   ├── GET /itineraries/{id}
│   ├── POST /itineraries
│   ├── PUT /itineraries/{id}
│   ├── DELETE /itineraries/{id}
│   ├── GET /itineraries/{id}/pdf
│   ├── POST /itineraries/{id}/email
│   └── GET /itineraries/public/{token}
├── /packages
│   ├── GET /packages
│   ├── GET /packages/{id}
│   ├── POST /packages
│   ├── PUT /packages/{id}
│   └── DELETE /packages/{id}
├── /destinations
│   ├── GET /destinations
│   ├── GET /destinations/{id}
│   ├── GET /destinations/search
│   ├── GET /destinations/{from_id}/{to_id}
│   ├── POST /destinations
│   └── PUT /destinations/{id}
├── /accommodations
│   ├── GET /accommodations
│   ├── GET /accommodations/{id}
│   ├── POST /accommodations
│   └── PUT /accommodations/{id}
├── /notifications
│   ├── GET /notifications
│   ├── GET /notifications/{id}
│   ├── PUT /notifications/{id}/read
│   └── DELETE /notifications/{id}
├── /analytics
│   ├── GET /analytics/dashboard
│   ├── GET /analytics/itineraries
│   └── POST /analytics/events
└── /payments
    ├── GET /payments
    ├── GET /payments/{id}
    └── PUT /payments/{id}
```

## Frontend Route Structure

```
/
├── / (Home page)
├── /auth
│   ├── /login
│   ├── /register
│   ├── /forgot-password
│   └── /reset-password
├── /dashboard (Protected)
│   ├── /itineraries
│   │   ├── /new
│   │   └── /{id}
│   │       └── /edit
│   ├── /packages
│   │   └── /{id}
│   ├── /notifications
│   ├── /analytics
│   └── /profile
├── /admin (Admin Only)
│   ├── /users
│   │   └── /{id}
│   ├── /destinations
│   │   └── /{id}
│   ├── /accommodations
│   │   └── /{id}
│   └── /settings
└── /itinerary/{id} (Public View)
```
