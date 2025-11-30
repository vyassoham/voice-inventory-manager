"""
Test Suite for NLP Parser

Tests natural language processing including:
- Intent detection
- Entity extraction
- Fuzzy matching
- Number word conversion
"""

import pytest
from core.nlp_parser import NLPParser
from unittest.mock import Mock


@pytest.fixture
def nlp_parser():
    """Create NLP parser instance."""
    config = {
        'fuzzy_threshold': 80,
        'enable_fuzzy_matching': True,
        'confidence_threshold': 0.6,
        'context_memory_size': 5
    }

    inventory_engine = Mock()

    return NLPParser(config=config, inventory_engine=inventory_engine)


class TestNLPParser:
    """Test NLPParser class."""

    def test_parse_add_item_structured(self, nlp_parser):
        """Test parsing structured add item command."""
        result = nlp_parser.parse("add item apple quantity 5 price 100")

        assert result['success'] is True
        assert result['intent'] == 'add_item'
        assert result['entities']['item_name'] is not None
        assert result['entities']['quantity'] == 5
        assert result['entities']['price'] == 100.0

    def test_parse_add_item_conversational(self, nlp_parser):
        """Test parsing conversational add item command."""
        result = nlp_parser.parse("bro add 10 kurkure packets")

        assert result['success'] is True
        assert result['intent'] == 'add_item'
        assert result['entities']['quantity'] == 10

    def test_parse_update_stock(self, nlp_parser):
        """Test parsing update stock command."""
        result = nlp_parser.parse("increase rice by 3")

        assert result['success'] is True
        assert result['intent'] == 'update_stock'
        assert result['entities']['quantity_change'] == 3
        assert result['entities']['operation'] == 'add'

    def test_parse_remove_item(self, nlp_parser):
        """Test parsing remove item command."""
        result = nlp_parser.parse("delete pepsi")

        assert result['success'] is True
        assert result['intent'] == 'remove_item'
        assert result['entities']['item_name'] is not None

    def test_parse_query(self, nlp_parser):
        """Test parsing query command."""
        result = nlp_parser.parse("how many apples left")

        assert result['success'] is True
        assert result['intent'] == 'query'
        assert result['entities']['query_type'] == 'single'

    def test_parse_report(self, nlp_parser):
        """Test parsing report command."""
        result = nlp_parser.parse("give me daily report")

        assert result['success'] is True
        assert result['intent'] == 'report'
        assert result['entities']['report_type'] == 'daily'

    def test_number_word_conversion(self, nlp_parser):
        """Test number word to digit conversion."""
        result = nlp_parser.parse("add five apples")

        assert result['success'] is True
        assert result['entities']['quantity'] == 5

    def test_normalize_text(self, nlp_parser):
        """Test text normalization."""
        normalized = nlp_parser._normalize_text("Bro, can you please add five apples?")

        assert "bro" not in normalized
        assert "please" not in normalized
        assert "5" in normalized

    def test_invalid_command(self, nlp_parser):
        """Test parsing invalid command."""
        result = nlp_parser.parse("xyz abc def")

        assert result['success'] is False
        assert result['error'] is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
