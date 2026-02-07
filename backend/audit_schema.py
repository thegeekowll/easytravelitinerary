
import sys
import os
from sqlalchemy import inspect, text

# Add the parent directory to sys.path to ensure we can import 'app'
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from app.db.session import engine, Base
# Import all models to ensure they are registered with Base
from app.models import *

def audit_schema():
    inspector = inspect(engine)
    
    print("="*60)
    print("STARTING SCHEMA AUDIT")
    print("="*60)
    
    issues_found = 0
    
    # Get all table names from the database
    db_table_names = inspector.get_table_names()
    
    # Iterate over all registered models
    for mapper in Base.registry.mappers:
        model = mapper.class_
        table_name = model.__tablename__
        
        print(f"Checking model: {model.__name__} (Table: {table_name})")
        
        if table_name not in db_table_names:
            print(f"  [CRITICAL] Table '{table_name}' MISSING in database!")
            issues_found += 1
            continue
            
        # Get columns from database
        db_columns = {col['name']: col for col in inspector.get_columns(table_name)}
        
        # Get columns from model
        model_columns = mapper.columns
        
        for column in model_columns:
            col_name = column.name
            
            if col_name not in db_columns:
                print(f"  [ERROR] Column '{col_name}' missing in DB table '{table_name}'")
                issues_found += 1
            else:
                # Optional: Check type mismatches (basic check)
                db_col_type = str(db_columns[col_name]['type']).lower()
                model_col_type = str(column.type).lower()
                
                # Very basic type check - can be expanded
                # print(f"    {col_name}: DB={db_col_type}, Model={model_col_type}")
                pass
                
    print("="*60)
    if issues_found:
        print(f"AUDIT COMPLETE: {issues_found} ISSUES FOUND")
    else:
        print("AUDIT COMPLETE: NO SCHEMA DISCREPANCIES FOUND")
    print("="*60)

if __name__ == "__main__":
    audit_schema()
