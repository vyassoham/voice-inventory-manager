"""
NLP Parser Module

Natural Language Processing for command parsing and intent extraction.

Handles:
- Intent detection (add, update, delete, query, report)
- Entity extraction (item name, quantity, price, category)
- Fuzzy matching for item names
- Number word conversion ("five" -> 5)
- Synonym handling
- Context memory
- Confidence scoring
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from utils.logger import get_logger
from utils.fuzzy_match import FuzzyMatcher
import nltk
from word2number import w2n


class NLPIntentError(Exception):
    """Exception for NLP intent errors."""
    pass


class NLPParser:
    """
    Natural Language Parser for voice commands.
    """

    def __init__(self, config: Dict[str, Any], inventory_engine):
        """
        Initialize NLP parser.

        Args:
            config: NLP configuration
            inventory_engine: Reference to inventory engine for item matching
        """
        self.config = config
        self.inventory_engine = inventory_engine
        self.logger = get_logger(__name__)

        # Configuration
        self.fuzzy_threshold = config.get('fuzzy_threshold', 80)
        self.enable_fuzzy = config.get('enable_fuzzy_matching', True)
        self.confidence_threshold = config.get('confidence_threshold', 0.6)

        # Fuzzy matcher
        self.fuzzy_matcher = FuzzyMatcher(threshold=self.fuzzy_threshold)

        # Context memory
        self.context_memory_size = config.get('context_memory_size', 5)
        self.context_history = []

        # Download required NLTK data
        self._setup_nltk()

        # Intent patterns
        self._setup_intent_patterns()

        # Filler words to remove
        self.filler_words = {'bro', 'please', 'can', 'you', 'could', 'would', 'like', 'to', 'the', 'a', 'an'}

        self.logger.info("NLP Parser initialized")

    def _setup_nltk(self):
        """Download required NLTK data."""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('stopwords', quiet=True)
        except Exception as e:
            self.logger.warning(f"Failed to download NLTK data: {e}")

    def _setup_intent_patterns(self):
        """Setup regex patterns for intent detection."""
        self.intent_patterns = {
            'add_item': [
                r'\b(add|insert|store|create|new)\b.*\b(item|product|stock)\b',
                r'\b(add|insert|store|put)\b',
            ],
            'update_stock': [
                r'\b(update|change|modify|increase|decrease|reduce)\b',
                r'\b(add|remove)\b.*\b(to|from)\b.*\b(stock|inventory)\b',
            ],
            'remove_item': [
                r'\b(delete|remove|drop|eliminate)\b',
            ],
            'query': [
                r'\b(how many|how much|what|show|display|find|search|get|check)\b',
                r'\b(left|remaining|available|in stock)\b',
            ],
            'report': [
                r'\b(report|summary|list|show all|display all)\b',
            ],
        }

        # Compile patterns
        self.compiled_patterns = {}
        for intent, patterns in self.intent_patterns.items():
            self.compiled_patterns[intent] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]

    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language command.

        Args:
            text: Input text from speech recognition

        Returns:
            Dictionary with intent, entities, and confidence
        """
        result = {
            'success': False,
            'text': text,
            'normalized_text': None,
            'intent': None,
            'entities': {},
            'confidence': 0.0,
            'error': None
        }

        try:
            # Normalize text
            normalized = self._normalize_text(text)
            result['normalized_text'] = normalized

            self.logger.debug(f"Normalized: '{normalized}'")

            # Detect intent
            intent, confidence = self._detect_intent(normalized)

            if intent is None:
                result['error'] = "Could not understand the command intent"
                return result

            result['intent'] = intent
            result['confidence'] = confidence

            # Extract entities based on intent
            entities = self._extract_entities(normalized, intent)
            result['entities'] = entities

            # Validate entities
            validation_result = self._validate_entities(intent, entities)

            if not validation_result['valid']:
                result['error'] = validation_result['error']
                return result

            # Add to context
            self._add_to_context(result)

            result['success'] = True

            self.logger.info(f"Parsed: intent={intent}, entities={entities}, confidence={confidence:.2f}")

            return result

        except Exception as e:
            self.logger.error(f"Error parsing command: {e}", exc_info=True)
            result['error'] = f"Parsing error: {str(e)}"
            return result

    def _normalize_text(self, text: str) -> str:
        """
        Normalize input text.

        Args:
            text: Raw input text

        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower().strip()

        # Remove filler words
        words = text.split()
        words = [w for w in words if w not in self.filler_words]
        text = ' '.join(words)

        # Convert number words to digits
        text = self._convert_number_words(text)

        return text

    def _convert_number_words(self, text: str) -> str:
        """
        Convert number words to digits.

        Args:
            text: Input text

        Returns:
            Text with numbers converted
        """
        words = text.split()
        converted = []

        for word in words:
            try:
                # Try to convert word to number
                number = w2n.word_to_num(word)
                converted.append(str(number))
            except ValueError:
                # Not a number word, keep as is
                converted.append(word)

        return ' '.join(converted)

    def _detect_intent(self, text: str) -> Tuple[Optional[str], float]:
        """
        Detect intent from normalized text.

        Args:
            text: Normalized text

        Returns:
            Tuple of (intent, confidence)
        """
        scores = {}

        # Check each intent pattern
        for intent, patterns in self.compiled_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern.search(text):
                    score += 1

            if score > 0:
                # Normalize score
                scores[intent] = score / len(patterns)

        if not scores:
            return None, 0.0

        # Get intent with highest score
        best_intent = max(scores, key=scores.get)
        confidence = scores[best_intent]

        # Check confidence threshold
        if confidence < self.confidence_threshold:
            return None, confidence

        return best_intent, confidence

    def _extract_entities(self, text: str, intent: str) -> Dict[str, Any]:
        """
        Extract entities from text based on intent.

        Args:
            text: Normalized text
            intent: Detected intent

        Returns:
            Dictionary of extracted entities
        """
        entities = {}

        if intent == 'add_item':
            entities = self._extract_add_item_entities(text)
        elif intent == 'update_stock':
            entities = self._extract_update_stock_entities(text)
        elif intent == 'remove_item':
            entities = self._extract_remove_item_entities(text)
        elif intent == 'query':
            entities = self._extract_query_entities(text)
        elif intent == 'report':
            entities = self._extract_report_entities(text)

        return entities

    def _extract_add_item_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities for add_item intent."""
        entities = {
            'item_name': None,
            'quantity': 1,
            'price': None,
            'category': None
        }

        # Extract quantity
        qty_match = re.search(r'\b(\d+)\s*(?:pcs|pieces|packets?|kg|liters?|units?)?\b', text)
        if qty_match:
            entities['quantity'] = int(qty_match.group(1))

        # Extract price
        price_match = re.search(r'\bprice\s+(\d+(?:\.\d+)?)\b', text)
        if price_match:
            entities['price'] = float(price_match.group(1))

        # Extract item name (everything between action word and quantity/price)
        # Remove action words
        cleaned = re.sub(r'\b(add|insert|store|item|product|stock)\b', '', text)
        cleaned = re.sub(r'\bquantity\s+\d+\b', '', cleaned)
        cleaned = re.sub(r'\bprice\s+\d+(?:\.\d+)?\b', '', cleaned)
        cleaned = re.sub(r'\b\d+\s*(?:pcs|pieces|packets?|kg|liters?|units?)\b', '', cleaned)

        # Clean up and extract name
        cleaned = cleaned.strip()
        if cleaned:
            # Take first meaningful word(s)
            words = cleaned.split()
            if words:
                entities['item_name'] = ' '.join(words[:3])  # Max 3 words for item name

        return entities

    def _extract_update_stock_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities for update_stock intent."""
        entities = {
            'item_name': None,
            'quantity_change': 0,
            'operation': 'add'  # add or subtract
        }

        # Detect operation
        if re.search(r'\b(increase|add)\b', text):
            entities['operation'] = 'add'
        elif re.search(r'\b(decrease|reduce|remove|subtract)\b', text):
            entities['operation'] = 'subtract'

        # Extract quantity
        qty_match = re.search(r'\b(\d+)\b', text)
        if qty_match:
            qty = int(qty_match.group(1))
            entities['quantity_change'] = qty if entities['operation'] == 'add' else -qty

        # Extract item name
        cleaned = re.sub(r'\b(update|increase|decrease|reduce|add|remove|by|to|from|stock|inventory)\b', '', text)
        cleaned = re.sub(r'\b\d+\b', '', cleaned)
        cleaned = cleaned.strip()

        if cleaned:
            words = cleaned.split()
            if words:
                entities['item_name'] = ' '.join(words[:3])

        return entities

    def _extract_remove_item_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities for remove_item intent."""
        entities = {
            'item_name': None,
            'quantity': None  # If specified, remove quantity; if None, remove item completely
        }

        # Extract quantity (optional)
        qty_match = re.search(r'\b(\d+)\b', text)
        if qty_match:
            entities['quantity'] = int(qty_match.group(1))

        # Extract item name
        cleaned = re.sub(r'\b(delete|remove|drop|eliminate|item|product)\b', '', text)
        cleaned = re.sub(r'\b\d+\b', '', cleaned)
        cleaned = cleaned.strip()

        if cleaned:
            words = cleaned.split()
            if words:
                entities['item_name'] = ' '.join(words[:3])

        return entities

    def _extract_query_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities for query intent."""
        entities = {
            'item_name': None,
            'query_type': 'single'  # single or all
        }

        # Check if querying all items
        if re.search(r'\b(all|everything|total)\b', text):
            entities['query_type'] = 'all'
            return entities

        # Extract item name
        cleaned = re.sub(r'\b(how|many|much|what|show|display|find|search|get|check|left|remaining|available|in|stock)\b', '', text)
        cleaned = cleaned.strip()

        if cleaned:
            words = cleaned.split()
            if words:
                entities['item_name'] = ' '.join(words[:3])

        return entities

    def _extract_report_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities for report intent."""
        entities = {
            'report_type': 'summary',  # summary, daily, weekly, monthly
            'format': 'text'  # text, voice
        }

        # Detect report type
        if re.search(r'\b(daily|today)\b', text):
            entities['report_type'] = 'daily'
        elif re.search(r'\b(weekly|week)\b', text):
            entities['report_type'] = 'weekly'
        elif re.search(r'\b(monthly|month)\b', text):
            entities['report_type'] = 'monthly'

        return entities

    def _validate_entities(self, intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted entities.

        Args:
            intent: Intent type
            entities: Extracted entities

        Returns:
            Validation result
        """
        result = {'valid': True, 'error': None}

        if intent == 'add_item':
            if not entities.get('item_name'):
                result['valid'] = False
                result['error'] = "Item name is required"
            elif entities.get('quantity', 0) <= 0:
                result['valid'] = False
                result['error'] = "Quantity must be positive"

        elif intent == 'update_stock':
            if not entities.get('item_name'):
                result['valid'] = False
                result['error'] = "Item name is required"
            elif entities.get('quantity_change') == 0:
                result['valid'] = False
                result['error'] = "Quantity change must be specified"

        elif intent == 'remove_item':
            if not entities.get('item_name'):
                result['valid'] = False
                result['error'] = "Item name is required"

        elif intent == 'query':
            if entities.get('query_type') == 'single' and not entities.get('item_name'):
                result['valid'] = False
                result['error'] = "Item name is required for single item query"

        return result

    def _add_to_context(self, parse_result: Dict[str, Any]):
        """Add parse result to context history."""
        self.context_history.append(parse_result)

        # Trim history
        if len(self.context_history) > self.context_memory_size:
            self.context_history.pop(0)

    def get_context(self) -> List[Dict[str, Any]]:
        """Get context history."""
        return self.context_history.copy()

    def clear_context(self):
        """Clear context history."""
        self.context_history.clear()
