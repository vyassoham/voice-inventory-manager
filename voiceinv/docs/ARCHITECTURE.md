# Architecture Overview

## System Architecture

The Voice Inventory Manager follows a modular, layered architecture designed for maintainability, testability, and extensibility.

```
┌─────────────────────────────────────────────────────────┐
│                    User Interfaces                       │
│              (CLI / GUI / Voice Input)                   │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│                  Voice Engine                            │
│         (Orchestrates entire pipeline)                   │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐    ┌────────▼────────┐
│  STT Pipeline  │    │   NLP Parser    │
│  (Speech→Text) │    │ (Intent/Entity) │
└───────┬────────┘    └────────┬────────┘
        │                      │
        └──────────┬───────────┘
                   │
        ┌──────────▼──────────┐
        │   Intent Router     │
        │  (Route to handler) │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │  Inventory Engine   │
        │  (Business Logic)   │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │   Database Layer    │
        │    (SQLite DB)      │
        └─────────────────────┘
```

## Core Components

### 1. Voice Engine (`core/voice_engine.py`)

**Responsibility**: Orchestrates the complete voice processing pipeline

**Key Features**:
- Voice activation and listening
- Command segmentation
- Retry mechanisms
- Error recovery
- Confidence scoring
- Statistics tracking

**Interfaces**:
- `listen_for_command()`: Capture voice input
- `process_command()`: Process complete pipeline
- `run_continuous()`: Continuous listening mode

### 2. STT Pipeline (`core/stt_pipeline.py`)

**Responsibility**: Speech-to-text conversion

**Key Features**:
- Multiple provider support (Google, Sphinx, Whisper)
- Ambient noise calibration
- Timeout handling
- Retry logic
- Audio preprocessing

**Providers**:
- **Google**: Cloud-based, high accuracy (requires internet)
- **Sphinx**: Offline, lower accuracy
- **Whisper**: Advanced AI model (optional)

### 3. NLP Parser (`core/nlp_parser.py`)

**Responsibility**: Natural language understanding

**Key Features**:
- Intent detection using regex patterns
- Entity extraction (item name, quantity, price)
- Fuzzy matching for variations
- Number word conversion ("five" → 5)
- Context memory
- Confidence scoring

**Supported Intents**:
- `add_item`: Add new inventory item
- `update_stock`: Modify stock quantity
- `remove_item`: Delete item
- `query`: Search/retrieve items
- `report`: Generate reports

### 4. Intent Router (`core/intent_router.py`)

**Responsibility**: Route intents to appropriate handlers

**Key Features**:
- Intent-to-handler mapping
- Security checks
- Confirmation for destructive operations
- Error handling

### 5. Inventory Engine (`core/inventory_engine.py`)

**Responsibility**: Core business logic

**Key Features**:
- Item CRUD operations
- Stock validation
- Transaction logging
- Fuzzy item matching
- Report generation
- Low stock alerts

**Business Rules**:
- Prevent negative stock
- Alert on low stock
- Validate data integrity
- Log all transactions

### 6. Database Layer (`db/database.py`)

**Responsibility**: Data persistence

**Technology**: SQLite

**Schema**:

```sql
items:
  - id (PK)
  - name (UNIQUE)
  - category
  - quantity
  - unit_price
  - created_at
  - last_updated

transactions:
  - id (PK)
  - item_id (FK)
  - action
  - amount
  - timestamp
```

**Features**:
- ACID compliance
- Automatic backups
- Transaction logging
- Full-text search
- Indexes for performance

### 7. Response Generator (`core/response_generator.py`)

**Responsibility**: Generate user-friendly responses

**Key Features**:
- Text response generation
- Text-to-speech output (pyttsx3)
- Intent-specific formatting
- Error message translation
- Multi-format support

## Data Flow

### Add Item Flow

```
User: "Add 10 apples at $2 each"
  ↓
STT Pipeline: "add 10 apples at 2 each"
  ↓
NLP Parser:
  Intent: add_item
  Entities: {name: "apples", quantity: 10, price: 2.0}
  ↓
Intent Router: Route to add_item handler
  ↓
Inventory Engine:
  - Validate data
  - Check if item exists
  - Add/update item
  - Log transaction
  ↓
Database: INSERT/UPDATE
  ↓
Response Generator: "Added 10 apples at $2.00 per unit to inventory."
  ↓
User: Text + Voice output
```

## Error Handling Strategy

### Error Hierarchy

