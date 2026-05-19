"""
MoneyMap - AI Based Money & Expense Management System
Main Flask Application
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename 
import sqlite3
import os
from datetime import datetime, timedelta
import json

# Import AI modules
from ai_modules.receipt_scanner import scan_receipt_image
from ai_modules.expense_analyzer import analyze_expenses, get_spending_summary
from ai_modules.finance_chatbot import chat_with_bot

# Import helpers
from utils.helpers import (
    hash_password, verify_password, login_required,
    format_currency, format_date, allowed_file, validate_receipt_image,
    get_current_month_range, calculate_percentage, sanitize_input,
    generate_unique_filename, get_category_color
)

app = Flask(__name__)
app.secret_key = 'moneymap_secret_key_2024_change_this_in_production'

# Configuration
DATABASE = 'database.db'
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'receipts')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with schema"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create income table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            source TEXT NOT NULL,
            amount REAL NOT NULL,
            date DATE NOT NULL,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date DATE NOT NULL,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create budgets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            monthly_limit REAL NOT NULL,
            spent REAL DEFAULT 0,
            category TEXT,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create savings_goals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS savings_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0,
            deadline DATE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = sanitize_input(request.form.get('username'))
        email = sanitize_input(request.form.get('email'))
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('register.html')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                flash('Username or email already exists', 'danger')
                conn.close()
                return render_template('register.html')
            
            # Create user
            password_hash = hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            
            conn.commit()
            conn.close()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = sanitize_input(request.form.get('username'))
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password required', 'danger')
            return render_template('login.html')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            conn.close()
            
            if user and verify_password(user[2], password):
                session['user_id'] = user[0]
                session['username'] = user[1]
                flash(f'Welcome back, {user[1]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'danger')
        
        except Exception as e:
            flash(f'Login failed: {str(e)}', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))


# ==================== DASHBOARD ROUTES ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    # Get totals
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM income WHERE user_id = ?", (user_id,))
    total_income = cursor.fetchone()[0]
    
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ?", (user_id,))
    total_expenses = cursor.fetchone()[0]
    
    balance = total_income - total_expenses
    
    # Get current month range
    first_day, last_day = get_current_month_range()
    
    # Monthly expenses
    cursor.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ? AND date BETWEEN ? AND ?",
        (user_id, first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d'))
    )
    monthly_expenses = cursor.fetchone()[0]
    
    # Recent transactions
    cursor.execute(
        """SELECT 'expense' as type, title as label, amount, category, date 
           FROM expenses WHERE user_id = ?
           UNION ALL
           SELECT 'income' as type, source as label, amount, '' as category, date
           FROM income WHERE user_id = ?
           ORDER BY date DESC LIMIT 10""",
        (user_id, user_id)
    )
    recent_transactions = cursor.fetchall()
    
    # Category breakdown
    cursor.execute(
        "SELECT category, SUM(amount) FROM expenses WHERE user_id = ? GROUP BY category",
        (user_id,)
    )
    categories = cursor.fetchall()
    
    # Get budget
    current_month = datetime.now().month
    current_year = datetime.now().year
    cursor.execute(
        "SELECT monthly_limit FROM budgets WHERE user_id = ? AND month = ? AND year = ?",
        (user_id, current_month, current_year)
    )
    budget_row = cursor.fetchone()
    budget_limit = budget_row[0] if budget_row else 0
    
    # Get savings goals
    cursor.execute("SELECT name, target_amount, current_amount FROM savings_goals WHERE user_id = ?", (user_id,))
    savings_goals = cursor.fetchall()
    
    conn.close()
    
    # Prepare chart data
    category_data = {row[0]: row[1] for row in categories}
    
    return render_template('dashboard.html',
                         total_income=total_income,
                         total_expenses=total_expenses,
                         balance=balance,
                         monthly_expenses=monthly_expenses,
                         budget_limit=budget_limit,
                         recent_transactions=recent_transactions,
                         category_data=category_data,
                         savings_goals=savings_goals)


# ==================== INCOME MANAGEMENT ====================

@app.route('/income')
@login_required
def income():
    """Income management page"""
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM income WHERE user_id = ? ORDER BY date DESC",
        (user_id,)
    )
    income_list = cursor.fetchall()
    
    conn.close()
    
    return render_template('income.html', income_list=income_list)


@app.route('/add_income', methods=['POST'])
@login_required
def add_income():
    """Add new income"""
    user_id = session['user_id']
    source = sanitize_input(request.form.get('source'))
    amount = request.form.get('amount')
    date = request.form.get('date')
    description = sanitize_input(request.form.get('description'))
    
    if not all([source, amount, date]):
        flash('Source, amount, and date are required', 'danger')
        return redirect(url_for('income'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO income (user_id, source, amount, date, description) VALUES (?, ?, ?, ?, ?)",
            (user_id, source, float(amount), date, description)
        )
        
        conn.commit()
        conn.close()
        
        flash('Income added successfully!', 'success')
    
    except Exception as e:
        flash(f'Failed to add income: {str(e)}', 'danger')
    
    return redirect(url_for('income'))


@app.route('/edit_income/<int:income_id>', methods=['POST'])
@login_required
def edit_income(income_id):
    """Edit income"""
    user_id = session['user_id']
    source = sanitize_input(request.form.get('source'))
    amount = request.form.get('amount')
    date = request.form.get('date')
    description = sanitize_input(request.form.get('description'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE income SET source=?, amount=?, date=?, description=? WHERE id=? AND user_id=?",
            (source, float(amount), date, description, income_id, user_id)
        )
        
        conn.commit()
        conn.close()
        
        flash('Income updated successfully!', 'success')
    
    except Exception as e:
        flash(f'Failed to update income: {str(e)}', 'danger')
    
    return redirect(url_for('income'))


@app.route('/delete_income/<int:income_id>')
@login_required
def delete_income(income_id):
    """Delete income"""
    user_id = session['user_id']
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM income WHERE id=? AND user_id=?", (income_id, user_id))
        
        conn.commit()
        conn.close()
        
        flash('Income deleted successfully!', 'success')
    
    except Exception as e:
        flash(f'Failed to delete income: {str(e)}', 'danger')
    
    return redirect(url_for('income'))


# ==================== EXPENSE MANAGEMENT ====================

@app.route('/expenses')
@login_required
def expenses():
    """Expenses management page"""
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC",
        (user_id,)
    )
    expense_list = cursor.fetchall()
    
    conn.close()
    
    return render_template('expenses.html', expense_list=expense_list)


@app.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    """Add new expense"""
    user_id = session['user_id']
    title = sanitize_input(request.form.get('title'))
    amount = request.form.get('amount')
    category = sanitize_input(request.form.get('category'))
    date = request.form.get('date')
    description = sanitize_input(request.form.get('description'))
    
    if not all([title, amount, category, date]):
        flash('Title, amount, category, and date are required', 'danger')
        return redirect(url_for('expenses'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO expenses (user_id, title, amount, category, date, description) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, title, float(amount), category, date, description)
        )
        
        conn.commit()
        conn.close()
        
        flash('Expense added successfully!', 'success')
    
    except Exception as e:
        flash(f'Failed to add expense: {str(e)}', 'danger')
    
    return redirect(url_for('expenses'))


@app.route('/edit_expense/<int:expense_id>', methods=['POST'])
@login_required
def edit_expense(expense_id):
    """Edit expense"""
    user_id = session['user_id']
    title = sanitize_input(request.form.get('title'))
    amount = request.form.get('amount')
    category = sanitize_input(request.form.get('category'))
    date = request.form.get('date')
    description = sanitize_input(request.form.get('description'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE expenses SET title=?, amount=?, category=?, date=?, description=? WHERE id=? AND user_id=?",
            (title, float(amount), category, date, description, expense_id, user_id)
        )
        
        conn.commit()
        conn.close()
        
        flash('Expense updated successfully!', 'success')
    
    except Exception as e:
        flash(f'Failed to update expense: {str(e)}', 'danger')
    
    return redirect(url_for('expenses'))


@app.route('/delete_expense/<int:expense_id>')
@login_required
def delete_expense(expense_id):
    """Delete expense"""
    user_id = session['user_id']
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM expenses WHERE id=? AND user_id=?", (expense_id, user_id))
        
        conn.commit()
        conn.close()
        
        flash('Expense deleted successfully!', 'success')
    
    except Exception as e:
        flash(f'Failed to delete expense: {str(e)}', 'danger')
    
    return redirect(url_for('expenses'))


# ==================== BUDGET MANAGEMENT ====================

@app.route('/set_budget', methods=['POST'])
@login_required
def set_budget():
    """Set monthly budget"""
    user_id = session['user_id']
    monthly_limit = request.form.get('monthly_limit')
    category = sanitize_input(request.form.get('category'))
    
    if not monthly_limit:
        flash('Monthly limit is required', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Update or insert budget
        cursor.execute(
            """INSERT OR REPLACE INTO budgets (user_id, monthly_limit, category, month, year)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, float(monthly_limit), category if category else None, current_month, current_year)
        )
        
        conn.commit()
        conn.close()
        
        flash('Budget set successfully!', 'success')
    
    except Exception as e:
        flash(f'Failed to set budget: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard'))


