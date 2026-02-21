import os
import re

def replace_colors(directory):
    replacements = {
        r'text-blue-(?:500|600|700|800|900)': 'text-primary',
        r'bg-blue-(?:50|100)': 'bg-primary/10',
        r'bg-blue-200': 'bg-primary/20',
        r'bg-blue-500': 'bg-primary/80',
        r'bg-blue-(?:600|700|800|900)': 'bg-primary',
        r'border-blue-(?:100|200)': 'border-primary/20',
        r'border-blue-(?:300|400)': 'border-primary/50',
        r'border-blue-(?:500|600|700|800|900)': 'border-primary',
        r'ring-blue-(?:400|500|600)': 'ring-primary',
        r'hover:text-blue-(?:500|600|700)': 'hover:text-primary',
        r'hover:bg-blue-(?:50|100)': 'hover:bg-primary/10',
        r'hover:border-blue-(?:500|600|700)': 'hover:border-primary',
        r'text-blue-100': 'text-primary-foreground', # assuming on dark bg
        r'text-blue-400': 'text-primary/80',
    }

    modified_files = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.tsx') or file.endswith('.ts') or file.endswith('.jsx') or file.endswith('.js'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    for pattern, replacement in replacements.items():
                        content = re.sub(pattern, replacement, content)
                        
                    if content != original_content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        modified_files += 1
                        print(f"Updated: {filepath}")
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
                    
    print(f"\nDone. Modified {modified_files} files.")

if __name__ == "__main__":
    replace_colors("frontend/app")
