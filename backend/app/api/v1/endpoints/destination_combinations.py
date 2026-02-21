"""
Destination Combination endpoints.

Manages the 2D matrix table of pre-written destination descriptions and activities.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
import csv
from io import StringIO

from app.api.v1.deps import (
    get_db,
    get_current_active_user,
    require_admin,
    PaginationParams
)
from app.models.user import User
from app.schemas.destination_combination import (
    DestinationCombinationCreate,
    DestinationCombinationUpdate,
    DestinationCombinationResponse,
    DestinationCombinationLookup,
    AutoFillResponse,
    CombinationGridResponse
)
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services.destination_combination_service import destination_combination_service
from app.models.destination_combination import DestinationCombination
from app.services.import_export_service import ImportExportService
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/destination-combinations", tags=["destination-combinations"])


@router.get("", response_model=PaginatedResponse[DestinationCombinationResponse])
def list_destination_combinations(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(None, description="Search in content"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all destination combinations with pagination."""
    query = db.query(DestinationCombination)

    # Search filter
    if search:
        combinations = destination_combination_service.search_combinations(search, db)
        total = len(combinations)
        items = combinations[pagination.skip:pagination.skip + pagination.limit]
    else:
        # Get total count
        total = query.count()

        # Apply pagination
        items = query.offset(pagination.skip).limit(pagination.limit).all()

    total_pages = (total + pagination.page_size - 1) // pagination.page_size

    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
        has_next=pagination.page < total_pages,
        has_prev=pagination.page > 1
    )


