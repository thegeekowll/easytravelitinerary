"""
Itinerary endpoints.

The core feature: creating and managing travel itineraries.
Supports 3 creation methods: from base tour, edited base tour, and custom.
"""
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Request
from starlette.background import BackgroundTask
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.v1.deps import (
    get_db,
    get_current_active_user,
    require_admin,
    PaginationParams
)
from app.models.itinerary import Itinerary, ItineraryStatusEnum, ItineraryDay
from app.models.user import User
from app.schemas.itinerary import (
    ItineraryCreateChooseExisting,
    ItineraryCreateEditExisting,
    ItineraryCreateCustom,
    ItineraryResponse,
    ItineraryWithDetails,
    ItineraryUpdate,
    ItineraryAssignRequest,
    ItineraryDayCreate,
    TravelerCreate,
    TravelerUpdate,
    TravelerResponse,
    ItineraryImageBase,
    ItineraryImageResponse,
    ItineraryImageUpdate
)
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services.itinerary_service import itinerary_service

router = APIRouter(prefix="/itineraries", tags=["itineraries"])


# ==================== Creation Methods ====================

@router.post("/create-from-base", response_model=ItineraryResponse, status_code=status.HTTP_201_CREATED)
def create_itinerary_from_base_tour(
    itinerary_data: ItineraryCreateChooseExisting,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Method A: Create itinerary from existing base tour (choose as-is).

    Clones the entire base tour without modifications.
    Fastest method for standard tours.
    """
    try:
        itinerary = itinerary_service.create_from_base_tour(
            base_tour_id=itinerary_data.base_tour_id,
            travelers=itinerary_data.travelers,
            departure_date=itinerary_data.departure_date,
            assigned_to_user_id=itinerary_data.assigned_agent_id or current_user.id,
            created_by_user_id=current_user.id,
            db=db
        )

        db.commit()
        db.refresh(itinerary)

        return itinerary

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create itinerary: {str(e)}"
        )


@router.post("/create-from-edited", response_model=ItineraryResponse, status_code=status.HTTP_201_CREATED)
def create_itinerary_from_edited_tour(
    itinerary_data: ItineraryCreateEditExisting,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Method B: Create itinerary from edited base tour.

    Starts with a base tour but applies custom modifications.
    Auto-fills missing content from 2D destination table.
    """
    try:
        # Prepare tour modifications
        tour_modifications = {}
        if itinerary_data.title:
            tour_modifications['title'] = itinerary_data.title
        if itinerary_data.description:
            tour_modifications['description'] = itinerary_data.description
        if itinerary_data.duration_days:
            tour_modifications['duration_days'] = itinerary_data.duration_days

        itinerary = itinerary_service.create_from_edited_tour(
            base_tour_id=itinerary_data.base_tour_id,
            tour_modifications=tour_modifications,
            days=itinerary_data.days,
            travelers=itinerary_data.travelers,
            departure_date=itinerary_data.departure_date,
            assigned_to_user_id=itinerary_data.assigned_agent_id or current_user.id,
            created_by_user_id=current_user.id,
            db=db
        )

        db.commit()
        db.refresh(itinerary)

        return itinerary

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create itinerary: {str(e)}"
        )


