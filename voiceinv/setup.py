"""
Installation and Setup Script for Voice Inventory Manager

This script automates the installation process including:
- Dependency installation
- Directory creation
- Configuration setup
- Database initialization
- Initial testing
"""

import subprocess
import sys
import os
from pathlib import Path
import platform


class Installer:
    """Installation manager for Voice Inventory Manager."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.python_executable = sys.executable
        self.os_type = platform.system()

    def print_header(self, text: str):
        """Print formatted header."""
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60 + "\n")

    def print_step(self, step: str):
        """Print step information."""
        print(f"→ {step}...")

    def print_success(self, message: str):
        """Print success message."""
        print(f"✓ {message}")

    def print_error(self, message: str):
        """Print error message."""
        print(f"✗ {message}")

    def run_command(self, command: list, description: str) -> bool:
        """
        Run a shell command.

        Args:
            command: Command to run as list
            description: Description of command

        Returns:
            True if successful, False otherwise
        """
        self.print_step(description)

        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            self.print_success(f"{description} completed")
            return True

        except subprocess.CalledProcessError as e:
            self.print_error(f"{description} failed: {e}")
            if e.stderr:
                print(f"Error: {e.stderr}")
            return False

    def check_python_version(self) -> bool:
        """Check if Python version is compatible."""
        self.print_step("Checking Python version")

        version = sys.version_info

        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.print_error(f"Python 3.8+ required, found {version.major}.{version.minor}")
            return False

        self.print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
        return True

    def install_dependencies(self) -> bool:
        """Install Python dependencies."""
        self.print_header("Installing Dependencies")

        # Upgrade pip
        if not self.run_command(
            [self.python_executable, "-m", "pip", "install", "--upgrade", "pip"],
            "Upgrading pip"
        ):
            return False

        # Install requirements
        requirements_file = self.project_root / "requirements.txt"

        if not requirements_file.exists():
            self.print_error("requirements.txt not found")
            return False

        if not self.run_command(
            [self.python_executable, "-m", "pip", "install", "-r", str(requirements_file)],
            "Installing dependencies from requirements.txt"
        ):
            return False

        return True

    def create_directories(self) -> bool:
        """Create necessary directories."""
        self.print_header("Creating Directories")

        directories = [
            "data",
            "data/backups",
            "logs",
            "cache",
            "plugins"
        ]

        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            self.print_success(f"Created directory: {directory}")

        return True

    def initialize_database(self) -> bool:
        """Initialize the database."""
        self.print_header("Initializing Database")

        try:
            from db.database import Database

            db_path = self.project_root / "data" / "inventory.db"
            db = Database(db_path=str(db_path), backup_enabled=False)
            db.initialize()
            db.close()

            self.print_success("Database initialized successfully")
            return True

        except Exception as e:
            self.print_error(f"Database initialization failed: {e}")
            return False

    def download_nltk_data(self) -> bool:
        """Download required NLTK data."""
        self.print_header("Downloading NLTK Data")

        try:
            import nltk

            datasets = ['punkt', 'averaged_perceptron_tagger', 'stopwords']

            for dataset in datasets:
                self.print_step(f"Downloading {dataset}")
                nltk.download(dataset, quiet=True)
                self.print_success(f"Downloaded {dataset}")

            return True

        except Exception as e:
            self.print_error(f"NLTK data download failed: {e}")
            return False

    def test_microphone(self) -> bool:
        """Test microphone availability."""
        self.print_header("Testing Microphone")

        try:
            import speech_recognition as sr

            recognizer = sr.Recognizer()
            microphone = sr.Microphone()

            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)

            self.print_success("Microphone test passed")
            return True

        except Exception as e:
            self.print_error(f"Microphone test failed: {e}")
            print("\nNote: Microphone is required for voice input.")
            print("You can still use text input mode.")
            return True  # Don't fail installation

    def run_tests(self) -> bool:
        """Run basic tests."""
        self.print_header("Running Tests")

        # Run pytest if available
        try:
            result = subprocess.run(
                [self.python_executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                self.print_success("All tests passed")
                return True
            else:
                self.print_error("Some tests failed")
                print(result.stdout)
                return False

        except subprocess.TimeoutExpired:
            self.print_error("Tests timed out")
            return False
        except Exception as e:
            self.print_error(f"Test execution failed: {e}")
            return False

    def create_desktop_shortcut(self) -> bool:
        """Create desktop shortcut (OS-specific)."""
        self.print_header("Creating Shortcut")

        # This is OS-specific and optional
        self.print_step("Skipping shortcut creation (manual step)")
        return True

    def print_installation_summary(self, success: bool):
        """Print installation summary."""
        self.print_header("Installation Summary")

        if success:
            print("✓ Installation completed successfully!\n")
            print("Next steps:")
            print("1. Review configuration in config.yaml")
            print("2. Run the application:")
            print(f"   {self.python_executable} main.py")
            print("\nFor GUI mode:")
            print(f"   {self.python_executable} main.py --mode gui")
            print("\nFor help:")
            print(f"   {self.python_executable} main.py --help")
            print("\nDocumentation:")
            print("   - README.md: Overview and quick start")
            print("   - docs/ARCHITECTURE.md: System architecture")
            print("   - docs/COMMANDS.md: Command reference")
            print("   - docs/API_SPEC.md: API documentation")
            print("   - docs/ROADMAP.md: Future plans")
        else:
            print("✗ Installation encountered errors.\n")
            print("Please check the error messages above and:")
            print("1. Ensure Python 3.8+ is installed")
            print("2. Check internet connection for package downloads")
            print("3. Verify system permissions")
            print("\nFor support, please check the documentation or open an issue.")

    def install(self):
        """Run complete installation process."""
        self.print_header("Voice Inventory Manager - Installation")

        print("This script will install and configure Voice Inventory Manager.\n")

        steps = [
            ("Checking Python version", self.check_python_version),
            ("Installing dependencies", self.install_dependencies),
            ("Creating directories", self.create_directories),
            ("Downloading NLTK data", self.download_nltk_data),
            ("Initializing database", self.initialize_database),
            ("Testing microphone", self.test_microphone),
            # ("Running tests", self.run_tests),  # Optional, can be slow
        ]

        success = True

        for description, step_func in steps:
            if not step_func():
                success = False
                print(f"\n⚠ Warning: {description} failed but continuing...\n")

        self.print_installation_summary(success)

        return success


def main():
    """Main entry point."""
    installer = Installer()

    try:
        success = installer.install()
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)

    except Exception as e:
        print(f"\n\nUnexpected error during installation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
