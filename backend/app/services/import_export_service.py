import csv
import io
import json
from typing import List, Dict, Any, Type
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

class ImportExportService:
    """Service to handle generating and parsing CSVs for SQLAlchemy models."""

    @staticmethod
    def _parse_value_for_csv(val: Any) -> str:
        """Convert a python variable to a CSV safe string."""
        if val is None:
            return ""
        if isinstance(val, (dict, list)):
            return json.dumps(val)
        if isinstance(val, datetime):
            return val.isoformat()
        if isinstance(val, uuid.UUID):
            return str(val)
        if hasattr(val, 'value'): # For Enums
            return str(val.value)
        return str(val)

    @staticmethod
    def export_to_csv(query_results: List[Any], exclude_fields: List[str] = None) -> io.StringIO:
        """Generate a CSV StringIO from a list of SQLAlchemy objects or dicts."""
        output = io.StringIO()
        if not query_results:
            return output
        
        exclude_fields = exclude_fields or ['hashed_password']

        # Determine headers based on the first item
        first_item = query_results[0]
        if hasattr(first_item, '__table__'):
            # It's an ORM model
            headers = [c.name for c in first_item.__table__.columns if c.name not in exclude_fields]
        elif isinstance(first_item, dict):
            headers = [k for k in first_item.keys() if k not in exclude_fields]
        else:
            raise ValueError("Unsupported data type for CSV export")

        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()

        for item in query_results:
            row = {}
            for col in headers:
                val = getattr(item, col) if hasattr(item, col) else (item.get(col) if isinstance(item, dict) else None)
                row[col] = ImportExportService._parse_value_for_csv(val)
            writer.writerow(row)

        output.seek(0)
        return output

    @staticmethod
    def parse_csv(csv_content: str) -> List[Dict[str, Any]]:
        """Parse raw CSV string into a list of dictionaries with basic type coercion."""
        f = io.StringIO(csv_content)
        reader = csv.DictReader(f)
        results = []

        for row in reader:
            parsed_row = {}
            for k, v in row.items():
                if v == "":
                    parsed_row[k] = None
                    continue
                
                # Try to parse JSON arrays/objects
                if (v.startswith('[') and v.endswith(']')) or (v.startswith('{') and v.endswith('}')):
                    try:
                        parsed_row[k] = json.loads(v)
                    except json.JSONDecodeError:
                        parsed_row[k] = v
                # Booleans
                elif v.lower() in ('true', 'false'):
                    parsed_row[k] = v.lower() == 'true'
                else:
                    parsed_row[k] = v
            results.append(parsed_row)
            
        return results