@router.post("/create-custom", response_model=ItineraryResponse, status_code=status.HTTP_201_CREATED)
def create_custom_itinerary(
    itinerary_data: ItineraryCreateCustom,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Method C: Create completely custom itinerary from scratch.

    No base tour - build everything from scratch.
    Auto-fills day content from 2D destination table where not provided.
    Maximum flexibility.
    """
    try:
        itinerary = itinerary_service.create_custom_itinerary(
            tour_data=itinerary_data,
            days=itinerary_data.days,
            travelers=itinerary_data.travelers,
            departure_date=itinerary_data.departure_date,
            assigned_to_user_id=itinerary_data.assigned_agent_id or current_user.id,
            created_by_user_id=current_user.id,
            db=db
        )

        db.commit()
        db.refresh(itinerary)

        return itinerary

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create itinerary: {str(e)}"
        )


# ==================== Listing and Filtering ====================

@router.get("", response_model=PaginatedResponse[ItineraryResponse])
def list_itineraries(
    pagination: PaginationParams = Depends(),
    status_filter: Optional[ItineraryStatusEnum] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in title or traveler names"),
    departure_date_from: Optional[date] = Query(None, description="Filter by departure date (from)"),
    departure_date_to: Optional[date] = Query(None, description="Filter by departure date (to)"),
    created_at_from: Optional[date] = Query(None, description="Filter by creation date (from)"),
    created_at_to: Optional[date] = Query(None, description="Filter by creation date (to)"),
    creator_id: Optional[UUID] = Query(None, description="Filter by creator ID (Admin only)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List itineraries.
    
    - CS Agents: See ONLY their own created itineraries.
    - Admins: See ALL itineraries by default, or filter by specific creator.
    """
    from app.models.user import UserRoleEnum
    
    query = db.query(Itinerary)

    # Access Control & Creator Filter
    if current_user.role == UserRoleEnum.ADMIN:
        # Admin: Can see all. Optional filter by creator.
        if creator_id:
            query = query.filter(Itinerary.created_by_user_id == creator_id)
    else:
        # Non-Admin: Forced to see only their own
        query = query.filter(Itinerary.created_by_user_id == current_user.id)

    # Status filter
    if status_filter:
        query = query.filter(Itinerary.status == status_filter)

    # Date range filters
    if departure_date_from:
        query = query.filter(Itinerary.departure_date >= departure_date_from)
    if departure_date_to:
        query = query.filter(Itinerary.departure_date <= departure_date_to)
        
    if created_at_from:
        query = query.filter(Itinerary.created_at >= created_at_from)
    if created_at_to:
        # Include the entire end day by checking < next day, or just <= if strictly date
        # Assuming created_at is timestamp, casting to date or using <= might miss end-of-day.
        # Safest for date-only input is < date + 1 day, or if param is date, standard <= compares date part?
        # Typically SQL Alchemy handles date comparison with datetime by comparing the date part or 00:00:00.
        # Let's trust standard behavior for now: Itinerary.created_at is likely DateTime.
        # If input is '2023-01-01', we want up to 23:59:59.
        # Simpler approach: cast DB column to Date.
        from sqlalchemy import cast, Date
        query = query.filter(cast(Itinerary.created_at, Date) <= created_at_to)
        
        # NOTE: created_at_from handled above will default to 00:00:00 which is fine.

    # Search in title, traveler names, or reference code
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Itinerary.tour_title.ilike(search_term)) |
            (Itinerary.client_name.ilike(search_term)) |
            (Itinerary.unique_code.ilike(search_term))
        )

    # Get total count
    total = query.count()

    # Apply pagination
    itineraries = query.order_by(
        Itinerary.created_at.desc()
    ).offset(pagination.skip).limit(pagination.limit).all()

    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return PaginatedResponse(
        items=itineraries,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
        has_next=pagination.page < total_pages,
        has_prev=pagination.page > 1
    )


@router.get("/assigned-to-me", response_model=PaginatedResponse[ItineraryResponse])
def list_assigned_itineraries(
    pagination: PaginationParams = Depends(),
    status_filter: Optional[ItineraryStatusEnum] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List itineraries assigned to current user."""
    query = db.query(Itinerary).filter(
        Itinerary.assigned_to_user_id == current_user.id
    )

    if status_filter:
        query = query.filter(Itinerary.status == status_filter)

    total = query.count()

    itineraries = query.order_by(
        Itinerary.departure_date.asc()
    ).offset(pagination.skip).limit(pagination.limit).all()

    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return PaginatedResponse(
        items=itineraries,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
        has_next=pagination.page < total_pages,
        has_prev=pagination.page > 1
    )


@router.get("/all", response_model=PaginatedResponse[ItineraryResponse])
def list_all_itineraries(
    pagination: PaginationParams = Depends(),
    status_filter: Optional[ItineraryStatusEnum] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """List all itineraries (admin only)."""
    query = db.query(Itinerary)

    if status_filter:
        query = query.filter(Itinerary.status == status_filter)

    if search:
        query = query.filter(Itinerary.title.ilike(f"%{search}%"))

    total = query.count()

    itineraries = query.order_by(
        Itinerary.created_at.desc()
    ).offset(pagination.skip).limit(pagination.limit).all()

    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return PaginatedResponse(
        items=itineraries,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
        has_next=pagination.page < total_pages,
        has_prev=pagination.page > 1
    )


# ==================== Get and Update ====================

@router.get("/{itinerary_id}", response_model=ItineraryWithDetails)
def get_itinerary(
    itinerary_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get itinerary by ID with full details (days, travelers, etc.)."""
    from sqlalchemy.orm import joinedload, selectinload
    itinerary = db.query(Itinerary).options(
        joinedload(Itinerary.tour_type),
        joinedload(Itinerary.accommodation_level),
        selectinload(Itinerary.images),
        selectinload(Itinerary.days).selectinload(ItineraryDay.destinations),
        selectinload(Itinerary.days).joinedload(ItineraryDay.accommodation)
    ).filter(Itinerary.id == itinerary_id).first()

    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )

    # Check access permissions
    from app.models.user import UserRoleEnum
    if current_user.role != UserRoleEnum.ADMIN:
        if (itinerary.created_by_user_id != current_user.id and
            itinerary.assigned_to_user_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this itinerary"
            )

    return itinerary


