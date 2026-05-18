# 🚀 MoneyMap - Quick Start Guide

## Installation & Setup (5 Minutes)

### Step 1: Install Python Dependencies
```bash
cd c:\Users\Harshada\Desktop\moneymap
pip install -r requirements.txt
```

### Step 2: Install Tesseract OCR (Required for Receipt Scanner)

**Windows:**
1. Download installer: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer(default location: `C:\Program Files\Tesseract-OCR`)
3. Add to PATH: 
   - Open System Properties → Environment Variables
   - Edit "Path" variable
   - Add: `C:\Program Files\Tesseract-OCR`

**Verify Tesseract Installation:**
```bash
tesseract --version
```

### Step 3: Run the Application
```bash
python app.py
```

### Step 4: Access in Browser
Open: **http://localhost:5000**

---

## 📋 First Time Usage

### 1. Create Account
- Click "Register" on login page
- Enter username, email, password
- Password must be 6+ characters
- Click "Create Account"

### 2. Login
- Enter username and password
- Click "Login"

### 3. Add Your First Income
- Click "Income" in sidebar
- Click "+ Add New Income"
- Select source (e.g., Salary)
- Enter amount and date
- Click "Add Income"

### 4. Add Your First Expense
- Click "Expenses" in sidebar
- Click "+ Add New Expense"
- Fill in details (title, amount, category)
- Click "Add Expense"

### 5. Try AI Receipt Scanner
- On Expenses page, find "AI Receipt Scanner"
- Upload a receipt image (PNG/JPG)
- AI extracts amount, date, merchant
- Auto-fills expense form
- Submit to save

### 6. Set Savings Goal
- Click "Savings Goals" in sidebar
- Click "+ Create New Goal"
- Enter goal name (e.g., "Buy Laptop")
- Set target amount
- Optionally set deadline
- Click "Create Goal"

### 7. View Dashboard
- Click "Dashboard" in sidebar
- See all your financial data
- View charts and graphs
- Track budget progress

### 8. Chat with Finance Bot
- Go to "Reports" page
- Scroll to "Ask Finance Bot"
- Ask questions like:
  - "What is my total expense?"
  - "How much did I spend on food?"
  - "What's my balance?"
  - "How can I save money?"

---

## 🎯 Key Features to Explore

### Dashboard Features
- ✅ Total income, expenses, balance cards
- ✅ Monthly spending tracker with budget
- ✅ Expense category pie chart
- ✅ Recent transactions table
- ✅ Savings goals preview

### Expense Management
- ✅ Manual expense entry
- ✅ Category-based tracking
- ✅ Edit/delete expenses
- ✅ **AI receipt scanning**
- ✅ Automatic data extraction

### Income Tracking
- ✅ Multiple income sources
- ✅ Date-wise records
- ✅ Description support

### Budget Planning
- ✅ Set monthly spending limits
- ✅ Visual progress bars
- ✅ Warning when near limit

### Savings Goals
- ✅ Create multiple goals
- ✅ Track progress visually
- ✅ Update amounts anytime
- ✅ Set target dates

### AI Features
- 🤖 **Receipt Scanner**: Upload images → auto-extract data
- 🤖 **Expense Analyzer**: Get spending insights
- 🤖 **Finance Chatbot**: Ask natural language questions

### Reports
- 📄 Export PDF reports
- 📊 View category breakdowns
- 📈 Get AI-powered insights
- 💬 Chat with finance bot

---

## 🔧 Troubleshooting

### "Tesseract not found" Error
**Solution:**
1. Verify Tesseract is installed
2. Add to system PATH
3. Restart terminal/command prompt
4. Test: `tesseract --version`

### Database Locked Error
**Solution:**
- Close any other instances of the app
- Delete `database.db` if needed (creates fresh)

### Port 5000 Already in Use
**Solution:**
Edit `app.py` line 952:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change port
```

### Can't Login
**Solution:**
- Ensure you registered first
- Check username/password spelling
- Clear browser cache

### Receipt Scanner Not Working
**Solution:**
- Verify Tesseract is installed correctly
- Use clear, high-quality receipt images
- Supported formats: PNG, JPG, JPEG
- Max file size: 10MB

---

## 📊 Sample Test Data

Want to test quickly? Add this sample data:

### Income
- Source: Salary
- Amount: ₹50,000
- Date: Today

### Expenses
1. **Grocery Shopping**
   - Category: Food
   - Amount: ₹5,000
   
2. **Uber Ride**
   - Category: Travel
   - Amount: ₹500
   
3. **Netflix Subscription**
   - Category: Entertainment
   - Amount: ₹800
   
4. **Electricity Bill**
   - Category: Bills
   - Amount: ₹2,000

### Savings Goal
- Name: Emergency Fund
- Target: ₹100,000
- Current: ₹10,000

---

## 🌟 Pro Tips

1. **Regular Tracking**: Add expenses daily for accurate insights
2. **Receipt Scanning**: Use good lighting for better OCR results
3. **Budget Alerts**: Set realistic monthly budgets
4. **Review Insights**: Check AI analysis weekly
5. **Export Reports**: Download PDFs monthly for records
6. **Chat Bot**: Ask specific questions for better answers

---

## 📱 Mobile Access

The app is fully responsive! Access from mobile:
1. Find your computer's IP address:
   - Windows: `ipconfig` in terminal
   - Look for IPv4 Address (e.g., 192.168.1.x)
2. On mobile browser: `http://YOUR_IP:5000`
3. Same network required

---

## 🎓 Project Demo Flow

Impress your professors with this demo sequence:

1. **Show Registration** (30 sec)
   - Create new account
   
2. **Dashboard Overview** (1 min)
   - Point out cards and charts
   
3. **Add Income** (30 sec)
   - Show manual entry
   
4. **Add Expense + AI Scanner** (2 min) ⭐
   - Manual entry first
   - Then upload receipt image
   - Show auto-fill magic!
   
5. **Savings Goals** (1 min)
   - Create a goal
   - Show progress bar
   
6. **AI Features** (2 min) ⭐
   - Run expense analysis
   - Chat with finance bot
   
7. **Export Report** (30 sec)
   - Download PDF
   - Show professional formatting

**Total: ~8 minutes**

---

## 🏆 Highlights for Final Year Project

✅ **Full-Stack Development**: Flask backend + modern frontend
✅ **AI/ML Integration**: OCR, NLP, data analysis
✅ **Database Design**: Normalized SQLite schema
✅ **Security**: Password hashing, session management
✅ **Responsive Design**: Works on all devices
✅ **Production-Ready**: Clean, documented code
✅ **Innovation**: Real AI features, not just CRUD

---

## 📞 Need Help?

1. Check error messages in browser console (F12)
2. Review terminal output for Python errors
3. Verify all dependencies installed
4. Ensure Tesseract OCR configured correctly

---

**Happy Tracking! 💰📊**

**MoneyMap - Your Smart Companion for Financial Success!**
