"""
Base Tour Package management endpoints.

Handles CRUD operations for tour templates with nested days.
"""
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_db,
    get_current_active_user,
    require_admin,
    PaginationParams,
    require_permission
)

from app.models.base_tour import BaseTour, BaseTourDay, TourType, BaseTourImage
from app.models.accommodation import AccommodationLevel
from app.models.user import User
from app.schemas.base_tour import (
    BaseTourCreate,
    BaseTourUpdate,
    BaseTourResponse,
    BaseTourWithDetails,
    TourTypeCreate,
    TourTypeResponse,
    BaseTourDayCreate,
    BaseTourDayCreate,
    BaseTourImageResponse,
    BaseTourImageUpdate,
    BaseTourImageLink
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.azure_blob_service import azure_blob_service
from app.services.import_export_service import ImportExportService
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/base-tours", tags=["base-tours"])


# ==================== Tour Types ====================

@router.get("/types", response_model=List[TourTypeResponse])
async def list_tour_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all tour types."""
    types = db.query(TourType).all()
    return types


@router.post("/types", response_model=TourTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_tour_type(
    type_data: TourTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new tour type (admin only)."""
    existing = db.query(TourType).filter(TourType.name == type_data.name).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tour type already exists"
        )

    tour_type = TourType(**type_data.model_dump())
    db.add(tour_type)
    db.commit()
    db.refresh(tour_type)

    return tour_type


# ==================== Base Tours ====================

