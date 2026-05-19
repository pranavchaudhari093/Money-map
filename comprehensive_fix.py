"""Comprehensive fix for app.py indentation issues"""
import re

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_count = 0

# Pattern 1: Fix the index() function (around lines 125-127)
for i in [125, 126]:  # Lines 126-127 (0-indexed)
    if i < len(lines):
        if 'return redirect(url_for(\'dashboard\'))' in lines[i]:
            lines[i] = '    return redirect(url_for(\'dashboard\'))\n'  # 4 spaces indentation
            print(f"Fixed line {i+1} (dashboard redirect)")
            fixed_count += 1
        elif 'return redirect(url_for(\'login\'))' in lines[i]:
            lines[i] = '    return redirect(url_for(\'login\'))\n'  # 4 spaces indentation
            print(f"Fixed line {i+1} (login return)")
            fixed_count += 1

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"\n✓ Fixed {fixed_count} lines")
print("Now checking syntax...")
