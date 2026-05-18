# Simply remove the problematic not_found handler - it's not critical
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and remove the entire not_found function
start = content.find('@app.errorhandler(404)\ndef not_found(e):')
if start == -1:
    print("Function not found with exact match")
else:
    # Find the next function or end
    end = content.find('\n\nif __name__', start)
    if end != -1:
        new_content = content[:start] + content[end+1:]
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Removed not_found function successfully!")
    else:
        print("Could not find end of function")
