# Command Reference

Complete reference for all voice and text commands supported by the Voice Inventory Manager.

## Command Formats

The system supports two command formats:

1. **Structured Format**: Explicit keywords and parameters
2. **Conversational Format**: Natural language

Both formats are processed identically by the NLP parser.

---

## Add Item Commands

### Intent: `add_item`

Add a new item to inventory or increase quantity of existing item.

### Structured Format

```
add item <name> quantity <number> price <amount>
add item <name> quantity <number>
add <number> <name> price <amount>
```

### Conversational Format

```
"add 10 apples"
"bro add 5 packets of kurkure"
"store 20 bottles of pepsi at 50 rupees each"
"insert 3 kg of sugar"
```

### Examples

| Command | Result |
|---------|--------|
| `add item apple quantity 10 price 1.50` | Add 10 apples at $1.50 each |
| `add 5 bananas` | Add 5 bananas (price defaults to 0) |
| `bro add 20 maggi packets` | Add 20 Maggi packets |
| `store 3 milk bottles at 3.50 each` | Add 3 milk bottles at $3.50 each |

### Parameters

- **name** (required): Item name (max 100 characters)
- **quantity** (optional): Number of units (default: 1)
- **price** (optional): Price per unit (default: 0.00)
- **category** (optional): Item category (default: "General")

### Notes

- If item already exists, quantity is added to existing stock
- Price is updated if specified
- Supports plural forms ("apples" vs "apple")
- Filler words are ignored ("bro", "please", etc.)

---

## Update Stock Commands

### Intent: `update_stock`

Increase or decrease stock quantity for an existing item.

### Structured Format

```
update item <name> quantity <change>
increase <name> by <number>
decrease <name> by <number>
```

### Conversational Format

```
"increase rice by 5 kg"
"add 10 more apples to stock"
"reduce sugar by 2 kg"
"remove 3 pepsi from inventory"
```

### Examples

| Command | Result |
|---------|--------|
| `increase apple by 5` | Add 5 to apple stock |
| `decrease sugar by 2` | Remove 2 from sugar stock |
| `add 10 more bananas` | Add 10 to banana stock |
| `reduce milk by 3` | Remove 3 from milk stock |

### Parameters

- **name** (required): Item name
- **change** (required): Quantity change (positive or negative)

### Notes

- Cannot reduce stock below zero
- System will alert if operation would result in negative stock
- Fuzzy matching helps find items even with typos

---

## Remove Item Commands

### Intent: `remove_item`

Remove an item completely from inventory or remove specific quantity.

### Structured Format

```
delete item <name>
remove <number> <name>
drop <name>
```

### Conversational Format

```
"delete pepsi"
"remove 5 apples"
"drop maggi from inventory"
"eliminate sugar"
```

### Examples

| Command | Result |
|---------|--------|
| `delete apple` | Remove apple completely |
| `remove 5 bananas` | Remove 5 bananas (item remains if stock > 5) |
| `drop pepsi` | Remove pepsi completely |

### Parameters

- **name** (required): Item name
- **quantity** (optional): If specified, removes only that quantity

### Notes

- Without quantity: Removes item completely
- With quantity: Reduces stock by that amount
- Confirmation required for bulk deletions (configurable)

---

## Query Commands

### Intent: `query`

Search for and display item information.

### Structured Format

```
search item <name>
show <name>
get <name>
```

### Conversational Format

```
"how many apples left?"
"how much sugar do we have?"
"show me all bananas"
"what's the stock of milk?"
"check apple inventory"
```

### Examples

| Command | Result |
|---------|--------|
| `how many apples` | Show apple quantity and details |
| `show all items` | Display all inventory items |
| `what's left in stock` | Show all items |
| `search tomato` | Find and display tomato details |

### Parameters

- **name** (optional): Item name for single item query
- If no name specified, shows all items

### Response Format

**Single Item**:
```
Apple: 50 units at $1.50 per unit. Total value: $75.00
```

**All Items**:
```
You have 5 items in inventory:
- Apple: 50 units at $1.50 each
- Banana: 100 units at $0.75 each
- Milk: 20 units at $3.50 each
...
```

---

## Report Commands

### Intent: `report`

Generate inventory reports.

### Structured Format

```
report <type>
generate <type> report
show summary
```

### Conversational Format

```
"give me daily report"
"show inventory summary"
"generate weekly report"
"what's the monthly summary"
```

### Examples

| Command | Result |
|---------|--------|
| `report summary` | Generate summary report |
| `daily report` | Generate daily transaction report |
| `weekly report` | Generate weekly report |
| `monthly report` | Generate monthly report |

### Report Types

1. **Summary**: Overall inventory statistics
2. **Daily**: Today's transactions and changes
3. **Weekly**: Last 7 days activity
4. **Monthly**: Last 30 days activity

### Report Contents

- Total items count
- Total quantity across all items
- Total inventory value
- Low stock alerts
- Recent transactions (for time-based reports)

---

## System Commands

These commands control the application itself.

### Help

```
help
show help
what can you do
```

Shows available commands and usage instructions.

### Mode Toggle (CLI only)

