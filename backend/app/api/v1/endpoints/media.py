"""
Media management endpoints.

Handles file uploads, deletions, and listing operations.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_db,
    get_current_active_user,
    require_admin
)
from app.models.user import User
from app.schemas.common import MessageResponse
from app.services.azure_blob_service import azure_blob_service

router = APIRouter(prefix="/media", tags=["media"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    container: str = Query("general", description="Azure container name"),
    folder: str = Query("", description="Folder path within container"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a file to Azure Blob Storage.

    Returns the URL of the uploaded file.
    """
    try:
        # Upload to Azure
        file_url = await azure_blob_service.upload_image(
            file,
            container=container,
            folder=folder
        )

        return {
            "success": True,
            "message": "File uploaded successfully",
            "url": file_url,
            "filename": file.filename
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.post("/upload-multiple", status_code=status.HTTP_201_CREATED)
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    container: str = Query("general", description="Azure container name"),
    folder: str = Query("", description="Folder path within container"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload multiple files to Azure Blob Storage.

    Returns a list of uploaded file URLs.
    """
    uploaded_files = []
    failed_files = []

    for file in files:
        try:
            file_url = await azure_blob_service.upload_image(
                file,
                container=container,
                folder=folder
            )

            uploaded_files.append({
                "filename": file.filename,
                "url": file_url,
                "success": True
            })

        except Exception as e:
            failed_files.append({
                "filename": file.filename,
                "error": str(e),
                "success": False
            })

    return {
        "success": len(failed_files) == 0,
        "message": f"Uploaded {len(uploaded_files)} of {len(files)} files",
        "uploaded": uploaded_files,
        "failed": failed_files
    }


@router.delete("", response_model=MessageResponse)
async def delete_file(
    file_url: str = Query(..., description="Full URL of the file to delete"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a file from Azure Blob Storage by URL.
    """
    try:
        await azure_blob_service.delete_image(file_url)

        return MessageResponse(message="File deleted successfully")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )


@router.get("/list")
async def list_files(
    container: str = Query("general", description="Azure container name"),
    folder: str = Query("", description="Folder path within container"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all files in a container/folder.
    """
    try:
        files = await azure_blob_service.list_images(
            container=container,
            folder=folder
        )

        return {
            "success": True,
            "container": container,
            "folder": folder,
            "count": len(files),
            "files": files
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}"
        )


@router.get("/library")
async def get_media_library(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    source_type: Optional[str] = Query(None, description="destination or accommodation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get aggregated media library from existing system images.
    
    Returns images from Destinations and Accommodations.
    """
    from app.models.destination import Destination, DestinationImage
    from app.models.accommodation import Accommodation, AccommodationImage
    from sqlalchemy import or_

    items = []
    
    # 1. Fetch Destination Images
    if not source_type or source_type == 'destination':
        dest_query = db.query(DestinationImage, Destination.name).join(Destination)
        
        if search:
            dest_query = dest_query.filter(
                or_(
                    Destination.name.ilike(f"%{search}%"),
                    DestinationImage.caption.ilike(f"%{search}%")
                )
            )
            
        # Execute query (simple limit for now, ideally pagination splits across types)
        # For simplicity in this combined view, we'll fetch a batch.
        dest_images = dest_query.limit(limit).all()
        
        for img, dest_name in dest_images:
            items.append({
                "id": str(img.id),
                "url": img.image_url,
                "caption": img.caption,
                "source_type": "destination",
                "source_name": dest_name,
                "created_at": img.created_at
            })

    # 2. Fetch Accommodation Images
    if not source_type or source_type == 'accommodation':
        acc_query = db.query(AccommodationImage, Accommodation.name).join(Accommodation)
        
        if search:
            acc_query = acc_query.filter(
                or_(
                    Accommodation.name.ilike(f"%{search}%"),
                    AccommodationImage.caption.ilike(f"%{search}%")
                )
            )
            
        acc_images = acc_query.limit(limit).all()
        
        for img, acc_name in acc_images:
            items.append({
                "id": str(img.id),
                "url": img.image_url,
                "caption": img.caption,
                "source_type": "accommodation",
                "source_name": acc_name,
                "created_at": img.created_at
            })

    # 3. Fetch Itinerary Images
    if not source_type or source_type == 'itinerary':
        from app.models.itinerary import Itinerary, ItineraryImage
        itinerary_query = db.query(ItineraryImage, Itinerary.tour_title).join(Itinerary)
        
        if search:
            itinerary_query = itinerary_query.filter(
                or_(
                    Itinerary.tour_title.ilike(f"%{search}%"),
                    ItineraryImage.caption.ilike(f"%{search}%")
                )
            )
            
        itinerary_images = itinerary_query.limit(limit).all()
        
        for img, tour_title in itinerary_images:
            items.append({
                "id": str(img.id),
                "url": img.image_url,
                "caption": img.caption,
                "source_type": "itinerary",
                "source_name": tour_title,
                "created_at": img.created_at
            })
            
    # 4. Fetch Company Assets (Logos, Badges, Defaults)
    if not source_type or source_type == 'company_asset':
        from app.models.company import CompanyAsset
        company_query = db.query(CompanyAsset)
        
        if search:
            company_query = company_query.filter(
                or_(
                    CompanyAsset.asset_name.ilike(f"%{search}%"),
                    CompanyAsset.asset_type.ilike(f"%{search}%")
                )
            )
            
        company_assets = company_query.limit(limit).all()
        
        for asset in company_assets:
            items.append({
                "id": str(asset.id),
                "url": asset.asset_url,
                "caption": asset.asset_name.replace('_', ' ').title(),
                "source_type": "company_asset",
                "source_name": "Company Asset",
                "created_at": asset.created_at
            })

    # 3. Sort and Paginate in memory (for mixed results)
    # Since we can't easily SQL union different schemas with ORM 
    # without complex queries, we'll do lightweight mixing here.
    # Note: This is an MVP approach. For millions of rows, use UNION ALL in SQL.
    items.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Slice for pagination
    start = (page - 1) * limit
    end = start + limit
    paginated_items = items[start:end]

    return {
        "items": paginated_items,
        "total": len(items),
        "page": page,
        "pages": (len(items) + limit - 1) // limit
    }

    return {
        "items": paginated_items,
        "total": len(items),
        "page": page,
        "pages": (len(items) + limit - 1) // limit
    }


@router.delete("/library/{source_type}/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_library_image(
    source_type: str,
    image_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an image from the media library (Destination or Accommodation).
    
    Deletes the database record AND the file from Azure Blob Storage.
    """
    from app.models.destination import DestinationImage
    from app.models.accommodation import AccommodationImage
    from app.models.itinerary import ItineraryImage
    from uuid import UUID

    try:
        image_uuid = UUID(image_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image ID format"
        )

    image_record = None
    
    if source_type == 'destination':
        image_record = db.query(DestinationImage).filter(DestinationImage.id == image_uuid).first()
    elif source_type == 'accommodation':
        image_record = db.query(AccommodationImage).filter(AccommodationImage.id == image_uuid).first()
    elif source_type == 'itinerary':
        image_record = db.query(ItineraryImage).filter(ItineraryImage.id == image_id).first()
    elif source_type == 'company_asset':
        from app.models.company import CompanyAsset
        image_record = db.query(CompanyAsset).filter(CompanyAsset.id == image_id).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid source type. Must be 'destination', 'accommodation', or 'itinerary'."
        )
        
    if not image_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
        
    # Delete from Storage
    if image_record.image_url:
        try:
            await azure_blob_service.delete_image(image_record.image_url)
        except Exception as e:
            # Log warning but proceed with DB deletion to avoid state mismatch
            print(f"Warning: Failed to delete blob {image_record.image_url}: {e}")

    # Delete from DB
    db.delete(image_record)
    db.commit()
    
    return None
