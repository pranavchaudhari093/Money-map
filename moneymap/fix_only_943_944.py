#!/usr/bin/env python
"""Fix ONLY lines 943-944 in app.py with proper indentation"""

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Check current state
print("Before fix:")
print(f"Line 943 ({len(lines[942]) - len(lines[942].lstrip())} spaces): {repr(lines[942][:50])}")
print(f"Line 944 ({len(lines[943]) - len(lines[943].lstrip())} spaces): {repr(lines[943][:50])}")

# Fix ONLY these two lines
lines[942] = '       return redirect(url_for(\'dashboard\'))\n'  # 8 spaces
lines[943] = '   return redirect(url_for(\'login\'))\n'  # 4 spaces

print("\nAfter fix:")
print(f"Line 943 ({len(lines[942]) - len(lines[942].lstrip())} spaces): {repr(lines[942][:50])}")
print(f"Line 944 ({len(lines[943]) - len(lines[943].lstrip())} spaces): {repr(lines[943][:50])}")

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\nFile updated! Checking syntax...")
