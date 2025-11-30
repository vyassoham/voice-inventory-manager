"""
Voice Inventory Manager - Main Entry Point

This is the main entry point for the Voice Inventory Manager application.
It initializes all components, handles command-line arguments, and starts
the appropriate user interface (CLI or GUI).

Author: AI Generated
License: MIT
"""

import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.voice_engine import VoiceEngine
from core.stt_pipeline import STTPipeline
from core.nlp_parser import NLPParser
from core.intent_router import IntentRouter
from core.inventory_engine import InventoryEngine
from core.response_generator import ResponseGenerator
from db.database import Database
from utils.logger import setup_logger, get_logger
from utils.validators import ConfigValidator
from ui.cli import CLIInterface
from ui.gui import GUIInterface

import yaml


class VoiceInventoryManager:
    """Main application class that orchestrates all components."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the Voice Inventory Manager.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = None
        self.logger = None
        self.components_initialized = False

        # Core components
        self.database = None
        self.voice_engine = None
        self.stt_pipeline = None
        self.nlp_parser = None
        self.intent_router = None
        self.inventory_engine = None
        self.response_generator = None

    def load_config(self) -> dict:
        """
        Load and validate configuration from YAML file.

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid
        """
        config_file = Path(self.config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        # Validate configuration
        validator = ConfigValidator()
        validator.validate(config)

        return config

    def initialize_logging(self):
        """Initialize logging system based on configuration."""
        log_config = self.config.get('logging', {})
        setup_logger(
            level=log_config.get('level', 'INFO'),
            log_to_file=log_config.get('log_to_file', True),
            log_file_path=log_config.get('log_file_path', 'logs/voice_inventory.log'),
            max_bytes=log_config.get('max_log_size_mb', 10) * 1024 * 1024,
            backup_count=log_config.get('backup_count', 5),
            log_format=log_config.get('log_format', 'detailed')
        )
        self.logger = get_logger(__name__)
        self.logger.info("=" * 60)
        self.logger.info("Voice Inventory Manager Starting")
        self.logger.info("=" * 60)

    def initialize_components(self):
        """Initialize all system components."""
        try:
            self.logger.info("Initializing components...")

            # Initialize database
            self.logger.info("Initializing database...")
            db_config = self.config.get('database', {})
            self.database = Database(
                db_path=db_config.get('path', 'data/inventory.db'),
                backup_enabled=db_config.get('backup_enabled', True),
                backup_path=db_config.get('backup_path', 'data/backups/')
            )
            self.database.initialize()

            # Initialize inventory engine
            self.logger.info("Initializing inventory engine...")
            self.inventory_engine = InventoryEngine(
                database=self.database,
                config=self.config.get('inventory', {})
            )

            # Initialize NLP parser
            self.logger.info("Initializing NLP parser...")
            self.nlp_parser = NLPParser(
                config=self.config.get('nlp', {}),
                inventory_engine=self.inventory_engine
            )

            # Initialize intent router
            self.logger.info("Initializing intent router...")
            self.intent_router = IntentRouter(
                inventory_engine=self.inventory_engine,
                config=self.config.get('security', {})
            )

            # Initialize response generator
            self.logger.info("Initializing response generator...")
            self.response_generator = ResponseGenerator(
                config=self.config.get('response', {})
            )

            # Initialize STT pipeline
            self.logger.info("Initializing STT pipeline...")
            self.stt_pipeline = STTPipeline(
                config=self.config.get('stt', {}),
                mic_config=self.config.get('microphone', {})
            )

            # Initialize voice engine
            self.logger.info("Initializing voice engine...")
            self.voice_engine = VoiceEngine(
                stt_pipeline=self.stt_pipeline,
                nlp_parser=self.nlp_parser,
                intent_router=self.intent_router,
                response_generator=self.response_generator,
                config=self.config
            )

            self.components_initialized = True
            self.logger.info("All components initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}", exc_info=True)
            raise

    def run_cli(self):
        """Run the application in CLI mode."""
        self.logger.info("Starting CLI interface...")
        cli = CLIInterface(
            voice_engine=self.voice_engine,
            inventory_engine=self.inventory_engine,
            config=self.config
        )
        cli.run()

    def run_gui(self):
        """Run the application in GUI mode."""
        self.logger.info("Starting GUI interface...")
        gui = GUIInterface(
            voice_engine=self.voice_engine,
            inventory_engine=self.inventory_engine,
            config=self.config
        )
        gui.run()

    def shutdown(self):
        """Gracefully shutdown all components."""
        self.logger.info("Shutting down Voice Inventory Manager...")

        if self.voice_engine:
            self.voice_engine.shutdown()

        if self.database:
            self.database.close()

        self.logger.info("Shutdown complete")

    def run(self, mode: str = "cli"):
        """
        Main run method.

        Args:
            mode: Interface mode - 'cli' or 'gui'
        """
        try:
            # Load configuration
            self.config = self.load_config()

            # Initialize logging
            self.initialize_logging()

            # Initialize components
            self.initialize_components()

            # Run appropriate interface
            if mode.lower() == "gui":
                self.run_gui()
            else:
                self.run_cli()

        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Fatal error: {e}", exc_info=True)
            else:
                print(f"Fatal error: {e}")
            sys.exit(1)
        finally:
            self.shutdown()


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Voice Inventory Manager - Voice-controlled inventory system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run in CLI mode (default)
  python main.py --mode gui         # Run in GUI mode
  python main.py --config custom.yaml  # Use custom config file
        """
    )

    parser.add_argument(
        '--mode',
        choices=['cli', 'gui'],
        default='cli',
        help='Interface mode (default: cli)'
    )

    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='Voice Inventory Manager v1.0.0'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    # Parse arguments
    args = parse_arguments()

    # Create and run application
    app = VoiceInventoryManager(config_path=args.config)

    # Override log level if debug mode
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run application
    app.run(mode=args.mode)


if __name__ == "__main__":
    main()