# ==================== SAVINGS GOALS ====================

@app.route('/goals')
@login_required
def goals():
    """Savings goals page"""
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM savings_goals WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    )
    goals_list = cursor.fetchall()
    
    conn.close()
    
    return render_template('goals.html', goals_list=goals_list)


@app.route('/add_goal', methods=['POST'])
@login_required
def add_goal():
    """Add savings goal"""
    user_id = session['user_id']
    name = sanitize_input(request.form.get('name'))
    target_amount = request.form.get('target_amount')
    current_amount = request.form.get('current_amount', 0)
    deadline = request.form.get('deadline')
    
    if not name or not target_amount:
        flash('Name and target amount are required', 'danger')
        return redirect(url_for('goals'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO savings_goals (user_id, name, target_amount, current_amount, deadline) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, float(target_amount), float(current_amount), deadline if deadline else None)
        )
        
        conn.commit()
        conn.close()
        
        flash('Savings goal added successfully!', 'success')
    
    except Exception as e:
        flash(f'Failed to add goal: {str(e)}', 'danger')
    
    return redirect(url_for('goals'))


@app.route('/update_goal/<int:goal_id>', methods=['POST'])
@login_required
def update_goal(goal_id):
    """Update savings goal progress"""
    user_id = session['user_id']
    current_amount = request.form.get('current_amount')
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE savings_goals SET current_amount=? WHERE id=? AND user_id=?",
            (float(current_amount), goal_id, user_id)
        )
        
        conn.commit()
        conn.close()
        
        flash('Goal updated successfully!', 'success')
    
    except Exception as e:
        flash(f'Failed to update goal: {str(e)}', 'danger')
    
    return redirect(url_for('goals'))