@router.get("", response_model=PaginatedResponse[BaseTourResponse])
async def list_base_tours(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(None, description="Search by title"),
    tour_type_id: Optional[UUID] = Query(None, description="Filter by tour type"),
    min_days: Optional[int] = Query(None, ge=1, description="Minimum duration"),
    max_days: Optional[int] = Query(None, ge=1, description="Maximum duration"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all base tours with pagination and filtering."""
    query = db.query(BaseTour)

    # Search by title
    if search:
        query = query.filter(BaseTour.tour_name.ilike(f"%{search}%"))

    # Filter by tour type
    if tour_type_id:
        query = query.filter(BaseTour.tour_type_id == tour_type_id)

    # Filter by duration
    if min_days:
        query = query.filter(BaseTour.number_of_days >= min_days)
    if max_days:
        query = query.filter(BaseTour.number_of_days <= max_days)

    # Filter by active status
    if is_active is not None:
        query = query.filter(BaseTour.is_active == is_active)

    # Get total count
    total = query.count()

    # Apply pagination
    tours = query.offset(pagination.skip).limit(pagination.limit).all()

    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return PaginatedResponse(
        items=tours,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
        has_next=pagination.page < total_pages,
        has_prev=pagination.page > 1
    )


@router.get("/{tour_id}", response_model=BaseTourWithDetails)
async def get_base_tour(
    tour_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get base tour by ID with all nested data."""
    tour = db.query(BaseTour).filter(BaseTour.id == tour_id).first()

    if not tour:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Base tour not found"
        )

    return tour


@router.post("", response_model=BaseTourResponse, status_code=status.HTTP_201_CREATED)
async def create_base_tour(
    tour_data: BaseTourCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new base tour (admin only).

    Note: Days should be added separately using POST /base-tours/{id}/days
    """
    # Verify tour type exists
    tour_type = db.query(TourType).filter(
        TourType.id == tour_data.tour_type_id
    ).first()

    if not tour_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tour type not found"
        )

    # Verify accommodation level exists if provided
    if tour_data.accommodation_level_id:
        acc_level = db.query(AccommodationLevel).filter(
            AccommodationLevel.id == tour_data.accommodation_level_id
        ).first()

        if not acc_level:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Accommodation level not found"
            )

    # Create tour
    tour = BaseTour(**tour_data.model_dump(exclude={"days", "inclusion_ids", "exclusion_ids"}))
    db.add(tour)
    db.flush()  # Get ID

    # Add Days
    for day_data in tour_data.days:
        day = BaseTourDay(
            base_tour_id=tour.id,
            day_number=day_data.day_number,
            day_title=day_data.day_title,
            description=day_data.description,
            activities=day_data.activities,
            accommodation_id=day_data.accommodation_id
        )
        db.add(day)
        db.flush() # Get Day ID

        # Add destinations for day
        if day_data.destination_ids:
            from app.models.destination import Destination
            destinations = db.query(Destination).filter(Destination.id.in_(day_data.destination_ids)).all()
            day.destinations = destinations

    # Add Inclusions
    if tour_data.inclusion_ids:
        from app.models.inclusion_exclusion import Inclusion
        inclusions = db.query(Inclusion).filter(Inclusion.id.in_(tour_data.inclusion_ids)).all()
        tour.inclusions = inclusions

    # Add Exclusions
    if tour_data.exclusion_ids:
        from app.models.inclusion_exclusion import Exclusion
        exclusions = db.query(Exclusion).filter(Exclusion.id.in_(tour_data.exclusion_ids)).all()
        tour.exclusions = exclusions

    db.commit()
    db.refresh(tour)

    return tour


@router.patch("/{tour_id}", response_model=BaseTourResponse)
async def update_base_tour(
    tour_id: UUID,
    tour_data: BaseTourUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update base tour (admin only)."""
    tour = db.query(BaseTour).filter(BaseTour.id == tour_id).first()

    if not tour:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Base tour not found"
        )

    # Update fields
    # Update fields
    update_dict = tour_data.model_dump(exclude_unset=True)
    
    # Handle nested fields separately
    days_data = update_dict.pop("days", None)
    inclusion_ids = update_dict.pop("inclusion_ids", None)
    exclusion_ids = update_dict.pop("exclusion_ids", None)

    for field, value in update_dict.items():
        setattr(tour, field, value)

    # Update Days: Replace Strategy
    if days_data is not None:
        # Delete existing days
        for day in tour.days:
            db.delete(day)
        
        # Create new days
        for day_data in days_data:
            day = BaseTourDay(
                base_tour_id=tour.id,
                day_number=day_data["day_number"],
                day_title=day_data["day_title"],
                description=day_data.get("description"),
                activities=day_data.get("activities"),

                accommodation_id=day_data.get("accommodation_id")
            )
            db.add(day)
            db.flush()

            # Add destinations
            if "destination_ids" in day_data and day_data["destination_ids"]:
                from app.models.destination import Destination
                destinations = db.query(Destination).filter(Destination.id.in_(day_data["destination_ids"])).all()
                day.destinations = destinations

    # Update Inclusions
    if inclusion_ids is not None:
        from app.models.inclusion_exclusion import Inclusion
        inclusions = db.query(Inclusion).filter(Inclusion.id.in_(inclusion_ids)).all()
        tour.inclusions = inclusions

    # Update Exclusions
    if exclusion_ids is not None:
        from app.models.inclusion_exclusion import Exclusion
        exclusions = db.query(Exclusion).filter(Exclusion.id.in_(exclusion_ids)).all()
        tour.exclusions = exclusions

    db.commit()
    db.refresh(tour)

    return tour


@router.delete("/{tour_id}", response_model=MessageResponse)
async def delete_base_tour(
    tour_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete base tour (admin only)."""
    tour = db.query(BaseTour).filter(BaseTour.id == tour_id).first()

    if not tour:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Base tour not found"
        )

    try:
        # Delete tour (cascade will handle days and images)
        db.delete(tour)
        db.commit()

        return MessageResponse(message="Base tour deleted successfully")

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete base tour: {str(e)}"
        )


@router.post("/{tour_id}/duplicate", response_model=BaseTourResponse)
async def duplicate_base_tour(
    tour_id: UUID,
    new_title: str = Query(..., description="Title for the duplicated tour"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Clone an existing base tour (admin only).

    Creates a complete copy including all days and their destinations.
    """
    original = db.query(BaseTour).filter(BaseTour.id == tour_id).first()

    if not original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Base tour not found"
        )

    try:
        # Create new tour
        new_tour = BaseTour(
            tour_name=new_title,
            tour_type_id=original.tour_type_id,
            number_of_days=original.number_of_days,
            number_of_nights=original.number_of_nights,
            description=original.description,
            highlights=original.highlights,
            difficulty_level=original.difficulty_level,
            is_active=False  # Start as inactive
        )

        db.add(new_tour)
        db.flush()  # Get new tour ID

        # Duplicate days
        for original_day in original.days:
            new_day = BaseTourDay(
                base_tour_id=new_tour.id,
                day_number=original_day.day_number,
                day_title=original_day.day_title,
                description=original_day.description,
                activities=original_day.activities,
                meals_included=original_day.meals_included,
                accommodation_id=original_day.accommodation_id
            )
            db.add(new_day)
            db.flush()

            # Copy destination associations
            new_day.destinations = original_day.destinations

        db.commit()
        db.refresh(new_tour)

        return new_tour

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to duplicate tour: {str(e)}"
        )


