# 💰 MoneyMap - AI Based Money & Expense Management System

A professional, production-ready web application for personal finance management built with Python Flask and modern frontend technologies.

---

## 📋 Project Overview

**MoneyMap** is a comprehensive expense tracking and financial management system that helps users:
- Track income and expenses
- Analyze spending patterns with AI
- Set and monitor savings goals
- Get intelligent financial recommendations
- Scan receipts automatically using OCR
- Chat with an AI finance assistant

---

## 🚀 Technologies Used

### Backend
- **Python 3.x**
- **Flask 3.0.0** - Web framework
- **SQLite** - Database
- **SQLAlchemy** - ORM
- **Werkzeug** - Security (password hashing)

### Frontend
- **HTML5** - Structure
- **CSS3** - Modern styling with gradients and animations
- **JavaScript (ES6+)** - Interactivity
- **Chart.js** - Data visualization

### AI/ML Libraries
- **pytesseract** - OCR for receipt scanning
- **OpenCV** - Image preprocessing
- **scikit-learn** - Spending pattern analysis
- **Pandas & NumPy** - Data processing

### Report Generation
- **ReportLab** - PDF generation
- **WeasyPrint** - HTML to PDF conversion
- **openpyxl** - Excel support

---

## 📁 Project Structure

```
MoneyMap/
│
├── app.py                          # Main Flask application
├── database.db                     # SQLite database (auto-created)
├── requirements.txt                # Python dependencies
│
├── templates/                      # HTML templates
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── expenses.html
│   ├── income.html
│   ├── goals.html
│   └── reports.html
│
├── static/                         # Static assets
│   ├── css/
│   │   └── style.css              # Modern fintech styling
│   ├── js/
│   │   └── script.js              # Interactive functionality
│   ├── images/
│   └── uploads/
│       └── receipts/              # Scanned receipt storage
│
├── ai_modules/                     # AI features
│   ├── __init__.py
│   ├── receipt_scanner.py         # OCR receipt scanning
│   ├── expense_analyzer.py        # Spending analysis
│   └── finance_chatbot.py         # Financial Q&A bot
│
└── utils/                          # Utility functions
    ├── __init__.py
    └── helpers.py                  # Authentication, formatting, etc.
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Tesseract OCR (install separately, see below)

### Step 1: Install Tesseract OCR

**Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location: `C:\Program Files\Tesseract-OCR`
3. Add to system PATH

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### Step 2: Install Python Dependencies

Navigate to the project directory and run:
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application

```bash
python app.py
```

The application will start on: `http://localhost:5000`

### Step 4: Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```

---

## 🎯 Features

### 1. User Authentication
- ✅ Secure registration and login
- ✅ Password hashing with Werkzeug
- ✅ Session-based authentication
- ✅ Protected routes

### 2. Dashboard
- ✅ Real-time financial overview
- ✅ Total income, expenses, and balance cards
- ✅ Monthly spending tracker
- ✅ Budget progress bars
- ✅ Recent transactions table
- ✅ Expense category pie chart
- ✅ Income vs expense trends

### 3. Income Management
- ✅ Add income with source (Salary, Freelance, Business, etc.)
- ✅ Edit and delete income entries
- ✅ Date-wise tracking
- ✅ Description support

### 4. Expense Management
- ✅ Add expenses with categories
- ✅ Categories: Food, Travel, Shopping, Bills, Entertainment, Others
- ✅ Edit and delete expenses
- ✅ **AI Receipt Scanner** - Upload receipt images for automatic data extraction

### 5. Savings Goals
- ✅ Create multiple savings goals
- ✅ Track progress with visual progress bars
- ✅ Update goal amounts
- ✅ Set target dates
- ✅ Percentage completion display

### 6. AI Features

#### AI Receipt Scanner
- 📷 Upload receipt images (PNG, JPG, JPEG)
- 🔍 OCR extracts amount, date, and merchant
- ⚡ Auto-fills expense form
- 📊 Supports drag-and-drop upload

#### AI Expense Analyzer
- 📈 Analyzes spending patterns
- 🎯 Identifies highest spending category
- 📊 Monthly trend detection
- 💡 Provides saving recommendations
- ⚠️ Detects unusual expenses

#### AI Finance Chatbot
- 💬 Natural language interface
- ❓ Answer questions like:
  - "What is my total expense?"
  - "How much did I spend on food?"
  - "What's my balance?"
  - "How can I save money?"
- 🤖 Contextual financial advice

### 7. Reports & Export
- 📄 Export financial reports as PDF
- 📊 Includes income/expense summaries
- 📈 Category breakdown charts
- 🤖 AI insights included

### 8. Data Visualization
- 🥧 Expense category pie chart
- 📊 Monthly spending bar chart
- 📈 Income vs expense line chart
- 📊 Interactive Chart.js graphs

---

## 🎨 UI/UX Design Features

- ✨ **Modern Fintech Design** - Professional gradient backgrounds
- 🎨 **Color Scheme** - Purple/blue gradients with semantic colors
- 📱 **Fully Responsive** - Works on desktop, tablet, and mobile
- 🎭 **Smooth Animations** - Hover effects, transitions, modal animations
- 🃏 **Dashboard Cards** - Beautiful card-based layout
- 📊 **Visual Progress** - Progress bars for budgets and goals
- 🎯 **Intuitive Navigation** - Sidebar navigation with active states
- 🔔 **Flash Messages** - Auto-dismissing notifications

