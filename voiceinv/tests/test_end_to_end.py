"""
End-to-End Test Suite

Tests complete workflows from voice input to database storage.
"""

import pytest
from unittest.mock import Mock, patch
from main import VoiceInventoryManager
import tempfile
import os


@pytest.fixture
def temp_config():
    """Create temporary configuration."""
    fd, path = tempfile.mkstemp(suffix='.yaml')
    os.close(fd)

    config_content = """
stt:
  provider: "google"
  language: "en-US"
  timeout: 5
  phrase_time_limit: 10
  energy_threshold: 4000
  dynamic_energy_threshold: true
  pause_threshold: 0.8

microphone:
  device_index: null
  sample_rate: 16000
  chunk_size: 1024

nlp:
  fuzzy_threshold: 80
  enable_fuzzy_matching: true
  context_memory_size: 5
  confidence_threshold: 0.6

inventory:
  min_stock_alert: 5
  enable_stock_alerts: true
  default_unit: "pcs"
  require_confirmation_for_delete: true
  enable_transaction_log: true

database:
  path: "test_inventory.db"
  backup_enabled: false

response:
  mode: "text"
  voice_enabled: false

logging:
  level: "ERROR"
  log_to_file: false

security:
  enable_voice_profile: false
  require_admin_password: false
  confirm_destructive_operations: false

ui:
  default_mode: "cli"
"""

    with open(path, 'w') as f:
        f.write(config_content)

    yield path

    # Cleanup
    if os.path.exists(path):
        os.remove(path)
    if os.path.exists("test_inventory.db"):
        os.remove("test_inventory.db")


class TestEndToEnd:
    """End-to-end integration tests."""

    @patch('core.stt_pipeline.STTPipeline.listen_and_recognize')
    def test_add_item_workflow(self, mock_listen, temp_config):
        """Test complete add item workflow."""
        # Mock voice input
        mock_listen.return_value = "add 10 apples at 1.50 each"

        # Create app
        app = VoiceInventoryManager(config_path=temp_config)
        app.config = app.load_config()
        app.initialize_logging()
        app.initialize_components()

        # Process command
        result = app.voice_engine.process_text_command("add 10 apples at 1.50 each")

        # Verify
        assert result['success'] is True
        assert result['intent'] == 'add_item'

        # Verify in database
        item = app.inventory_engine.get_item("apples")
        assert item is not None
        assert item['quantity'] == 10

        # Cleanup
        app.shutdown()

    @patch('core.stt_pipeline.STTPipeline.listen_and_recognize')
    def test_query_workflow(self, mock_listen, temp_config):
        """Test complete query workflow."""
        # Create app
        app = VoiceInventoryManager(config_path=temp_config)
        app.config = app.load_config()
        app.initialize_logging()
        app.initialize_components()

        # Add item first
        app.voice_engine.process_text_command("add 5 bananas")

        # Query item
        result = app.voice_engine.process_text_command("how many bananas")

        # Verify
        assert result['success'] is True
        assert result['intent'] == 'query'

        # Cleanup
        app.shutdown()

    @patch('core.stt_pipeline.STTPipeline.listen_and_recognize')
    def test_update_stock_workflow(self, mock_listen, temp_config):
        """Test complete update stock workflow."""
        # Create app
        app = VoiceInventoryManager(config_path=temp_config)
        app.config = app.load_config()
        app.initialize_logging()
        app.initialize_components()

        # Add item
        app.voice_engine.process_text_command("add 10 oranges")

        # Update stock
        result = app.voice_engine.process_text_command("increase oranges by 5")

        # Verify
        assert result['success'] is True

        item = app.inventory_engine.get_item("oranges")
        assert item['quantity'] == 15

        # Cleanup
        app.shutdown()

    @patch('core.stt_pipeline.STTPipeline.listen_and_recognize')
    def test_remove_item_workflow(self, mock_listen, temp_config):
        """Test complete remove item workflow."""
        # Create app
        app = VoiceInventoryManager(config_path=temp_config)
        app.config = app.load_config()
        app.initialize_logging()
        app.initialize_components()

        # Add item
        app.voice_engine.process_text_command("add 10 grapes")

        # Remove item
        result = app.voice_engine.process_text_command("delete grapes")

        # Verify
        assert result['success'] is True

        # Cleanup
        app.shutdown()

    @patch('core.stt_pipeline.STTPipeline.listen_and_recognize')
    def test_report_workflow(self, mock_config):
        """Test complete report generation workflow."""
        # Create app
        app = VoiceInventoryManager(config_path=temp_config)
        app.config = app.load_config()
        app.initialize_logging()
        app.initialize_components()

        # Add some items
        app.voice_engine.process_text_command("add 10 apples")
        app.voice_engine.process_text_command("add 5 bananas")

        # Generate report
        result = app.voice_engine.process_text_command("generate summary report")

        # Verify
        assert result['success'] is True
        assert result['intent'] == 'report'

        # Cleanup
        app.shutdown()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
