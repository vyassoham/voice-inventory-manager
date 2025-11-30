"""
Voice Engine Module

Orchestrates the complete voice processing pipeline from audio input
to command execution and response generation.

This module handles:
- Voice activation and listening
- Command segmentation
- Retry mechanisms
- Error recovery
- Confidence scoring
"""

import time
from typing import Optional, Dict, Any, Callable
from utils.logger import get_logger
from core.stt_pipeline import STTPipeline
from core.nlp_parser import NLPParser
from core.intent_router import IntentRouter
from core.response_generator import ResponseGenerator


class VoiceEngineError(Exception):
    """Base exception for voice engine errors."""
    pass


class VoiceEngine:
    """
    Main voice processing engine that coordinates all voice-related operations.
    """

    def __init__(
        self,
        stt_pipeline: STTPipeline,
        nlp_parser: NLPParser,
        intent_router: IntentRouter,
        response_generator: ResponseGenerator,
        config: Dict[str, Any]
    ):
        """
        Initialize the voice engine.

        Args:
            stt_pipeline: Speech-to-text pipeline
            nlp_parser: Natural language parser
            intent_router: Intent routing system
            response_generator: Response generation system
            config: Configuration dictionary
        """
        self.stt_pipeline = stt_pipeline
        self.nlp_parser = nlp_parser
        self.intent_router = intent_router
        self.response_generator = response_generator
        self.config = config
        self.logger = get_logger(__name__)

        # State
        self.is_listening = False
        self.is_active = True
        self.command_count = 0
        self.error_count = 0

        # Hotword settings
        self.hotword_enabled = config.get('hotword', {}).get('enabled', False)
        self.hotword_keyword = config.get('hotword', {}).get('keyword', 'inventory')

        # Callbacks
        self.on_command_received: Optional[Callable] = None
        self.on_command_processed: Optional[Callable] = None
        self.on_error: Optional[Callable] = None

    def calibrate_noise(self) -> bool:
        """
        Calibrate for ambient noise.

        Returns:
            True if calibration successful, False otherwise
        """
        try:
            self.logger.info("Calibrating for ambient noise...")
            self.response_generator.generate_and_output(
                "Calibrating for ambient noise. Please remain quiet for a moment.",
                output_voice=True
            )

            success = self.stt_pipeline.calibrate_for_ambient_noise(duration=2)

            if success:
                self.logger.info("Noise calibration complete")
                self.response_generator.generate_and_output(
                    "Calibration complete. Ready to receive commands.",
                    output_voice=True
                )
            else:
                self.logger.warning("Noise calibration failed")

            return success

        except Exception as e:
            self.logger.error(f"Error during noise calibration: {e}")
            return False

    def listen_for_command(self, timeout: Optional[int] = None) -> Optional[str]:
        """
        Listen for a single voice command.

        Args:
            timeout: Maximum time to wait for command (seconds)

        Returns:
            Recognized text or None if failed
        """
        try:
            self.is_listening = True

            if self.hotword_enabled:
                self.logger.debug("Waiting for hotword...")
                # In a real implementation, you'd use a hotword detection library
                # For now, we'll just listen directly

            self.logger.info("Listening for command...")

            # Get audio from STT pipeline
            text = self.stt_pipeline.listen_and_recognize(timeout=timeout)

            if text:
                self.logger.info(f"Recognized: '{text}'")
                self.command_count += 1

                # Trigger callback
                if self.on_command_received:
                    self.on_command_received(text)

            return text

        except Exception as e:
            self.logger.error(f"Error listening for command: {e}")
            self.error_count += 1

            if self.on_error:
                self.on_error(e)

            return None

        finally:
            self.is_listening = False

    def process_command(self, text: str) -> Dict[str, Any]:
        """
        Process a voice command through the complete pipeline.

        Args:
            text: Recognized text from speech

        Returns:
            Result dictionary with status and response
        """
        result = {
            'success': False,
            'text': text,
            'intent': None,
            'response': None,
            'error': None
        }

        try:
            # Parse command with NLP
            self.logger.debug(f"Parsing command: '{text}'")
            parse_result = self.nlp_parser.parse(text)

            if not parse_result['success']:
                result['error'] = parse_result.get('error', 'Failed to understand command')
                result['response'] = self.response_generator.generate_error_response(
                    result['error']
                )
                return result

            result['intent'] = parse_result['intent']

            # Route to appropriate handler
            self.logger.debug(f"Routing intent: {parse_result['intent']}")
            execution_result = self.intent_router.route(parse_result)

            if execution_result['success']:
                result['success'] = True
                result['response'] = self.response_generator.generate_success_response(
                    parse_result['intent'],
                    execution_result.get('data', {})
                )
            else:
                result['error'] = execution_result.get('error', 'Command execution failed')
                result['response'] = self.response_generator.generate_error_response(
                    result['error']
                )

            # Trigger callback
            if self.on_command_processed:
                self.on_command_processed(result)

            return result

        except Exception as e:
            self.logger.error(f"Error processing command: {e}", exc_info=True)
            result['error'] = str(e)
            result['response'] = self.response_generator.generate_error_response(
                "An unexpected error occurred while processing your command."
            )

            if self.on_error:
                self.on_error(e)

            return result

    def process_text_command(self, text: str) -> Dict[str, Any]:
        """
        Process a text command (for CLI/GUI input).

        Args:
            text: Command text

        Returns:
            Result dictionary
        """
        return self.process_command(text)

    def listen_and_process(self, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Listen for a command and process it in one operation.

        Args:
            timeout: Maximum time to wait for command

        Returns:
            Processing result or None if no command received
        """
        text = self.listen_for_command(timeout=timeout)

        if text:
            result = self.process_command(text)

            # Output response
            if result['response']:
                self.response_generator.output_response(result['response'])

            return result

        return None

    def run_continuous(self, on_exit_command: Optional[Callable] = None):
        """
        Run in continuous listening mode.

        Args:
            on_exit_command: Callback to check if should exit
        """
        self.logger.info("Starting continuous listening mode")

        # Initial calibration
        self.calibrate_noise()

        exit_commands = ['exit', 'quit', 'stop', 'goodbye', 'bye']

        while self.is_active:
            try:
                # Listen for command
                text = self.listen_for_command()

                if not text:
                    continue

                # Check for exit command
                if text.lower().strip() in exit_commands:
                    self.logger.info("Exit command received")
                    self.response_generator.generate_and_output(
                        "Goodbye! Shutting down.",
                        output_voice=True
                    )
                    break

                # Custom exit check
                if on_exit_command and on_exit_command(text):
                    break

                # Process command
                result = self.process_command(text)

                # Output response
                if result['response']:
                    self.response_generator.output_response(result['response'])

                # Small delay between commands
                time.sleep(0.5)

            except KeyboardInterrupt:
                self.logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                self.logger.error(f"Error in continuous mode: {e}")
                self.response_generator.generate_and_output(
                    "An error occurred. Please try again.",
                    output_voice=True
                )

        self.logger.info("Continuous listening mode stopped")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get engine statistics.

        Returns:
            Statistics dictionary
        """
        return {
            'command_count': self.command_count,
            'error_count': self.error_count,
            'is_listening': self.is_listening,
            'is_active': self.is_active,
            'stt_stats': self.stt_pipeline.get_statistics()
        }

    def shutdown(self):
        """Shutdown the voice engine."""
        self.logger.info("Shutting down voice engine")
        self.is_active = False
        self.is_listening = False

        # Cleanup STT pipeline
        if self.stt_pipeline:
            self.stt_pipeline.cleanup()

        # Cleanup response generator
        if self.response_generator:
            self.response_generator.cleanup()
