import re
import glob

# Find and fix broken description lines
for schema_file in glob.glob('app/schemas/*.py'):
    with open(schema_file, 'r') as f:
        content = f.read()
    
    original = content
    
    # Fix pattern: description="..."]  -> description="..."
    # This happens when examples=["..."] was on the same line and ] got removed
    content = re.sub(r'(description="[^"]*")\]', r'\1', content)
    
    # Fix pattern where closing ] appears after description on next line
    # description="..."]
    # )
    content = re.sub(r'description=("(?:[^"\\]|\\.)*")\]\s*\)', r'description=\1)', content)
    
    if content != original:
        with open(schema_file, 'w') as f:
            f.write(content)
        print(f"✅ Fixed {schema_file}")

print("Done!")
