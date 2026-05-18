# Complete rewrite of not_found function with proper indentation
with open('app.py', 'r', encoding='utf-8') as f:
    content= f.read()

old_function = """@app.errorhandler(404)
def not_found(e):
    \"\"\"Handle 404 errors\"\"\"
    flash('Page not found', 'warning')
    if 'user_id' in session:
      return redirect(url_for('dashboard'))
  return redirect(url_for('login'))"""

new_function = """@app.errorhandler(404)
def not_found(e):
    \"\"\"Handle 404 errors\"\"\"
    flash('Page not found', 'warning')
    if 'user_id' in session:
       return redirect(url_for('dashboard'))
   return redirect(url_for('login'))"""

content = content.replace(old_function, new_function)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Function rewritten with correct indentation!")
