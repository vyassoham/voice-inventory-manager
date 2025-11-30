"""
CLI Interface Module

Command-line interface for the Voice Inventory Manager.

Supports:
- Voice commands
- Text commands
- Interactive menu
- Status display
- Colored output
"""

from typing import Dict, Any, Optional
from utils.logger import get_logger
from core.voice_engine import VoiceEngine
from core.inventory_engine import InventoryEngine
from colorama import Fore, Back, Style, init
import sys


# Initialize colorama
init(autoreset=True)


class CLIInterface:
    """
    Command-line interface for voice inventory system.
    """

    def __init__(
        self,
        voice_engine: VoiceEngine,
        inventory_engine: InventoryEngine,
        config: Dict[str, Any]
    ):
        """
        Initialize CLI interface.

        Args:
            voice_engine: Voice engine instance
            inventory_engine: Inventory engine instance
            config: Configuration dictionary
        """
        self.voice_engine = voice_engine
        self.inventory_engine = inventory_engine
        self.config = config
        self.logger = get_logger(__name__)

        self.running = True
        self.voice_mode = True  # Start in voice mode

    def run(self):
        """Run the CLI interface."""
        self.print_banner()
        self.print_help()

        # Initial calibration
        self.voice_engine.calibrate_noise()

        while self.running:
            try:
                self.print_prompt()

                if self.voice_mode:
                    # Voice input mode
                    self.handle_voice_input()
                else:
                    # Text input mode
                    self.handle_text_input()

            except KeyboardInterrupt:
                self.print_info("\nReceived interrupt signal")
                self.confirm_exit()
            except Exception as e:
                self.logger.error(f"CLI error: {e}", exc_info=True)
                self.print_error(f"An error occurred: {e}")

        self.print_info("Goodbye!")

    def print_banner(self):
        """Print application banner."""
        banner = f"""
{Fore.CYAN}{'=' * 60}
{Fore.GREEN}    Voice Inventory Manager v1.0
{Fore.CYAN}    Voice-Controlled Inventory Management System
{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}
        """
        print(banner)

    def print_help(self):
        """Print help information."""
        help_text = f"""
{Fore.YELLOW}Available Commands:{Style.RESET_ALL}
  {Fore.GREEN}Voice Commands:{Style.RESET_ALL}
    - "add [quantity] [item name]"
    - "update [item name] by [quantity]"
    - "remove [item name]"
    - "how many [item name]"
    - "show all items"
    - "generate report"

  {Fore.GREEN}System Commands:{Style.RESET_ALL}
    - "help" - Show this help
    - "mode" - Toggle voice/text mode
    - "stats" - Show statistics
    - "exit" or "quit" - Exit application

{Fore.CYAN}Current Mode: {'VOICE' if self.voice_mode else 'TEXT'}{Style.RESET_ALL}
        """
        print(help_text)

    def print_prompt(self):
        """Print input prompt."""
        if self.voice_mode:
            print(f"\n{Fore.GREEN}🎤 Listening...{Style.RESET_ALL}", end=" ", flush=True)
        else:
            print(f"\n{Fore.CYAN}> {Style.RESET_ALL}", end="", flush=True)

    def handle_voice_input(self):
        """Handle voice input."""
        # Listen for command
        text = self.voice_engine.listen_for_command(timeout=5)

        if not text:
            print(f"{Fore.YELLOW}(no speech detected){Style.RESET_ALL}")
            return

        print(f"\n{Fore.BLUE}You said: {Style.RESET_ALL}{text}")

        # Check for system commands
        if self.handle_system_command(text):
            return

        # Process command
        result = self.voice_engine.process_command(text)

        # Display result
        self.display_result(result)

    def handle_text_input(self):
        """Handle text input."""
        try:
            text = input().strip()

            if not text:
                return

            # Check for system commands
            if self.handle_system_command(text):
                return

            # Process command
            result = self.voice_engine.process_text_command(text)

            # Display result
            self.display_result(result)

        except EOFError:
            self.running = False

    def handle_system_command(self, text: str) -> bool:
        """
        Handle system commands.

        Args:
            text: Command text

        Returns:
            True if system command was handled, False otherwise
        """
        text_lower = text.lower().strip()

        if text_lower in ['exit', 'quit', 'goodbye', 'bye']:
            self.confirm_exit()
            return True

        elif text_lower == 'help':
            self.print_help()
            return True

        elif text_lower == 'mode':
            self.toggle_mode()
            return True

        elif text_lower == 'stats':
            self.show_statistics()
            return True

        elif text_lower == 'clear':
            self.clear_screen()
            return True

        return False

    def display_result(self, result: Dict[str, Any]):
        """
        Display command result.

        Args:
            result: Result dictionary
        """
        if result['success']:
            self.print_success(result['response'])
        else:
            self.print_error(result['response'])

    def toggle_mode(self):
        """Toggle between voice and text mode."""
        self.voice_mode = not self.voice_mode
        mode_name = "VOICE" if self.voice_mode else "TEXT"
        self.print_info(f"Switched to {mode_name} mode")

    def show_statistics(self):
        """Show system statistics."""
        # Get voice engine stats
        voice_stats = self.voice_engine.get_statistics()

        # Get inventory stats
        inv_stats = self.inventory_engine.get_statistics()

        stats_text = f"""
{Fore.CYAN}{'=' * 40}
{Fore.GREEN}System Statistics
{Fore.CYAN}{'=' * 40}{Style.RESET_ALL}

{Fore.YELLOW}Voice Engine:{Style.RESET_ALL}
  Commands processed: {voice_stats['command_count']}
  Errors: {voice_stats['error_count']}
  STT Provider: {voice_stats['stt_stats']['provider']}

{Fore.YELLOW}Inventory:{Style.RESET_ALL}
  Total items: {inv_stats['total_items']}
  Total quantity: {inv_stats['total_quantity']}
  Total value: ${inv_stats['total_value']:.2f}
  Categories: {inv_stats['categories']}
  Low stock items: {inv_stats['low_stock_count']}
        """
        print(stats_text)

    def confirm_exit(self):
        """Confirm exit."""
        if self.voice_mode:
            # Switch to text mode for confirmation
            self.voice_mode = False

        print(f"\n{Fore.YELLOW}Are you sure you want to exit? (y/n): {Style.RESET_ALL}", end="")

        try:
            response = input().strip().lower()
            if response in ['y', 'yes']:
                self.running = False
            else:
                self.print_info("Continuing...")
                self.voice_mode = True
        except:
            self.running = False

    def clear_screen(self):
        """Clear the screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_banner()

    def print_success(self, message: str):
        """Print success message."""
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

    def print_error(self, message: str):
        """Print error message."""
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

    def print_info(self, message: str):
        """Print info message."""
        print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")

    def print_warning(self, message: str):
        """Print warning message."""
        print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
