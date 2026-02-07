# Travel Agency Management System

A comprehensive travel agency management platform built with FastAPI, Next.js 14, PostgreSQL, and Azure services. This system supports itinerary creation, tour package management, PDF generation, and role-based access control.

## Features

### Core Functionality
- **Role-Based Authentication**: Admin, CS Agent, and Public roles with granular permissions
- **Tour Package Management**: 200+ base tour packages database
- **Destination Database**: ~1000 destinations with cross-reference support
- **Accommodation Management**: Comprehensive accommodation database
- **Itinerary Builder**: 3 creation methods (template-based, custom, quick-create)
- **PDF Generation**: 8-page professional itinerary PDFs using Puppeteer
- **Public Web Links**: Shareable public itinerary views
- **Email Delivery**: SendGrid integration for automated emails
- **Notification System**: Automated alerts including 3-day advance arrival notifications
- **Analytics Dashboard**: Comprehensive analytics and reporting
- **Payment Tracking**: Track payment status (no processing)

### Technical Features
- **2D Destination Cross-Reference**: Auto-fill descriptions based on destination pairs
- **File Storage**: Azure Blob Storage integration
- **Async Task Processing**: Celery for background jobs
- **Caching**: Redis for performance optimization
- **Database Migrations**: Alembic for database versioning
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Type Safety**: Full TypeScript support on frontend
- **Responsive UI**: Tailwind CSS with shadcn/ui components

## Technology Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Task Queue**: Celery + Redis
- **Email**: SendGrid
- **Storage**: Azure Blob Storage
- **PDF**: WeasyPrint + ReportLab
- **Authentication**: JWT with python-jose

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (Radix UI)
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Forms**: React Hook Form + Zod
- **Tables**: TanStack Table
- **Charts**: Recharts

### Infrastructure
- **Deployment**: Microsoft Azure
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx (optional)
- **CI/CD**: GitHub Actions (recommended)

## Project Structure

```
.
├── backend/                  # FastAPI backend application
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/    # API route handlers
│   │   │       └── deps.py       # Dependency injection
│   │   ├── core/
│   │   │   ├── config.py         # Application settings
│   │   │   └── security.py       # Auth & security
│   │   ├── db/
│   │   │   ├── base.py           # Database models registry
│   │   │   └── session.py        # Database session
│   │   ├── models/               # SQLAlchemy models
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── services/             # Business logic
│   │   └── utils/                # Utility functions
│   ├── alembic/                  # Database migrations
│   ├── tests/                    # Backend tests
│   ├── main.py                   # Application entry point
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Backend container
│   └── .env.example              # Environment template
│
├── frontend/                 # Next.js frontend application
│   ├── app/
│   │   ├── dashboard/            # Protected dashboard routes
│   │   ├── admin/                # Admin-only routes
│   │   ├── auth/                 # Authentication pages
│   │   ├── itinerary/[id]/       # Public itinerary view
│   │   ├── layout.tsx            # Root layout
│   │   └── page.tsx              # Home page
│   ├── components/
│   │   ├── ui/                   # shadcn/ui components
│   │   ├── dashboard/            # Dashboard components
│   │   ├── itinerary/            # Itinerary components
│   │   └── shared/               # Shared components
│   ├── lib/
│   │   ├── api/                  # API client
│   │   ├── utils/                # Utility functions
│   │   └── hooks/                # Custom React hooks
│   ├── public/                   # Static assets
│   ├── styles/                   # Global styles
│   ├── package.json              # Node dependencies
│   ├── Dockerfile                # Frontend container
│   └── .env.local.example        # Environment template
│
├── shared/                   # Shared types/constants
│   ├── types/                    # TypeScript types
│   └── constants/                # Shared constants
│
├── docker-compose.yml        # Multi-container setup
├── .env.example              # Root environment template
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## Getting Started

### Prerequisites

- **Docker & Docker Compose**: Latest version
- **Node.js**: 20.x or higher (for local development)
- **Python**: 3.11 or higher (for local development)
- **PostgreSQL**: 16 (if running locally)
- **Redis**: 7.x (if running locally)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Itinerary Builder Platform"
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   cp backend/.env.example backend/.env
   cp frontend/.env.local.example frontend/.env.local
   ```

3. **Update environment variables**
   Edit the `.env` files with your actual credentials:
   - Database credentials
   - SendGrid API key
   - Azure Storage connection string
   - JWT secret keys

4. **Build and start services**
   ```bash
   docker-compose up -d
   ```

5. **Run database migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

6. **Create initial admin user**
   ```bash
   docker-compose exec backend python -m app.scripts.create_admin
   ```

7. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development Setup

