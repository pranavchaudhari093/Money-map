"""
MoneyMap - AI Finance Chatbot
Answers user questions about their finances
"""

import re
import sqlite3
from datetime import datetime, timedelta


class FinanceChatbot:
    """AI chatbot for financial queries"""
    
    def __init__(self, db_path='database.db'):
        self.db_path = db_path
        
    def get_user_financial_data(self, user_id):
        """Get all financial data for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get total income
        def to_float(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0

        cursor.execute(
            "SELECT SUM(amount) FROM income WHERE user_id = ?",
            (user_id,)
        )
        total_income = to_float(cursor.fetchone()[0])
        
        # Get total expenses
        cursor.execute(
            "SELECT SUM(amount) FROM expenses WHERE user_id = ?",
            (user_id,)
        )
        total_expenses = to_float(cursor.fetchone()[0])
        
        # Get expenses by category
        cursor.execute(
            """SELECT category, SUM(amount) 
               FROM expenses
               WHERE user_id = ? 
               GROUP BY category""",
            (user_id,)
        )
        category_breakdown = {cat: to_float(amount) for cat, amount in cursor.fetchall()}
        
        # Get monthly expenses
        current_month = datetime.now().strftime('%Y-%m')
        cursor.execute(
            """SELECT SUM(amount) 
               FROM expenses
               WHERE user_id = ? AND date LIKE ?""",
            (user_id, f"{current_month}%")
        )
        monthly_expenses = to_float(cursor.fetchone()[0])
        
        # Get recent transactions
        cursor.execute(
            """SELECT title, amount, category, date 
               FROM expenses
               WHERE user_id = ? 
               ORDER BY date DESC 
               LIMIT 5""",
            (user_id,)
        )
        recent_expenses = [
            (title, to_float(amount), category, date)
            for title, amount, category, date in cursor.fetchall()
        ]
        
        # Get savings goals
        cursor.execute(
            """SELECT name, target_amount, current_amount
               FROM savings_goals 
               WHERE user_id = ?""",
            (user_id,)
        )
        savings_goals = [
            (name, to_float(target), to_float(current))
            for name, target, current in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance': total_income - total_expenses,
            'category_breakdown': category_breakdown,
            'monthly_expenses': monthly_expenses,
            'recent_expenses': recent_expenses,
            'savings_goals': savings_goals
        }
    
    def parse_query(self, query):
        """Parse user query to identify intent"""
        query = query.lower().strip()
        
        intents = {
            'total_expense': [
                r'total expen[cs]e',
                r'how much.*spen[dt]',
                r'total spent',
                r'what.*my expen[cs]e'
            ],
            'total_income': [
                r'total income',
                r'how much.*earn',
                r'total earned',
                r'my income'
            ],
            'balance': [
                r'balance',
                r'how much.*left',
                r'remaining',
                r'saving'
            ],
            'category_spending': [
                r'spend.*on\s+(\w+)',
                r'how much.*(\w+)',
                r'expense.*(\w+)'
            ],
            'monthly_expense': [
                r'this month',
                r'current month',
                r'monthly expen[cs]e'
            ],
            'recent_transactions': [
                r'recent',
                r'last.*transaction',
                r'show.*transactions'
            ],
            'savings_goals': [
                r'savings goal',
                r'goal',
                r'saving for'
            ],
            'budget_advice': [
                r'how.*save',
                r'save money',
                r'reduce expen[cs]e',
                r'budget.*tip',
                r'financial.*advice'
            ]
        }
        
        # Check each intent
        for intent, patterns in intents.items():
            for pattern in patterns:
                match = re.search(pattern, query)
                if match:
                    # Extract category if present
                    category = None
                    if intent == 'category_spending' and match.groups():
                        category = match.group(1).title()
                    
                    return {
                        'intent': intent,
                        'category': category,
                        'confidence': 0.8
                    }
        
        return {
            'intent': 'unknown',
            'category': None,
            'confidence': 0.5
        }
    
    def generate_response(self, user_id, query):
        """Generate response based on parsed query"""
        # Parse the query
        parsed = self.parse_query(query)
        
        # Get financial data
        data = self.get_user_financial_data(user_id)
        
        intent = parsed['intent']
        category = parsed.get('category')
        
        # Generate response based on intent
        if intent == 'total_expense':
            response = (
                f"Your total expenses are ₹{data['total_expenses']:,.2f}. "
                f"This includes all your recorded expenses across all categories."
            )
        
        elif intent == 'total_income':
            response = (
                f"Your total income is ₹{data['total_income']:,.2f}. "
                f"This is the sum of all your recorded income sources."
            )
        
        elif intent == 'balance':
            balance = data['balance']
            if balance >= 0:
                response = (
                    f"Your current balance is ₹{balance:,.2f}. "
                    f"Great job managing your finances!"
                )
            else:
                response = (
                    f"Your current balance is ₹{balance:,.2f}. "
                    f"You might want to review your expenses to avoid overspending."
                )
        
        elif intent == 'monthly_expense':
            response = (
                f"You've spent ₹{data['monthly_expenses']:,.2f} this month. "
                f"Keep track of your spending to stay within budget."
            )
        
        elif intent == 'category_spending' and category:
            amount = data['category_breakdown'].get(category, 0)
            if amount > 0:
                percentage = (amount / data['total_expenses'] * 100) if data['total_expenses'] > 0 else 0
                response = (
                    f"You've spent ₹{amount:,.2f} on {category}, "
                    f"which is {percentage:.1f}% of your total expenses."
                )
            else:
                response = f"No expenses recorded for {category} yet."
        
        elif intent == 'recent_transactions':
            if data['recent_expenses']:
                transactions = "\n".join([
                    f"• {t[0]}: ₹{t[1]:,.2f} ({t[2]}) on {t[3]}"
                    for t in data['recent_expenses'][:3]
                ])
                response = f"Your recent expenses:\n{transactions}"
            else:
                response = "No recent transactions found."
        
        elif intent == 'savings_goals':
            if data['savings_goals']:
                goals = "\n".join([
                    f"• {g[0]}: ₹{g[2]:,.2f} / ₹{g[1]:,.2f}"
                    for g in data['savings_goals']
                ])
                response = f"Your savings goals:\n{goals}"
            else:
                response = "You haven't set any savings goals yet."
        
        elif intent == 'budget_advice':
            # Find highest spending category
            if data['category_breakdown']:
                highest_cat = max(data['category_breakdown'], key=data['category_breakdown'].get)
                highest_amt = data['category_breakdown'][highest_cat]
                
                response = (
                    f"Here are some money-saving tips:\n"
                    f"1. Your highest spending is on {highest_cat} (₹{highest_amt:,.2f}). "
                    f"Consider setting a budget for this category.\n"
                    f"2. Try the 50/30/20 rule: 50% needs, 30% wants, 20% savings.\n"
                    f"3. Track every expense to identify wasteful spending.\n"
                    f"4. Set up automatic transfers to your savings account."
                )
            else:
                response = (
                    "Start by tracking all your expenses. "
                    "Once you have data, I can provide personalized advice!"
                )
        
        elif intent == 'unknown':
            response = (
                "I'm not sure I understand. You can ask me things like:\n"
                "• What is my total expense?\n"
                "• How much did I spend on food?\n"
                "• What's my balance?\n"
                "• How can I save money?"
            )
        
        else:
            response = "Could you please rephrase that? I can help with questions about your expenses, income, and savings."
        
        return {
            'query': query,
            'response': response,
            'intent': intent,
            'confidence': parsed['confidence']
        }
    
    def chat(self, user_id, message):
        """Main chat interface"""
        result = self.generate_response(user_id, message)
        return result


def chat_with_bot(user_id, message, db_path='database.db'):
    """Convenience function to chat with the bot"""
    bot = FinanceChatbot(db_path)
    return bot.chat(user_id, message)


# Example usage
if __name__ == "__main__":
    # Test the chatbot
    test_queries = [
        "What is my total expense?",
        "How much did I spend on food?",
        "What's my balance?",
        "How can I save money?",
        "Show me recent transactions"
    ]
    
    for query in test_queries:
        print(f"\nUser: {query}")
        result = chat_with_bot(1, query)
        print(f"Bot: {result['response']}")
