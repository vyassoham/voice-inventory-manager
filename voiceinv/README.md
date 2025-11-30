# Voice Inventory Manager

A complete voice-controlled inventory management system with natural language processing, speech recognition, and persistent database storage.

## 🎯 Features

- **Voice-Controlled Operations**: Add, update, remove, and query inventory items using natural speech
- **Natural Language Understanding**: Supports both structured and conversational commands
- **Persistent Storage**: SQLite database with transaction logging
- **Dual Interface**: CLI and optional GUI (Tkinter) modes
- **Robust Error Handling**: Comprehensive error recovery and user feedback
- **Offline Support**: Works without internet connection
- **Fuzzy Matching**: Handles typos and variations in item names
- **Speech Synthesis**: Optional voice responses using pyttsx3
- **Comprehensive Logging**: Detailed logs for debugging and auditing
- **Extensible Architecture**: Plugin system for future enhancements

## 📋 Requirements

- Python 3.8+
- Microphone for voice input
- Speakers for voice output (optional)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
cd voice_inventory_manager

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### First Run

On first run, the system will:
1. Calibrate for ambient noise
2. Initialize the database
3. Create default configuration

## 🎤 Usage

### Voice Commands

**Structured Format:**
```
add item apple quantity 5 price 100
update item sugar quantity -2
delete item pepsi
search item tomato
report daily
```

**Conversational Format:**
```
"bro add 10 kurkure packets"
"increase rice by 3 kg"
"remove five maaza bottles"
"how many onions left?"
```

### CLI Mode

```bash
python main.py --mode cli
```

### GUI Mode

```bash
python main.py --mode gui
```

## 📁 Project Structure

```
voice_inventory_manager/
│
├── main.py                 # Entry point
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
│
├── core/                  # Core business logic
│   ├── voice_engine.py
│   ├── stt_pipeline.py
│   ├── nlp_parser.py
│   ├── intent_router.py
│   ├── inventory_engine.py
│   └── response_generator.py
│
├── db/                    # Database layer
│   ├── database.py
│   └── migrations.sql
│
├── utils/                 # Utility modules
│   ├── logger.py
│   ├── fuzzy_match.py
│   └── validators.py
│
├── ui/                    # User interfaces
│   ├── cli.py
│   └── gui.py
│
├── tests/                 # Test suite
│   ├── test_voice.py
│   ├── test_nlp.py
│   ├── test_inventory.py
│   ├── test_db.py
│   └── test_end_to_end.py
│
└── docs/                  # Documentation
    ├── ARCHITECTURE.md
    ├── COMMANDS.md
    ├── API_SPEC.md
    └── ROADMAP.md
```

## 🔧 Configuration

Edit `config.yaml` to customize:
- STT provider (Google, Sphinx, Whisper)
- Microphone settings
- Noise threshold
- Database path
- Logging preferences
- Voice output settings

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test suite
python -m pytest tests/test_nlp.py

# Run with coverage
python -m pytest --cov=core tests/
```

## 📖 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Command Reference](docs/COMMANDS.md)
- [API Specification](docs/API_SPEC.md)
- [Future Roadmap](docs/ROADMAP.md)

## 🔒 Security

- Optional voice profile authentication
- Password-protected admin mode
- Command confirmation for destructive operations
- Transaction logging for audit trails

## 🤝 Contributing

Contributions are welcome! Please read the contributing guidelines before submitting PRs.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- SpeechRecognition library
- SQLite database
- Python community

## 📞 Support

For issues and questions, please open a GitHub issue or contact the maintainers.