@app.route('/delete_goal/<int:goal_id>')
@login_required
def delete_goal(goal_id):
    """Delete savings goal"""
    user_id = session['user_id']
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM savings_goals WHERE id=? AND user_id=?", (goal_id, user_id))
        
        conn.commit()
        conn.close()
        
        flash('Goal deleted successfully!', 'success')
    
    except Exception as e:
        flash(f'Failed to delete goal: {str(e)}', 'danger')
    
    return redirect(url_for('goals'))


# ==================== AI FEATURES ====================

@app.route('/upload_receipt', methods=['POST'])
@login_required
def upload_receipt():
    """Upload and scan receipt"""
    user_id = session['user_id']
    
    if 'receipt' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    
    file = request.files['receipt']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    valid, message = validate_receipt_image(file)
    if not valid:
        return jsonify({'success': False, 'error': message}), 400
    
    try:
        # Save file
        filename = generate_unique_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Scan receipt
        result = scan_receipt_image(filepath)
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result,
                'filepath': filepath
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to scan receipt')
            }), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/analyze_expenses')
@login_required
def analyze_user_expenses():
    """Analyze user expenses"""
    user_id = session['user_id']
    
    try:
        result = analyze_expenses(user_id)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/chat', methods=['POST'])
@login_required
def chat():
    """Chat with finance bot"""
    user_id = session['user_id']
    message = request.json.get('message', '')
    
    if not message:
        return jsonify({'success': False, 'error': 'No message provided'}), 400
    
    try:
        result = chat_with_bot(user_id, message)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== REPORTS ====================