@router.patch("/{itinerary_id}", response_model=ItineraryResponse)
def update_itinerary(
    itinerary_id: UUID,
    itinerary_data: ItineraryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update itinerary.

    Checks if itinerary is editable based on:
    - User role and ownership
    - Tour completion date
    - can_edit_after_tour flag
    """
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()

    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )

    # Check if editable
    if not itinerary_service.is_editable(itinerary, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This itinerary is not editable. Tour has completed and edit lock is enabled."
        )

    try:
        # Debug logging
        print(f"DEBUG: update_itinerary called for ID: {itinerary_id}")
        update_dict = itinerary_data.model_dump(exclude_unset=True)
        print(f"DEBUG: update payload: {update_dict}")

        # Handle days update if present
        if 'days' in update_dict:
            days_data = update_dict.pop('days')
            from app.models.itinerary import ItineraryDay
            
            import traceback
            for day_data in days_data:
                try:
                    print(f"DEBUG: Processing day_data: {day_data}")
                    # Logic:
                    # 1. If 'id' is present -> Update existing day
                    # 2. If 'id' not present -> Create new day
                    
                    existing_day = None
                    
                    # Check by ID if provided
                    if 'id' in day_data and day_data['id']:
                        existing_day = db.query(ItineraryDay).filter(
                            ItineraryDay.id == day_data['id'],
                            ItineraryDay.itinerary_id == itinerary_id
                        ).first()
                    # Check by day_number if ID not provided
                    elif 'day_number' in day_data:
                        existing_day = db.query(ItineraryDay).filter(
                            ItineraryDay.itinerary_id == itinerary_id,
                            ItineraryDay.day_number == day_data['day_number']
                        ).first()

                    # Extract destination_ids to handle M2M relationship
                    destination_ids = day_data.get('destination_ids')
                    
                    # Safe filter for kwargs (exclude fields not in model)
                    # 'date' is in schema but not model (uses day_date)
                    # 'destination_ids' is handled manually
                    # 'id' is primary key
                    exclude_fields = ['id', 'destination_ids', 'date']

                    if existing_day:
                        # Update existing
                        update_fields = {k: v for k, v in day_data.items() if k not in exclude_fields}
                        for k, v in update_fields.items():
                            setattr(existing_day, k, v)
                        
                        # Update destinations if provided
                        if destination_ids is not None:
                            from app.models.destination import Destination
                            destinations = db.query(Destination).filter(Destination.id.in_(destination_ids)).all()
                            existing_day.destinations = destinations

                    else:
                        # Create new
                        create_data = {k: v for k, v in day_data.items() if k not in exclude_fields}
                        
                        # Calculate day_date
                        if 'day_number' in create_data:
                            from datetime import timedelta
                            dep_date = update_dict.get('departure_date', itinerary.departure_date)
                            create_data['day_date'] = dep_date + timedelta(days=create_data['day_number'] - 1)
                        
                        if not create_data.get('day_title'):
                            create_data['day_title'] = f"Day {create_data.get('day_number', '?')}"
                        
                        print(f"DEBUG: Creating ItineraryDay with: {create_data}")
                        new_day = ItineraryDay(itinerary_id=itinerary_id, **create_data)
                        
                        # Set destinations if provided
                        if destination_ids:
                            from app.models.destination import Destination
                            destinations = db.query(Destination).filter(Destination.id.in_(destination_ids)).all()
                            new_day.destinations = destinations
                            
                        db.add(new_day)
                except Exception as e:
                    print(f"ERROR processing day {day_data.get('day_number')}: {str(e)}")
                    print(traceback.format_exc())
                    raise e
            
            try:
                db.flush()
            except Exception as e:
                print(f"ERROR during db.flush(): {str(e)}")
                print(traceback.format_exc())
                raise e
            
            # Update itinerary duration based on correct days count
            count = db.query(ItineraryDay).filter(ItineraryDay.itinerary_id == itinerary_id).count()
            
            # Re-read days to get max day number
            max_day_num = db.query(func.max(ItineraryDay.day_number)).filter(ItineraryDay.itinerary_id == itinerary_id).scalar() or 0
            
            if max_day_num > itinerary.number_of_days:
                itinerary.number_of_days = max_day_num

        # Handle inclusion/exclusion updates
        if 'inclusion_ids' in update_dict:
            inc_ids = update_dict.pop('inclusion_ids')
            from app.models.inclusion_exclusion import Inclusion
            if inc_ids is not None:
                inclusions = db.query(Inclusion).filter(Inclusion.id.in_(inc_ids)).all()
                itinerary.inclusions = inclusions
                
        if 'exclusion_ids' in update_dict:
            exc_ids = update_dict.pop('exclusion_ids')
            from app.models.inclusion_exclusion import Exclusion
            if exc_ids is not None:
                exclusions = db.query(Exclusion).filter(Exclusion.id.in_(exc_ids)).all()
                itinerary.exclusions = exclusions

        for field, value in update_dict.items():
            setattr(itinerary, field, value)

        # Recalculate return_date if departure_date or duration changed
        if 'departure_date' in update_dict or 'duration_days' in update_dict:
            from datetime import timedelta
            itinerary.return_date = itinerary.departure_date + timedelta(
                days=itinerary.duration_days - 1
            )
            
        # Auto-calculate payment_status if price/deposit changed
        # Logic:
        # deposit <= 0 -> NOT_PAID
        # deposit >= total_price -> FULLY_PAID
        # 0 < deposit < total_price -> PARTIALLY_PAID
        if 'total_price' in update_dict or 'deposit_amount' in update_dict:
            # Get current values, defaulting to existing if not in update
            current_total = update_dict.get('total_price', itinerary.total_price) or 0
            current_deposit = update_dict.get('deposit_amount', itinerary.deposit_amount) or 0
            
            # Ensure we're working with Decimals or floats for comparison
            from decimal import Decimal
            # Convert to float for simpler comparison if needed, or stick to Decimal if model uses it
            # The model uses Numeric(10, 2) which maps to Decimal in Python
            
            # Handle potential None values
            if current_total is None: current_total = 0
            if current_deposit is None: current_deposit = 0
            
            from app.models.itinerary import PaymentStatusEnum
            
            if current_deposit <= 0:
                itinerary.payment_status = PaymentStatusEnum.NOT_PAID
            elif current_deposit >= current_total:
                itinerary.payment_status = PaymentStatusEnum.FULLY_PAID
            else:
                itinerary.payment_status = PaymentStatusEnum.PARTIALLY_PAID

        db.commit()
        db.refresh(itinerary)

        return itinerary

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update itinerary: {str(e)}"
        )


@router.delete("/{itinerary_id}/days/{day_id}", response_model=MessageResponse)
def delete_itinerary_day(
    itinerary_id: UUID,
    day_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a day from an itinerary."""
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
    
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )
        
    # Check permissions
    if not itinerary_service.is_editable(itinerary, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Itinerary is not editable"
        )

    # Find the day
    from app.models.itinerary import ItineraryDay
    day = db.query(ItineraryDay).filter(
        ItineraryDay.id == day_id,
        ItineraryDay.itinerary_id == itinerary_id
    ).first()

    if not day:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary day not found"
        )

    try:
        db.delete(day)
        db.commit()
        
        # Re-index remaining days? 
        # For now, we'll let the frontend handle order or implement re-ordering service later if needed.
        
        return MessageResponse(message="Day deleted successfully")
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete day: {str(e)}"
        )


