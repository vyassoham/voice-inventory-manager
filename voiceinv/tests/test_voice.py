"""
Test Suite for Voice Engine

Tests voice processing pipeline including:
- Voice command listening
- Command processing
- Error handling
- Statistics tracking
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from core.voice_engine import VoiceEngine
from core.stt_pipeline import STTPipeline
from core.nlp_parser import NLPParser
from core.intent_router import IntentRouter
from core.response_generator import ResponseGenerator


@pytest.fixture
def mock_components():
    """Create mock components for testing."""
    stt_pipeline = Mock(spec=STTPipeline)
    nlp_parser = Mock(spec=NLPParser)
    intent_router = Mock(spec=IntentRouter)
    response_generator = Mock(spec=ResponseGenerator)

    config = {
        'hotword': {'enabled': False},
        'stt': {},
        'nlp': {},
        'response': {}
    }

    return {
        'stt_pipeline': stt_pipeline,
        'nlp_parser': nlp_parser,
        'intent_router': intent_router,
        'response_generator': response_generator,
        'config': config
    }


@pytest.fixture
def voice_engine(mock_components):
    """Create voice engine instance."""
    return VoiceEngine(
        stt_pipeline=mock_components['stt_pipeline'],
        nlp_parser=mock_components['nlp_parser'],
        intent_router=mock_components['intent_router'],
        response_generator=mock_components['response_generator'],
        config=mock_components['config']
    )


class TestVoiceEngine:
    """Test VoiceEngine class."""

    def test_initialization(self, voice_engine):
        """Test voice engine initialization."""
        assert voice_engine is not None
        assert voice_engine.is_active is True
        assert voice_engine.command_count == 0

    def test_listen_for_command_success(self, voice_engine, mock_components):
        """Test successful command listening."""
        # Mock STT to return text
        mock_components['stt_pipeline'].listen_and_recognize.return_value = "add 5 apples"

        result = voice_engine.listen_for_command()

        assert result == "add 5 apples"
        assert voice_engine.command_count == 1

    def test_listen_for_command_no_speech(self, voice_engine, mock_components):
        """Test listening with no speech detected."""
        mock_components['stt_pipeline'].listen_and_recognize.return_value = None

        result = voice_engine.listen_for_command()

        assert result is None

    def test_process_command_success(self, voice_engine, mock_components):
        """Test successful command processing."""
        # Mock NLP parser
        mock_components['nlp_parser'].parse.return_value = {
            'success': True,
            'intent': 'add_item',
            'entities': {'item_name': 'apple', 'quantity': 5}
        }

        # Mock intent router
        mock_components['intent_router'].route.return_value = {
            'success': True,
            'data': {'item_id': 1}
        }

        # Mock response generator
        mock_components['response_generator'].generate_success_response.return_value = "Added 5 apples"

        result = voice_engine.process_command("add 5 apples")

        assert result['success'] is True
        assert result['intent'] == 'add_item'
        assert result['response'] == "Added 5 apples"

    def test_process_command_parse_failure(self, voice_engine, mock_components):
        """Test command processing with parse failure."""
        mock_components['nlp_parser'].parse.return_value = {
            'success': False,
            'error': 'Could not understand command'
        }

        mock_components['response_generator'].generate_error_response.return_value = "Error message"

        result = voice_engine.process_command("invalid command")

        assert result['success'] is False
        assert result['error'] is not None

    def test_get_statistics(self, voice_engine, mock_components):
        """Test statistics retrieval."""
        mock_components['stt_pipeline'].get_statistics.return_value = {
            'provider': 'google',
            'recognition_count': 10
        }

        # Process some commands
        voice_engine.command_count = 5
        voice_engine.error_count = 1

        stats = voice_engine.get_statistics()

        assert stats['command_count'] == 5
        assert stats['error_count'] == 1
        assert 'stt_stats' in stats


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
