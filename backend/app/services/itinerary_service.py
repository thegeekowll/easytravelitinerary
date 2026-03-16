"""
Itinerary Service.

Core business logic for creating and managing itineraries.
Supports 3 creation methods: from base tour, edited base tour, and custom.
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import date, timedelta
from sqlalchemy.orm import Session
import secrets
import string

from app.models.itinerary import Itinerary, ItineraryDay, Traveler, ItineraryStatusEnum
from app.models.base_tour import BaseTour
from app.models.user import User, UserRoleEnum
from app.schemas.itinerary import (
    ItineraryCreateChooseExisting,
    ItineraryCreateEditExisting,
    ItineraryCreateCustom,
    ItineraryDayCreate,
    TravelerCreate
)
from typing import Union

# Type alias for any itinerary create schema
ItineraryCreate = Union[ItineraryCreateChooseExisting, ItineraryCreateEditExisting, ItineraryCreateCustom]
from app.services.destination_combination_service import destination_combination_service


class ItineraryService:
    """Service for managing itineraries."""

    @staticmethod
    def generate_unique_code(db: Session) -> str:
        """
        Generate a unique alphanumeric code for public itinerary URL.

        Format: 8 characters, alphanumeric (uppercase + digits)
        Example: A7K9M2P4

        Returns:
            Unique 8-character code
        """
        attempts = 0
        max_attempts = 10

        while attempts < max_attempts:
            # Generate random 8-character code
            code = ''.join(
                secrets.choice(string.ascii_uppercase + string.digits)
                for _ in range(8)
            )

            # Check uniqueness
            existing = db.query(Itinerary).filter(
                Itinerary.unique_code == code
            ).first()

            if not existing:
                return code

            attempts += 1

        # Fallback: use timestamp-based code
        import time
        timestamp = str(int(time.time()))[-8:]
        return f"IT{timestamp}"

    @staticmethod
    def calculate_dates(departure_date: date, number_of_days: int) -> List[date]:
        """
        Calculate date for each day of the itinerary.

        Args:
            departure_date: Start date
            number_of_days: Total number of days

        Returns:
            List of dates, one per day
        """
        return [departure_date + timedelta(days=i) for i in range(number_of_days)]

    @staticmethod
    def auto_fill_day_content(
        destination_ids: List[UUID],
        db: Session
    ) -> Dict[str, Any]:
        """
        Auto-fill description and activity content based on destinations.

        Uses the 2D destination combination table.

        Args:
            destination_ids: List of destination IDs for the day
            db: Database session

        Returns:
            Dictionary with:
            - type: "single", "pair", or "multiple"
            - description: Auto-filled description (or None)
            - activity: Auto-filled activity (or None)
            - suggestions: List of suggestions (for 3+ destinations)
        """
        if len(destination_ids) == 0:
            return {
                'type': 'none',
                'description': None,
                'activity': None,
                'suggestions': []
            }

        elif len(destination_ids) == 1:
            # Single destination - diagonal lookup
            combination = destination_combination_service.get_combination(
                destination_ids[0], None, db
            )

            return {
                'type': 'single',
                'description': combination.description_content if combination else None,
                'activity': combination.activity_content if combination else None,
                'suggestions': []
            }

        elif len(destination_ids) == 2:
            # Two destinations - direct pair lookup
            combination = destination_combination_service.get_combination(
                destination_ids[0], destination_ids[1], db
            )

            return {
                'type': 'pair',
                'description': combination.description_content if combination else None,
                'activity': combination.activity_content if combination else None,
                'suggestions': []
            }

        else:
            # 3+ destinations - return suggestions
            suggestions = destination_combination_service.get_suggestions_for_multiple(
                destination_ids, db
            )

            return {
                'type': 'multiple',
                'description': None,
                'activity': None,
                'suggestions': [
                    {
                        'pair_name': s.pair_name,
                        'description': s.description,
                        'activity': s.activity
                    }
                    for s in suggestions
                ]
            }

    @staticmethod
    def is_editable(itinerary: Itinerary, user: User) -> bool:
        """
        Check if user can edit the itinerary.

        Rules:
        - Admins can always edit
        - After tour completion (return_date < today):
          - Only editable if can_edit_after_tour flag is True OR user is admin
        - Before/during tour:
          - Editable by assigned agent or creator

        Args:
            itinerary: Itinerary to check
            user: User attempting to edit

        Returns:
            True if editable, False otherwise
        """
        from datetime import date

        # Admins can always edit
        if user.role == UserRoleEnum.ADMIN:
            return True

        # Check if tour has ended
        tour_ended = itinerary.return_date < date.today()

        if tour_ended and not itinerary.can_edit_after_tour:
            return False

        # Check if user is assigned or creator
        if user.id == itinerary.assigned_to_user_id or user.id == itinerary.created_by_user_id:
            return True

        return False

    @staticmethod
    def apply_default_images(itinerary_id: UUID, db: Session):
        """
        Apply default company images to specific slots if they are empty.
        
        This ensures new itineraries have default branding/imagery 
        (e.g., Cover, End Image) if not provided by the source.
        """
        from app.models.company import CompanyAsset, AssetTypeEnum
        from app.models.itinerary import ItineraryImage
        
        # Get defaults
        from sqlalchemy import cast, String
        defaults = db.query(CompanyAsset).filter(
            cast(CompanyAsset.asset_type, String) == "DEFAULT_IMAGE"
        ).all()
        
        if not defaults:
            return

        # Get existing itinerary images roles
        existing_roles = db.query(ItineraryImage.image_role).filter(
            ItineraryImage.itinerary_id == itinerary_id,
            ItineraryImage.image_role.isnot(None)
        ).all()
        existing_roles = [r[0] for r in existing_roles]
        
        for default in defaults:
            # If this role is missing in the itinerary, add the default
            # Ensure we match against the "DEFAULT_IMAGE" text or just check if it's default
            # Logic: If it's a default image (which the query ensures), add it.
            if default.asset_name and default.asset_name not in existing_roles:
                new_image = ItineraryImage(
                    itinerary_id=itinerary_id,
                    image_url=default.asset_url,
                    caption=f"Default {default.asset_name.replace('_', ' ').title()}",
                    image_role=default.asset_name,
                    sort_order=default.sort_order or 0
                )
                db.add(new_image)
        
        db.flush()

    @staticmethod
    def create_from_base_tour(
        base_tour_id: UUID,
        travelers: List[TravelerCreate],
        departure_date: date,
        assigned_to_user_id: UUID,
        created_by_user_id: UUID,
        db: Session
    ) -> Itinerary:
        """
        Method A: Create itinerary from existing base tour (choose as-is).

        Clones the entire base tour into a new itinerary without modifications.

        Args:
            base_tour_id: Base tour to clone
            travelers: List of travelers
            departure_date: Start date
            assigned_to_user_id: Agent assigned to this itinerary
            created_by_user_id: User who created it
            db: Database session

        Returns:
            Created Itinerary

        Raises:
            ValueError: If base tour not found or validation fails
        """
        # Get base tour
        base_tour = db.query(BaseTour).filter(BaseTour.id == base_tour_id).first()
        if not base_tour:
            raise ValueError(f"Base tour {base_tour_id} not found")

        if not base_tour.is_active:
            raise ValueError("Cannot create itinerary from inactive base tour")

        # Calculate dates
        return_date = departure_date + timedelta(days=base_tour.number_of_days - 1)
        day_dates = ItineraryService.calculate_dates(departure_date, base_tour.number_of_days)

        # Generate unique code
        unique_code = ItineraryService.generate_unique_code(db)

        # Create itinerary
        itinerary = Itinerary(
            created_from_base_tour_id=base_tour_id,
            tour_title=base_tour.tour_name,
            tour_type_id=base_tour.tour_type_id,
            number_of_days=base_tour.number_of_days,
            number_of_nights=base_tour.number_of_nights,
            description=base_tour.description,
            departure_date=departure_date,
            return_date=return_date,
            status=ItineraryStatusEnum.DRAFT,
            creation_method='choose_existing',
            unique_code=unique_code,
            assigned_to_user_id=assigned_to_user_id,
            created_by_user_id=created_by_user_id,
            can_edit_after_tour=False

        )

        db.add(itinerary)
        db.flush()

        # Clone days from base tour
        for base_day in base_tour.days:
            day_date = day_dates[base_day.day_number - 1]

            itinerary_day = ItineraryDay(
                itinerary_id=itinerary.id,
                accommodation_id=base_day.accommodation_id,
                day_number=base_day.day_number,
                day_date=day_date,
                day_title=base_day.day_title,
                description=base_day.description,
                activities=base_day.activities,
                meals_included=base_day.meals_included,
                is_description_custom=False,  # Came from base tour
                is_activity_custom=False
            )

            db.add(itinerary_day)
            db.flush()

            # Copy destination associations
            itinerary_day.destinations = base_day.destinations

        # Copy inclusions and exclusions
        itinerary.inclusions = base_tour.inclusions
        itinerary.exclusions = base_tour.exclusions

        # Create travelers
        for traveler_data in travelers:
            traveler = Traveler(
                itinerary_id=itinerary.id,
                **traveler_data.model_dump()
            )
            db.add(traveler)

        db.flush()
        
        # Apply default images
        ItineraryService.apply_default_images(itinerary.id, db)

        return itinerary

    @staticmethod
    def create_from_edited_tour(
        base_tour_id: UUID,
        tour_modifications: Dict[str, Any],
        days: List[ItineraryDayCreate],
        travelers: List[TravelerCreate],
        departure_date: date,
        assigned_to_user_id: UUID,
        created_by_user_id: UUID,
        db: Session
    ) -> Itinerary:
        """
        Method B: Create itinerary from edited base tour.

        Starts with a base tour but applies modifications and custom days.
        Auto-fills missing descriptions/activities from 2D table.

        Args:
            base_tour_id: Base tour to start from
            tour_modifications: Dict of fields to override (title, description, etc.)
            days: Custom day configurations
            travelers: List of travelers
            departure_date: Start date
            assigned_to_user_id: Agent assigned
            created_by_user_id: User who created
            db: Database session

        Returns:
            Created Itinerary

        Raises:
            ValueError: If validation fails
        """
        # Get base tour
        base_tour = db.query(BaseTour).filter(BaseTour.id == base_tour_id).first()
        if not base_tour:
            raise ValueError(f"Base tour {base_tour_id} not found")

        # Calculate dates
        duration_days = tour_modifications.get('duration_days', base_tour.number_of_days)
        return_date = departure_date + timedelta(days=duration_days - 1)
        day_dates = ItineraryService.calculate_dates(departure_date, duration_days)

        # Generate unique code
        unique_code = ItineraryService.generate_unique_code(db)

        # Create itinerary with modifications
        itinerary = Itinerary(
            created_from_base_tour_id=base_tour_id,
            tour_title=tour_modifications.get('title', base_tour.tour_name),
            tour_type_id=base_tour.tour_type_id,
            number_of_days=duration_days,
            number_of_nights=duration_days - 1, # Approximation
            description=tour_modifications.get('description', base_tour.description),
            departure_date=departure_date,
            return_date=return_date,
            status=ItineraryStatusEnum.DRAFT,
            creation_method='edit_existing',
            unique_code=unique_code,
            assigned_to_user_id=assigned_to_user_id,
            created_by_user_id=created_by_user_id,
            can_edit_after_tour=False
        )

        db.add(itinerary)
        db.flush()

        # Create custom days
        for day_data in days:
            day_date = day_dates[day_data.day_number - 1]

            # Auto-fill if content not provided
            description = day_data.description
            activities = day_data.activities
            is_description_custom = True
            is_activity_custom = True

            if not description or not activities:
                # Try auto-fill from destination combinations
                auto_fill = ItineraryService.auto_fill_day_content(
                    day_data.destination_ids, db
                )

                if auto_fill['type'] in ['single', 'pair']:
                    if not description and auto_fill['description']:
                        description = auto_fill['description']
                        is_description_custom = False

                    if not activities and auto_fill['activity']:
                        activities = auto_fill['activity']
                        is_activity_custom = False

            itinerary_day = ItineraryDay(
                itinerary_id=itinerary.id,
                accommodation_id=day_data.accommodation_id,
                day_number=day_data.day_number,
                day_date=day_date,
                day_title=day_data.day_title,
                description=description,
                activities=activities,
                # meals_included=day_data.meals_included, # Field missing in model
                is_description_custom=is_description_custom,
                is_activity_custom=is_activity_custom,
                atmospheric_image_url=day_data.atmospheric_image_url
            )

            db.add(itinerary_day)
            db.flush()

            # Set destination associations
            if day_data.destination_ids:
                from app.models.destination import Destination
                destinations = db.query(Destination).filter(
                    Destination.id.in_(day_data.destination_ids)
                ).all()
                itinerary_day.destinations = destinations

            # Set accommodation associations
            # if day_data.accommodation_ids:
            #     from app.models.accommodation import Accommodation
            #     accommodations = db.query(Accommodation).filter(
            #         Accommodation.id.in_(day_data.accommodation_ids)
            #     ).all()
            #     itinerary_day.accommodations = accommodations

        # Copy inclusions/exclusions from base tour (can be overridden later)
        itinerary.inclusions = base_tour.inclusions
        itinerary.exclusions = base_tour.exclusions

        # Create travelers
        for traveler_data in travelers:
            traveler = Traveler(
                itinerary_id=itinerary.id,
                **traveler_data.model_dump()
            )
            db.add(traveler)

        db.flush()
        
        # Apply default images
        ItineraryService.apply_default_images(itinerary.id, db)

        return itinerary

    @staticmethod
    def create_custom_itinerary(
        tour_data: ItineraryCreate,
        days: List[ItineraryDayCreate],
        travelers: List[TravelerCreate],
        departure_date: date,
        assigned_to_user_id: UUID,
        created_by_user_id: UUID,
        db: Session
    ) -> Itinerary:
        """
        Method C: Create completely custom itinerary from scratch.

        No base tour - build everything from scratch.
        Auto-fills day content from 2D table where not provided.

        Args:
            tour_data: Itinerary metadata
            days: Day configurations
            travelers: List of travelers
            departure_date: Start date
            assigned_to_user_id: Agent assigned
            created_by_user_id: User who created
            db: Database session

        Returns:
            Created Itinerary

        Raises:
            ValueError: If validation fails
        """
        # Calculate dates
        duration_days = len(days)
        return_date = departure_date + timedelta(days=duration_days - 1)
        day_dates = ItineraryService.calculate_dates(departure_date, duration_days)

        # Generate unique code
        unique_code = ItineraryService.generate_unique_code(db)

        # Create itinerary
        itinerary = Itinerary(
            created_from_base_tour_id=None,  # No base tour
            tour_title=tour_data.tour_title,
            tour_type_id=tour_data.tour_type_id,
            number_of_days=duration_days,
            number_of_nights=duration_days - 1,
            departure_date=departure_date,
            return_date=return_date,
            status=ItineraryStatusEnum.DRAFT,
            creation_method='custom',
            unique_code=unique_code,
            assigned_to_user_id=assigned_to_user_id,
            created_by_user_id=created_by_user_id,
            can_edit_after_tour=False,
            # Client Details
            client_name=tour_data.client_name,
            client_email=tour_data.client_email,
            client_phone=tour_data.client_phone,
            number_of_travelers=tour_data.number_of_travelers,
            # General Info
            accommodation_level_id=tour_data.accommodation_level_id,
            difficulty_level=tour_data.difficulty_level,
            description=tour_data.description,
            highlights=tour_data.highlights
        )

        db.add(itinerary)
        db.flush()

        # Create custom days
        for day_data in days:
            day_date = day_dates[day_data.day_number - 1]

            # Auto-fill if content not provided
            description = day_data.description
            activities = day_data.activities
            is_description_custom = True
            is_activity_custom = True

            if not description or not activities:
                # Try auto-fill from destination combinations
                auto_fill = ItineraryService.auto_fill_day_content(
                    day_data.destination_ids, db
                )

                if auto_fill['type'] in ['single', 'pair']:
                    if not description and auto_fill['description']:
                        description = auto_fill['description']
                        is_description_custom = False

                    if not activities and auto_fill['activity']:
                        activities = auto_fill['activity']
                        is_activity_custom = False

            itinerary_day = ItineraryDay(
                itinerary_id=itinerary.id,
                accommodation_id=day_data.accommodation_id,
                day_number=day_data.day_number,
                day_date=day_date,
                day_title=day_data.day_title,
                description=description,
                activities=activities,
                meals_included=day_data.meals_included,
                is_description_custom=is_description_custom,
                is_activity_custom=is_activity_custom,
                atmospheric_image_url=day_data.atmospheric_image_url
            )

            db.add(itinerary_day)
            db.flush()

            # Set destination associations
            if day_data.destination_ids:
                from app.models.destination import Destination
                destinations = db.query(Destination).filter(
                    Destination.id.in_(day_data.destination_ids)
                ).all()
                itinerary_day.destinations = destinations

            # Set accommodation associations
            # if day_data.accommodation_ids:
            #     from app.models.accommodation import Accommodation
            #     accommodations = db.query(Accommodation).filter(
            #         Accommodation.id.in_(day_data.accommodation_ids)
            #     ).all()
            #     itinerary_day.accommodations = accommodations

        # Set inclusions/exclusions if provided
        if tour_data.inclusion_ids:
            from app.models.inclusion_exclusion import Inclusion
            inclusions = db.query(Inclusion).filter(
                Inclusion.id.in_(tour_data.inclusion_ids)
            ).all()
            itinerary.inclusions = inclusions

        if tour_data.exclusion_ids:
            from app.models.inclusion_exclusion import Exclusion
            exclusions = db.query(Exclusion).filter(
                Exclusion.id.in_(tour_data.exclusion_ids)
            ).all()
            itinerary.exclusions = exclusions

        # Create travelers
        for traveler_data in travelers:
            traveler = Traveler(
                itinerary_id=itinerary.id,
                **traveler_data.model_dump()
            )
            db.add(traveler)

        db.flush()
        
        # Apply default images
        ItineraryService.apply_default_images(itinerary.id, db)

        return itinerary


# Create singleton instance
itinerary_service = ItineraryService()
