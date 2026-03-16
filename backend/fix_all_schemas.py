import re
import glob

def remove_examples(content):
    """Remove all examples parameters from Field() calls"""
    # Pattern matches examples=[...] including nested brackets
    pattern = r',?\s*examples=\[[^\]]*\]'
    content = re.sub(pattern, '', content)
    return content

def fix_optional_date_fields(content):
    """Convert Optional[date] = Field(...) patterns to use Annotated if needed"""
    # For fields with constraints, use Annotated
    # For fields without constraints, just use Optional[date] = None
    
    # Pattern: field_name: Optional[date] = Field(None, description=..., examples=...)
    # After removing examples, we might have: Optional[date] = Field(None, description=...)
    # If only Field(None, description=X) or Field(None), can be simplified to: Optional[date] = None
    
    return content  # For now, keep as-is since Pydantic 2.12.5 should handle it

# Process all schema files
schema_files = glob.glob('app/schemas/*.py')
for schema_file in schema_files:
    print(f"Processing {schema_file}...")
    try:
        with open(schema_file, 'r') as f:
            content = f.read()
        
        # Apply fixes
        new_content = remove_examples(content)
        
        # Only write if changed
        if new_content != content:
            with open(schema_file, 'w') as f:
                f.write(new_content)
            print(f"  ✅ Updated {schema_file}")
        else:
            print(f"  ⏭️  No changes needed for {schema_file}")
    except Exception as e:
        print(f"  ❌ Error processing {schema_file}: {e}")

print("\n✅ Done processing all schema files!")
