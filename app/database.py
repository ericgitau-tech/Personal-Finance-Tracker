"""
Database management for storing and retrieving transactions.
Uses JSON file for simplicity, easily replaceable with SQLite.
"""
import json
import os
from typing import List, Dict, Any
from pathlib import Path
import logging

from app.models import Transaction

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages transaction data storage and retrieval.
    
    Responsibilities:
    - Save transactions to JSON file
    - Load transactions from JSON file
    - Generate unique IDs
    - Handle file operations safely
    """
    
    def __init__(self, file_path: str = "data/transactions.json"):
        """
        Initialize database manager.
        
        Args:
            file_path: Path to the JSON data file
        """
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_data_file()
    
    def _ensure_data_file(self) -> None:
        """Create data file if it doesn't exist."""
        if not self.file_path.exists():
            try:
                with open(self.file_path, 'w') as f:
                    json.dump([], f)
                logger.info(f"Created new data file: {self.file_path}")
            except IOError as e:
                logger.error(f"Failed to create data file: {e}")
                raise
    
    def load_transactions(self) -> List[Dict[str, Any]]:
        """
        Load all transactions from the data file.
        
        Returns:
            List of transaction dictionaries
            
        Raises:
            IOError: If file cannot be read
            JSONDecodeError: If file contains invalid JSON
        """
        try:
            with open(self.file_path, 'r') as f:
                transactions = json.load(f)
            logger.info(f"Loaded {len(transactions)} transactions")
            return transactions
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error loading transactions: {e}")
            raise
    
    def save_transactions(self, transactions: List[Dict[str, Any]]) -> None:
        """
        Save transactions to the data file.
        
        Args:
            transactions: List of transaction dictionaries to save
            
        Raises:
            IOError: If file cannot be written
        """
        try:
            # Create backup of existing data
            backup_path = self.file_path.with_suffix('.json.backup')
            if self.file_path.exists():
                import shutil
                shutil.copy2(self.file_path, backup_path)
            
            # Save new data
            with open(self.file_path, 'w') as f:
                json.dump(transactions, f, indent=2)
            logger.info(f"Saved {len(transactions)} transactions")
        except IOError as e:
            logger.error(f"Error saving transactions: {e}")
            raise
    
    def get_next_id(self) -> int:
        """
        Generate next available transaction ID.
        
        Returns:
            Next available integer ID
        """
        transactions = self.load_transactions()
        if not transactions:
            return 1
        return max(t['id'] for t in transactions) + 1