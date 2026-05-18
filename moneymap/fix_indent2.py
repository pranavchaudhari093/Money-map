# Fix indentation in app.py properly
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines 942-944 need proper 4-space indentation
for i, line in enumerate(lines):
    if i == 942:  # Line 943 (if statement body)
        lines[i] = '       return redirect(url_for(\'dashboard\'))\n'
        print(f"Fixed line {i+1} to 8 spaces")
    elif i == 943:  # Line 944 (after if)
        lines[i] = '   return redirect(url_for(\'login\'))\n'
        print(f"Fixed line {i+1} to 4 spaces")

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Indentation fixed!")
