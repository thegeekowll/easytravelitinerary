import re

def fix_pydantic_fields(content):
    """Convert Optional[Type] = Field(...) to Annotated[Optional[Type], Field(...)]"""
    
    # Add Annotated import if not present
    if 'from typing import' in content and 'Annotated' not in content:
        content = content.replace(
            'from typing import',
            'from typing import Annotated,'
        )
    
    # Pattern to match: field_name: Optional[Type] = Field(...)
    # Captures: field_name, Type, Field arguments
    pattern = r'(\w+):\s*Optional\[([^\]]+)\]\s*=\s*(Field\([^)]*(?:\([^)]*\))*[^)]*\))'
    
    def replacer(match):
        field_name = match.group(1)
        type_name = match.group(2)
        field_call = match.group(3)
        
        # Extract default value from Field if present
        # Check if Field has first positional arg (default value)
        field_inner = field_call[6:-1]  # Remove "Field(" and ")"
        
        # Handle case where Field(None, ...) - default is None
        if field_inner.strip().startswith('None'):
            # Move default outside of Field
            # Field(None, desc=...) -> Field(desc=...)
            field_inner_no_none = field_inner.split(',', 1)[1].strip() if ',' in field_inner else ''
            if field_inner_no_none:
                new_field = f'Field({field_inner_no_none})'
            else:
                new_field = 'Field()'
            return f'{field_name}: Annotated[Optional[{type_name}], {new_field}] = None'
        elif field_inner.strip().startswith('...'):
            # Field(..., desc=...) - required field
            return f'{field_name}: Annotated[Optional[{type_name}], {field_call}]'
        else:
            # Field has a default value
            # Try to extract it
            parts = field_inner.split(',', 1)
            if len(parts) == 2:
                default_val = parts[0].strip()
                field_args = parts[1].strip()
                new_field = f'Field({field_args})' if field_args else 'Field()'
                return f'{field_name}: Annotated[Optional[{type_name}], {new_field}] = {default_val}'
            else:
                # Just a default, no other args
                return f'{field_name}: Annotated[Optional[{type_name}], Field()] = {field_inner}'
    
    content = re.sub(pattern, replacer, content)
    
    return content

# Read the file
with open('app/schemas/itinerary.py', 'r') as f:
    content = f.read()

# Fix the patterns
new_content = fix_pydantic_fields(content)

# Write back
with open('app/schemas/itinerary.py', 'w') as f:
    f.write(new_content)

print("✅ Fixed Pydantic field patterns in itinerary.py")
