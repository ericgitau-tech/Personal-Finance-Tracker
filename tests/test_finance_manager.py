"""
Unit tests for FinanceManager class.
Tests core functionality and edge cases.
"""
import unittest
import tempfile
import os
import json
from datetime import datetime

from app.models import Transaction, TransactionType, Category
from app.finance_manager import FinanceManager
from app.database import DatabaseManager


class TestFinanceManager(unittest.TestCase):
    """Test cases for FinanceManager functionality."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        )
        json.dump([], self.temp_file)
        self.temp_file.close()
        
        # Initialize database and finance manager with temp file
        self.db_manager = DatabaseManager(self.temp_file.name)
        self.finance_manager = FinanceManager(self.db_manager)
    
    def tearDown(self):
        """Clean up after each test."""
        os.unlink(self.temp_file.name)
    
    def test_add_income_transaction(self):
        """Test adding an income transaction."""
        transaction = self.finance_manager.add_transaction(
            amount=1000.0,
            transaction_type=TransactionType.INCOME,
            category=Category.SALARY,
            description="Monthly salary"
        )
        
        self.assertEqual(transaction.amount, 1000.0)
        self.assertEqual(transaction.type, TransactionType.INCOME)
        self.assertEqual(transaction.category, Category.SALARY)
        self.assertEqual(transaction.description, "Monthly salary")
    
    def test_add_expense_transaction(self):
        """Test adding an expense transaction."""
        transaction = self.finance_manager.add_transaction(
            amount=50.0,
            transaction_type=TransactionType.EXPENSE,
            category=Category.FOOD,
            description="Groceries"
        )
        
        self.assertEqual(transaction.amount, 50.0)
        self.assertEqual(transaction.type, TransactionType.EXPENSE)
        self.assertEqual(transaction.category, Category.FOOD)
    
    def test_add_transaction_invalid_amount(self):
        """Test adding transaction with invalid amount."""
        with self.assertRaises(ValueError):
            self.finance_manager.add_transaction(
                amount=-100.0,  # Invalid negative amount
                transaction_type=TransactionType.INCOME,
                category=Category.SALARY
            )
    
    def test_get_balance_calculation(self):
        """Test balance calculation with multiple transactions."""
        # Add income
        self.finance_manager.add_transaction(
            amount=1000.0,
            transaction_type=TransactionType.INCOME,
            category=Category.SALARY
        )
        
        # Add expenses
        self.finance_manager.add_transaction(
            amount=100.0,
            transaction_type=TransactionType.EXPENSE,
            category=Category.FOOD
        )
        self.finance_manager.add_transaction(
            amount=50.0,
            transaction_type=TransactionType.EXPENSE,
            category=Category.TRANSPORT
        )
        
        balance = self.finance_manager.get_balance()
        expected_balance = 1000.0 - 100.0 - 50.0
        self.assertEqual(balance, expected_balance)
    
    def test_get_transactions_with_filters(self):
        """Test transaction filtering functionality."""
        # Add test transactions
        self.finance_manager.add_transaction(
            amount=1000.0,
            transaction_type=TransactionType.INCOME,
            category=Category.SALARY
        )
        self.finance_manager.add_transaction(
            amount=100.0,
            transaction_type=TransactionType.EXPENSE,
            category=Category.FOOD
        )
        
        # Test income filter
        income_transactions = self.finance_manager.get_transactions(
            transaction_type=TransactionType.INCOME
        )
        self.assertEqual(len(income_transactions), 1)
        self.assertEqual(income_transactions[0].type, TransactionType.INCOME)
        
        # Test expense filter
        expense_transactions = self.finance_manager.get_transactions(
            transaction_type=TransactionType.EXPENSE
        )
        self.assertEqual(len(expense_transactions), 1)
        self.assertEqual(expense_transactions[0].type, TransactionType.EXPENSE)
    
    def test_delete_transaction(self):
        """Test transaction deletion."""
        transaction = self.finance_manager.add_transaction(
            amount=100.0,
            transaction_type=TransactionType.EXPENSE,
            category=Category.FOOD
        )
        
        # Verify transaction exists
        transactions_before = self.finance_manager.get_transactions()
        self.assertEqual(len(transactions_before), 1)
        
        # Delete transaction
        result = self.finance_manager.delete_transaction(transaction.id)
        self.assertTrue(result)
        
        # Verify transaction deleted
        transactions_after = self.finance_manager.get_transactions()
        self.assertEqual(len(transactions_after), 0)
    
    def test_delete_nonexistent_transaction(self):
        """Test deleting a transaction that doesn't exist."""
        result = self.finance_manager.delete_transaction(999)  # Non-existent ID
        self.assertFalse(result)


class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        )
        json.dump([], self.temp_file)
        self.temp_file.close()
        
        self.db_manager = DatabaseManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up after each test."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_save_and_load_transactions(self):
        """Test saving and loading transactions."""
        # Create test data
        test_data = [
            {
                'id': 1,
                'amount': 100.0,
                'type': 'income',
                'category': 'Salary',
                'description': 'Test income',
                'date': '2023-01-01T00:00:00'
            }
        ]
        
        # Save data
        self.db_manager.save_transactions(test_data)
        
        # Load data
        loaded_data = self.db_manager.load_transactions()
        
        self.assertEqual(loaded_data, test_data)
    
    def test_get_next_id(self):
        """Test ID generation."""
        test_data = [
            {'id': 1, 'amount': 100.0, 'type': 'income', 
             'category': 'Salary', 'description': 'Test', 'date': '2023-01-01T00:00:00'},
            {'id': 5, 'amount': 50.0, 'type': 'expense', 
             'category': 'Food', 'description': 'Test', 'date': '2023-01-01T00:00:00'}
        ]
        
        self.db_manager.save_transactions(test_data)
        next_id = self.db_manager.get_next_id()
        
        self.assertEqual(next_id, 6)  # Should be max(1, 5) + 1 = 6


if __name__ == '__main__':
    unittest.main()