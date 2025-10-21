"""
Generates financial reports and summaries.
Provides insights into spending patterns and financial health.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

from app.models import Transaction, TransactionType, Category

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates various financial reports and analyses.
    
    Responsibilities:
    - Generate spending summaries
    - Create category breakdowns
    - Calculate monthly trends
    - Format reports for display
    """
    
    def __init__(self, finance_manager):
        """
        Initialize report generator.
        
        Args:
            finance_manager: FinanceManager instance
        """
        self.finance_manager = finance_manager
    
    def generate_spending_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive spending report.
        
        Args:
            days: Number of days to include in report
            
        Returns:
            Dictionary containing report data
        """
        try:
            recent_transactions = self.finance_manager.get_transactions(days=days)
            category_totals = self.finance_manager.get_category_totals()
            balance = self.finance_manager.get_balance()
            
            # Calculate metrics
            total_income = sum(
                t.amount for t in recent_transactions 
                if t.type == TransactionType.INCOME
            )
            total_expenses = sum(
                t.amount for t in recent_transactions 
                if t.type == TransactionType.EXPENSE
            )
            
            # Find largest expense
            expenses = [t for t in recent_transactions if t.type == TransactionType.EXPENSE]
            largest_expense = max(expenses, key=lambda x: x.amount) if expenses else None
            
            report = {
                'period_days': days,
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_balance': total_income - total_expenses,
                'current_balance': balance,
                'transaction_count': len(recent_transactions),
                'category_breakdown': category_totals,
                'largest_expense': {
                    'amount': largest_expense.amount,
                    'category': largest_expense.category.value,
                    'description': largest_expense.description
                } if largest_expense else None,
                'average_daily_spending': total_expenses / days if days > 0 else 0,
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info(f"Generated spending report for {days} days")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate spending report: {e}")
            raise
    
    def generate_category_report(self) -> Dict[str, Dict[str, float]]:
        """
        Generate detailed report by category.
        
        Returns:
            Dictionary with income and expense totals by category
        """
        transactions = self.finance_manager.get_transactions()
        
        income_by_category = {}
        expenses_by_category = {}
        
        for transaction in transactions:
            category_name = transaction.category.value
            
            if transaction.type == TransactionType.INCOME:
                income_by_category[category_name] = (
                    income_by_category.get(category_name, 0) + transaction.amount
                )
            else:
                expenses_by_category[category_name] = (
                    expenses_by_category.get(category_name, 0) + transaction.amount
                )
        
        return {
            'income': income_by_category,
            'expenses': expenses_by_category
        }
    
    def format_report_for_display(self, report: Dict[str, Any]) -> str:
        """
        Format report data into human-readable string.
        
        Args:
            report: Report data dictionary
            
        Returns:
            Formatted string report
        """
        lines = []
        lines.append("=" * 50)
        lines.append("FINANCIAL REPORT")
        lines.append("=" * 50)
        lines.append(f"Period: Last {report['period_days']} days")
        lines.append(f"Generated: {datetime.fromisoformat(report['generated_at']).strftime('%Y-%m-%d %H:%M')}")
        lines.append("-" * 50)
        lines.append(f"Total Income: ${report['total_income']:.2f}")
        lines.append(f"Total Expenses: ${report['total_expenses']:.2f}")
        lines.append(f"Net Balance: ${report['net_balance']:.2f}")
        lines.append(f"Current Overall Balance: ${report['current_balance']:.2f}")
        lines.append(f"Transactions: {report['transaction_count']}")
        lines.append(f"Average Daily Spending: ${report['average_daily_spending']:.2f}")
        
        if report['largest_expense']:
            lines.append("-" * 50)
            lines.append("Largest Expense:")
            lines.append(f"  Amount: ${report['largest_expense']['amount']:.2f}")
            lines.append(f"  Category: {report['largest_expense']['category']}")
            if report['largest_expense']['description']:
                lines.append(f"  Description: {report['largest_expense']['description']}")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)