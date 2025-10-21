"""
Core business logic for managing financial transactions.
Handles adding, retrieving, and analyzing transactions.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from app.models import Transaction, TransactionType, Category
from app.database import DatabaseManager

logger = logging.getLogger(__name__)


class FinanceManager:
    """
    Main class for managing financial operations.
    
    Responsibilities:
    - Add and retrieve transactions
    - Calculate financial metrics
    - Filter and search transactions
    - Validate business rules
    """
    
    def __init__(self, db_manager: DatabaseManager = None):
        """
        Initialize finance manager.
        
        Args:
            db_manager: Database manager instance (optional)
        """
        self.db_manager = db_manager or DatabaseManager()
        self._transactions: List[Transaction] = []
        self._load_transactions()
    
    def _load_transactions(self) -> None:
        """Load transactions from database."""
        try:
            transaction_data = self.db_manager.load_transactions()
            self._transactions = [
                Transaction.from_dict(t) for t in transaction_data
            ]
        except Exception as e:
            logger.error(f"Failed to load transactions: {e}")
            self._transactions = []
    
    def _save_transactions(self) -> None:
        """Save transactions to database."""
        try:
            transaction_data = [t.to_dict() for t in self._transactions]
            self.db_manager.save_transactions(transaction_data)
        except Exception as e:
            logger.error(f"Failed to save transactions: {e}")
            raise
    
    def add_transaction(
        self,
        amount: float,
        transaction_type: TransactionType,
        category: Category,
        description: Optional[str] = None
    ) -> Transaction:
        """
        Add a new transaction.
        
        Args:
            amount: Transaction amount
            transaction_type: Type of transaction (income/expense)
            category: Transaction category
            description: Optional description
            
        Returns:
            Created Transaction object
            
        Raises:
            ValueError: If amount is invalid
        """
        try:
            # Validate amount
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            # Create new transaction
            transaction_id = self.db_manager.get_next_id()
            transaction = Transaction(
                id=transaction_id,
                amount=amount,
                type=transaction_type,
                category=category,
                description=description
            )
            
            # Add to list and save
            self._transactions.append(transaction)
            self._save_transactions()
            
            logger.info(f"Added {transaction_type.value} transaction: ${amount}")
            return transaction
            
        except ValueError as e:
            logger.error(f"Invalid transaction data: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to add transaction: {e}")
            raise
    
    def get_transactions(
        self,
        transaction_type: Optional[TransactionType] = None,
        category: Optional[Category] = None,
        days: Optional[int] = None
    ) -> List[Transaction]:
        """
        Get transactions with optional filtering.
        
        Args:
            transaction_type: Filter by transaction type
            category: Filter by category
            days: Filter by last N days
            
        Returns:
            List of filtered transactions
        """
        filtered_transactions = self._transactions.copy()
        
        # Apply filters
        if transaction_type:
            filtered_transactions = [
                t for t in filtered_transactions 
                if t.type == transaction_type
            ]
        
        if category:
            filtered_transactions = [
                t for t in filtered_transactions 
                if t.category == category
            ]
        
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_transactions = [
                t for t in filtered_transactions 
                if t.date >= cutoff_date
            ]
        
        # Sort by date (newest first)
        filtered_transactions.sort(key=lambda x: x.date, reverse=True)
        
        return filtered_transactions
    
    def get_balance(self) -> float:
        """Calculate current balance (total income - total expenses)."""
        total_income = sum(
            t.amount for t in self._transactions 
            if t.type == TransactionType.INCOME
        )
        total_expenses = sum(
            t.amount for t in self._transactions 
            if t.type == TransactionType.EXPENSE
        )
        return total_income - total_expenses
    
    def get_category_totals(self) -> Dict[str, float]:
        """
        Calculate total amounts by category.
        
        Returns:
            Dictionary mapping category names to total amounts
        """
        category_totals = {}
        
        for transaction in self._transactions:
            category_name = transaction.category.value
            amount = transaction.amount
            
            if transaction.type == TransactionType.EXPENSE:
                amount = -amount  # Show expenses as negative
            
            category_totals[category_name] = (
                category_totals.get(category_name, 0) + amount
            )
        
        return category_totals
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """
        Delete a transaction by ID.
        
        Args:
            transaction_id: ID of transaction to delete
            
        Returns:
            True if deleted, False if not found
        """
        initial_count = len(self._transactions)
        self._transactions = [
            t for t in self._transactions 
            if t.id != transaction_id
        ]
        
        if len(self._transactions) < initial_count:
            self._save_transactions()
            logger.info(f"Deleted transaction {transaction_id}")
            return True
        
        logger.warning(f"Transaction {transaction_id} not found")
        return False