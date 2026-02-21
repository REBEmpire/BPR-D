import os
import re

def fix_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return False

    # Regex to find unquoted Author/Model lines with pipes/colons
    # Look for: Author: Name | Model: ID
    # Capture groups: 1=Key (Author), 2=Value (Name | Model: ID)
    # We only want to quote if it's NOT already quoted.

    # Pattern: ^(Author|Model):\s*(?!["'])(.*\|.*:.*)(?<!["'])\s*$
    # This checks for keys Author or Model, followed by text containing | and :

    pattern = re.compile(r'^(Author|Model|Date):\s*(?!["\'])(.*\|.*)(?<!["\'])\s*$', re.MULTILINE)

    new_content = content
    modified = False

    def replacement(match):
        key = match.group(1)
        value = match.group(2).strip()
        return f'{key}: "{value}"'

    if pattern.search(content):
        new_content = pattern.sub(replacement, content)
        modified = True

    if modified:
        print(f"Fixing {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    count = 0
    for root, dirs, files in os.walk('.'):
        if '.git' in dirs:
            dirs.remove('.git')
        if 'node_modules' in dirs:
            dirs.remove('node_modules')

        for file in files:
            if file.endswith('.md'):
                if fix_file(os.path.join(root, file)):
                    count += 1
    print(f"Fixed {count} files.")

if __name__ == '__main__':
    main()