@router.get("/search", response_model=Optional[DestinationCombinationResponse])
def search_specific_combination(
    destination_1_id: UUID = Query(..., description="First destination ID"),
    destination_2_id: Optional[UUID] = Query(None, description="Second destination ID (None for diagonal)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Search for a specific destination combination.

    Use this to look up pre-written content for destination pairs.
    - Single destination: provide only destination_1_id
    - Two destinations: provide both IDs (order doesn't matter due to symmetry)
    """
    combination = destination_combination_service.get_combination(
        destination_1_id, destination_2_id, db
    )

    if not combination:
        return None

    return combination


@router.post("/auto-fill", response_model=AutoFillResponse)
def auto_fill_destinations(
    request: DestinationCombinationLookup,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get auto-fill suggestions for destination combinations.

    - 1 destination: Returns single description/activity from diagonal
    - 2 destinations: Returns single description/activity from pair
    - 3+ destinations: Returns list of suggestions to choose from
    """
    destination_ids = request.destination_ids

    if request.mode == "chain":
        # Sequential chain lookup
        result = destination_combination_service.get_chained_content(destination_ids, db)
        return AutoFillResponse(
            type="chain",
            description=result['description'],
            activity=result['activity'],
            suggestions=[]
        )

    if len(destination_ids) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one destination required"
        )

    elif len(destination_ids) == 1:
        # Single destination - diagonal lookup
        combination = destination_combination_service.get_combination(
            destination_ids[0], None, db
        )

        if not combination:
            return AutoFillResponse(
                type="single",
                description=None,
                activity=None,
                suggestions=[]
            )

        return AutoFillResponse(
            type="single",
            description=combination.description_content,
            activity=combination.activity_content,
            suggestions=[]
        )

    elif len(destination_ids) == 2:
        # Two destinations - direct pair lookup
        combination = destination_combination_service.get_combination(
            destination_ids[0], destination_ids[1], db
        )

        if not combination:
            return AutoFillResponse(
                type="pair",
                description=None,
                activity=None,
                suggestions=[]
            )

        return AutoFillResponse(
            type="pair",
            description=combination.description_content,
            activity=combination.activity_content,
            suggestions=[]
        )

    else:
        # 3+ destinations - return suggestions
        suggestions = destination_combination_service.get_suggestions_for_multiple(
            destination_ids, db
        )

        return AutoFillResponse(
            type="multiple",
            description=None,
            activity=None,
            suggestions=[
                {
                    "pair_name": s.pair_name,
                    "destination_1_id": str(s.destination_1_id),
                    "destination_2_id": str(s.destination_2_id),
                    "description": s.description,
                    "activity": s.activity
                }
                for s in suggestions
            ]
        )


@router.post("", response_model=DestinationCombinationResponse, status_code=status.HTTP_201_CREATED)
def create_destination_combination(
    combination_data: DestinationCombinationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new destination combination (admin only)."""
    try:
        combination = destination_combination_service.create_combination(
            dest_1_id=combination_data.destination_1_id,
            dest_2_id=combination_data.destination_2_id,
            description=combination_data.description_content,
            activity=combination_data.activity_content,
            db=db,
            bidirectional=combination_data.bidirectional
        )

        db.commit()
        db.refresh(combination)

        return combination

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create combination: {str(e)}"
        )


@router.patch("/{combination_id}", response_model=DestinationCombinationResponse)
def update_destination_combination(
    combination_id: UUID,
    combination_data: DestinationCombinationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a destination combination (admin only)."""
    try:
        combination = destination_combination_service.update_combination(
            combination_id=combination_id,
            description=combination_data.description_content,
            activity=combination_data.activity_content,
            db=db,
            bidirectional=combination_data.bidirectional or False
        )

        db.commit()
        db.refresh(combination)

        return combination

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update combination: {str(e)}"
        )


@router.delete("/{combination_id}", response_model=MessageResponse)
def delete_destination_combination(
    combination_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a destination combination (admin only)."""
    try:
        destination_combination_service.delete_combination(combination_id, db)
        db.commit()

        return MessageResponse(message="Destination combination deleted successfully")

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete combination: {str(e)}"
        )


@router.get("/grid", response_model=CombinationGridResponse)
def get_combination_grid(
    page_row: int = Query(0, ge=0, description="Row page number"),
    page_col: int = Query(0, ge=0, description="Column page number"),
    page_size: int = Query(20, ge=1, le=100, description="Destinations per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get paginated grid data for visual 2D matrix UI.

    Returns destinations and combinations for building an Excel-like grid interface.
    """
    try:
        grid_data = destination_combination_service.get_grid_data(
            page_row=page_row,
            page_col=page_col,
            page_size=page_size,
            db=db
        )

        return CombinationGridResponse(**grid_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get grid data: {str(e)}"
        )


@router.get("/export/csv")
def export_combinations_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Export all destination combinations to CSV format."""
    items = db.query(DestinationCombination).all()
    output = ImportExportService.export_to_csv(items, exclude_fields=['id'])
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=destination_combinations.csv"}
    )

@router.post("/bulk-import", response_model=dict)
def bulk_import_combinations(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Bulk import destination combinations from CSV.
    Matches on destination_1_id and destination_2_id.
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
                dest_1_id = row.get('destination_1_id')
                dest_2_id = row.get('destination_2_id')

                if not dest_1_id:
                    failed.append({'row': row_num, 'error': 'Missing required destination_1_id'})
                    continue
                
                # Check existing combination
                existing = None
                if dest_2_id:
                    existing = destination_combination_service.get_combination(UUID(dest_1_id), UUID(dest_2_id), db)
                else:
                    existing = destination_combination_service.get_combination(UUID(dest_1_id), None, db)
                
                if existing:
                    # Update Fields
                    for k, v in row.items():
                        if hasattr(existing, k) and k not in ['id', 'created_at', 'updated_at']:
                            setattr(existing, k, v)
                    imported.append(f"{dest_1_id} x {dest_2_id}")
                else:
                    # Create
                    comb_kwargs = {k: v for k, v in row.items() if hasattr(DestinationCombination, k) and k not in ['id', 'created_at', 'updated_at']}
                    comb_kwargs['destination_1_id'] = UUID(dest_1_id)
                    if dest_2_id:
                        comb_kwargs['destination_2_id'] = UUID(dest_2_id)
                    new_item = DestinationCombination(**comb_kwargs)
                    db.add(new_item)
                    imported.append(f"{dest_1_id} x {dest_2_id}")
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