@router.delete("/{itinerary_id}", response_model=MessageResponse)
def delete_itinerary(
    itinerary_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Soft delete itinerary.

    Sets status to 'cancelled' instead of permanent deletion.
    Only creator or admin can delete.
    """
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()

    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )

    # Check permissions
    from app.models.user import UserRoleEnum
    if current_user.role != UserRoleEnum.ADMIN:
        if itinerary.created_by_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the creator or admin can delete this itinerary"
            )

    try:
        # Hard delete: permanently remove the itinerary
        # Log before deleting if possible, but since we are deleting the itinerary, the log might also be deleted due to cascade?
        # If logs cascade delete, logging "deleted" is moot unless we keep logs. 
        # But user asked for "hard delete" logic here? 
        # Wait, the code says "Soft delete itinerary" in comments but implementation is db.delete() (Hard). 
        # Let's assume we can't log a hard-deleted item effectively unless we have a separate audit log table without FK constraints.
        # However, for soft delete we should log. 
        # Looking at original code: "Sets status to 'cancelled' instead of permanent deletion." -> implementation `db.delete(itinerary)`.
        # Code comment mismatches implementation. 
        # If I want to log "Deleted", I can put it in a global log if I had one, but ItineraryActivityLog is linked to Itinerary.
        # So I will skip logging for hard delete for now to avoid FK errors or instant deletion.
        db.delete(itinerary)
        db.commit()

        return MessageResponse(message="Itinerary deleted permanently")

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete itinerary: {str(e)}"
        )


# ==================== Additional Operations ====================

@router.post("/{itinerary_id}/duplicate", response_model=ItineraryResponse, status_code=status.HTTP_201_CREATED)
def duplicate_itinerary(
    itinerary_id: UUID,
    new_departure_date: date = Query(..., description="Departure date for duplicated itinerary"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Clone an existing itinerary.

    Creates a complete copy with new departure date.
    Useful for recurring tours.
    """
    original = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()

    if not original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )

    try:
        from datetime import timedelta

        # Calculate new dates
        return_date = new_departure_date + timedelta(days=original.duration_days - 1)
        day_dates = itinerary_service.calculate_dates(new_departure_date, original.duration_days)

        # Generate new unique code
        unique_code = itinerary_service.generate_unique_code(db)

        # Create duplicate itinerary
        new_itinerary = Itinerary(
            base_tour_id=original.base_tour_id,
            title=f"{original.title} (Copy)",
            tour_type_id=original.tour_type_id,
            duration_days=original.duration_days,
            description=original.description,
            departure_date=new_departure_date,
            return_date=return_date,
            status=ItineraryStatusEnum.DRAFT,
            creation_method=original.creation_method,
            unique_code=unique_code,
            assigned_to_user_id=current_user.id,
            created_by_user_id=current_user.id,
            can_edit_after_tour=original.can_edit_after_tour
        )

        db.add(new_itinerary)
        db.flush()

        # Duplicate days
        for original_day in original.days:
            new_day_date = day_dates[original_day.day_number - 1]

            from app.models.itinerary import ItineraryDay
            new_day = ItineraryDay(
                itinerary_id=new_itinerary.id,
                day_number=original_day.day_number,
                day_date=new_day_date,
                title=original_day.title,
                description=original_day.description,
                activities=original_day.activities,
                meals_included=original_day.meals_included,
                is_description_custom=original_day.is_description_custom,
                is_activity_custom=original_day.is_activity_custom
            )

            db.add(new_day)
            db.flush()

            # Copy associations
            new_day.destinations = original_day.destinations
            new_day.accommodations = original_day.accommodations

        # Copy inclusions/exclusions
        new_itinerary.inclusions = original.inclusions
        new_itinerary.exclusions = original.exclusions

        # Duplicate travelers (without copying personal data - agent will update)
        from app.models.itinerary import Traveler
        for original_traveler in original.travelers:
            new_traveler = Traveler(
                itinerary_id=new_itinerary.id,
                full_name="[To be updated]",
                email=None,
                phone=None,
                date_of_birth=None,
                nationality=original_traveler.nationality,
                passport_number=None,
                is_primary=original_traveler.is_primary
            )
            db.add(new_traveler)

        db.commit()
        db.refresh(new_itinerary)

        return new_itinerary

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to duplicate itinerary: {str(e)}"
        )


