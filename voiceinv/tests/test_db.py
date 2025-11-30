"""
Test Suite for Database Operations

Tests database CRUD operations, transactions, and backups.
"""

import pytest
import tempfile
import os
from db.database import Database, DatabaseError


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


class TestDatabase:
    """Test Database class."""

    def test_initialization(self, temp_db):
        """Test database initialization."""
        assert temp_db.connection is not None

    def test_add_item(self, temp_db):
        """Test adding an item."""
        item_id = temp_db.add_item(
            name="Test Item",
            category="Test",
            quantity=10,
            unit_price=5.00
        )

        assert item_id is not None
        assert item_id > 0

    def test_add_duplicate_item(self, temp_db):
        """Test adding duplicate item raises error."""
        temp_db.add_item(name="Duplicate", category="Test", quantity=1, unit_price=1.0)

        with pytest.raises(DatabaseError):
            temp_db.add_item(name="Duplicate", category="Test", quantity=1, unit_price=1.0)

    def test_get_item_by_id(self, temp_db):
        """Test retrieving item by ID."""
        item_id = temp_db.add_item(name="Item1", category="Test", quantity=5, unit_price=2.0)

        item = temp_db.get_item_by_id(item_id)

        assert item is not None
        assert item['name'] == "Item1"
        assert item['quantity'] == 5

    def test_get_item_by_name(self, temp_db):
        """Test retrieving item by name."""
        temp_db.add_item(name="Item2", category="Test", quantity=5, unit_price=2.0)

        item = temp_db.get_item_by_name("Item2")

        assert item is not None
        assert item['name'] == "Item2"

    def test_update_item(self, temp_db):
        """Test updating item."""
        item_id = temp_db.add_item(name="Item3", category="Test", quantity=5, unit_price=2.0)

        temp_db.update_item(item_id=item_id, quantity=10, unit_price=3.0)

        item = temp_db.get_item_by_id(item_id)
        assert item['quantity'] == 10
        assert item['unit_price'] == 3.0

    def test_delete_item(self, temp_db):
        """Test deleting item."""
        item_id = temp_db.add_item(name="Item4", category="Test", quantity=5, unit_price=2.0)

        temp_db.delete_item(item_id)

        item = temp_db.get_item_by_id(item_id)
        assert item is None

    def test_get_all_items(self, temp_db):
        """Test getting all items."""
        temp_db.add_item(name="Item5", category="Test", quantity=5, unit_price=2.0)
        temp_db.add_item(name="Item6", category="Test", quantity=10, unit_price=3.0)

        items = temp_db.get_all_items()

        assert len(items) == 2

    def test_search_items(self, temp_db):
        """Test searching items."""
        temp_db.add_item(name="Apple", category="Fruits", quantity=5, unit_price=1.0)
        temp_db.add_item(name="Banana", category="Fruits", quantity=10, unit_price=0.5)
        temp_db.add_item(name="Orange", category="Fruits", quantity=7, unit_price=1.5)

        results = temp_db.search_items("app")

        assert len(results) == 1
        assert results[0]['name'] == "Apple"

    def test_log_transaction(self, temp_db):
        """Test logging a transaction."""
        item_id = temp_db.add_item(name="Item7", category="Test", quantity=5, unit_price=2.0)

        temp_db.log_transaction(item_id=item_id, action="add", amount=5)

        # Verify transaction was logged (would need to add get_transactions method)

    def test_get_recent_transactions(self, temp_db):
        """Test getting recent transactions."""
        item_id = temp_db.add_item(name="Item8", category="Test", quantity=5, unit_price=2.0)
        temp_db.log_transaction(item_id=item_id, action="add", amount=5)

        transactions = temp_db.get_recent_transactions(days=7)

        assert len(transactions) >= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
