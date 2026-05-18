# Fix indentation in app.py
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 944 (index 943) - should have 4 spaces like line 942
for i, line in enumerate(lines):
    if i == 943 and 'return redirect(url_for("login"))' in line:
        lines[i] = '   return redirect(url_for(\'login\'))\n'
        print(f"Fixed line {i+1}")

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Indentation fixed!")