#### Backend Setup

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start PostgreSQL and Redis**
   ```bash
   docker-compose up -d postgres redis
   ```

5. **Run migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start development server**
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Set up environment variables**
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

## Database Schema Overview

### Core Tables
- **users**: User accounts with role-based access
- **permissions**: Granular permission system
- **role_permissions**: Role-permission mappings
- **tour_packages**: Base tour package templates (200+)
- **destinations**: Destination database (~1000)
- **destination_cross_reference**: 2D destination mapping for auto-descriptions
- **accommodations**: Accommodation database
- **itineraries**: Customer itineraries
- **itinerary_items**: Daily itinerary items
- **notifications**: User notifications
- **analytics_events**: Analytics tracking
- **payment_tracking**: Payment status tracking

## API Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Key API Endpoints

#### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout

#### Itineraries
- `GET /api/v1/itineraries` - List itineraries
- `POST /api/v1/itineraries` - Create itinerary
- `GET /api/v1/itineraries/{id}` - Get itinerary details
- `PUT /api/v1/itineraries/{id}` - Update itinerary
- `DELETE /api/v1/itineraries/{id}` - Delete itinerary
- `GET /api/v1/itineraries/{id}/pdf` - Generate PDF
- `GET /api/v1/itineraries/public/{token}` - Public view

#### Tour Packages
- `GET /api/v1/packages` - List packages
- `POST /api/v1/packages` - Create package
- `GET /api/v1/packages/{id}` - Get package details

#### Destinations
- `GET /api/v1/destinations` - List destinations
- `GET /api/v1/destinations/search` - Search destinations
- `GET /api/v1/destinations/{id}/cross-reference` - Get destination pairs

## Development

### Running Tests

**Backend Tests**
```bash
cd backend
pytest
pytest --cov=app tests/  # With coverage
```

**Frontend Tests**
```bash
cd frontend
npm test
npm run test:watch  # Watch mode
```

### Code Quality

**Backend**
```bash
# Format code
black app/
isort app/

# Lint
flake8 app/
mypy app/
```

**Frontend**
```bash
# Format code
npm run format

# Lint
npm run lint

# Type check
npm run type-check
```

### Database Migrations

**Create a new migration**
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

**Apply migrations**
```bash
alembic upgrade head
```

**Rollback migration**
```bash
alembic downgrade -1
```

## Deployment

### Azure Deployment

1. **Create Azure Resources**
   - App Service for backend
   - Static Web App for frontend
   - PostgreSQL Flexible Server
   - Redis Cache
   - Blob Storage
   - Application Insights (optional)

2. **Configure Environment Variables**
   Set all required environment variables in Azure App Service Configuration

3. **Deploy Backend**
   ```bash
   az webapp up --name your-backend-app --resource-group your-rg
   ```

4. **Deploy Frontend**
   ```bash
   cd frontend
   npm run build
   # Deploy to Azure Static Web Apps
   ```

5. **Run Migrations**
   ```bash
   az webapp ssh --name your-backend-app
   alembic upgrade head
   ```

### Docker Production Deployment

```bash
# Build for production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Or use specific profile
docker-compose --profile production up -d
```

## Environment Variables

See the following files for all available environment variables:
- Root: `.env.example`
- Backend: `backend/.env.example`
- Frontend: `frontend/.env.local.example`

### Critical Variables to Configure

**Backend**
- `SECRET_KEY`: Application secret key
- `DATABASE_URL`: PostgreSQL connection string
- `SENDGRID_API_KEY`: SendGrid API key
- `AZURE_STORAGE_CONNECTION_STRING`: Azure Storage connection

**Frontend**
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_APP_URL`: Frontend application URL

## Security Considerations

- All passwords are hashed using bcrypt
- JWT tokens for authentication
- CORS configured for allowed origins
- SQL injection prevention via SQLAlchemy ORM
- XSS protection in frontend
- CSRF protection enabled
- Rate limiting on API endpoints
- Input validation with Pydantic
- File upload size limits
- Secure headers configuration

## Monitoring and Logging

- Application logs stored in `backend/logs/`
- Structured logging with Loguru
- Health check endpoints: `/health`
- Database connection pooling monitoring
- Redis connection monitoring
- Celery task monitoring

## Troubleshooting

### Common Issues

**Database Connection Errors**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres
```

**Migration Issues**
```bash
# Reset database (development only!)
alembic downgrade base
alembic upgrade head
```

**Frontend Build Errors**
```bash
# Clear cache and reinstall
rm -rf node_modules .next
npm install
npm run build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## License

[Your License Here]

## Support

For support, email support@youragency.com or open an issue in the repository.

## Acknowledgments

- FastAPI framework
- Next.js team
- shadcn/ui components
- All open-source contributors