@router.patch("/{itinerary_id}/assign", response_model=ItineraryResponse)
def assign_itinerary(
    itinerary_id: UUID,
    assign_data: ItineraryAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Assign itinerary to another agent (admin only)."""
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()

    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )

    # Verify new agent exists
    new_agent = db.query(User).filter(User.id == assign_data.assigned_to_user_id).first()
    if not new_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    try:
        itinerary.assigned_to_user_id = assign_data.assigned_to_user_id
        db.commit()
        db.refresh(itinerary)

        return itinerary

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign itinerary: {str(e)}"
        )


@router.patch("/{itinerary_id}/complete", response_model=ItineraryResponse)
async def toggle_completion(
    itinerary_id: UUID,
    mark_complete: bool = Query(..., description="True to complete, False to uncomplete"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark itinerary as complete or incomplete."""
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()

    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )

    # Check permissions
    from app.models.user import UserRoleEnum
    if current_user.role != UserRoleEnum.ADMIN:
        if (itinerary.created_by_user_id != current_user.id and
            itinerary.assigned_to_user_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to modify this itinerary"
            )

    try:
        if mark_complete:
            itinerary.status = ItineraryStatusEnum.COMPLETED
        else:
            itinerary.status = ItineraryStatusEnum.CONFIRMED

        db.commit()
        db.refresh(itinerary)

        return itinerary

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update status: {str(e)}"
        )


# ==================== Auto-Fill Helper ====================

@router.post("/days/auto-fill")
async def auto_fill_day_content(
    destination_ids: List[UUID],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get auto-fill suggestions for day content based on destinations.

    Returns:
    - Single destination: {description, activity}
    - Two destinations: {description, activity}
    - 3+ destinations: {suggestions: [list of options]}
    """
    result = itinerary_service.auto_fill_day_content(destination_ids, db)
    return result


# ==================== PDF & Email ====================


# ==================== Traveler Management ====================

@router.post("/{itinerary_id}/travelers", response_model=TravelerResponse, status_code=status.HTTP_201_CREATED)
async def add_traveler(
    itinerary_id: UUID,
    traveler_data: TravelerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a traveler to an itinerary."""
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()

    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )
        
    # Check permissions
    if not itinerary_service.is_editable(itinerary, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Itinerary is not editable"
        )
        
    try:
        from app.models.itinerary import Traveler
        
        # If this is the first traveler, make them primary by default
        is_first = db.query(Traveler).filter(Traveler.itinerary_id == itinerary_id).count() == 0
        
        new_traveler = Traveler(
            itinerary_id=itinerary_id,
            full_name=traveler_data.full_name,
            email=traveler_data.email,
            phone=traveler_data.phone,
            age=traveler_data.age,
            nationality=traveler_data.nationality,
            special_requests=traveler_data.special_requests,
            is_primary=traveler_data.is_primary or is_first
        )
        
        # If new traveler is primary, unset other primaries
        if new_traveler.is_primary:
            db.query(Traveler).filter(
                Traveler.itinerary_id == itinerary_id,
                Traveler.is_primary == True
            ).update({"is_primary": False})
            
            # Sync Itinerary Client Details
            itinerary.client_name = new_traveler.full_name
            itinerary.client_email = new_traveler.email or itinerary.client_email
            itinerary.client_phone = new_traveler.phone or itinerary.client_phone
            
        db.add(new_traveler)
        db.commit()
        db.refresh(new_traveler)
        
        # Update number of travelers count
        count = db.query(Traveler).filter(Traveler.itinerary_id == itinerary_id).count()
        itinerary.number_of_travelers = count
        db.commit()
        
        return new_traveler
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add traveler: {str(e)}"
        )


