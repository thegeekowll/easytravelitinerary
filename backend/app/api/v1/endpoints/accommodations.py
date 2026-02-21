"""
Accommodation management endpoints.

Handles CRUD operations for accommodations, types, and images.
"""
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_db,
    get_current_active_user,
    require_admin,
    PaginationParams,
    require_permission
)
from app.models.accommodation import Accommodation, AccommodationType, AccommodationImage
from app.models.user import User
from app.schemas.accommodation import (
    AccommodationCreate,
    AccommodationUpdate,
    AccommodationResponse,
    AccommodationWithDetails,
    AccommodationTypeCreate,
    AccommodationTypeResponse,
    AccommodationImageResponse
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.azure_blob_service import azure_blob_service
from app.services.import_export_service import ImportExportService
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/accommodations", tags=["accommodations"])


# ==================== Accommodation Types ====================

@router.get("/types", response_model=List[AccommodationTypeResponse])
async def list_accommodation_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all accommodation types."""
    types = db.query(AccommodationType).all()
    return types


@router.post("/types", response_model=AccommodationTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_accommodation_type(
    type_data: AccommodationTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new accommodation type (admin only)."""
    # Check if type already exists
    existing = db.query(AccommodationType).filter(
        AccommodationType.name == type_data.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Accommodation type already exists"
        )

    acc_type = AccommodationType(**type_data.model_dump())
    db.add(acc_type)
    db.commit()
    db.refresh(acc_type)

    return acc_type


# ==================== Accommodations ====================

@router.get("", response_model=PaginatedResponse[AccommodationResponse])
async def list_accommodations(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(None, description="Search by name"),
    destination_id: Optional[UUID] = Query(None, description="Filter by destination"),
    accommodation_type_id: Optional[UUID] = Query(None, description="Filter by type"),
    level_id: Optional[UUID] = Query(None, description="Filter by level"),
    min_star_rating: Optional[Decimal] = Query(None, ge=0, le=5, description="Minimum star rating"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all accommodations with pagination and filtering."""
    query = db.query(Accommodation)

    # Search by name
    if search:
        query = query.filter(Accommodation.name.ilike(f"%{search}%"))

    # Filter by destination
    if destination_id:
        query = query.filter(Accommodation.location_destination_id == destination_id)

    # Filter by type
    if accommodation_type_id:
        query = query.filter(Accommodation.type_id == accommodation_type_id)

    # Filter by level
    if level_id:
        query = query.filter(Accommodation.level_id == level_id)

    # Filter by star rating
    if min_star_rating is not None:
        query = query.filter(Accommodation.star_rating >= min_star_rating)

    # Get total count
    total = query.count()

    # Apply pagination
    accommodations = query.offset(pagination.skip).limit(pagination.limit).all()

    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return PaginatedResponse(
        items=accommodations,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
        has_next=pagination.page < total_pages,
        has_prev=pagination.page > 1
    )


@router.get("/{accommodation_id}", response_model=AccommodationWithDetails)
async def get_accommodation(
    accommodation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get accommodation by ID with all details."""
    accommodation = db.query(Accommodation).filter(
        Accommodation.id == accommodation_id
    ).first()

    if not accommodation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accommodation not found"
        )

    return accommodation


@router.post("", response_model=AccommodationResponse, status_code=status.HTTP_201_CREATED)
async def create_accommodation(
    accommodation_data: AccommodationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("create_accommodation"))
):
    """Create a new accommodation."""
    # Verify destination exists
    from app.models.destination import Destination
    destination = db.query(Destination).filter(
        Destination.id == accommodation_data.location_destination_id
    ).first()

    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )

    # Verify accommodation type exists
    acc_type = db.query(AccommodationType).filter(
        AccommodationType.id == accommodation_data.type_id
    ).first()

    if not acc_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accommodation type not found"
        )

    # Verify accommodation level exists if provided
    if accommodation_data.level_id:
        from app.models.accommodation import AccommodationLevel
        acc_level = db.query(AccommodationLevel).filter(
            AccommodationLevel.id == accommodation_data.level_id
        ).first()

        if not acc_level:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Accommodation level not found"
            )

    # Create accommodation
    accommodation = Accommodation(**accommodation_data.model_dump())
    db.add(accommodation)
    db.commit()
    db.refresh(accommodation)

    return accommodation


