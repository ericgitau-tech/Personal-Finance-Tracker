"""
Data models for the finance tracker application.
Defines the structure for transactions and categories.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class TransactionType(Enum):
    """Enumeration for transaction types."""
    INCOME = "income"
    EXPENSE = "expense"


class Category(Enum):
    """Predefined categories for transactions."""
    # Income categories
    SALARY = "Salary"
    FREELANCE = "Freelance"
    INVESTMENT = "Investment"
    GIFT = "Gift"
    
    # Expense categories
    FOOD = "Food"
    TRANSPORT = "Transport"
    ENTERTAINMENT = "Entertainment"
    UTILITIES = "Utilities"
    SHOPPING = "Shopping"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    OTHER = "Other"


@dataclass
class Transaction:
    """
    Represents a financial transaction.
    
    Attributes:
        id: Unique identifier for the transaction
        amount: Transaction amount (positive)
        type: Type of transaction (income/expense)
        category: Category of transaction
        description: Optional description
        date: Transaction date
    """
    id: int
    amount: float
    type: TransactionType
    category: Category
    description: Optional[str] = None
    date: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate transaction data after initialization."""
        if self.amount <= 0:
            raise ValueError("Amount must be positive")
        
        if self.date is None:
            self.date = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary for storage."""
        return {
            'id': self.id,
            'amount': self.amount,
            'type': self.type.value,
            'category': self.category.value,
            'description': self.description,
            'date': self.date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """Create Transaction instance from dictionary."""
        return cls(
            id=data['id'],
            amount=data['amount'],
            type=TransactionType(data['type']),
            category=Category(data['category']),
            description=data.get('description'),
            date=datetime.fromisoformat(data['date'])
        )