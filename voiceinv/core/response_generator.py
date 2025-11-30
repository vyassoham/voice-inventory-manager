"""
Response Generator Module

Generates user-friendly responses in text and voice formats.

Handles:
- Success responses
- Error responses
- Report formatting
- Text-to-speech output
- CLI formatting
"""

from typing import Dict, Any, Optional
from utils.logger import get_logger
import pyttsx3


class ResponseGenerator:
    """
    Generates and outputs responses in multiple formats.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize response generator.

        Args:
            config: Response configuration
        """
        self.config = config
        self.logger = get_logger(__name__)

        # Configuration
        self.mode = config.get('mode', 'both')  # text, voice, both
        self.voice_enabled = config.get('voice_enabled', True)

        # TTS engine
        self.tts_engine = None
        if self.voice_enabled:
            self._initialize_tts()

        self.logger.info("Response Generator initialized")

    def _initialize_tts(self):
        """Initialize text-to-speech engine."""
        try:
            self.tts_engine = pyttsx3.init()

            # Configure TTS
            rate = self.config.get('voice_rate', 150)
            volume = self.config.get('voice_volume', 0.9)

            self.tts_engine.setProperty('rate', rate)
            self.tts_engine.setProperty('volume', volume)

            # Set voice gender if specified
            gender = self.config.get('voice_gender', 'female')
            voices = self.tts_engine.getProperty('voices')

            for voice in voices:
                if gender.lower() in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break

            self.logger.info("TTS engine initialized")

        except Exception as e:
            self.logger.warning(f"Failed to initialize TTS: {e}")
            self.voice_enabled = False

    def generate_success_response(self, intent: str, data: Dict[str, Any]) -> str:
        """
        Generate success response based on intent.

        Args:
            intent: Intent type
            data: Result data

        Returns:
            Response text
        """
        if intent == 'add_item':
            return self._generate_add_item_response(data)
        elif intent == 'update_stock':
            return self._generate_update_stock_response(data)
        elif intent == 'remove_item':
            return self._generate_remove_item_response(data)
        elif intent == 'query':
            return self._generate_query_response(data)
        elif intent == 'report':
            return self._generate_report_response(data)
        else:
            return "Operation completed successfully."

    def generate_error_response(self, error: str) -> str:
        """
        Generate user-friendly error response.

        Args:
            error: Error message

        Returns:
            User-friendly error text
        """
        # Map technical errors to user-friendly messages
        error_lower = error.lower()

        if 'not found' in error_lower:
            return f"I couldn't find that item. {error}"
        elif 'insufficient' in error_lower:
            return f"Not enough stock available. {error}"
        elif 'required' in error_lower:
            return f"Missing information. {error}"
        elif 'understand' in error_lower or 'intent' in error_lower:
            return "I didn't understand that command. Please try again with a clearer instruction."
        else:
            return f"An error occurred: {error}"

    def _generate_add_item_response(self, data: Dict[str, Any]) -> str:
        """Generate response for add_item."""
        item_name = data.get('item_name', 'item')
        quantity = data.get('quantity', 0)
        price = data.get('price')

        response = f"Added {quantity} {item_name}"

        if price:
            response += f" at ${price:.2f} per unit"

        response += " to inventory."

        return response

    def _generate_update_stock_response(self, data: Dict[str, Any]) -> str:
        """Generate response for update_stock."""
        item_name = data.get('item_name', 'item')
        quantity_change = data.get('quantity_change', 0)
        new_quantity = data.get('new_quantity', 0)

        if quantity_change > 0:
            action = "Added"
        else:
            action = "Removed"
            quantity_change = abs(quantity_change)

        return f"{action} {quantity_change} {item_name}. New stock: {new_quantity} units."

    def _generate_remove_item_response(self, data: Dict[str, Any]) -> str:
        """Generate response for remove_item."""
        item_name = data.get('item_name', 'item')

        if data.get('removed_completely'):
            return f"Removed {item_name} from inventory completely."
        else:
            quantity = data.get('quantity_removed', 0)
            new_quantity = data.get('new_quantity', 0)
            return f"Removed {quantity} {item_name}. Remaining: {new_quantity} units."

    def _generate_query_response(self, data: Dict[str, Any]) -> str:
        """Generate response for query."""
        query_type = data.get('query_type', 'single')

        if query_type == 'all':
            items = data.get('items', [])
            total = data.get('total_items', 0)

            if total == 0:
                return "Inventory is empty."

            response = f"You have {total} items in inventory:\n"
            for item in items[:10]:  # Limit to first 10 for voice
                response += f"- {item['name']}: {item['quantity']} units"
                if item['unit_price'] > 0:
                    response += f" at ${item['unit_price']:.2f} each"
                response += "\n"

            if total > 10:
                response += f"... and {total - 10} more items."

            return response
        else:
            item = data.get('item')

            if not item:
                return "Item not found."

            response = f"{item['name']}: {item['quantity']} units"

            if item['unit_price'] > 0:
                response += f" at ${item['unit_price']:.2f} per unit"
                total_value = item['quantity'] * item['unit_price']
                response += f". Total value: ${total_value:.2f}"

            return response

    def _generate_report_response(self, data: Dict[str, Any]) -> str:
        """Generate response for report."""
        report = data.get('report', {})
        report_type = data.get('report_type', 'summary')

        response = f"Inventory {report_type} report:\n"
        response += f"Total items: {report.get('total_items', 0)}\n"
        response += f"Total quantity: {report.get('total_quantity', 0)} units\n"
        response += f"Total value: ${report.get('total_value', 0):.2f}\n"

        low_stock = report.get('low_stock_items', [])
        if low_stock:
            response += f"\nLow stock alerts ({len(low_stock)} items):\n"
            for item in low_stock[:5]:
                response += f"- {item['name']}: {item['quantity']} units\n"

        return response

    def output_response(self, text: str, output_voice: bool = None):
        """
        Output response in configured format(s).

        Args:
            text: Response text
            output_voice: Override voice output setting
        """
        # Always output text
        print(text)

        # Output voice if enabled
        if output_voice is None:
            output_voice = self.voice_enabled and self.mode in ['voice', 'both']

        if output_voice and self.tts_engine:
            self._speak(text)

    def generate_and_output(self, text: str, output_voice: bool = None):
        """
        Generate and output a simple text response.

        Args:
            text: Response text
            output_voice: Override voice output setting
        """
        self.output_response(text, output_voice)

    def _speak(self, text: str):
        """
        Speak text using TTS engine.

        Args:
            text: Text to speak
        """
        try:
            if self.tts_engine:
                # Clean text for speech (remove special characters)
                clean_text = text.replace('\n', '. ')
                self.tts_engine.say(clean_text)
                self.tts_engine.runAndWait()
        except Exception as e:
            self.logger.error(f"TTS error: {e}")

    def cleanup(self):
        """Cleanup TTS resources."""
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