```
Exception
├── VoiceEngineError
├── STTError
├── NLPIntentError
├── InventoryError
│   ├── ItemNotFoundError
│   └── InsufficientStockError
├── DatabaseError
└── ValidationError
```

### Error Recovery

1. **STT Errors**: Retry with adjustable attempts
2. **NLP Errors**: Provide suggestions, ask for clarification
3. **Inventory Errors**: Explain issue, suggest correction
4. **Database Errors**: Log, backup, graceful degradation

## Logging Architecture

### Log Channels

1. **Main Log**: All system events
2. **Voice Commands Log**: All recognized commands
3. **NLP Parsing Log**: Intent detection details
4. **Database Operations Log**: All DB transactions

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (e.g., low stock)
- **ERROR**: Error events
- **CRITICAL**: Critical failures

### Log Rotation

- Maximum file size: 10 MB
- Backup count: 5 files
- Format: Timestamp, level, logger, message

## Configuration System

### Configuration File: `config.yaml`

Organized into sections:
- `stt`: Speech recognition settings
- `microphone`: Audio input settings
- `nlp`: NLP parser settings
- `inventory`: Business rules
- `database`: Database settings
- `response`: Output settings
- `logging`: Logging configuration
- `security`: Security settings

### Configuration Loading

1. Load YAML file
2. Validate structure
3. Apply defaults for missing values
4. Pass to components

## Security Considerations

### Current Implementation

1. **Input Validation**: All user input sanitized
2. **SQL Injection Prevention**: Parameterized queries
3. **Transaction Logging**: Audit trail
4. **Confirmation**: Destructive operations require confirmation

### Future Enhancements

1. **Voice Biometrics**: Speaker verification
2. **Encryption**: Database encryption at rest
3. **Authentication**: Multi-user support with passwords
4. **Authorization**: Role-based access control

## Performance Considerations

### Optimization Strategies

1. **Database Indexing**: Indexes on frequently queried fields
2. **Connection Pooling**: Reuse database connections
3. **Caching**: Cache frequently accessed items
4. **Async Operations**: Non-blocking voice processing

### Scalability

Current design supports:
- **Items**: Up to 100,000 items
- **Transactions**: Unlimited (with rotation)
- **Concurrent Users**: Single user (can be extended)

## Testing Strategy

### Test Levels

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing
3. **End-to-End Tests**: Complete workflow testing
4. **Performance Tests**: Load and stress testing

### Test Coverage Goals

- Core modules: 90%+
- Utilities: 80%+
- UI: 60%+

## Deployment Architecture

### Standalone Application

```
User's Computer
├── Python Runtime
├── Application Code
├── SQLite Database
├── Configuration Files
└── Log Files
```

### Future: Client-Server Architecture

```
Client (Voice Interface)
    ↓ HTTP/WebSocket
Server (Business Logic + DB)
    ↓
Cloud Storage (Backups)
```

## Extension Points

### Plugin System

Location: `plugins/` directory

**Supported Plugin Types**:
1. **STT Providers**: Custom speech recognition
2. **NLP Enhancers**: Additional intent detection
3. **Storage Backends**: Alternative databases
4. **Export Formats**: Custom report formats
5. **Integrations**: External systems (barcode, QR, etc.)

### Plugin Interface

```python
class Plugin:
    def initialize(self, config): pass
    def execute(self, context): pass
    def cleanup(self): pass
```

## Monitoring and Observability

### Metrics Collected

1. **Voice Engine**: Command count, error rate, avg processing time
2. **STT Pipeline**: Recognition count, accuracy, latency
3. **Inventory**: Total items, stock levels, transaction rate
4. **Database**: Query count, response time

### Health Checks

- Database connectivity
- Microphone availability
- STT service availability
- Disk space for logs/backups

## Disaster Recovery

### Backup Strategy

1. **Automatic Backups**: On application shutdown
2. **Manual Backups**: Via CLI command
3. **Backup Location**: `data/backups/`
4. **Retention**: Keep last 10 backups

### Recovery Procedure

1. Stop application
2. Restore from backup file
3. Verify database integrity
4. Restart application

## Future Architecture Evolution

### Planned Enhancements

1. **Microservices**: Split into independent services
2. **Cloud Deployment**: AWS/Azure/GCP hosting
3. **Mobile App**: iOS/Android clients
4. **Web Dashboard**: Browser-based interface
5. **Multi-tenancy**: Support multiple organizations
6. **Real-time Sync**: Cross-device synchronization
7. **ML Integration**: Demand forecasting, anomaly detection