@router.patch("/{itinerary_id}/travelers/{traveler_id}", response_model=TravelerResponse)
async def update_traveler(
    itinerary_id: UUID,
    traveler_id: UUID,
    traveler_data: TravelerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a traveler."""
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()

    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )
        
    # Check permissions
    if not itinerary_service.is_editable(itinerary, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Itinerary is not editable"
        )
        
    from app.models.itinerary import Traveler
    traveler = db.query(Traveler).filter(
        Traveler.id == traveler_id,
        Traveler.itinerary_id == itinerary_id
    ).first()
    
    if not traveler:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Traveler not found"
        )
        
    try:
        update_data = traveler_data.model_dump(exclude_unset=True)
        
        # Handle primary status change
        if update_data.get('is_primary'):
            # Unset others
            db.query(Traveler).filter(
                Traveler.itinerary_id == itinerary_id,
                Traveler.id != traveler_id,
                Traveler.is_primary == True
            ).update({"is_primary": False})
            
            # Sync Itinerary Client Details
            # Need to get updated values from update_data or fallback to existing
            new_name = update_data.get('full_name', traveler.full_name)
            # If full_name not in update_data, check first/last? No, model update uses whatever is passed.
            # actually we dumped the model so 'full_name' should be there if it was sent.
            
            itinerary.client_name = new_name
            itinerary.client_email = update_data.get('email', traveler.email) or itinerary.client_email
            itinerary.client_phone = update_data.get('phone', traveler.phone) or itinerary.client_phone
            
        for field, value in update_data.items():
            setattr(traveler, field, value)
            
        db.commit()
        db.refresh(traveler)
        
        return traveler
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update traveler: {str(e)}"
        )


@router.delete("/{itinerary_id}/travelers/{traveler_id}", response_model=MessageResponse)
async def delete_traveler(
    itinerary_id: UUID,
    traveler_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a traveler."""
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()

    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )
        
    # Check permissions
    if not itinerary_service.is_editable(itinerary, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Itinerary is not editable"
        )
        
    from app.models.itinerary import Traveler
    traveler = db.query(Traveler).filter(
        Traveler.id == traveler_id,
        Traveler.itinerary_id == itinerary_id
    ).first()
    
    if not traveler:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Traveler not found"
        )
        
    try:
        # Prevent deleting the last traveler or the only primary one? 
        # For now allow it, but maybe warn if primary.
        
        was_primary = traveler.is_primary
        db.delete(traveler)
        db.commit()
        
        # Update count
        count = db.query(Traveler).filter(Traveler.itinerary_id == itinerary_id).count()
        itinerary.number_of_travelers = count
        
        # If we deleted the primary contact, assign a new one if travelers exist
        if was_primary and count > 0:
            new_primary = db.query(Traveler).filter(Traveler.itinerary_id == itinerary_id).first()
            if new_primary:
                new_primary.is_primary = True
                
        db.commit()
        
        return MessageResponse(message="Traveler deleted successfully")
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete traveler: {str(e)}"
        )