```
mode
toggle mode
switch mode
```

Toggles between voice and text input modes.

### Statistics

```
stats
statistics
show stats
```

Displays system statistics:
- Commands processed
- Error count
- Inventory summary
- STT provider info

### Exit

```
exit
quit
goodbye
bye
stop
```

Exits the application (with confirmation).

---

## Number Formats

The system understands multiple number formats:

### Digits
```
"add 5 apples"
"increase by 10"
```

### Words
```
"add five apples"
"increase by ten"
```

### Mixed
```
"add 5 apples and three bananas"
```

### Supported Number Words

- one, two, three, four, five
- six, seven, eight, nine, ten
- eleven through nineteen
- twenty, thirty, forty, etc.
- hundred, thousand

---

## Units

The system recognizes common units:

- **Pieces**: pcs, pieces, units
- **Weight**: kg, grams, pounds, oz
- **Volume**: liters, ml, gallons
- **Packets**: packets, packs, boxes

### Examples

```
"add 5 kg of rice"
"add 10 liters of milk"
"add 20 packets of chips"
```

---

## Fuzzy Matching

The system uses fuzzy matching to handle:

### Typos
```
"add aple" → matches "apple"
"show bannana" → matches "banana"
```

### Variations
```
"add apples" → matches "apple"
"show pepsis" → matches "pepsi"
```

### Partial Matches
```
"show tom" → matches "tomato"
```

### Threshold

- Default: 80% similarity required
- Configurable in `config.yaml`

---

## Context and Memory

The system remembers recent commands for context:

```
User: "add 10 apples"
System: "Added 10 apples"

User: "make that 15"
System: (understands "that" refers to apples)
```

- Memory size: 5 commands (configurable)
- Helps resolve ambiguous references

---

## Error Messages

### Item Not Found
```
Input: "show xyz"
Output: "I couldn't find that item. Item 'xyz' not found"
```

### Insufficient Stock
```
Input: "remove 100 apples" (only 10 available)
Output: "Not enough stock available. Available: 10, Requested: 100"
```

### Missing Information
```
Input: "add item"
Output: "Missing information. Item name is required"
```

### Unclear Command
```
Input: "xyz abc def"
Output: "I didn't understand that command. Please try again with a clearer instruction."
```

---

## Best Practices

### For Voice Commands

1. **Speak Clearly**: Enunciate words clearly
2. **Avoid Background Noise**: Use in quiet environment
3. **Use Natural Language**: Don't need to be overly formal
4. **Be Specific**: Include necessary details (name, quantity)
5. **Wait for Prompt**: Ensure system is listening

### For Text Commands

1. **Use Simple Language**: Keep commands concise
2. **Include Units**: Specify quantities clearly
3. **Check Spelling**: Though fuzzy matching helps
4. **Use Consistent Names**: Stick to same item names

### General Tips

1. **Start Simple**: Use basic commands first
2. **Check Results**: Verify operations completed
3. **Use Help**: Reference help when unsure
4. **Review Reports**: Regularly check inventory status

---

## Advanced Usage

### Batch Operations (Future)

```
"add 5 apples, 10 bananas, and 3 oranges"
```

### Conditional Operations (Future)

```
"if apples less than 10, add 20 more"
```

### Scheduled Operations (Future)

```
"add 10 milk bottles every Monday"
```

---

## Troubleshooting

### Command Not Recognized

**Problem**: System doesn't understand command

**Solutions**:
1. Rephrase using simpler language
2. Use structured format
3. Check for typos
4. Speak more clearly (voice mode)

### Wrong Item Matched

**Problem**: System matches wrong item

**Solutions**:
1. Use full item name
2. Be more specific
3. Check existing item names
4. Adjust fuzzy threshold in config

### Voice Not Detected

**Problem**: System doesn't hear voice

**Solutions**:
1. Check microphone connection
2. Increase volume
3. Reduce background noise
4. Recalibrate noise threshold
5. Check microphone permissions

---

## Configuration

Customize command behavior in `config.yaml`:

```yaml
nlp:
  fuzzy_threshold: 80  # Adjust matching sensitivity
  confidence_threshold: 0.6  # Minimum confidence for intent
  context_memory_size: 5  # Number of commands to remember

stt:
  timeout: 5  # Seconds to wait for speech
  phrase_time_limit: 10  # Max seconds for phrase
```

---

## Examples by Use Case

### Grocery Store

```
"add 50 apples at 1.50 each"
"add 100 bananas at 0.75 each"
"customer bought 5 apples"  → "remove 5 apples"
"how many bananas left?"
"daily report"
```

### Warehouse

```
"add 1000 units of SKU-12345"
"increase SKU-12345 by 500"
"show all items in electronics category"
"generate monthly report"
```

### Restaurant

```
"add 10 kg of rice"
"add 5 liters of oil"
"used 2 kg rice"  → "decrease rice by 2"
"how much oil left?"
```

### Pharmacy

```
"add 100 tablets of medicine-A"
"sold 10 medicine-A"  → "remove 10 medicine-A"
"show all medicines"
"low stock report"
```
