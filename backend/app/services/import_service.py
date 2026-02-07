"""
CSV Import Service.

Handles bulk data imports from CSV files for destinations, accommodations, and tours.
"""
import csv
from io import StringIO
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.destination import Destination
from app.models.accommodation import Accommodation, AccommodationType
from app.models.base_tour import BaseTour, BaseTourDay, TourType
from app.schemas.destination import DestinationCreate
from app.schemas.accommodation import AccommodationCreate
from app.schemas.base_tour import BaseTourCreate, BaseTourDayCreate


class ImportService:
    """Service for importing data from CSV files."""

    @staticmethod
    async def import_destinations_from_csv(
        csv_content: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Import destinations from CSV file.

        Expected columns: name, country, region, description, best_time_to_visit,
                         average_temp_celsius, highlights, activities
        """
        imported = []
        failed = []

        try:
            csv_file = StringIO(csv_content)
            reader = csv.DictReader(csv_file)

            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                try:
                    # Parse highlights and activities (comma-separated)
                    highlights = [h.strip() for h in row.get('highlights', '').split(',') if h.strip()]
                    activities = [a.strip() for a in row.get('activities', '').split(',') if a.strip()]

                    # Check if destination already exists
                    existing = db.query(Destination).filter(
                        Destination.name == row['name'],
                        Destination.country == row['country']
                    ).first()

                    if existing:
                        failed.append({
                            'row': row_num,
                            'data': row,
                            'error': 'Destination already exists'
                        })
                        continue

                    # Create destination
                    destination = Destination(
                        name=row['name'],
                        country=row['country'],
                        region=row.get('region'),
                        description=row.get('description'),
                        best_time_to_visit=row.get('best_time_to_visit'),
                        average_temp_celsius=float(row['average_temp_celsius']) if row.get('average_temp_celsius') else None,
                        highlights=highlights,
                        activities=activities
                    )

                    db.add(destination)
                    db.flush()

                    imported.append({
                        'row': row_num,
                        'name': destination.name,
                        'id': str(destination.id)
                    })

                except Exception as e:
                    failed.append({
                        'row': row_num,
                        'data': row,
                        'error': str(e)
                    })

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
            return {
                'success': False,
                'error': f'Failed to parse CSV: {str(e)}',
                'imported_count': 0,
                'failed_count': 0,
                'imported': [],
                'failed': []
            }

    @staticmethod
    async def import_accommodations_from_csv(
        csv_content: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Import accommodations from CSV file.

        Expected columns: name, accommodation_type_id, destination_id, location,
                         star_rating, description, amenities, contact_email, contact_phone
        """
        imported = []
        failed = []

        try:
            csv_file = StringIO(csv_content)
            reader = csv.DictReader(csv_file)

            for row_num, row in enumerate(reader, start=2):
                try:
                    # Parse amenities (comma-separated)
                    amenities = [a.strip() for a in row.get('amenities', '').split(',') if a.strip()]

                    # Validate foreign keys
                    type_id = UUID(row['accommodation_type_id'])
                    destination_id = UUID(row['destination_id'])

                    acc_type = db.query(AccommodationType).filter(AccommodationType.id == type_id).first()
                    if not acc_type:
                        failed.append({
                            'row': row_num,
                            'data': row,
                            'error': f'Accommodation type {type_id} not found'
                        })
                        continue

                    destination = db.query(Destination).filter(Destination.id == destination_id).first()
                    if not destination:
                        failed.append({
                            'row': row_num,
                            'data': row,
                            'error': f'Destination {destination_id} not found'
                        })
                        continue

                    # Check if accommodation already exists
                    existing = db.query(Accommodation).filter(
                        Accommodation.name == row['name'],
                        Accommodation.destination_id == destination_id
                    ).first()

                    if existing:
                        failed.append({
                            'row': row_num,
                            'data': row,
                            'error': 'Accommodation already exists'
                        })
                        continue

                    # Create accommodation
                    accommodation = Accommodation(
                        name=row['name'],
                        accommodation_type_id=type_id,
                        destination_id=destination_id,
                        location=row.get('location'),
                        star_rating=int(row['star_rating']) if row.get('star_rating') else None,
                        description=row.get('description'),
                        amenities=amenities,
                        contact_email=row.get('contact_email'),
                        contact_phone=row.get('contact_phone')
                    )

                    db.add(accommodation)
                    db.flush()

                    imported.append({
                        'row': row_num,
                        'name': accommodation.name,
                        'id': str(accommodation.id)
                    })

                except Exception as e:
                    failed.append({
                        'row': row_num,
                        'data': row,
                        'error': str(e)
                    })

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
            return {
                'success': False,
                'error': f'Failed to parse CSV: {str(e)}',
                'imported_count': 0,
                'failed_count': 0,
                'imported': [],
                'failed': []
            }

    @staticmethod
    async def import_base_tours_from_csv(
        csv_content: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Import base tours from CSV file.

        Expected columns: title, tour_type_id, duration_days, description,
                         highlights, difficulty_level, is_active

        Note: This only imports the tour header. Days must be added separately.
        """
        imported = []
        failed = []

        try:
            csv_file = StringIO(csv_content)
            reader = csv.DictReader(csv_file)

            for row_num, row in enumerate(reader, start=2):
                try:
                    # Parse highlights (comma-separated)
                    highlights = [h.strip() for h in row.get('highlights', '').split(',') if h.strip()]

                    # Validate tour type
                    type_id = UUID(row['tour_type_id'])
                    tour_type = db.query(TourType).filter(TourType.id == type_id).first()
                    if not tour_type:
                        failed.append({
                            'row': row_num,
                            'data': row,
                            'error': f'Tour type {type_id} not found'
                        })
                        continue

                    # Check if tour already exists
                    existing = db.query(BaseTour).filter(BaseTour.title == row['title']).first()
                    if existing:
                        failed.append({
                            'row': row_num,
                            'data': row,
                            'error': 'Tour with this title already exists'
                        })
                        continue

                    # Create tour
                    tour = BaseTour(
                        title=row['title'],
                        tour_type_id=type_id,
                        duration_days=int(row['duration_days']),
                        description=row.get('description'),
                        highlights=highlights,
                        difficulty_level=row.get('difficulty_level'),
                        is_active=row.get('is_active', 'true').lower() == 'true'
                    )

                    db.add(tour)
                    db.flush()

                    imported.append({
                        'row': row_num,
                        'title': tour.title,
                        'id': str(tour.id)
                    })

                except Exception as e:
                    failed.append({
                        'row': row_num,
                        'data': row,
                        'error': str(e)
                    })

            db.commit()

            return {
                'success': True,
                'imported_count': len(imported),
                'failed_count': len(failed),
                'imported': imported,
                'failed': failed,
                'note': 'Tour days must be added separately via the API'
            }

        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'error': f'Failed to parse CSV: {str(e)}',
                'imported_count': 0,
                'failed_count': 0,
                'imported': [],
                'failed': []
            }


# Create singleton instance
import_service = ImportService()
