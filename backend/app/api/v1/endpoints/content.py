"""
Content management endpoints.

Handles inclusions, exclusions, and company content (logo, awards, templates).
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_db,
    get_current_active_user,
    require_admin,
    require_permission
)
from app.models.inclusion_exclusion import Inclusion, Exclusion
from app.models.company import CompanyContent, CompanyAsset, AssetTypeEnum
from app.models.user import User
from app.schemas.inclusion import InclusionCreate, InclusionUpdate, InclusionResponse
from app.schemas.exclusion import ExclusionCreate, ExclusionUpdate, ExclusionResponse
from app.schemas.company import (
    CompanyContentResponse,
    CompanyContentUpdate,
    CompanyAssetResponse,
    CompanyAssetLink
)
from app.schemas.common import MessageResponse
from app.services.azure_blob_service import azure_blob_service

router = APIRouter(prefix="/content", tags=["content"])



# ==================== Inclusions ====================

@router.get("/inclusions", response_model=List[InclusionResponse])
async def list_inclusions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all inclusions."""
    inclusions = db.query(Inclusion).order_by(Inclusion.title).all()
    return inclusions


@router.post("/inclusions", response_model=InclusionResponse, status_code=status.HTTP_201_CREATED)
async def create_inclusion(
    inclusion_data: InclusionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new inclusion (admin only)."""
    # Check for duplicate title
    existing = db.query(Inclusion).filter(Inclusion.title == inclusion_data.title).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inclusion with this title already exists"
        )

    inclusion = Inclusion(**inclusion_data.model_dump())
    db.add(inclusion)
    db.commit()
    db.refresh(inclusion)

    return inclusion


@router.patch("/inclusions/{inclusion_id}", response_model=InclusionResponse)
async def update_inclusion(
    inclusion_id: UUID,
    inclusion_data: InclusionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update an inclusion (admin only)."""
    inclusion = db.query(Inclusion).filter(Inclusion.id == inclusion_id).first()

    if not inclusion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inclusion not found"
        )

    # Check for duplicate title if changing
    if inclusion_data.title and inclusion_data.title != inclusion.title:
        existing = db.query(Inclusion).filter(Inclusion.title == inclusion_data.title).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inclusion with this title already exists"
            )

    # Update fields
    update_dict = inclusion_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(inclusion, field, value)

    db.commit()
    db.refresh(inclusion)

    return inclusion


@router.delete("/inclusions/{inclusion_id}", response_model=MessageResponse)
async def delete_inclusion(
    inclusion_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete an inclusion (admin only)."""
    inclusion = db.query(Inclusion).filter(Inclusion.id == inclusion_id).first()

    if not inclusion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inclusion not found"
        )

    try:
        db.delete(inclusion)
        db.commit()
        return MessageResponse(message="Inclusion deleted successfully")

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete inclusion: {str(e)}"
        )


# ==================== Exclusions ====================

@router.get("/exclusions", response_model=List[ExclusionResponse])
async def list_exclusions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all exclusions."""
    exclusions = db.query(Exclusion).order_by(Exclusion.title).all()
    return exclusions


@router.post("/exclusions", response_model=ExclusionResponse, status_code=status.HTTP_201_CREATED)
async def create_exclusion(
    exclusion_data: ExclusionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new exclusion (admin only)."""
    # Check for duplicate title
    existing = db.query(Exclusion).filter(Exclusion.title == exclusion_data.title).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exclusion with this title already exists"
        )

    exclusion = Exclusion(**exclusion_data.model_dump())
    db.add(exclusion)
    db.commit()
    db.refresh(exclusion)

    return exclusion


@router.patch("/exclusions/{exclusion_id}", response_model=ExclusionResponse)
async def update_exclusion(
    exclusion_id: UUID,
    exclusion_data: ExclusionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update an exclusion (admin only)."""
    exclusion = db.query(Exclusion).filter(Exclusion.id == exclusion_id).first()

    if not exclusion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exclusion not found"
        )

    # Check for duplicate title if changing
    if exclusion_data.title and exclusion_data.title != exclusion.title:
        existing = db.query(Exclusion).filter(Exclusion.title == exclusion_data.title).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exclusion with this title already exists"
            )

    # Update fields
    update_dict = exclusion_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(exclusion, field, value)

    db.commit()
    db.refresh(exclusion)

    return exclusion


