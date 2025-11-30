# API Specification

## Overview

This document describes the internal API structure of the Voice Inventory Manager. While the current version is a standalone application, this API specification serves as a foundation for future web service and integration capabilities.

---

## Core APIs

### Voice Engine API

#### `VoiceEngine.listen_for_command(timeout: Optional[int]) -> Optional[str]`

Listen for a voice command.

**Parameters:**
- `timeout` (optional): Maximum time to wait in seconds

**Returns:**
- Recognized text string or None

**Example:**
```python
text = voice_engine.listen_for_command(timeout=5)
if text:
    print(f"Heard: {text}")
```

#### `VoiceEngine.process_command(text: str) -> Dict[str, Any]`

Process a command through the complete pipeline.

**Parameters:**
- `text`: Command text

**Returns:**
```python
{
    'success': bool,
    'text': str,
    'intent': str,
    'response': str,
    'error': Optional[str]
}
```

**Example:**
```python
result = voice_engine.process_command("add 10 apples")
if result['success']:
    print(result['response'])
```

---

### Inventory Engine API

#### `InventoryEngine.add_item(...) -> int`

Add a new item or update existing item quantity.

**Parameters:**
```python
name: str              # Item name (required)
quantity: int          # Quantity (required)
unit_price: float      # Price per unit (optional)
category: str          # Category (optional)
```

**Returns:**
- Item ID (integer)

**Raises:**
- `InventoryError`: If operation fails

**Example:**
```python
item_id = inventory_engine.add_item(
    name="Apple",
    quantity=10,
    unit_price=1.50,
    category="Fruits"
)
```

#### `InventoryEngine.update_stock(item_name: str, quantity_change: int) -> int`

Update stock quantity for an item.

**Parameters:**
- `item_name`: Name of item
- `quantity_change`: Change in quantity (positive or negative)

**Returns:**
- New quantity

**Raises:**
- `ItemNotFoundError`: If item doesn't exist
- `InsufficientStockError`: If trying to remove more than available

**Example:**
```python
new_qty = inventory_engine.update_stock("Apple", 5)  # Add 5
new_qty = inventory_engine.update_stock("Apple", -3)  # Remove 3
```

#### `InventoryEngine.remove_item(item_name: str) -> bool`

Remove an item completely from inventory.

**Parameters:**
- `item_name`: Name of item to remove

**Returns:**
- True if successful

**Raises:**
- `ItemNotFoundError`: If item doesn't exist

**Example:**
```python
inventory_engine.remove_item("Apple")
```

#### `InventoryEngine.get_item(item_name: str) -> Dict[str, Any]`

Get item details by name.

**Parameters:**
- `item_name`: Name of item

**Returns:**
```python
{
    'id': int,
    'name': str,
    'category': str,
    'quantity': int,
    'unit_price': float,
    'created_at': str,
    'last_updated': str
}
```

**Raises:**
- `ItemNotFoundError`: If item doesn't exist

**Example:**
```python
item = inventory_engine.get_item("Apple")
print(f"{item['name']}: {item['quantity']} units")
```

#### `InventoryEngine.get_all_items() -> List[Dict[str, Any]]`

Get all items in inventory.

**Returns:**
- List of item dictionaries

**Example:**
```python
items = inventory_engine.get_all_items()
for item in items:
    print(f"{item['name']}: {item['quantity']}")
```

#### `InventoryEngine.search_items(query: str) -> List[Dict[str, Any]]`

Search for items by name.

**Parameters:**
- `query`: Search query string

**Returns:**
- List of matching item dictionaries

**Example:**
```python
results = inventory_engine.search_items("app")
# Returns items with "app" in name (e.g., "Apple", "Pineapple")
```

#### `InventoryEngine.generate_report(report_type: str) -> Dict[str, Any]`

Generate inventory report.

**Parameters:**
- `report_type`: Type of report ('summary', 'daily', 'weekly', 'monthly')

**Returns:**
```python
{
    'type': str,
    'generated_at': str,
    'total_items': int,
    'total_quantity': int,
    'total_value': float,
    'low_stock_items': List[Dict],
    'items': List[Dict],
    'recent_transactions': List[Dict]  # For time-based reports
}
```

