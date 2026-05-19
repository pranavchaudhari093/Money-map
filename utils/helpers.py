"""
MoneyMap - Helper Utilities
Authentication decorators, formatting functions, and file validation
"""

from functools import wraps
from flask import session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import re


def hash_password(password):
    """Hash a password using Werkzeug"""
    return generate_password_hash(password)


def verify_password(password_hash, password):
    """Verify a password against its hash"""
    return check_password_hash(password_hash, password)


def login_required(f):
    """Decorator to protect routes that require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def format_currency(amount):
    """Format amount as currency"""
    if amount is None:
        return "₹0.00"
    try:
        return f"₹{float(amount):,.2f}"
    except (ValueError, TypeError):
        return "₹0.00"


def format_date(date_obj, format="%d %b %Y"):
    """Format date object to string"""
    if date_obj is None:
        return ""
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
        except ValueError:
            return date_obj
    return date_obj.strftime(format)


def parse_date(date_string):
    """Parse date string to datetime object"""
    if not date_string:
        return None
    
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    return None


def allowed_file(filename, allowed_extensions=None):
    """Check if file has allowed extension"""
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in allowed_extensions


def validate_receipt_image(file):
    """Validate receipt image file"""
    if not file or file.filename == '':
        return False, "No file selected"
    
    allowed_exts = {'png', 'jpg', 'jpeg'}
    
    if '.' not in file.filename:
        return False, "Invalid file name"
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    
    if ext not in allowed_exts:
        return False, f"File type {ext} not allowed. Allowed: PNG, JPG, JPEG"
    
    # Check file size (max 10MB)
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size > 10 * 1024 * 1024:
        return False, "File size exceeds 10MB"
    
    return True, "Valid file"


def get_current_month_range():
    """Get first and last day of current month"""
    now = datetime.now()
    first_day = now.replace(day=1)
    
    if now.month == 12:
        last_day = now.replace(year=now.year +1, month=1, day=1)
    else:
        last_day = now.replace(month=now.month + 1, day=1)
    
    return first_day, last_day


def get_month_start_end(month=None, year=None):
    """Get start and end dates for a specific month"""
    if month is None or year is None:
        now = datetime.now()
        month = now.month
        year = now.year
    
    from datetime import timedelta
    
    start = datetime(year, month, 1)
    
    if month == 12:
        end = datetime(year +1, 1, 1) - timedelta(days=1)
    else:
        end = datetime(year, month +1, 1) - timedelta(days=1)
    
    return start, end


def calculate_percentage(part, whole):
    """Calculate percentage safely"""
    if whole is None or whole == 0:
        return 0.0
    try:
        return (float(part) / float(whole)) * 100
    except (ValueError, TypeError):
        return 0.0


def sanitize_input(text):
    """Basic input sanitization"""
    if text is None:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', str(text))
    
    # Escape special characters
    text = text.replace("'", "''")
    
    return text.strip()


def generate_unique_filename(original_filename):
    """Generate unique filename for uploads"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if '.' in original_filename:
        ext = original_filename.rsplit('.', 1)[1].lower()
        return f"receipt_{timestamp}.{ext}"
    else:
        return f"receipt_{timestamp}"


def flash_errors(errors):
    """Flash multiple error messages"""
    from flask import flash as flask_flash
    
    if isinstance(errors, list):
        for error in errors:
            flask_flash(error, 'danger')
    elif isinstance(errors, str):
        flask_flash(errors, 'danger')


def get_category_color(category):
    """Get color for expense category"""
    colors = {
        'Food': '#FF6384',
        'Travel': '#36A2EB',
        'Shopping': '#FFCE56',
        'Bills': '#4BC0C0',
        'Entertainment': '#9966FF',
        'Others': '#FF9F40',
        'Salary': '#4CAF50',
        'Freelance': '#2196F3',
        'Business': '#9C27B0'
    }
    
    return colors.get(category, '#999999')
