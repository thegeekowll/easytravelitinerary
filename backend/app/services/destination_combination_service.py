"""
Destination Combination Service.

Handles 2D matrix table logic for pre-written destination descriptions and activities.
Supports symmetrical lookups and auto-fill suggestions.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.destination_combination import DestinationCombination
from app.models.destination import Destination


class AutoFillSuggestion:
    """Suggestion for auto-filling day content when multiple destinations selected."""

    def __init__(self, destination_1_name: str, destination_2_name: str,
                 description: str, activity: str, destination_1_id: UUID, destination_2_id: UUID):
        self.destination_1_name = destination_1_name
        self.destination_2_name = destination_2_name
        self.pair_name = f"{destination_1_name} × {destination_2_name}"
        self.description = description
        self.activity = activity
        self.destination_1_id = destination_1_id
        self.destination_2_id = destination_2_id


class DestinationCombinationService:
    """Service for managing destination combinations (2D matrix table)."""

    @staticmethod
    def _normalize_ids(dest_1_id: UUID, dest_2_id: Optional[UUID] = None) -> tuple[UUID, Optional[UUID]]:
        """
        Normalize destination IDs to maintain consistency.

        For symmetry: always store with dest_1_id < dest_2_id (lexicographically)
        For diagonal: dest_2_id is None
        """
        if dest_2_id is None:
            return (dest_1_id, None)

        # Convert to strings for comparison to maintain consistency
        id1_str, id2_str = str(dest_1_id), str(dest_2_id)

        if id1_str < id2_str:
            return (dest_1_id, dest_2_id)
        else:
            return (dest_2_id, dest_1_id)

    @staticmethod
    def get_combination(
        dest_1_id: UUID,
        dest_2_id: Optional[UUID] = None,
        db: Session = None,
        allow_reverse: bool = True  # Default to True to maintain current behavior for existing data check
    ) -> Optional[DestinationCombination]:
        """
        Get a destination combination from the 2D table.

        Args:
            dest_1_id: First destination ID
            dest_2_id: Second destination ID (None for diagonal/single destination)
            db: Database session
            allow_reverse: If True, also checks (dest_2, dest_1) if (dest_1, dest_2) not found

        Returns:
            DestinationCombination if found, None otherwise
        """
        # Direct lookup first (Directional)
        combination = db.query(DestinationCombination).filter(
            DestinationCombination.destination_1_id == dest_1_id,
            DestinationCombination.destination_2_id == dest_2_id
        ).first()

        # If not found and reverse is allowed (and it's a pair, not diagonal)
        if not combination and allow_reverse and dest_2_id:
            combination = db.query(DestinationCombination).filter(
                DestinationCombination.destination_1_id == dest_2_id,
                DestinationCombination.destination_2_id == dest_1_id
            ).first()

        return combination

    @staticmethod
    def get_suggestions_for_multiple(
        destination_ids: List[UUID],
        db: Session
    ) -> List[AutoFillSuggestion]:
        """
        Get auto-fill suggestions when 3+ destinations are selected.

        Generates all possible pairs and looks up their combinations.
        Returns list of suggestions for agent to choose from.

        Args:
            destination_ids: List of 3+ destination IDs
            db: Database session

        Returns:
            List of AutoFillSuggestion objects (one per found combination)

        Example:
            destination_ids = [serengeti, ngorongoro, tarangire]
            Returns suggestions for:
            - Serengeti × Ngorongoro
            - Ngorongoro × Tarangire
            - Serengeti × Tarangire
        """
        if len(destination_ids) < 3:
            return []

        suggestions = []

        # Get destination names for display
        destinations = db.query(Destination).filter(
            Destination.id.in_(destination_ids)
        ).all()

        dest_map = {str(d.id): d.name for d in destinations}

        # Generate all pairs (combinations, not permutations)
        seen_pairs = set()

        for i, dest_1_id in enumerate(destination_ids):
            for dest_2_id in destination_ids[i+1:]:
                # Check directly A->B
                # The service.get_combination method will handle reverse lookup if allow_reverse is True (default)
                
                # Look up combination
                combination = DestinationCombinationService.get_combination(
                    dest_1_id, dest_2_id, db
                )

                if combination:
                    # Get destination names
                    dest_1_name = dest_map.get(str(combination.destination_1_id), "Unknown")
                    dest_2_name = dest_map.get(str(combination.destination_2_id), "Unknown")

                    suggestion = AutoFillSuggestion(
                        destination_1_name=dest_1_name,
                        destination_2_name=dest_2_name,
                        description=combination.description_content,
                        activity=combination.activity_content,
                        destination_1_id=combination.destination_1_id,
                        destination_2_id=combination.destination_2_id
                    )
                    suggestions.append(suggestion)

        return suggestions

    @staticmethod
    def create_combination(
        dest_1_id: UUID,
        dest_2_id: Optional[UUID],
        description: str,
        activity: str,
        db: Session,
        bidirectional: bool = False
    ) -> DestinationCombination:
        """
        Create a new destination combination in the 2D table.
        Supports directional combinations (A->B != B->A).

        Args:
            dest_1_id: First destination ID
            dest_2_id: Second destination ID (None for diagonal)
            description: Pre-written description content
            activity: Pre-written activity content
            db: Database session
            bidirectional: If True, also creates/overwrites the reverse combination

        Returns:
            Created DestinationCombination (the primary one)

        Raises:
            ValueError: If combination (in this specific direction) already exists
        """
        # NO NORMALIZATION - respecting user direction

        # Check if destinations exist
        dest_1 = db.query(Destination).filter(Destination.id == dest_1_id).first()
        if not dest_1:
            raise ValueError(f"Destination {dest_1_id} not found")

        if dest_2_id:
            dest_2 = db.query(Destination).filter(Destination.id == dest_2_id).first()
            if not dest_2:
                raise ValueError(f"Destination {dest_2_id} not found")

        # Check if combination already exists (in this specific direction)
        existing = db.query(DestinationCombination).filter(
            DestinationCombination.destination_1_id == dest_1_id,
            DestinationCombination.destination_2_id == dest_2_id
        ).first()

        if existing:
            if dest_2_id:
                raise ValueError(
                    f"Combination already exists from {dest_1.name} to {dest_2.name}"
                )
            else:
                raise ValueError(f"Diagonal combination already exists for {dest_1.name}")

        # Create combination
        combination = DestinationCombination(
            destination_1_id=dest_1_id,
            destination_2_id=dest_2_id,
            description_content=description,
            activity_content=activity
        )

        db.add(combination)
        db.flush()

        # Handle Bidirectional
        if bidirectional and dest_2_id and dest_1_id != dest_2_id:
             # Check if reverse exists
            reverse_existing = db.query(DestinationCombination).filter(
                DestinationCombination.destination_1_id == dest_2_id,
                DestinationCombination.destination_2_id == dest_1_id
            ).first()
            
            if not reverse_existing:
                reverse_combo = DestinationCombination(
                    destination_1_id=dest_2_id,
                    destination_2_id=dest_1_id,
                    description_content=description,
                    activity_content=activity
                )
                db.add(reverse_combo)
                db.flush()

        return combination

    @staticmethod
    def update_combination(
        combination_id: UUID,
        description: Optional[str],
        activity: Optional[str],
        db: Session,
        bidirectional: bool = False
    ) -> DestinationCombination:
        """
        Update an existing destination combination.

        Args:
            combination_id: Combination ID to update
            description: New description (or None to keep existing)
            activity: New activity (or None to keep existing)
            db: Database session
            bidirectional: If True, also updates/creates the reverse combination

        Returns:
            Updated DestinationCombination

        Raises:
            ValueError: If combination not found
        """
        combination = db.query(DestinationCombination).filter(
            DestinationCombination.id == combination_id
        ).first()

        if not combination:
            raise ValueError(f"Combination {combination_id} not found")

        # Capture old values if new ones are None? No, we update what is provided.
        # But for reverse creation, we need full values if creating new.
        # If updating reverse, we match what's provided.

        if description is not None:
            combination.description_content = description

        if activity is not None:
            combination.activity_content = activity

        db.flush()

        # Handle Bidirectional
        if bidirectional and combination.destination_2_id and combination.destination_1_id != combination.destination_2_id:
            # Find reverse
            reverse_combo = db.query(DestinationCombination).filter(
                DestinationCombination.destination_1_id == combination.destination_2_id,
                DestinationCombination.destination_2_id == combination.destination_1_id
            ).first()

            if reverse_combo:
                # Update existing reverse
                if description is not None:
                    reverse_combo.description_content = description
                if activity is not None:
                    reverse_combo.activity_content = activity
                db.flush()
            else:
                # Create reverse if not exists
                # We need description/activity. If they are None in this call, we should use existing values from primary?
                # User intention "Make it bidirectional" with partial update:
                # likely implies "Make reverse match current state of primary".
                # So use `combination.description_content` (which includes just-applied updates).
                
                DestinationCombinationService.create_combination(
                    dest_1_id=combination.destination_2_id,
                    dest_2_id=combination.destination_1_id,
                    description=combination.description_content,
                    activity=combination.activity_content,
                    db=db,
                    bidirectional=False # Avoid infinite loop
                )

        return combination

    @staticmethod
    def delete_combination(combination_id: UUID, db: Session) -> None:
        """
        Delete a destination combination.

        Args:
            combination_id: Combination ID to delete
            db: Database session

        Raises:
            ValueError: If combination not found
        """
        combination = db.query(DestinationCombination).filter(
            DestinationCombination.id == combination_id
        ).first()

        if not combination:
            raise ValueError(f"Combination {combination_id} not found")

        db.delete(combination)
        db.flush()

    @staticmethod
    def get_grid_data(
        page_row: int = 0,
        page_col: int = 0,
        page_size: int = 20,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Get paginated grid data for visual 2D matrix UI.

        Returns destinations for rows/columns and existing combinations.
        Used for building an Excel-like grid interface.

        Args:
            page_row: Row page number (0-indexed)
            page_col: Column page number (0-indexed)
            page_size: Number of destinations per page
            db: Database session

        Returns:
            Dictionary with:
            - row_destinations: List of destinations for rows
            - col_destinations: List of destinations for columns
            - combinations: List of existing combinations in this grid section
            - total_destinations: Total count
        """
        # Get total count
        total = db.query(Destination).count()

        # Get destinations for rows
        row_destinations = db.query(Destination).order_by(
            Destination.name
        ).offset(page_row * page_size).limit(page_size).all()

        # Get destinations for columns
        col_destinations = db.query(Destination).order_by(
            Destination.name
        ).offset(page_col * page_size).limit(page_size).all()

        # Get row and column IDs
        row_ids = [d.id for d in row_destinations]
        col_ids = [d.id for d in col_destinations]

        # Get all combinations in this grid section
        combinations = db.query(DestinationCombination).filter(
            or_(
                and_(
                    DestinationCombination.destination_1_id.in_(row_ids),
                    or_(
                        DestinationCombination.destination_2_id.in_(col_ids),
                        DestinationCombination.destination_2_id == None
                    )
                ),
                and_(
                    DestinationCombination.destination_1_id.in_(col_ids),
                    or_(
                        DestinationCombination.destination_2_id.in_(row_ids),
                        DestinationCombination.destination_2_id == None
                    )
                )
            )
        ).all()

        print(f"DEBUG: Grid Data - Found {len(combinations)} combinations")
        for c in combinations:
            print(f"DEBUG: Combo {c.destination_1_id} -> {c.destination_2_id} | {c.description_content}")

        return {
            'row_destinations': row_destinations,
            'col_destinations': col_destinations,
            'combinations': combinations,
            'total_destinations': total,
            'page_row': page_row,
            'page_col': page_col,
            'page_size': page_size
        }

    @staticmethod
    def search_combinations(
        query: str,
        db: Session
    ) -> List[DestinationCombination]:
        """
        Search combinations by destination names or content.

        Args:
            query: Search query string
            db: Database session

        Returns:
            List of matching DestinationCombination objects
        """
        # Search in description and activity content
        combinations = db.query(DestinationCombination).filter(
            or_(
                DestinationCombination.description_content.ilike(f"%{query}%"),
                DestinationCombination.activity_content.ilike(f"%{query}%")
            )
        ).all()

        return combinations

    @staticmethod
    def get_chained_content(
        destination_ids: list[UUID],
        db: Session
    ) -> dict:
        """
        Get chained content for a sequence of destinations. 
        Concatenates content for A->B, B->C, C->D, etc.
        """
        if not destination_ids:
            return {'description': None, 'activity': None}
        
        # If only 1 destination, fallback to diagonal (A->A)
        if len(destination_ids) == 1:
            combo = DestinationCombinationService.get_combination(destination_ids[0], None, db)
            return {
                'description': combo.description_content if combo else None,
                'activity': combo.activity_content if combo else None
            }

        descriptions = []
        activities = []
        
        # Iterate through pairs
        for i in range(len(destination_ids) - 1):
            id1 = destination_ids[i]
            id2 = destination_ids[i+1]
            
            # Lookup with allow_reverse=False (strict direction) or True? 
            # User said: "get data of A-B and B-C". 
            # If A->B doesn't exist but B->A does, strict check prefers A->B.
            # But the 'get_combination' method defaults to allow_reverse=True. 
            # If I want true directional accuracy, I should probably rely on get_combination's check
            # but usually for flow, we want the specific direction.
            # However, I will trust get_combination to handle it (it tries direct first).
            combo = DestinationCombinationService.get_combination(id1, id2, db)
            
            if combo:
                if combo.description_content:
                    descriptions.append(combo.description_content)
                if combo.activity_content:
                    activities.append(combo.activity_content)
        
        return {
            'description': "\n\n".join(descriptions) if descriptions else None,
            'activity': "\n\n".join(activities) if activities else None
        }


# Create singleton instance
destination_combination_service = DestinationCombinationService()