@app.route('/reports')
@login_required
def reports():
    """Reports page"""
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    # Get summary data
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM income WHERE user_id = ?", (user_id,))
    total_income = cursor.fetchone()[0]
    
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ?", (user_id,))
    total_expenses = cursor.fetchone()[0]
    
    # Get category breakdown
    cursor.execute(
        "SELECT category, SUM(amount) FROM expenses WHERE user_id = ? GROUP BY category",
        (user_id,)
    )
    category_data = cursor.fetchall()
    
    conn.close()
    
    spending_summary = get_spending_summary(user_id)
    
    return render_template('reports.html',
                         total_income=total_income,
                         total_expenses=total_expenses,
                         category_data=category_data,
                         spending_summary=spending_summary)


@app.route('/export_pdf')
@login_required
def export_pdf():
    """Export report as PDF"""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    # Get data
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM income WHERE user_id = ?", (user_id,))
    total_income = cursor.fetchone()[0]
    
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ?", (user_id,))
    total_expenses = cursor.fetchone()[0]
    
    cursor.execute(
        "SELECT source, SUM(amount) FROM income WHERE user_id = ? GROUP BY source",
        (user_id,)
    )
    income_by_source = cursor.fetchall()
    
    cursor.execute(
        "SELECT category, SUM(amount) FROM expenses WHERE user_id = ? GROUP BY category",
        (user_id,)
    )
    expenses_by_category = cursor.fetchall()
    
    conn.close()

    def to_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    total_income = to_float(total_income)
    total_expenses = to_float(total_expenses)
    income_by_source = [(src, to_float(amt)) for src, amt in income_by_source]
    expenses_by_category = [(cat, to_float(amt)) for cat, amt in expenses_by_category]

    # Create PDF
    filename = f"moneymap_report_{session['username']}_{datetime.now().strftime('%Y%m%d')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    elements.append(Paragraph("MoneyMap Financial Report", styles['Heading1']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Generated for: {session['username']}", styles['Normal']))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%d %B %Y')}", styles['Normal']))
    elements.append(Spacer(1, 24))
    
    # Summary
    elements.append(Paragraph("Financial Summary", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    summary_data = [
        ['Total Income', f'₹{total_income:,.2f}'],
        ['Total Expenses', f'₹{total_expenses:,.2f}'],
        ['Balance', f'₹{(total_income - total_expenses):,.2f}']
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 24))
    
    # Income by Source
    elements.append(Paragraph("Income by Source", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    income_data = [['Source', 'Amount']] + [[src, f'₹{amt:,.2f}'] for src, amt in income_by_source]
    income_table = Table(income_data)
    income_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(income_table)
    elements.append(Spacer(1, 24))
    
    # Expenses by Category
    elements.append(Paragraph("Expenses by Category", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    expense_data = [['Category', 'Amount']] + [[cat, f'₹{amt:,.2f}'] for cat, amt in expenses_by_category]
    expense_table = Table(expense_data)
    expense_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(expense_table)
    
    # Build PDF
    doc.build(elements)
    
    flash('Report exported successfully!', 'success')
    return redirect(url_for('reports'))


# ==================== API ENDPOINTS ====================

@app.route('/api/transactions')
@login_required
def get_transactions():
    """Get transactions for charts"""
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    # Get last 6 months data
    six_months_ago = datetime.now() - timedelta(days=180)
    
    cursor.execute(
        """SELECT strftime('%Y-%m', date) as month, SUM(amount)
           FROM expenses
           WHERE user_id = ? AND date >= ?
           GROUP BY month
           ORDER BY month""",
        (user_id, six_months_ago.strftime('%Y-%m-%d'))
    )
    expense_trends = cursor.fetchall()
    
    cursor.execute(
        """SELECT strftime('%Y-%m', date) as month, SUM(amount)
           FROM income
           WHERE user_id = ? AND date >= ?
           GROUP BY month
           ORDER BY month""",
        (user_id, six_months_ago.strftime('%Y-%m-%d'))
    )
    income_trends = cursor.fetchall()
    
    conn.close()
    
    return jsonify({
        'expense_trends': dict(expense_trends),
        'income_trends': dict(income_trends)
    })


# ==================== ERROR HANDLERS ====================

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    flash('File size exceeds limit (16MB)', 'danger')
    return redirect(request.referrer)


# @app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    flash('Page not found', 'warning')
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Create upload folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Run app
    app.run(debug=True, host='0.0.0.0', port=5000)

