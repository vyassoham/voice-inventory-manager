"""
Database Module

SQLite database operations for inventory management.

Handles:
- Item CRUD operations
- Transaction logging
- Database initialization
- Backup management
- Search operations
"""

import sqlite3
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, timedelta
import shutil
from utils.logger import get_logger


class DatabaseError(Exception):
    """Base exception for database errors."""
    pass


class Database:
    """
    SQLite database manager for inventory system.
    """

    def __init__(self, db_path: str, backup_enabled: bool = True, backup_path: str = "data/backups/"):
        """
        Initialize database.

        Args:
            db_path: Path to SQLite database file
            backup_enabled: Enable automatic backups
            backup_path: Path to backup directory
        """
        self.db_path = Path(db_path)
        self.backup_enabled = backup_enabled
        self.backup_path = Path(backup_path)
        self.logger = get_logger(__name__)

        # Create directories if needed
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if self.backup_enabled:
            self.backup_path.mkdir(parents=True, exist_ok=True)

        self.connection = None

    def initialize(self):
        """Initialize database and create tables if needed."""
        try:
            self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.connection.row_factory = sqlite3.Row

            self._create_tables()

            self.logger.info(f"Database initialized: {self.db_path}")

        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")

    def _create_tables(self):
        """Create database tables."""
        cursor = self.connection.cursor()

        # Items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL DEFAULT 'General',
                quantity INTEGER NOT NULL DEFAULT 0,
                unit_price REAL NOT NULL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                amount INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_name ON items(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_item_id ON transactions(item_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp)")

        self.connection.commit()

        self.logger.debug("Database tables created/verified")

    def add_item(self, name: str, category: str, quantity: int, unit_price: float) -> int:
        """
        Add a new item to inventory.

        Args:
            name: Item name
            category: Item category
            quantity: Initial quantity
            unit_price: Price per unit

        Returns:
            Item ID

        Raises:
            DatabaseError: If operation fails
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute("""
                INSERT INTO items (name, category, quantity, unit_price)
                VALUES (?, ?, ?, ?)
            """, (name, category, quantity, unit_price))

            self.connection.commit()

            item_id = cursor.lastrowid

            self.logger.debug(f"Added item: {name} (ID: {item_id})")

            return item_id

        except sqlite3.IntegrityError as e:
            self.logger.error(f"Item already exists: {name}")
            raise DatabaseError(f"Item '{name}' already exists")
        except Exception as e:
            self.logger.error(f"Error adding item: {e}")
            raise DatabaseError(f"Failed to add item: {e}")

    def update_item(
        self,
        item_id: int,
        quantity: Optional[int] = None,
        unit_price: Optional[float] = None,
        category: Optional[str] = None
    ):
        """
        Update item details.

        Args:
            item_id: Item ID
            quantity: New quantity (optional)
            unit_price: New unit price (optional)
            category: New category (optional)

        Raises:
            DatabaseError: If operation fails
        """
        try:
            cursor = self.connection.cursor()

            updates = []
            params = []

            if quantity is not None:
                updates.append("quantity = ?")
                params.append(quantity)

            if unit_price is not None:
                updates.append("unit_price = ?")
                params.append(unit_price)

            if category is not None:
                updates.append("category = ?")
                params.append(category)

            if not updates:
                return

            updates.append("last_updated = CURRENT_TIMESTAMP")

            query = f"UPDATE items SET {', '.join(updates)} WHERE id = ?"
            params.append(item_id)

            cursor.execute(query, params)
            self.connection.commit()

            self.logger.debug(f"Updated item ID: {item_id}")

        except Exception as e:
            self.logger.error(f"Error updating item: {e}")
            raise DatabaseError(f"Failed to update item: {e}")

    def delete_item(self, item_id: int):
        """
        Delete an item from inventory.

        Args:
            item_id: Item ID

        Raises:
            DatabaseError: If operation fails
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
            self.connection.commit()

            self.logger.debug(f"Deleted item ID: {item_id}")

        except Exception as e:
            self.logger.error(f"Error deleting item: {e}")
            raise DatabaseError(f"Failed to delete item: {e}")

    def get_item_by_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        """
        Get item by ID.

        Args:
            item_id: Item ID

        Returns:
            Item dictionary or None
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
            row = cursor.fetchone()

            if row:
                return dict(row)

            return None

        except Exception as e:
            self.logger.error(f"Error getting item: {e}")
            return None

    def get_item_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get item by exact name.

        Args:
            name: Item name

        Returns:
            Item dictionary or None
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute("SELECT * FROM items WHERE LOWER(name) = LOWER(?)", (name,))
            row = cursor.fetchone()

            if row:
                return dict(row)

            return None

        except Exception as e:
            self.logger.error(f"Error getting item: {e}")
            return None

    def get_all_items(self) -> List[Dict[str, Any]]:
        """
        Get all items in inventory.

        Returns:
            List of item dictionaries
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute("SELECT * FROM items ORDER BY name")
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

        except Exception as e:
            self.logger.error(f"Error getting all items: {e}")
            return []

    def search_items(self, query: str) -> List[Dict[str, Any]]:
        """
        Search items by name.

        Args:
            query: Search query

        Returns:
            List of matching items
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute(
                "SELECT * FROM items WHERE LOWER(name) LIKE LOWER(?) ORDER BY name",
                (f"%{query}%",)
            )
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

        except Exception as e:
            self.logger.error(f"Error searching items: {e}")
            return []

    def log_transaction(self, item_id: int, action: str, amount: int):
        """
        Log a transaction.

        Args:
            item_id: Item ID
            action: Action type (add, remove, delete)
            amount: Amount involved

        Raises:
            DatabaseError: If operation fails
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute("""
                INSERT INTO transactions (item_id, action, amount)
                VALUES (?, ?, ?)
            """, (item_id, action, amount))

            self.connection.commit()

            self.logger.debug(f"Logged transaction: item_id={item_id}, action={action}, amount={amount}")

        except Exception as e:
            self.logger.error(f"Error logging transaction: {e}")
            raise DatabaseError(f"Failed to log transaction: {e}")

    def get_recent_transactions(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get recent transactions.

        Args:
            days: Number of days to look back

        Returns:
            List of transaction dictionaries
        """
        try:
            cursor = self.connection.cursor()

            cutoff_date = datetime.now() - timedelta(days=days)

            cursor.execute("""
                SELECT t.*, i.name as item_name
                FROM transactions t
                JOIN items i ON t.item_id = i.id
                WHERE t.timestamp >= ?
                ORDER BY t.timestamp DESC
            """, (cutoff_date,))

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

        except Exception as e:
            self.logger.error(f"Error getting transactions: {e}")
            return []

    def backup(self) -> bool:
        """
        Create a backup of the database.

        Returns:
            True if successful, False otherwise
        """
        if not self.backup_enabled:
            return False

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_path / f"inventory_backup_{timestamp}.db"

            shutil.copy2(self.db_path, backup_file)

            self.logger.info(f"Database backed up to: {backup_file}")

            return True

        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False

    def close(self):
        """Close database connection."""
        if self.connection:
            # Create backup before closing
            if self.backup_enabled:
                self.backup()

            self.connection.close()
            self.logger.info("Database connection closed")