@router.post("/{tour_id}/images", response_model=List[BaseTourImageResponse])
async def upload_tour_images(
    tour_id: UUID,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Upload multiple images for a base tour."""
    tour = db.query(BaseTour).filter(BaseTour.id == tour_id).first()

    if not tour:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Base tour not found"
        )

    uploaded_images = []

    try:
        for idx, file in enumerate(files):
            # Upload to Azure
            image_url = await azure_blob_service.upload_image(
                file,
                container="tours",
                folder=str(tour_id)
            )

            # Create image record
            image = BaseTourImage(
                base_tour_id=tour_id,
                image_url=image_url,
                caption=f"Image {idx + 1}",
                sort_order=len(tour.images) + idx
            )

            db.add(image)
            uploaded_images.append(image)

        db.commit()

        for image in uploaded_images:
            db.refresh(image)

        return uploaded_images

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload images: {str(e)}"
        )


@router.post("/{tour_id}/images/link", response_model=List[BaseTourImageResponse])
async def link_tour_images(
    tour_id: UUID,
    images: List[BaseTourImageLink],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Link existing images (by URL) to a base tour."""
    tour = db.query(BaseTour).filter(BaseTour.id == tour_id).first()

    if not tour:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Base tour not found"
        )

    linked_images = []

    try:
        current_count = len(tour.images)
        
        for idx, img_data in enumerate(images):
            # Create image record
            image = BaseTourImage(
                base_tour_id=tour_id,
                image_url=img_data.image_url,
                caption=img_data.caption or f"Linked Image {idx + 1}",
                image_role=img_data.image_role,
                sort_order=current_count + idx
            )

            db.add(image)
            linked_images.append(image)

        db.commit()

        for image in linked_images:
            db.refresh(image)

        return linked_images

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to link images: {str(e)}"
        )


@router.delete("/images/{image_id}", status_code=status.HTTP_200_OK)
async def delete_tour_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a base tour image."""
    image = db.query(BaseTourImage).filter(BaseTourImage.id == image_id).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Optional: Delete from Azure Blob Storage here if implemented
    # await azure_blob_service.delete_blob(image.image_url)

    db.delete(image)
    db.commit()
    
    return {"message": "Image deleted successfully"}


@router.put("/images/{image_id}", response_model=BaseTourImageResponse)
async def update_tour_image(
    image_id: UUID,
    image_update: BaseTourImageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update a base tour image (caption, role, etc.).
    """
    image = db.query(BaseTourImage).filter(BaseTourImage.id == image_id).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
        
    update_data = image_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(image, field, value)
        
    db.commit()
    db.refresh(image)
    
    return image

@router.get("/export/csv")
def export_base_tours_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Export all base tours to CSV format."""
    items = db.query(BaseTour).all()
    output = ImportExportService.export_to_csv(items, exclude_fields=['id'])
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=base_tours.csv"}
    )

@router.post("/bulk-import", response_model=dict)
def bulk_import_base_tours(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Bulk import base tours from CSV file. Matches on tour_name."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )

    try:
        content = file.file.read()
        csv_str = content.decode('utf-8')
        rows = ImportExportService.parse_csv(csv_str)

        imported = []
        failed = []

        for row_num, row in enumerate(rows, start=2):
            try:
                name = row.get('tour_name')
                type_id = row.get('tour_type_id')

                if not name or not type_id:
                    failed.append({'row': row_num, 'error': 'Missing required fields (tour_name, tour_type_id)'})
                    continue
                
                existing = db.query(BaseTour).filter(BaseTour.tour_name == name).first()
                if existing:
                    # Update Fields
                    for k, v in row.items():
                        if hasattr(existing, k) and k not in ['id', 'created_at', 'updated_at']:
                            setattr(existing, k, v)
                    imported.append(name)
                else:
                    # Create
                    new_item = BaseTour()
                    for k, v in row.items():
                        if hasattr(new_item, k) and k not in ['id', 'created_at', 'updated_at']:
                            setattr(new_item, k, v)
                    db.add(new_item)
                    imported.append(name)
            except Exception as e:
                failed.append({'row': row_num, 'error': str(e)})

        db.commit()
        return {
            'success': True,
            'imported_count': len(imported),
            'failed_count': len(failed),
            'imported': imported,
            'failed': failed
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

