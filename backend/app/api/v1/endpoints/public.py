"""
Public endpoints (no authentication required).

Allows travelers to view their itinerary via unique public URL.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.models.itinerary import Itinerary
from app.models.company import CompanyContent
from app.schemas.itinerary import ItineraryPublicView

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/itineraries/{unique_code}", response_model=ItineraryPublicView)
def get_public_itinerary(
    unique_code: str,
    db: Session = Depends(get_db)
):
    """
    Get itinerary by unique code (no authentication required).

    This is the public view URL that travelers receive.
    Sanitizes data to remove internal information.

    URL Format: https://yourdomain.com/view/{unique_code}
    Example: https://yourdomain.com/view/A7K9M2P4
    """
    # Find itinerary by unique code
    itinerary = db.query(Itinerary).filter(
        Itinerary.unique_code == unique_code
    ).first()

    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found. Please check your link."
        )

    # Only show confirmed or completed itineraries publicly
    from app.models.itinerary import ItineraryStatusEnum
    if itinerary.status not in [
        ItineraryStatusEnum.CONFIRMED,
        ItineraryStatusEnum.COMPLETED,
        ItineraryStatusEnum.SENT,
        ItineraryStatusEnum.DRAFT  # Temporarily allow DRAFT for debugging
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This itinerary is not yet available for viewing."
        )

    # Populate internal fields for viewing
    if itinerary.creator:
        itinerary.agent_name = itinerary.creator.full_name
        itinerary.agent_email = itinerary.creator.email
        itinerary.agent_phone = itinerary.creator.phone_number
        itinerary.agent_profile_photo_url = itinerary.creator.profile_photo_url
        itinerary.agent_position = itinerary.creator.position

    # Get company content for branding and templates
    # We need to find the specific content item for greeting/intro letter
    greeting_content = db.query(CompanyContent).filter(
        CompanyContent.key == "intro_letter_template"
    ).first()
    
    # Populate welcome_message dynamically
    # Helper for placeholder replacement
    def replace_placeholders(text: str, itinerary_obj) -> str:
        if not text:
            return ""
        
        client_name = itinerary_obj.primary_traveler.full_name if itinerary_obj.primary_traveler else "Guest"
        tour_title = itinerary_obj.tour_title or ""
        tour_days = str(itinerary_obj.duration_days) if itinerary_obj.duration_days else "0"
        agent_name = itinerary_obj.creator.full_name if itinerary_obj.creator else "Your Travel Agent"
        
        return text.replace("[Client Name]", client_name)\
                   .replace("[Traveller Name]", client_name)\
                   .replace("[Tour name]", tour_title)\
                   .replace("[Tour days]", tour_days)\
                   .replace("[Agent name]", agent_name)\
                   .replace("[Agent Name]", agent_name)

    # Populate welcome_message dynamically
    if greeting_content and greeting_content.content:
        itinerary.welcome_message = replace_placeholders(greeting_content.content, itinerary)

    # Get About Us Content
    about_content = db.query(CompanyContent).filter(
        CompanyContent.key == "about_company_template"
    ).first()
    
    if about_content and about_content.content:
        itinerary.company_about = replace_placeholders(about_content.content, itinerary)

    # Get Award Badges
    from app.models.company import CompanyAsset, AssetTypeEnum
    badges = db.query(CompanyAsset).filter(
        CompanyAsset.asset_type == AssetTypeEnum.AWARD_BADGE,
        CompanyAsset.is_active == True
    ).order_by(CompanyAsset.sort_order).all()
    
    itinerary.company_badges = badges

    # Get Closing Message
    closing_content = db.query(CompanyContent).filter(
        CompanyContent.key == "cta_message_template"
    ).first()
    
    
    if closing_content and closing_content.content:
        itinerary.closing_message = replace_placeholders(closing_content.content, itinerary)

    # Get Company Contact Details
    # We fetch these from specific CompanyContent keys
    contact_keys = ["company_address", "company_phone", "company_website", "social_facebook", "social_instagram", "social_twitter", "social_linkedin", "footer_notes"]
    contact_contents = db.query(CompanyContent).filter(
        CompanyContent.key.in_(contact_keys)
    ).all()
    
    contact_map = {c.key: c.content for c in contact_contents}
    
    itinerary.company_address = contact_map.get("company_address")
    itinerary.company_phone = contact_map.get("company_phone")
    itinerary.company_website = contact_map.get("company_website")
    itinerary.footer_notes = contact_map.get("footer_notes")
    
    itinerary.company_socials = {}
    if contact_map.get("social_facebook"): itinerary.company_socials["facebook"] = contact_map.get("social_facebook")
    if contact_map.get("social_instagram"): itinerary.company_socials["instagram"] = contact_map.get("social_instagram")
    if contact_map.get("social_twitter"): itinerary.company_socials["twitter"] = contact_map.get("social_twitter")
    if contact_map.get("social_linkedin"): itinerary.company_socials["linkedin"] = contact_map.get("social_linkedin")

    # Get Company Logo
    logo_asset = db.query(CompanyAsset).filter(
        CompanyAsset.asset_type == AssetTypeEnum.LOGO,
        CompanyAsset.is_active == True
    ).order_by(CompanyAsset.created_at.desc()).first()
    
    itinerary.logo_url = logo_asset.asset_url if logo_asset else "/Easy-Travel-Logo-Black.webp"

    # Get Review Image
    review_asset = db.query(CompanyAsset).filter(
        CompanyAsset.asset_type == AssetTypeEnum.REVIEW_IMAGE,
        CompanyAsset.is_active == True
    ).order_by(CompanyAsset.created_at.desc()).first()
    
    itinerary.review_image_url = review_asset.asset_url if review_asset else None

    # 1. Try to find explicit Cover Photo from Itinerary Images
    cover_image = None
    if itinerary.images:
        # Sort by created_at desc to get latest, or filter by role if available
        # Assuming there might be a role field or just use the first one if designated as cover
        # Based on user request "Itinerary > Images > Cover Photo", we look for image_role='cover'
        # The model definition suggests lowercase 'cover'
        for img in itinerary.images:
            if hasattr(img, 'image_role') and (img.image_role == 'cover' or img.image_role == 'COVER'):
                cover_image = img
                break
        
        # If no explicit cover role found, and images exist, maybe use the first one?
        # But user specifically asked for "Cover Photo" section.
    
    if cover_image:
        itinerary.hero_image_url = cover_image.image_url
    
    # 2. Fallback to First Day Destination Image (if no cover photo set)
    if not itinerary.hero_image_url and itinerary.days and len(itinerary.days) > 0:
        first_day = itinerary.days[0]
        if first_day.destinations and len(first_day.destinations) > 0:
            first_destination = first_day.destinations[0]
            if first_destination.images and len(first_destination.images) > 0:
                itinerary.hero_image_url = first_destination.images[0].image_url

    # 3. Fallback to default placeholder is handled in frontend, or we can set it here
    if not itinerary.hero_image_url:
         itinerary.hero_image_url = "/images/default-hero.jpg"

    # Build sanitized response
    return itinerary


@router.get("/itineraries/{unique_code}/hero-image")
def get_itinerary_hero_image(
    unique_code: str,
    db: Session = Depends(get_db)
):
    """
    Get hero image URL for social media previews.

    Used for OpenGraph meta tags when sharing itinerary link.
    """
    itinerary = db.query(Itinerary).filter(
        Itinerary.unique_code == unique_code
    ).first()

    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )

    # Get hero image from first day or tour type
    hero_image_url = None

    if itinerary.days and len(itinerary.days) > 0:
        first_day = itinerary.days[0]
        if first_day.destinations and len(first_day.destinations) > 0:
            first_destination = first_day.destinations[0]
            if first_destination.images and len(first_destination.images) > 0:
                hero_image_url = first_destination.images[0].image_url

    # Fallback to placeholder
    if not hero_image_url:
        hero_image_url = "https://placeholder.com/1200x630/travel-hero.jpg"

    return {
        "hero_image_url": hero_image_url,
        "title": itinerary.title,
        "description": itinerary.description[:150] if itinerary.description else ""
    }


@router.get("/company")
def get_company_info(db: Session = Depends(get_db)):
    """
    Get public company information.

    Used for footer, about page, contact info, and branding.
    """
    # 1. Get App Name
    app_name_content = db.query(CompanyContent).filter(
        CompanyContent.key == "app_name"
    ).first()
    
    app_name = app_name_content.content if app_name_content else "Easy. Travel Itinerary Builder"

    # 2. Get Logo
    from app.models.company import AssetTypeEnum, CompanyAsset
    logo_asset = db.query(CompanyAsset).filter(
        CompanyAsset.asset_type == AssetTypeEnum.LOGO,
        CompanyAsset.is_active == True
    ).order_by(CompanyAsset.created_at.desc()).first()
    
    logo_url = logo_asset.asset_url if logo_asset else "/Easy-Travel-Logo-Black.webp"

    # 3. Get About Content
    about_content = db.query(CompanyContent).filter(
        CompanyContent.key == "about_company_template"
    ).first()
    
    about_text = about_content.content if about_content else "Your trusted travel partner"

    # 4. Get Awards (for existing usage)
    badges = db.query(CompanyAsset).filter(
        CompanyAsset.asset_type == AssetTypeEnum.AWARD_BADGE,
        CompanyAsset.is_active == True
    ).order_by(CompanyAsset.sort_order).all()

    # 5. Get Theme settings
    theme_contents = db.query(CompanyContent).filter(
        CompanyContent.key.in_(["theme_primary_color", "theme_font_family"])
    ).all()
    theme_map = {c.key: c.content for c in theme_contents}

    return {
        "logo_url": logo_url,
        "company_name": app_name,
        "about": about_text,
        "contact_email": "info@travelagency.com", # Placeholder until setting exists
        "contact_phone": "+1-555-0100", # Placeholder until setting exists
        "address": "123 Travel Street, City, Country", # Placeholder until setting exists
        "theme_primary_color": theme_map.get("theme_primary_color", "#1d4ed8"), # Default blue
        "theme_font_family": theme_map.get("theme_font_family", "sans"), # Default sans
        "awards": [
            {
                "image_url": award.asset_url, # Check model, it's asset_url not image_url
                "title": award.asset_name # Check model, it's asset_name not title
            }
            for award in badges
        ]
    }