---

## 🗄️ Database Schema

### Users Table
```sql
- id (PRIMARY KEY)
- username (UNIQUE)
- email (UNIQUE)
- password_hash
- created_at
```

### Income Table
```sql
- id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- source
- amount
- date
- description
```

### Expenses Table
```sql
- id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- title
- amount
- category
- date
- description
```

### Budgets Table
```sql
- id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- monthly_limit
- spent
- category
- month
- year
```

### Savings Goals Table
```sql
- id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- name
- target_amount
- current_amount
- deadline
```

---

## 🔒 Security Features

- 🔐 **Password Hashing** - Werkzeug secure hashing
- 🛡️ **Session Management** - Secure session-based auth
- ✅ **Input Validation** - Server-side validation
- 🚫 **SQL Injection Prevention** - Parameterized queries
- 📁 **File Upload Security** - Type and size validation
- 👤 **Route Protection** - Login required decorators

---

## 📊 Sample Usage

### Register a New Account
1. Click "Register" on login page
2. Enter username, email, and password
3. Confirm password (min 6 characters)
4. Click "Create Account"

### Add Income
1. Navigate to "Income" from sidebar
2. Click "+ Add New Income"
3. Select source, enter amount and date
4. Optionally add description
5. Click "Add Income"

### Add Expense with Receipt Scanner
1. Go to "Expenses" page
2. Drag and drop receipt image or click to upload
3. AI extracts amount, date, and merchant
4. Review auto-filled expense form
5. Submit to save

### Set Budget
1. On dashboard, find "Monthly Spending" card
2. Enter monthly limit
3. Select category (optional)
4. Track progress with progress bar

### Ask Finance Bot
1. Go to "Reports" page
2. Scroll to "Ask Finance Bot"
3. Type question like "How much did I spend on food?"
4. Get instant AI-powered answer

---

## 🐛 Troubleshooting

### Tesseract Not Found Error
**Solution:** Ensure Tesseract OCR is installed and in system PATH

### Database Locked Error
**Solution:** Close any other applications using database.db

### Module Not Found Error
**Solution:** Run `pip install -r requirements.txt`

### Port Already in Use
**Solution:** Change port in app.py: `app.run(port=5001)`

---

## 📝 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Income
- `GET /income` - View all income
- `POST /add_income` - Add new income
- `POST /edit_income/<id>` - Edit income
- `GET /delete_income/<id>` - Delete income

### Expenses
- `GET /expenses` - View all expenses
- `POST /add_expense` - Add new expense
- `POST /edit_expense/<id>` - Edit expense
- `GET /delete_expense/<id>` - Delete expense
- `POST /upload_receipt` - Upload and scan receipt

### Goals
- `GET /goals` - View all goals
- `POST /add_goal` - Create new goal
- `POST /update_goal/<id>` - Update goal progress
- `GET /delete_goal/<id>` - Delete goal

### Reports & AI
- `GET /reports` - View reports page
- `GET /export_pdf` - Export PDF report
- `GET /analyze_expenses` - Get AI analysis
- `POST /chat` - Chat with finance bot

### API
- `GET /api/transactions` - Get transaction data for charts

---

## 🎓 Perfect For

- ✅ Final Year Engineering Projects
- ✅ Web Development Portfolios
- ✅ Full-Stack Flask Applications
- ✅ AI/ML Integration Projects
- ✅ Finance & FinTech Applications

---

## 🌟 Key Highlights

1. **Production-Ready Code** - Clean, well-documented, scalable architecture
2. **No Placeholder Code** - All features fully implemented
3. **Separation of Concerns** - Modular design with clear responsibilities
4. **Modern UI/UX** - Professional fintech design
5. **AI-Powered** - Real OCR, analysis, and chatbot features
6. **Secure** - Industry-standard security practices
7. **Responsive** - Mobile-friendly design
8. **Well-Tested** - All features verified working

---

## 📄 License

This project is created for educational purposes. Feel free to use and modify for your needs.

---

## 👨‍💻 Developer Notes

### Running in Development Mode
```bash
python app.py
```
Application runs with debug mode enabled on `http://0.0.0.0:5000`

### Creating Production Build
1. Set `debug=False` in app.py
2. Use a production WSGI server (Gunicorn/uWSGI)
3. Set strong secret key
4. Use PostgreSQL instead of SQLite for production

---

## 🎉 Getting Started Quick Guide

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Tesseract OCR (Windows example)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki

# 3. Run the app
python app.py

# 4. Open browser
# Navigate to: http://localhost:5000

# 5. Register a new account and start tracking!
```

---

## 💡 Tips for Best Experience

1. Use high-quality receipt images for better OCR results
2. Set realistic monthly budgets
3. Track expenses regularly for accurate insights
4. Ask the chatbot specific questions for better answers
5. Review AI recommendations monthly
6. Export reports for tax planning

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review error messages in console
3. Verify all dependencies are installed
4. Ensure Tesseract OCR is properly configured

---

**Built with ❤️ using Python, Flask, and AI**

**MoneyMap - Your Smart Companion for Financial Success!**
