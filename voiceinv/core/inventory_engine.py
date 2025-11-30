"""
Inventory Engine Module

Core business logic for inventory management operations.

Handles:
- Adding items
- Updating stock
- Removing items
- Querying items
- Stock validation
- Transaction logging
- Report generation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from utils.logger import get_logger
from utils.fuzzy_match import FuzzyMatcher
from db.database import Database


class InventoryError(Exception):
    """Base exception for inventory errors."""
    pass


class ItemNotFoundError(InventoryError):
    """Exception when item is not found."""
    pass


class InsufficientStockError(InventoryError):
    """Exception when stock is insufficient."""
    pass


class InventoryEngine:
    """
    Core inventory management engine.
    """

    def __init__(self, database: Database, config: Dict[str, Any]):
        """
        Initialize inventory engine.

        Args:
            database: Database instance
            config: Inventory configuration
        """
        self.database = database
        self.config = config
        self.logger = get_logger(__name__)

        # Configuration
        self.min_stock_alert = config.get('min_stock_alert', 5)
        self.enable_stock_alerts = config.get('enable_stock_alerts', True)
        self.default_unit = config.get('default_unit', 'pcs')
        self.enable_transaction_log = config.get('enable_transaction_log', True)

        # Fuzzy matcher for item names
        self.fuzzy_matcher = FuzzyMatcher(threshold=80)

        self.logger.info("Inventory Engine initialized")

    def add_item(
        self,
        name: str,
        quantity: int,
        unit_price: Optional[float] = None,
        category: Optional[str] = None
    ) -> int:
        """
        Add a new item to inventory or update existing item.

        Args:
            name: Item name
            quantity: Quantity to add
            unit_price: Price per unit
            category: Item category

        Returns:
            Item ID

        Raises:
            InventoryError: If operation fails
        """
        try:
            # Check if item already exists
            existing_item = self._find_item_fuzzy(name)

            if existing_item:
                # Update existing item
                self.logger.info(f"Item '{name}' already exists, updating stock")
                new_quantity = existing_item['quantity'] + quantity

                self.database.update_item(
                    item_id=existing_item['id'],
                    quantity=new_quantity,
                    unit_price=unit_price or existing_item['unit_price']
                )

                # Log transaction
                if self.enable_transaction_log:
                    self.database.log_transaction(
                        item_id=existing_item['id'],
                        action='add',
                        amount=quantity
                    )

                return existing_item['id']
            else:
                # Add new item
                self.logger.info(f"Adding new item: {name}")

                item_id = self.database.add_item(
                    name=name,
                    category=category or 'General',
                    quantity=quantity,
                    unit_price=unit_price or 0.0
                )

                # Log transaction
                if self.enable_transaction_log:
                    self.database.log_transaction(
                        item_id=item_id,
                        action='add',
                        amount=quantity
                    )

                return item_id

        except Exception as e:
            self.logger.error(f"Error adding item: {e}")
            raise InventoryError(f"Failed to add item: {e}")

    def update_stock(self, item_name: str, quantity_change: int) -> int:
        """
        Update stock quantity for an item.

        Args:
            item_name: Name of item
            quantity_change: Change in quantity (positive or negative)

        Returns:
            New quantity

        Raises:
            ItemNotFoundError: If item not found
            InsufficientStockError: If trying to remove more than available
        """
        try:
            # Find item
            item = self._find_item_fuzzy(item_name)

            if not item:
                raise ItemNotFoundError(f"Item '{item_name}' not found")

            # Calculate new quantity
            new_quantity = item['quantity'] + quantity_change

            if new_quantity < 0:
                raise InsufficientStockError(
                    f"Insufficient stock for '{item_name}'. "
                    f"Available: {item['quantity']}, Requested: {abs(quantity_change)}"
                )

            # Update database
            self.database.update_item(
                item_id=item['id'],
                quantity=new_quantity
            )

            # Log transaction
            if self.enable_transaction_log:
                action = 'add' if quantity_change > 0 else 'remove'
                self.database.log_transaction(
                    item_id=item['id'],
                    action=action,
                    amount=abs(quantity_change)
                )

            # Check for low stock alert
            if self.enable_stock_alerts and new_quantity <= self.min_stock_alert:
                self.logger.warning(
                    f"Low stock alert: '{item['name']}' has only {new_quantity} units left"
                )

            return new_quantity

        except (ItemNotFoundError, InsufficientStockError):
            raise
        except Exception as e:
            self.logger.error(f"Error updating stock: {e}")
            raise InventoryError(f"Failed to update stock: {e}")

    def remove_item(self, item_name: str) -> bool:
        """
        Remove an item completely from inventory.

        Args:
            item_name: Name of item to remove

        Returns:
            True if successful

        Raises:
            ItemNotFoundError: If item not found
        """
        try:
            # Find item
            item = self._find_item_fuzzy(item_name)

            if not item:
                raise ItemNotFoundError(f"Item '{item_name}' not found")

            # Log transaction
            if self.enable_transaction_log:
                self.database.log_transaction(
                    item_id=item['id'],
                    action='delete',
                    amount=item['quantity']
                )

            # Remove from database
            self.database.delete_item(item_id=item['id'])

            self.logger.info(f"Removed item: {item['name']}")

            return True

        except ItemNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error removing item: {e}")
            raise InventoryError(f"Failed to remove item: {e}")

    def get_item(self, item_name: str) -> Dict[str, Any]:
        """
        Get item details by name.

        Args:
            item_name: Name of item

        Returns:
            Item dictionary

        Raises:
            ItemNotFoundError: If item not found
        """
        item = self._find_item_fuzzy(item_name)

        if not item:
            raise ItemNotFoundError(f"Item '{item_name}' not found")

        return item

    def get_all_items(self) -> List[Dict[str, Any]]:
        """
        Get all items in inventory.

        Returns:
            List of item dictionaries
        """
        return self.database.get_all_items()

    def search_items(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for items by name.

        Args:
            query: Search query

        Returns:
            List of matching items
        """
        return self.database.search_items(query)

    def generate_report(self, report_type: str = 'summary') -> Dict[str, Any]:
        """
        Generate inventory report.

        Args:
            report_type: Type of report (summary, daily, weekly, monthly)

        Returns:
            Report data dictionary
        """
        try:
            all_items = self.get_all_items()

            report = {
                'type': report_type,
                'generated_at': datetime.now().isoformat(),
                'total_items': len(all_items),
                'total_quantity': sum(item['quantity'] for item in all_items),
                'total_value': sum(item['quantity'] * item['unit_price'] for item in all_items),
                'low_stock_items': [],
                'items': all_items
            }

            # Find low stock items
            if self.enable_stock_alerts:
                report['low_stock_items'] = [
                    item for item in all_items
                    if item['quantity'] <= self.min_stock_alert
                ]

            # Get recent transactions for time-based reports
            if report_type in ['daily', 'weekly', 'monthly']:
                days = {'daily': 1, 'weekly': 7, 'monthly': 30}[report_type]
                report['recent_transactions'] = self.database.get_recent_transactions(days=days)

            return report

        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            raise InventoryError(f"Failed to generate report: {e}")

    def _find_item_fuzzy(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find item using fuzzy matching.

        Args:
            name: Item name to search

        Returns:
            Item dictionary or None
        """
        # First try exact match
        items = self.database.search_items(name)

        if items:
            # Check for exact match
            for item in items:
                if item['name'].lower() == name.lower():
                    return item

            # Return first match
            return items[0]

        # Try fuzzy matching
        all_items = self.get_all_items()
        item_names = [item['name'] for item in all_items]

        best_match = self.fuzzy_matcher.find_best_match(name, item_names)

        if best_match:
            # Find item with matching name
            for item in all_items:
                if item['name'] == best_match:
                    return item

        return None

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get inventory statistics.

        Returns:
            Statistics dictionary
        """
        all_items = self.get_all_items()

        return {
            'total_items': len(all_items),
            'total_quantity': sum(item['quantity'] for item in all_items),
            'total_value': sum(item['quantity'] * item['unit_price'] for item in all_items),
            'categories': len(set(item['category'] for item in all_items)),
            'low_stock_count': len([
                item for item in all_items
                if item['quantity'] <= self.min_stock_alert
            ])
        }