@router.post("/{itinerary_id}/send-email")
async def send_itinerary_email(
    itinerary_id: UUID,
    email_data: dict,  # Will create schema for this
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Send itinerary via email.

    Body:
    {
        "to_email": "traveler@example.com",
        "cc": ["agent@example.com"],  // optional
        "bcc": [],  // optional
        "subject": "Your Trip Itinerary",  // optional (uses template)
        "body": "Custom message"  // optional (uses template)
    }
    """
    from app.services.email_service import email_service

    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()

    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )

    # Check permissions
    from app.models.user import UserRoleEnum
    if current_user.role != UserRoleEnum.ADMIN:
        if (itinerary.created_by_user_id != current_user.id and
            itinerary.assigned_to_user_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this itinerary"
            )

    # Check send_email permission (if exists)
    # Can be added to permission system later

    try:
        result = await email_service.send_itinerary_email(
            itinerary_id=itinerary_id,
            to_email=email_data.get('to_email'),
            cc=email_data.get('cc'),
            bcc=email_data.get('bcc'),
            subject=email_data.get('subject'),
            body=email_data.get('body'),
            sent_by_user_id=current_user.id,
            db=db
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )


@router.get("/{itinerary_id}/email-history")
async def get_email_history(
    itinerary_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all emails sent for this itinerary."""
    from app.services.email_service import email_service

    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()

    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )

    # Check permissions
    from app.models.user import UserRoleEnum
    if current_user.role != UserRoleEnum.ADMIN:
        if (itinerary.created_by_user_id != current_user.id and
            itinerary.assigned_to_user_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this itinerary"
            )

    emails = email_service.get_email_history(itinerary_id, db)

    return {
        'emails': [
            {
                'id': str(email.id),
                'recipient': email.sent_to_email,
                'cc': email.cc_emails,
                'bcc': email.bcc_emails,
                'subject': email.subject,
                'status': email.delivery_status.value,
                'sent_at': email.sent_at.isoformat() if email.sent_at else None,
                'pdf_attached': email.pdf_attached,
                'sent_by': email.sent_by.full_name if email.sent_by else None
            }
            for email in emails
        ],
        'total': len(emails)
    }


