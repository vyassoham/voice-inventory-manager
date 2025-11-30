"""
Test Suite for Inventory Engine

Tests inventory management operations including:
- Adding items
- Updating stock
- Removing items
- Querying items
- Report generation
"""

import pytest
from core.inventory_engine import InventoryEngine, ItemNotFoundError, InsufficientStockError
from db.database import Database
import tempfile
import os


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    db = Database(db_path=path, backup_enabled=False)
    db.initialize()

    yield db

    # Cleanup
    db.close()
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def inventory_engine(temp_db):
    """Create inventory engine instance."""
    config = {
        'min_stock_alert': 5,
        'enable_stock_alerts': True,
        'default_unit': 'pcs',
        'enable_transaction_log': True
    }

    return InventoryEngine(database=temp_db, config=config)


class TestInventoryEngine:
    """Test InventoryEngine class."""

    def test_add_new_item(self, inventory_engine):
        """Test adding a new item."""
        item_id = inventory_engine.add_item(
            name="Apple",
            quantity=10,
            unit_price=1.50,
            category="Fruits"
        )

        assert item_id is not None
        assert item_id > 0

    def test_add_existing_item(self, inventory_engine):
        """Test adding to existing item increases quantity."""
        # Add first time
        inventory_engine.add_item(name="Banana", quantity=5, unit_price=0.75)

        # Add again
        inventory_engine.add_item(name="Banana", quantity=3, unit_price=0.75)

        # Check quantity
        item = inventory_engine.get_item("Banana")
        assert item['quantity'] == 8

    def test_update_stock_increase(self, inventory_engine):
        """Test increasing stock."""
        inventory_engine.add_item(name="Orange", quantity=10)

        new_qty = inventory_engine.update_stock("Orange", 5)

        assert new_qty == 15

    def test_update_stock_decrease(self, inventory_engine):
        """Test decreasing stock."""
        inventory_engine.add_item(name="Mango", quantity=10)

        new_qty = inventory_engine.update_stock("Mango", -3)

        assert new_qty == 7

    def test_update_stock_insufficient(self, inventory_engine):
        """Test updating stock with insufficient quantity."""
        inventory_engine.add_item(name="Grape", quantity=5)

        with pytest.raises(InsufficientStockError):
            inventory_engine.update_stock("Grape", -10)

    def test_remove_item(self, inventory_engine):
        """Test removing an item."""
        inventory_engine.add_item(name="Peach", quantity=10)

        result = inventory_engine.remove_item("Peach")

        assert result is True

        # Verify item is gone
        with pytest.raises(ItemNotFoundError):
            inventory_engine.get_item("Peach")

    def test_remove_nonexistent_item(self, inventory_engine):
        """Test removing non-existent item."""
        with pytest.raises(ItemNotFoundError):
            inventory_engine.remove_item("NonExistent")

    def test_get_item(self, inventory_engine):
        """Test getting item details."""
        inventory_engine.add_item(
            name="Watermelon",
            quantity=3,
            unit_price=5.00,
            category="Fruits"
        )

        item = inventory_engine.get_item("Watermelon")

        assert item is not None
        assert item['name'] == "Watermelon"
        assert item['quantity'] == 3
        assert item['unit_price'] == 5.00

    def test_get_all_items(self, inventory_engine):
        """Test getting all items."""
        inventory_engine.add_item(name="Item1", quantity=5)
        inventory_engine.add_item(name="Item2", quantity=10)
        inventory_engine.add_item(name="Item3", quantity=15)

        items = inventory_engine.get_all_items()

        assert len(items) == 3

    def test_generate_report(self, inventory_engine):
        """Test report generation."""
        inventory_engine.add_item(name="Item1", quantity=10, unit_price=2.00)
        inventory_engine.add_item(name="Item2", quantity=5, unit_price=3.00)

        report = inventory_engine.generate_report('summary')

        assert report['total_items'] == 2
        assert report['total_quantity'] == 15
        assert report['total_value'] == 35.00

    def test_fuzzy_matching(self, inventory_engine):
        """Test fuzzy item name matching."""
        inventory_engine.add_item(name="Strawberry", quantity=10)

        # Try with typo
        item = inventory_engine.get_item("Strawbery")  # Missing 'r'

        assert item is not None
        assert item['name'] == "Strawberry"

    def test_statistics(self, inventory_engine):
        """Test statistics generation."""
        inventory_engine.add_item(name="Item1", quantity=10, unit_price=2.00)
        inventory_engine.add_item(name="Item2", quantity=3, unit_price=5.00)  # Low stock

        stats = inventory_engine.get_statistics()

        assert stats['total_items'] == 2
        assert stats['low_stock_count'] == 1  # Item2 is below threshold


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