**Example:**
```python
report = inventory_engine.generate_report('summary')
print(f"Total items: {report['total_items']}")
print(f"Total value: ${report['total_value']:.2f}")
```

---

### Database API

#### `Database.add_item(...) -> int`

Add item to database.

**Parameters:**
```python
name: str
category: str
quantity: int
unit_price: float
```

**Returns:**
- Item ID

**Raises:**
- `DatabaseError`: If item already exists or operation fails

#### `Database.update_item(item_id: int, ...) -> None`

Update item in database.

**Parameters:**
```python
item_id: int           # Required
quantity: int          # Optional
unit_price: float      # Optional
category: str          # Optional
```

#### `Database.delete_item(item_id: int) -> None`

Delete item from database.

**Parameters:**
- `item_id`: Item ID to delete

#### `Database.log_transaction(...) -> None`

Log a transaction.

**Parameters:**
```python
item_id: int
action: str           # 'add', 'remove', 'delete', 'update'
amount: int
```

---

### NLP Parser API

#### `NLPParser.parse(text: str) -> Dict[str, Any]`

Parse natural language command.

**Parameters:**
- `text`: Input text from speech or keyboard

**Returns:**
```python
{
    'success': bool,
    'text': str,
    'normalized_text': str,
    'intent': str,
    'entities': Dict[str, Any],
    'confidence': float,
    'error': Optional[str]
}
```

**Intents:**
- `add_item`
- `update_stock`
- `remove_item`
- `query`
- `report`

**Example:**
```python
result = nlp_parser.parse("add 10 apples at 1.50 each")

if result['success']:
    print(f"Intent: {result['intent']}")
    print(f"Entities: {result['entities']}")
    # Intent: add_item
    # Entities: {'item_name': 'apples', 'quantity': 10, 'price': 1.50}
```

---

## Future REST API (v2.0)

### Planned Endpoints

#### Items

```
GET    /api/v1/items              # List all items
GET    /api/v1/items/{id}         # Get item by ID
POST   /api/v1/items              # Create item
PUT    /api/v1/items/{id}         # Update item
DELETE /api/v1/items/{id}         # Delete item
GET    /api/v1/items/search?q=... # Search items
```

#### Inventory Operations

```
POST   /api/v1/inventory/add      # Add stock
POST   /api/v1/inventory/remove   # Remove stock
POST   /api/v1/inventory/transfer # Transfer between locations
```

#### Reports

```
GET    /api/v1/reports/summary    # Summary report
GET    /api/v1/reports/daily      # Daily report
GET    /api/v1/reports/weekly     # Weekly report
GET    /api/v1/reports/monthly    # Monthly report
```

#### Voice Commands

```
POST   /api/v1/voice/command      # Process voice command
POST   /api/v1/voice/text         # Process text command
```

#### Transactions

```
GET    /api/v1/transactions       # List transactions
GET    /api/v1/transactions/{id}  # Get transaction
```

### Example REST Requests

#### Add Item

```http
POST /api/v1/items
Content-Type: application/json

{
  "name": "Apple",
  "category": "Fruits",
  "quantity": 10,
  "unit_price": 1.50
}
```

**Response:**
```json
{
  "success": true,
  "item_id": 123,
  "message": "Item added successfully"
}
```

#### Get All Items

```http
GET /api/v1/items
```

**Response:**
```json
{
  "success": true,
  "items": [
    {
      "id": 1,
      "name": "Apple",
      "category": "Fruits",
      "quantity": 10,
      "unit_price": 1.50,
      "created_at": "2025-11-30T10:00:00Z",
      "last_updated": "2025-11-30T10:00:00Z"
    }
  ],
  "total": 1
}
```

#### Process Voice Command

```http
POST /api/v1/voice/command
Content-Type: application/json

{
  "command": "add 10 apples at 1.50 each"
}
```

**Response:**
```json
{
  "success": true,
  "intent": "add_item",
  "entities": {
    "item_name": "apples",
    "quantity": 10,
    "price": 1.50
  },
  "response": "Added 10 apples at $1.50 per unit to inventory.",
  "item_id": 123
}
```