@router.delete("/exclusions/{exclusion_id}", response_model=MessageResponse)
async def delete_exclusion(
    exclusion_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete an exclusion (admin only)."""
    exclusion = db.query(Exclusion).filter(Exclusion.id == exclusion_id).first()

    if not exclusion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exclusion not found"
        )

    try:
        db.delete(exclusion)
        db.commit()
        return MessageResponse(message="Exclusion deleted successfully")

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete exclusion: {str(e)}"
        )


# ==================== Company Content ====================

@router.get("/company", response_model=CompanyContentResponse)
async def get_company_content(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get company content (logo, templates)."""
    # There should only be one company content record
    company = db.query(CompanyContent).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company content not found. Please initialize company content."
        )

    return company


@router.post("/company/logo", response_model=CompanyContentResponse)
async def upload_company_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Upload company logo (admin only)."""
    # Get or create company content
    company = db.query(CompanyContent).first()
    if not company:
        company = CompanyContent()
        db.add(company)
        db.flush()

    try:
        # Upload to Azure
        logo_url = await azure_blob_service.upload_image(
            file,
            container="company",
            folder="logo"
        )

        # Delete old logo if exists
        if company.logo_url:
            try:
                await azure_blob_service.delete_image(company.logo_url)
            except:
                pass  # Ignore if old logo can't be deleted

        company.logo_url = logo_url
        db.commit()
        db.refresh(company)

        return company

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload logo: {str(e)}"
        )


@router.get("/company/awards", response_model=List[CompanyAssetResponse])
async def list_award_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all award badges."""
    awards = db.query(CompanyAsset).order_by(CompanyAsset.sort_order).all()
    return awards


@router.post("/company/awards", response_model=CompanyAssetResponse, status_code=status.HTTP_201_CREATED)
async def upload_award_badge(
    file: UploadFile = File(...),
    title: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Upload award badge (admin only)."""
    try:
        # Upload to Azure
        badge_url = await azure_blob_service.upload_image(
            file,
            container="company",
            folder="awards"
        )

        # Get next display order
        max_order = db.query(CompanyAsset).count()

        # Create award badge
        award = CompanyAsset(
            image_url=badge_url,
            title=title or file.filename,
            display_order=max_order
        )

        db.add(award)
        db.commit()
        db.refresh(award)

        return award

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload award badge: {str(e)}"
        )


@router.delete("/company/awards/{award_id}", response_model=MessageResponse)
async def delete_award_badge(
    award_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete award badge (admin only)."""
    award = db.query(CompanyAsset).filter(CompanyAsset.id == award_id).first()

    if not award:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Award badge not found"
        )

    try:
        # Delete from Azure
        if award.image_url:
            try:
                await azure_blob_service.delete_image(award.image_url)
            except:
                pass  # Ignore if deletion fails

        db.delete(award)
        db.commit()

        return MessageResponse(message="Award badge deleted successfully")

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete award badge: {str(e)}"
        )


# ==================== Company Content (Templates) ====================

@router.get("/company/templates", response_model=List[CompanyContentResponse])
async def get_company_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all company templates."""
    # Return all content records
    contents = db.query(CompanyContent).all()
    # If empty, might want to initialize default keys, but frontend can handle empty
    return contents 


@router.patch("/company/templates/{template_key}", response_model=CompanyContentResponse)
async def update_company_template(
    template_key: str,
    template_data: CompanyContentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a company template (admin only)."""
    # Allow dynamic keys or restrict? User requirements imply specific keys but flexibility is good.
    # We'll allow any key for extensibility.
    
    content_record = db.query(CompanyContent).filter(CompanyContent.key == template_key).first()
    
    if not content_record:
        # Create new record for this key
        content_record = CompanyContent(
            key=template_key,
            content=template_data.content,
            updated_by_user_id=current_user.id
        )
        db.add(content_record)
    else:
        content_record.content = template_data.content
        content_record.updated_by_user_id = current_user.id

    db.commit()
    db.refresh(content_record)

    return content_record


# ==================== Company Assets (Generic) ====================