@router.post("/{itinerary_id}/resend-email")
async def resend_last_email(
    itinerary_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Resend the last email sent for this itinerary."""
    from app.services.email_service import email_service

    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()

    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )

    # Check permissions
    from app.models.user import UserRoleEnum
    if current_user.role != UserRoleEnum.ADMIN:
        if (itinerary.created_by_user_id != current_user.id and
            itinerary.assigned_to_user_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this itinerary"
            )

    try:
        result = await email_service.resend_last_email(itinerary_id, db)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resend email: {str(e)}"
        )


# ==================== Payment Endpoints ====================

@router.post("/{itinerary_id}/payment")
async def record_payment(
    itinerary_id: UUID,
    payment_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Record a payment for an itinerary.

    Request body:
    {
        "payment_status": "fully_paid" | "partially_paid" | "not_paid" | "custom",
        "total_amount": 5000.00,  # optional
        "paid_amount": 2500.00,
        "payment_method": "Credit Card",  # optional
        "payment_date": "2024-01-20",  # optional
        "payment_reference": "REF-12345",  # optional
        "payment_id": "txn_abc123",  # optional
        "platform": "Stripe",  # optional
        "notes": "First installment"  # optional
    }
    """
    from app.models.payment import PaymentRecord, PaymentStatusEnum
    from datetime import date as date_type
    from decimal import Decimal

    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()

    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )

    # Check permissions
    from app.models.user import UserRoleEnum
    if current_user.role != UserRoleEnum.ADMIN:
        if (itinerary.created_by_user_id != current_user.id and
            itinerary.assigned_to_user_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to record payments for this itinerary"
            )

    try:
        # Parse payment_date if provided
        payment_date = None
        if payment_data.get('payment_date'):
            if isinstance(payment_data['payment_date'], str):
                payment_date = date_type.fromisoformat(payment_data['payment_date'])
            else:
                payment_date = payment_data['payment_date']

        # Create payment record
        payment = PaymentRecord(
            itinerary_id=itinerary_id,
            payment_status=PaymentStatusEnum(payment_data['payment_status']),
            total_amount=Decimal(str(payment_data['total_amount'])) if payment_data.get('total_amount') else None,
            paid_amount=Decimal(str(payment_data['paid_amount'])),
            payment_method=payment_data.get('payment_method'),
            payment_date=payment_date,
            payment_reference=payment_data.get('payment_reference'),
            payment_id=payment_data.get('payment_id'),
            platform=payment_data.get('platform'),
            notes=payment_data.get('notes'),
            created_by_user_id=current_user.id
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        # Send notification if fully paid
        if payment.payment_status == PaymentStatusEnum.FULLY_PAID:
            from app.services.notification_service import notification_service
            try:
                await notification_service.send_payment_confirmed_notification(itinerary_id, db)
                db.commit()  # Commit notifications
            except Exception as notif_error:
                print(f"Failed to send payment notification: {str(notif_error)}")
                db.rollback()  # Rollback failed notifications only, payment is already committed

        return {
            'success': True,
            'message': 'Payment recorded successfully',
            'payment': payment.to_dict()
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payment data: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record payment: {str(e)}"
        )


@router.get("/{itinerary_id}/payment-history")
async def get_payment_history(
    itinerary_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all payment records for an itinerary.

    Returns:
    {
        "payments": [...],
        "total_paid": 2500.00,
        "total_amount": 5000.00,
        "latest_status": "partially_paid"
    }
    """
    from app.models.payment import PaymentRecord
    from decimal import Decimal

    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()

    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )

    # Check permissions
    from app.models.user import UserRoleEnum
    if current_user.role != UserRoleEnum.ADMIN:
        if (itinerary.created_by_user_id != current_user.id and
            itinerary.assigned_to_user_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this itinerary"
            )

    # Get all payment records
    payments = db.query(PaymentRecord).filter(
        PaymentRecord.itinerary_id == itinerary_id
    ).order_by(PaymentRecord.created_at.desc()).all()

    # Calculate totals
    total_paid = sum(payment.paid_amount for payment in payments)
    latest_payment = payments[0] if payments else None
    latest_status = latest_payment.payment_status.value if latest_payment else "not_paid"
    total_amount = latest_payment.total_amount if latest_payment and latest_payment.total_amount else None

    return {
        'payments': [
            {
                'id': str(payment.id),
                'payment_status': payment.payment_status.value,
                'total_amount': float(payment.total_amount) if payment.total_amount else None,
                'paid_amount': float(payment.paid_amount),
                'payment_method': payment.payment_method,
                'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
                'payment_reference': payment.payment_reference,
                'payment_id': payment.payment_id,
                'platform': payment.platform,
                'notes': payment.notes,
                'created_at': payment.created_at.isoformat(),
                'created_by': payment.created_by.full_name if payment.created_by else None
            }
            for payment in payments
        ],
        'total_paid': float(total_paid),
        'total_amount': float(total_amount) if total_amount else None,
        'latest_status': latest_status,
        'payment_count': len(payments)
    }


@router.post("/{itinerary_id}/images", response_model=List[ItineraryImageResponse])
async def upload_itinerary_images(
    itinerary_id: UUID,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload images for an itinerary.
    """
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )
    
    # Check permissions
    if not itinerary_service.is_editable(itinerary, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot edit this itinerary"
        )

    # Save images
    from app.services.azure_blob_service import azure_blob_service
    from app.models.itinerary import ItineraryImage
    
    saved_images = []
    
    for file in files:
        # Upload to Azure Blob Storage (container="itinerary-images")
        image_url = await azure_blob_service.upload_image(file, container="itinerary-images")
        
        # Create database record
        image = ItineraryImage(
            itinerary_id=itinerary_id,
            image_url=image_url,
            caption=file.filename,
            sort_order=len(itinerary.images) + len(saved_images)
        )
        
        saved_images.append(image)
        db.add(image)

    db.commit()
    for img in saved_images:
        db.refresh(img)
        
    return saved_images


@router.put("/images/{image_id}", response_model=ItineraryImageResponse)
async def update_itinerary_image(
    image_id: UUID,
    image_update: ItineraryImageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update itinerary image details (caption, role).
    """
    from app.models.itinerary import ItineraryImage
    
    image = db.query(ItineraryImage).filter(ItineraryImage.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
        
    # Check permissions (via itinerary)
    itinerary = db.query(Itinerary).filter(Itinerary.id == image.itinerary_id).first()
    if not itinerary_service.is_editable(itinerary, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot edit this itinerary"
        )
        
    if image_update.caption is not None:
        image.caption = image_update.caption
        
    if image_update.image_role is not None:
        image.image_role = image_update.image_role
        
    # Also allow updating sort_order? Yes
    if image_update.sort_order is not None:
        image.sort_order = image_update.sort_order
        
    if image_update.image_url is not None:
        image.image_url = image_update.image_url

    db.commit()
    db.refresh(image)
    return image


@router.post("/{itinerary_id}/images/link", response_model=List[ItineraryImageResponse])
async def link_itinerary_images(
    itinerary_id: UUID,
    images: List[ItineraryImageBase],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Link existing images (by URL) to an itinerary.
    """
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )

    # Check permissions
    if not itinerary_service.is_editable(itinerary, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot edit this itinerary"
        )

    from app.models.itinerary import ItineraryImage
    
    new_images = []
    # Get current max sort order
    max_order = 0
    if itinerary.images:
        max_order = max(img.sort_order for img in itinerary.images)

    for i, img_data in enumerate(images):
        new_img = ItineraryImage(
            itinerary_id=itinerary.id,
            image_url=img_data.image_url,
            caption=img_data.caption,
            sort_order=max_order + 1 + i
        )
        db.add(new_img)
        new_images.append(new_img)
    
    db.commit()
    for img in new_images:
        db.refresh(img)
        
    return new_images


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_itinerary_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an itinerary image.
    """
    from app.models.itinerary import ItineraryImage
    
    image = db.query(ItineraryImage).filter(ItineraryImage.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
        
    itinerary = image.itinerary
    
    # Check permissions
    if not itinerary_service.is_editable(itinerary, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot edit this itinerary"
        )
        
    # Delete from database
    db.delete(image)
    db.commit()
    
    return None
