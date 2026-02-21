"""
Destination management endpoints.

Handles CRUD operations for destinations and their images.
"""
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.api.v1.deps import (
    get_db,
    get_current_active_user,
    require_admin,
    PaginationParams,
    require_permission
)
from app.models.destination import Destination, DestinationImage
from app.models.user import User
from app.schemas.destination import (
    DestinationCreate,
    DestinationUpdate,
    DestinationResponse,
    DestinationWithImages,
    DestinationImageCreate,
    DestinationImageResponse
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.azure_blob_service import azure_blob_service
from app.services.import_export_service import ImportExportService
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/destinations", tags=["destinations"])


@router.get("", response_model=PaginatedResponse[DestinationWithImages])
def list_destinations(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(None, description="Search by name"),
    country: Optional[str] = Query(None, description="Filter by country"),
    region: Optional[str] = Query(None, description="Filter by region"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all destinations with pagination and filtering.

    Supports:
    - Search by name
    - Filter by country
    - Filter by region
    """
    query = db.query(Destination)

    # Search by name
    if search:
        query = query.filter(Destination.name.ilike(f"%{search}%"))

    # Filter by country
    if country:
        query = query.filter(Destination.country.ilike(f"%{country}%"))

    # Filter by region
    if region:
        query = query.filter(Destination.region.ilike(f"%{region}%"))

    # Get total count
    total = query.count()

    # Apply pagination
    destinations = query.offset(pagination.skip).limit(pagination.limit).all()

    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return PaginatedResponse(
        items=destinations,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
        has_next=pagination.page < total_pages,
        has_prev=pagination.page > 1
    )


@router.get("/{destination_id}", response_model=DestinationWithImages)
def get_destination(
    destination_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get destination by ID with all images."""
    destination = db.query(Destination).filter(Destination.id == destination_id).first()

    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )

    return destination


@router.post("", response_model=DestinationResponse, status_code=status.HTTP_201_CREATED)
def create_destination(
    destination_data: DestinationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("create_destination"))
):
    """Create a new destination."""
    # Check if destination with same name already exists
    existing = db.query(Destination).filter(
        Destination.name == destination_data.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Destination with this name already exists"
        )

    # Prepare data for creation
    data = destination_data.model_dump(exclude={'image_urls', 'gps_coordinates', 'timezone', 'attractions', 'travel_tips'})
    
    # Handle GPS coordinates
    if destination_data.gps_coordinates:
        try:
            lat_str, lon_str = destination_data.gps_coordinates.split(',')
            data['gps_latitude'] = float(lat_str.strip())
            data['gps_longitude'] = float(lon_str.strip())
        except (ValueError, AttributeError):
            pass  # Validation handled by Pydantic, but safety check here

    # Create destination
    destination = Destination(**data)
    db.add(destination)
    db.commit()
    db.refresh(destination)

    # Handle image URLs if provided
    if destination_data.image_urls:
        for idx, url in enumerate(destination_data.image_urls):
            image = DestinationImage(
                destination_id=destination.id,
                image_url=url,
                caption=f"Image {idx + 1}",
                image_type="general",  # Default type
                sort_order=idx
            )
            db.add(image)
        db.commit()
        db.refresh(destination)

    return destination


@router.patch("/{destination_id}", response_model=DestinationResponse)
def update_destination(
    destination_id: UUID,
    destination_data: DestinationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("edit_destination"))
):
    """Update destination."""
    destination = db.query(Destination).filter(Destination.id == destination_id).first()

    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )

    # Update fields
    update_dict = destination_data.model_dump(exclude_unset=True, exclude={'image_urls'})
    for field, value in update_dict.items():
        setattr(destination, field, value)

    # Handle image updates if provided
    if destination_data.image_urls is not None:
        # Get existing images
        existing_images = {img.image_url: img for img in destination.images}
        new_urls = destination_data.image_urls
        
        # 1. Update/Add images
        for idx, url in enumerate(new_urls):
            if url in existing_images:
                # Update existing
                existing_images[url].sort_order = idx
                # Remove from tracking dict so we know what's left to delete
                del existing_images[url]
            else:
                # Add new
                new_image = DestinationImage(
                    destination_id=destination.id,
                    image_url=url,
                    caption=f"Image {idx + 1}",
                    image_type="general",
                    sort_order=idx
                )
                db.add(new_image)
        
        # 2. Delete removed images
        for img in existing_images.values():
            db.delete(img)

    db.commit()
    db.refresh(destination)

    return destination


@router.delete("/{destination_id}", response_model=MessageResponse)
def delete_destination(
    destination_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete destination (admin only).

    Note: This will fail if destination is used in any tours/itineraries.
    """
    destination = db.query(Destination).filter(Destination.id == destination_id).first()

    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )

    try:
        # Delete associated images from Azure
        for image in destination.images:
            try:
                azure_blob_service.delete_image(image.image_url)
            except:
                pass  # Continue even if Azure delete fails

        # Delete destination
        db.delete(destination)
        db.commit()

        return MessageResponse(message="Destination deleted successfully")

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete destination: {str(e)}"
        )


@router.post("/{destination_id}/images", response_model=List[DestinationImageResponse])
async def upload_destination_images(
    destination_id: UUID,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("edit_destination"))
):
    """Upload multiple images for a destination."""
    destination = db.query(Destination).filter(Destination.id == destination_id).first()

    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )

    uploaded_images = []

    try:
        for idx, file in enumerate(files):
            # Upload to Azure Blob Storage
            image_url = await azure_blob_service.upload_image(
                file,
                container="destinations",
                folder=str(destination_id)
            )

            # Create image record
            image = DestinationImage(
                destination_id=destination_id,
                image_url=image_url,
                caption=f"Image {idx + 1}",
                # is_primary field removed as it doesn't exist in model
                # sort_order renamed from display_order to match model
                sort_order=len(destination.images) + idx
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
async def delete_destination_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("edit_destination"))
):
    """Delete a destination image."""
    image = db.query(DestinationImage).filter(DestinationImage.id == image_id).first()

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
def export_destinations_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Export all destinations to CSV format using ImportExportService.
    """
    destinations = db.query(Destination).all()
    output = ImportExportService.export_to_csv(destinations, exclude_fields=['id'])
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=destinations.csv"}
    )

@router.post("/bulk-import", response_model=dict)
def bulk_import_destinations(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Bulk import destinations from CSV file using ImportExportService. Matches on name.
    """
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
                country = row.get('country')

                if not name or not country:
                    failed.append({'row': row_num, 'error': 'Missing required fields (name, country)'})
                    continue
                
                existing = db.query(Destination).filter(Destination.name == name).first()
                if existing:
                    # Update Fields
                    for k, v in row.items():
                        if hasattr(existing, k) and k not in ['id', 'created_at', 'updated_at']:
                            setattr(existing, k, v)
                    imported.append(name)
                else:
                    # Create
                    new_item = Destination()
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
