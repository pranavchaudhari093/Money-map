"""
MoneyMap - AI Expense Analyzer
Analyzes spending patterns and provides insights
"""

from datetime import datetime, timedelta
import sqlite3
from sklearn.preprocessing import LabelEncoder
import numpy as np


class ExpenseAnalyzer:
    """AI-powered expense analyzer for spending insights"""
    
    def __init__(self, db_path='database.db'):
        self.db_path = db_path
        self.label_encoder = LabelEncoder()
        
    def get_user_expenses(self, user_id, months=6):
        """Get user expenses for the last N months"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate date range
        start_date = datetime.now() - timedelta(days=months * 30)
        
        query = """
            SELECT 
                id, title, amount, category, date, description
            FROM expenses
            WHERE user_id = ? AND date >= ?
            ORDER BY date DESC
        """
        
        cursor.execute(query, (user_id, start_date.strftime('%Y-%m-%d')))
        expenses = cursor.fetchall()
        
        conn.close()
        
        return [
            {
                'id': row[0],
                'title': row[1],
                'amount': row[2],
                'category': row[3],
                'date': row[4],
                'description': row[5]
            }
            for row in expenses
        ]
    
    def get_user_income(self, user_id, months=6):
        """Get user income for the last N months"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=months * 30)
        
        query = """
            SELECT 
                id, source, amount, date, description
            FROM income
            WHERE user_id = ? AND date >= ?
            ORDER BY date DESC
        """
        
        cursor.execute(query, (user_id, start_date.strftime('%Y-%m-%d')))
        income_list = cursor.fetchall()
        
        conn.close()
        
        return [
            {
                'id': row[0],
                'source': row[1],
                'amount': row[2],
                'date': row[3],
                'description': row[4]
            }
            for row in income_list
        ]
    
    def analyze_category_spending(self, expenses):
        """Analyze spending by category"""
        category_totals = {}
        
        for expense in expenses:
            category = expense['category']
            amount = float(expense['amount'])
            
            if category not in category_totals:
                category_totals[category] = 0
            
            category_totals[category] += amount
        
        # Sort by total amount
        sorted_categories = sorted(
            category_totals.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return dict(sorted_categories)
    
    def analyze_monthly_trends(self, expenses):
        """Analyze monthly spending trends"""
        monthly_totals = {}
        
        for expense in expenses:
            date = expense['date']
            amount = float(expense['amount'])
            
            # Extract month (YYYY-MM)
            if isinstance(date, str):
                month = date[:7]  # YYYY-MM
            else:
                month = date.strftime('%Y-%m')
            
            if month not in monthly_totals:
                monthly_totals[month] = 0
            
            monthly_totals[month] += amount
        
        # Sort by month
        sorted_months = sorted(monthly_totals.items())
        
        return dict(sorted_months)
    
    def identify_highest_spending_category(self, category_analysis):
        """Identify the category with highest spending"""
        if not category_analysis:
            return None, 0
        
        highest_category = max(category_analysis, key=category_analysis.get)
        highest_amount = category_analysis[highest_category]
        
        return highest_category, highest_amount
    
    def calculate_saving_potential(self, income_list, expenses):
        """Calculate potential savings"""
        total_income = sum(float(inc['amount']) for inc in income_list)
        total_expenses = sum(float(exp['amount']) for exp in expenses)
        
        if total_income == 0:
            return 0, 0
        
        actual_savings = total_income - total_expenses
        savings_rate = (actual_savings / total_income) * 100
        
        # Recommend 20% savings rule
        recommended_savings = total_income * 0.20
        potential_additional_savings = max(0, recommended_savings - actual_savings)
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'actual_savings': actual_savings,
            'savings_rate': savings_rate,
            'recommended_savings': recommended_savings,
            'potential_additional_savings': potential_additional_savings
        }
    
    def detect_unusual_spending(self, expenses, threshold=1.5):
        """Detect unusually high expenses"""
        if len(expenses) < 3:
            return []
        
        amounts = [float(exp['amount']) for exp in expenses]
        avg_amount = np.mean(amounts)
        std_amount = np.std(amounts)
        
        unusual_expenses = []
        
        for expense in expenses:
            amount = float(expense['amount'])
            
            # Check if expense is significantly above average
            if amount > (avg_amount + threshold * std_amount):
                unusual_expenses.append({
                    'expense': expense,
                    'deviation': (amount - avg_amount) / std_amount if std_amount > 0 else 0
                })
        
        return unusual_expenses
    
    def generate_insights(self, user_id):
        """Generate comprehensive financial insights"""
        # Get data
        expenses = self.get_user_expenses(user_id)
        income_list = self.get_user_income(user_id)
        
        if not expenses:
            return {
                'success': False,
                'message': 'No expenses found to analyze'
            }
        
        # Perform analyses
        category_analysis = self.analyze_category_spending(expenses)
        monthly_trends = self.analyze_monthly_trends(expenses)
        highest_category, highest_amount = self.identify_highest_spending_category(category_analysis)
        saving_potential = self.calculate_saving_potential(income_list, expenses)
        unusual_expenses = self.detect_unusual_spending(expenses)
        
        # Generate recommendations
        recommendations = []
        
        if highest_category:
            percentage = (highest_amount / sum(category_analysis.values())) * 100
            recommendations.append(
                f"You spend {percentage:.1f}% of your income on {highest_category}. "
                f"Consider setting a budget for this category."
            )
        
        if saving_potential['savings_rate'] < 20:
            recommendations.append(
                f"Your current savings rate is {saving_potential['savings_rate']:.1f}%. "
                f"Try to save at least 20% of your income."
            )
        
        if unusual_expenses:
            recommendations.append(
                f"We detected {len(unusual_expenses)} unusually high expenses. "
                f"Review these to optimize your spending."
            )
        
        # Monthly trend analysis
        trend_message = ""
        if len(monthly_trends) >= 2:
            months = list(monthly_trends.keys())
            recent_month = monthly_trends[months[-1]]
            previous_month = monthly_trends[months[-2]]
            
            if recent_month > previous_month:
                change = ((recent_month - previous_month) / previous_month) * 100
                trend_message = f"Your spending increased by {change:.1f}% this month."
            else:
                change = ((previous_month - recent_month) / previous_month) * 100
                trend_message = f"Great! Your spending decreased by {change:.1f}% this month."
        
        return {
            'success': True,
            'category_breakdown': category_analysis,
            'monthly_trends': monthly_trends,
            'highest_spending_category': {
                'category': highest_category,
                'amount': highest_amount
            },
            'saving_analysis': saving_potential,
            'unusual_expenses': unusual_expenses,
            'recommendations': recommendations,
            'trend_message': trend_message
        }
    
    def get_spending_summary(self, user_id):
        """Get a quick spending summary"""
        insights = self.generate_insights(user_id)
        
        if not insights['success']:
            return "No spending data available."
        
        summary_parts = []
        
        if insights.get('trend_message'):
            summary_parts.append(insights['trend_message'])
        
        if insights.get('highest_spending_category'):
            cat = insights['highest_spending_category']
            summary_parts.append(
                f"Your highest spending category is {cat['category']} "
                f"(₹{cat['amount']:,.2f})"
            )
        
        if insights.get('saving_analysis'):
            savings = insights['saving_analysis']
            summary_parts.append(
                f"You're saving {savings['savings_rate']:.1f}% of your income"
            )
        
        return " ".join(summary_parts)


def analyze_expenses(user_id, db_path='database.db'):
    """Convenience function to analyze user expenses"""
    analyzer = ExpenseAnalyzer(db_path)
    return analyzer.generate_insights(user_id)


def get_spending_summary(user_id, db_path='database.db'):
    """Convenience function to get spending summary"""
    analyzer = ExpenseAnalyzer(db_path)
    return analyzer.get_spending_summary(user_id)


# Example usage
if __name__ == "__main__":
    # Test the analyzer
    result = analyze_expenses(user_id=1)
    
    if result['success']:
        print("Category Breakdown:", result['category_breakdown'])
        print("Monthly Trends:", result['monthly_trends'])
        print("Recommendations:", result['recommendations'])
    else:
        print(result['message'])