@router.patch("/{accommodation_id}", response_model=AccommodationResponse)
async def update_accommodation(
    accommodation_id: UUID,
    accommodation_data: AccommodationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("edit_accommodation"))
):
    """Update accommodation."""
    accommodation = db.query(Accommodation).filter(
        Accommodation.id == accommodation_id
    ).first()

    if not accommodation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accommodation not found"
        )

    # Update fields
    update_dict = accommodation_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(accommodation, field, value)

    db.commit()
    db.refresh(accommodation)

    return accommodation


@router.delete("/{accommodation_id}", response_model=MessageResponse)
async def delete_accommodation(
    accommodation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete accommodation (admin only)."""
    accommodation = db.query(Accommodation).filter(
        Accommodation.id == accommodation_id
    ).first()

    if not accommodation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accommodation not found"
        )

    try:
        # Delete associated images from Azure
        for image in accommodation.images:
            try:
                azure_blob_service.delete_image(image.image_url)
            except:
                pass

        # Delete accommodation
        db.delete(accommodation)
        db.commit()

        return MessageResponse(message="Accommodation deleted successfully")

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete accommodation: {str(e)}"
        )


@router.post("/{accommodation_id}/images", response_model=List[AccommodationImageResponse])
async def upload_accommodation_images(
    accommodation_id: UUID,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("edit_accommodation"))
):
    """Upload multiple images for an accommodation."""
    accommodation = db.query(Accommodation).filter(
        Accommodation.id == accommodation_id
    ).first()

    if not accommodation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accommodation not found"
        )

    uploaded_images = []

    try:
        for idx, file in enumerate(files):
            # Upload to Azure
            image_url = await azure_blob_service.upload_image(
                file,
                container="accommodations",
                folder=str(accommodation_id)
            )

            # Create image record
            image = AccommodationImage(
                accommodation_id=accommodation_id,
                image_url=image_url,
                caption=f"Image {idx + 1}",
                # is_primary removed as it's not in the model
                # display_order renamed to sort_order
                sort_order=len(accommodation.images) + idx
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


@router.delete("/images/{image_id}", response_model=MessageResponse)
async def delete_accommodation_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("edit_accommodation"))
):
    """Delete an accommodation image."""
    image = db.query(AccommodationImage).filter(
        AccommodationImage.id == image_id
    ).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    try:
        # Delete from Azure
        azure_blob_service.delete_image(image.image_url)

        # Delete from database
        db.delete(image)
        db.commit()

        return MessageResponse(message="Image deleted successfully")

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete image: {str(e)}"
        )

@router.get("/export/csv")
def export_accommodations_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Export all accommodations to CSV format."""
    items = db.query(Accommodation).all()
    output = ImportExportService.export_to_csv(items, exclude_fields=['id'])
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=accommodations.csv"}
    )

@router.post("/bulk-import", response_model=dict)
def bulk_import_accommodations(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Bulk import accommodations from CSV file. Matches on name."""
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
                name = row.get('name')
                dest_id = row.get('location_destination_id')
                type_id = row.get('type_id')

                if not name or not dest_id or not type_id:
                    failed.append({'row': row_num, 'error': 'Missing required fields (name, location_destination_id, type_id)'})
                    continue
                
                existing = db.query(Accommodation).filter(Accommodation.name == name).first()
                if existing:
                    # Update Fields
                    for k, v in row.items():
                        if hasattr(existing, k) and k not in ['id', 'created_at', 'updated_at']:
                            setattr(existing, k, v)
                    imported.append(name)
                else:
                    # Create
                    new_item = Accommodation()
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
