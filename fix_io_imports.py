import os
import re

def fix_imports_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # IF the file uses tascpy.io.load but doesn't import tascpy, add it.
    if 'tascpy.io.load(' in content and 'import tascpy' not in content:
        # Find the last import and add our import right after
        lines = content.split('\n')
        last_import_idx = -1
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                last_import_idx = i
                
        if last_import_idx != -1:
            lines.insert(last_import_idx + 1, 'import tascpy')
            content = '\n'.join(lines)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Added 'import tascpy' to {filepath}")

def main():
    search_dirs = [
        'examples',
        'tests',
    ]
    for search_dir in search_dirs:
        for root, dirs, files in os.walk(search_dir):
            for file in files:
                if file.endswith('.py'):
                    fix_imports_in_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
