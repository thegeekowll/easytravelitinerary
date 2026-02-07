from fastapi import APIRouter
from app.api.v1.endpoints import (
    users,
    auth,
    destinations,
    accommodations,
    accommodation_levels,
    base_tours,
    content,
    media,
    destination_combinations,
    itineraries,
    notifications,
    notifications,
    dashboard,
    public,
    inclusions,
    exclusions,
    tour_types,
    permissions,
    analytics
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(destinations.router)
api_router.include_router(accommodations.router)
api_router.include_router(accommodation_levels.router)
api_router.include_router(base_tours.router)
api_router.include_router(content.router)
api_router.include_router(media.router)
api_router.include_router(destination_combinations.router)
api_router.include_router(itineraries.router)
api_router.include_router(notifications.router)
api_router.include_router(dashboard.router)
api_router.include_router(public.router)
api_router.include_router(inclusions.router)
api_router.include_router(inclusions.router)
api_router.include_router(exclusions.router)
api_router.include_router(tour_types.router, prefix="/tour-types", tags=["tour-types"])
api_router.include_router(permissions.router)
api_router.include_router(analytics.router)