@router.get("/company/assets", response_model=List[CompanyAssetResponse])
async def list_company_assets(
    asset_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List company assets, optionally filtered by type."""
    from sqlalchemy import cast, String
    query = db.query(CompanyAsset)
    if asset_type:
        # Cast Enum column to String for comparison to ensure we match the value "AWARD_BADGE"
        # even if SQLAlchemy expects an Enum object.
        query = query.filter(cast(CompanyAsset.asset_type, String) == asset_type)
    
    assets = query.order_by(CompanyAsset.sort_order, CompanyAsset.created_at).all()
    return assets


@router.post("/company/assets", response_model=CompanyAssetResponse, status_code=status.HTTP_201_CREATED)
async def upload_company_asset(
    file: UploadFile = File(...),
    asset_type: str = Form(...),
    title: Optional[str] = Form(None),
    asset_name: Optional[str] = Form(None), # Useful for specific default slots (e.g. 'cover')
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Upload a company asset (admin only)."""
    try:
        # Validate asset_type
        # (Assuming asset_type param matches Enum values)
        
        container_folder_map = {
            "logo": "logo",
            "award_badge": "awards",
            "certification": "certs",
            "review_image": "reviews",
            "default_image": "defaults"
        }
        folder = container_folder_map.get(asset_type, "misc")

        # Upload to Azure
        image_url = await azure_blob_service.upload_image(
            file,
            container="company",
            folder=folder
        )

        # Handle "Default Images" uniqueness? 
        # If uploading 'default_image' for 'cover', should we delete old one?
        # User implies "set default images", usually one per slot.
        if asset_type == "default_image" and asset_name:
             # Find existing default for this slot and delete/disable it?
             # Let's just create new one, frontend can pick latest or we can delete old.
             # Better to replace to keep cleanup automatic.
             existing = db.query(CompanyAsset).filter(
                 CompanyAsset.asset_type == "default_image",
                 CompanyAsset.asset_name == asset_name
             ).first()
             if existing:
                 # Delete old asset file? Maybe not yet just in case. 
                 # Just delete record or mark inactive?
                 db.delete(existing) 

        # Get max sort order if list
        max_order = 0
        if asset_type in ["award_badge", "certification"]:
             count = db.query(CompanyAsset).filter(CompanyAsset.asset_type == asset_type).count()
             max_order = count

        # Create asset record
        asset = CompanyAsset(
            asset_type=asset_type,
            asset_url=image_url,
            # Use provided title/name or filename
            asset_name=asset_name or title or file.filename, 
            sort_order=max_order
        )

        db.add(asset)
        db.commit()
        db.refresh(asset)

        return asset

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload asset: {str(e)}"
        )

@router.delete("/company/assets/{asset_id}", response_model=MessageResponse)
async def delete_company_asset(
    asset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a company asset."""
    asset = db.query(CompanyAsset).filter(CompanyAsset.id == asset_id).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    try:
        db.delete(asset)
        db.commit()
        return MessageResponse(message="Asset deleted")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/company/assets/link", response_model=CompanyAssetResponse)
async def link_company_asset(
    link_data: CompanyAssetLink,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Link an existing asset (by URL) as a company asset (admin only)."""
    try:
        # Handle "Default Images" uniqueness
        if link_data.asset_type == "default_image" and link_data.asset_name:
             # Find existing default for this slot and delete it from DB (not blob, as it might be used elsewhere)
             existing = db.query(CompanyAsset).filter(
                 CompanyAsset.asset_type == "default_image",
                 CompanyAsset.asset_name == link_data.asset_name
             ).first()
             if existing:
                 db.delete(existing)

        # Get max sort order if list
        max_order = 0
        if link_data.asset_type in ["award_badge", "certification"]:
             count = db.query(CompanyAsset).filter(CompanyAsset.asset_type == link_data.asset_type).count()
             max_order = count

        # Create asset record
        asset = CompanyAsset(
            asset_type=link_data.asset_type,
            asset_url=link_data.asset_url,
            asset_name=link_data.asset_name or link_data.title or "Linked Asset",
            sort_order=max_order
        )

        db.add(asset)
        db.commit()
        db.refresh(asset)

        return asset

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to link asset: {str(e)}"
        )
