"""
Command-line interface for the finance tracker.
Provides user-friendly menu system for interacting with the application.
"""
import sys
from typing import Optional
import logging

from app.models import TransactionType, Category
from app.finance_manager import FinanceManager
from app.report_generator import ReportGenerator

logger = logging.getLogger(__name__)


class FinanceCLI:
    """
    Command-line interface for the Personal Finance Tracker.
    
    Responsibilities:
    - Display menus and prompts
    - Handle user input
    - Coordinate between different components
    - Provide user-friendly output
    """
    
    def __init__(self):
        """Initialize CLI with finance manager and report generator."""
        self.finance_manager = FinanceManager()
        self.report_generator = ReportGenerator(self.finance_manager)
    
    def display_menu(self) -> None:
        """Display main menu options."""
        print("\n" + "="*40)
        print("    PERSONAL FINANCE TRACKER")
        print("="*40)
        print("1. Add Income")
        print("2. Add Expense")
        print("3. View Transactions")
        print("4. View Balance")
        print("5. Generate Report")
        print("6. Delete Transaction")
        print("7. Exit")
        print("-"*40)
    
    def get_user_choice(self) -> str:
        """Get and validate user menu choice."""
        while True:
            choice = input("Enter your choice (1-7): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7']:
                return choice
            print("Invalid choice. Please enter a number between 1-7.")
    
    def get_amount_input(self) -> float:
        """Get and validate amount input from user."""
        while True:
            try:
                amount = float(input("Enter amount: $"))
                if amount <= 0:
                    print("Amount must be positive. Please try again.")
                    continue
                return amount
            except ValueError:
                print("Invalid amount. Please enter a valid number.")
    
    def get_category_input(self, transaction_type: TransactionType) -> Category:
        """Get and validate category input from user."""
        categories = {
            TransactionType.INCOME: [
                Category.SALARY, Category.FREELANCE, 
                Category.INVESTMENT, Category.GIFT
            ],
            TransactionType.EXPENSE: [
                Category.FOOD, Category.TRANSPORT, Category.ENTERTAINMENT,
                Category.UTILITIES, Category.SHOPPING, Category.HEALTHCARE,
                Category.EDUCATION, Category.OTHER
            ]
        }
        
        print("Available categories:")
        available_categories = categories[transaction_type]
        for i, category in enumerate(available_categories, 1):
            print(f"{i}. {category.value}")
        
        while True:
            try:
                choice = int(input("Select category (number): "))
                if 1 <= choice <= len(available_categories):
                    return available_categories[choice - 1]
                print(f"Please enter a number between 1-{len(available_categories)}")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    def add_transaction_flow(self, transaction_type: TransactionType) -> None:
        """Handle the flow for adding a new transaction."""
        try:
            print(f"\nAdding {transaction_type.value.title()}...")
            
            amount = self.get_amount_input()
            category = self.get_category_input(transaction_type)
            description = input("Enter description (optional): ").strip() or None
            
            transaction = self.finance_manager.add_transaction(
                amount=amount,
                transaction_type=transaction_type,
                category=category,
                description=description
            )
            
            print(f"\n✅ {transaction_type.value.title()} added successfully!")
            print(f"   Amount: ${amount:.2f}")
            print(f"   Category: {category.value}")
            if description:
                print(f"   Description: {description}")
                
        except Exception as e:
            print(f"❌ Error adding transaction: {e}")
            logger.error(f"Error in add_transaction_flow: {e}")
    
    def view_transactions_flow(self) -> None:
        """Display transactions with filtering options."""
        try:
            print("\nView Transactions")
            print("1. All transactions")
            print("2. Income only")
            print("3. Expenses only")
            print("4. Last 7 days")
            print("5. Last 30 days")
            
            choice = input("Select filter (1-5): ").strip()
            
            filters = {}
            if choice == '2':
                filters['transaction_type'] = TransactionType.INCOME
            elif choice == '3':
                filters['transaction_type'] = TransactionType.EXPENSE
            elif choice == '4':
                filters['days'] = 7
            elif choice == '5':
                filters['days'] = 30
            
            transactions = self.finance_manager.get_transactions(**filters)
            
            if not transactions:
                print("No transactions found.")
                return
            
            print(f"\n{'Date':<12} {'Type':<8} {'Category':<15} {'Amount':<10} {'Description'}")
            print("-" * 60)
            
            for transaction in transactions:
                date_str = transaction.date.strftime('%Y-%m-%d')
                type_str = transaction.type.value
                category_str = transaction.category.value
                amount_str = f"${transaction.amount:.2f}"
                desc_str = transaction.description or "-"
                
                print(f"{date_str:<12} {type_str:<8} {category_str:<15} {amount_str:<10} {desc_str}")
                
        except Exception as e:
            print(f"❌ Error viewing transactions: {e}")
            logger.error(f"Error in view_transactions_flow: {e}")
    
    def view_balance_flow(self) -> None:
        """Display current balance and category totals."""
        try:
            balance = self.finance_manager.get_balance()
            category_totals = self.finance_manager.get_category_totals()
            
            print(f"\nCurrent Balance: ${balance:.2f}")
            
            if category_totals:
                print("\nCategory Totals:")
                for category, total in category_totals.items():
                    print(f"  {category}: ${total:+.2f}")
                    
        except Exception as e:
            print(f"❌ Error viewing balance: {e}")
            logger.error(f"Error in view_balance_flow: {e}")
    
    def generate_report_flow(self) -> None:
        """Generate and display financial report."""
        try:
            days = input("Enter number of days for report (default 30): ").strip()
            days = int(days) if days.isdigit() else 30
            
            report = self.report_generator.generate_spending_report(days=days)
            formatted_report = self.report_generator.format_report_for_display(report)
            
            print("\n" + formatted_report)
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            logger.error(f"Error in generate_report_flow: {e}")
    
    def delete_transaction_flow(self) -> None:
        """Handle transaction deletion flow."""
        try:
            transactions = self.finance_manager.get_transactions()
            if not transactions:
                print("No transactions to delete.")
                return
            
            print("\nRecent Transactions:")
            for transaction in transactions[:10]:  # Show last 10
                date_str = transaction.date.strftime('%m/%d')
                print(f"{transaction.id}. [{date_str}] {transaction.type.value} - "
                      f"{transaction.category.value} - ${transaction.amount:.2f}")
            
            try:
                transaction_id = int(input("\nEnter transaction ID to delete: "))
            except ValueError:
                print("Invalid transaction ID.")
                return
            
            if self.finance_manager.delete_transaction(transaction_id):
                print("✅ Transaction deleted successfully!")
            else:
                print("❌ Transaction not found.")
                
        except Exception as e:
            print(f"❌ Error deleting transaction: {e}")
            logger.error(f"Error in delete_transaction_flow: {e}")
    
    def run(self) -> None:
        """Main application loop."""
        print("Welcome to Personal Finance Tracker!")
        
        while True:
            try:
                self.display_menu()
                choice = self.get_user_choice()
                
                if choice == '1':
                    self.add_transaction_flow(TransactionType.INCOME)
                elif choice == '2':
                    self.add_transaction_flow(TransactionType.EXPENSE)
                elif choice == '3':
                    self.view_transactions_flow()
                elif choice == '4':
                    self.view_balance_flow()
                elif choice == '5':
                    self.generate_report_flow()
                elif choice == '6':
                    self.delete_transaction_flow()
                elif choice == '7':
                    print("Thank you for using Personal Finance Tracker! 👋")
                    break
                    
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                logger.error(f"Unexpected error in main loop: {e}")