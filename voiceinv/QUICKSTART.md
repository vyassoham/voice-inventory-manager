# Quick Start Guide

Get up and running with Voice Inventory Manager in 5 minutes!

## Prerequisites

- **Python 3.8+** installed
- **Microphone** connected (for voice input)
- **Speakers** (optional, for voice output)
- **Internet connection** (for Google STT, optional for offline mode)

## Installation

### Step 1: Download/Clone

```bash
# If using Git
git clone <repository-url>
cd voice_inventory_manager

# Or download and extract ZIP file
```

### Step 2: Run Setup

```bash
python setup.py
```

This will:
- Install all dependencies
- Create necessary directories
- Initialize the database
- Download NLTK data
- Test your microphone

### Step 3: Verify Installation

```bash
python main.py --help
```

You should see the help message with available options.

## First Run

### CLI Mode (Default)

```bash
python main.py
```

You'll see:
```
============================================================
    Voice Inventory Manager v1.0
    Voice-Controlled Inventory Management System
============================================================

Calibrating for ambient noise. Please remain quiet for a moment.
Calibration complete. Ready to receive commands.

🎤 Listening...
```

### Try Your First Commands

**Voice Mode** (speak clearly):
```
"add 10 apples"
"how many apples"
"show all items"
```

**Text Mode** (type `mode` to switch):
```
add 5 bananas at 0.75 each
update apples by 5
generate summary report
```

## Common Commands

### Adding Items

```
Voice: "add 10 apples at 1.50 each"
Text:  add item apple quantity 10 price 1.50
```

### Checking Stock

```
Voice: "how many apples left?"
Text:  show apple
```

### Updating Stock

```
Voice: "increase apples by 5"
Text:  update apple quantity 5
```

### Removing Items

```
Voice: "delete pepsi"
Text:  remove item pepsi
```

### Reports

```
Voice: "give me daily report"
Text:  report summary
```

## GUI Mode

For a graphical interface:

```bash
python main.py --mode gui
```

Features:
- 🎤 Voice command button
- ⌨️ Text input field
- 📊 Real-time inventory table
- 📈 Statistics panel

## Configuration

Edit `config.yaml` to customize:

```yaml
# Change STT provider
stt:
  provider: "google"  # or "sphinx" for offline

# Adjust voice settings
response:
  voice_enabled: true
  voice_rate: 150

# Modify thresholds
nlp:
  fuzzy_threshold: 80
  confidence_threshold: 0.6
```

## Troubleshooting

### Microphone Not Working

1. Check microphone connection
2. Grant microphone permissions
3. Test with: `python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"`

### Voice Not Recognized

1. Speak clearly and slowly
2. Reduce background noise
3. Recalibrate: Restart application
4. Try text mode: Type `mode` to switch

### Dependencies Failed

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Database Issues

```bash
# Reset database
rm data/inventory.db
python setup.py
```

## Next Steps

1. **Read Documentation**:
   - `docs/COMMANDS.md` - Full command reference
   - `docs/ARCHITECTURE.md` - System design
   - `docs/API_SPEC.md` - API documentation

2. **Customize Configuration**:
   - Adjust voice settings
   - Configure database path
   - Set logging preferences

3. **Explore Features**:
   - Try different command formats
   - Generate reports
   - Check statistics

4. **Get Help**:
   - Type `help` in the application
   - Check GitHub issues
   - Read FAQ below

## FAQ

**Q: Can I use this without a microphone?**
A: Yes! Switch to text mode by typing `mode`.

**Q: Does it work offline?**
A: Yes, set `stt.provider: "sphinx"` in config.yaml for offline mode.

**Q: How do I backup my data?**
A: Database is automatically backed up to `data/backups/` on exit.

**Q: Can I import existing inventory?**
A: Currently manual entry only. CSV import coming in v1.1.

**Q: What languages are supported?**
A: Currently English only. Multi-language support planned for v1.1.

**Q: How accurate is voice recognition?**
A: 95%+ with Google STT in quiet environment. Lower with background noise.

## Tips & Tricks

### Voice Commands

- **Speak naturally**: "add 5 apples" works as well as "add item apple quantity 5"
- **Use numbers**: "five" and "5" both work
- **Be specific**: Include units when relevant ("5 kg of rice")

### Performance

- **Calibrate regularly**: Restart app if environment changes
- **Reduce noise**: Use in quiet environment for best results
- **Use text mode**: Faster for bulk operations

### Organization

- **Use categories**: Organize items by category
- **Consistent naming**: Use same names for items
- **Regular reports**: Check inventory status regularly

## Example Workflows

### Grocery Store

```bash
# Morning stock check
"show all items"
"generate daily report"

# Customer purchases
"remove 3 apples"
"remove 2 milk bottles"

# Restocking
"add 50 apples at 1.50 each"
"increase milk by 20"

# End of day
"generate summary report"
```

### Warehouse

```bash
# Receiving shipment
"add 1000 units of SKU-12345"
"add 500 units of SKU-67890"

# Picking orders
"remove 100 SKU-12345"
"remove 50 SKU-67890"

# Inventory check
"how many SKU-12345"
"show all items"
```

## Support

- **Documentation**: Check `docs/` folder
- **Issues**: Report bugs on GitHub
- **Questions**: Use GitHub Discussions
- **Email**: support@example.com (if available)

## What's Next?

- **Version 1.1**: Multi-language, better NLP, PDF reports
- **Version 1.5**: Barcode scanning, QR codes
- **Version 2.0**: Cloud sync, multi-user, web dashboard

See `docs/ROADMAP.md` for full roadmap.

---

**Congratulations!** You're now ready to use Voice Inventory Manager! 🎉

For detailed information, check the full documentation in the `docs/` folder.