---

## WebSocket API (v2.0)

### Real-time Updates

```javascript
// Connect
const ws = new WebSocket('ws://localhost:8000/ws');

// Subscribe to inventory updates
ws.send(JSON.stringify({
  action: 'subscribe',
  channel: 'inventory'
}));

// Receive updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Inventory updated:', data);
};
```

### Event Types

```json
{
  "event": "item_added",
  "data": {
    "item_id": 123,
    "name": "Apple",
    "quantity": 10
  },
  "timestamp": "2025-11-30T10:00:00Z"
}
```

```json
{
  "event": "stock_updated",
  "data": {
    "item_id": 123,
    "old_quantity": 10,
    "new_quantity": 15,
    "change": 5
  },
  "timestamp": "2025-11-30T10:01:00Z"
}
```

---

## Plugin API (v1.5)

### Plugin Interface

```python
from typing import Dict, Any

class Plugin:
    """Base plugin interface."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize plugin with configuration."""
        pass
    
    def initialize(self) -> bool:
        """Initialize plugin resources."""
        return True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin logic."""
        return {'success': True}
    
    def cleanup(self):
        """Cleanup plugin resources."""
        pass
```

### Example Plugin

```python
class BarcodeScanner(Plugin):
    """Barcode scanner plugin."""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Scan barcode and return item info."""
        barcode = self.scan_barcode()
        item = self.lookup_item(barcode)
        
        return {
            'success': True,
            'barcode': barcode,
            'item': item
        }
    
    def scan_barcode(self) -> str:
        """Scan barcode from scanner device."""
        # Implementation
        pass
    
    def lookup_item(self, barcode: str) -> Dict[str, Any]:
        """Lookup item by barcode."""
        # Implementation
        pass
```

---

## Error Codes

### HTTP Status Codes (Future)

- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid input
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., duplicate)
- `500 Internal Server Error`: Server error

### Application Error Codes

```python
ERROR_CODES = {
    1000: "Unknown error",
    1001: "Item not found",
    1002: "Insufficient stock",
    1003: "Invalid quantity",
    1004: "Invalid price",
    1005: "Duplicate item",
    2000: "Speech recognition failed",
    2001: "Intent not recognized",
    2002: "Entity extraction failed",
    3000: "Database error",
    3001: "Connection error",
}
```

---

## Rate Limiting (Future)

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1638316800
```

---

## Authentication (Future)

### API Key Authentication

```http
GET /api/v1/items
Authorization: Bearer YOUR_API_KEY
```

### JWT Authentication

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

## Versioning

API versioning strategy:
- URL versioning: `/api/v1/`, `/api/v2/`
- Header versioning: `Accept: application/vnd.vim.v1+json`

---

## SDK Examples (Future)

### Python SDK

```python
from vim_sdk import VoiceInventoryClient

client = VoiceInventoryClient(api_key="YOUR_API_KEY")

# Add item
item = client.items.create(
    name="Apple",
    quantity=10,
    unit_price=1.50
)

# Get all items
items = client.items.list()

# Process voice command
result = client.voice.process("add 10 bananas")
```

### JavaScript SDK

```javascript
const VIM = require('voice-inventory-sdk');

const client = new VIM.Client({ apiKey: 'YOUR_API_KEY' });

// Add item
const item = await client.items.create({
  name: 'Apple',
  quantity: 10,
  unitPrice: 1.50
});

// Get all items
const items = await client.items.list();
```

---

## Webhooks (Future)

Register webhooks for events:

```http
POST /api/v1/webhooks
Content-Type: application/json

{
  "url": "https://your-server.com/webhook",
  "events": ["item_added", "stock_low"],
  "secret": "your_webhook_secret"
}
```

Webhook payload:

```json
{
  "event": "stock_low",
  "data": {
    "item_id": 123,
    "item_name": "Apple",
    "current_quantity": 3,
    "threshold": 5
  },
  "timestamp": "2025-11-30T10:00:00Z",
  "signature": "sha256=..."
}
```

---

**Last Updated**: November 2025
**Version**: 1.0
