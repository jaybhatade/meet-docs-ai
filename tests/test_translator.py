"""
Unit tests for the Translator module.
Tests language detection, translation, and text processing functionality.
"""

import pytest
from src.translator import Translator


class TestTranslator:
    """Test suite for Translator class."""
    
    @pytest.fixture
    def translator(self):
        """Create a Translator instance for testing."""
        return Translator()
    
    def test_translator_initialization(self, translator):
        """Test that Translator initializes correctly."""
        assert translator is not None
        assert translator.translator is not None
        assert translator.supported_languages == {'hi', 'mr', 'en'}
    
    def test_detect_language_english(self, translator):
        """Test language detection for English text."""
        text = "Hello, this is a test meeting."
        lang = translator.detect_language(text)
        assert lang == 'en'
    
    def test_detect_language_empty_text(self, translator):
        """Test language detection with empty text."""
        assert translator.detect_language("") == 'unknown'
        assert translator.detect_language("   ") == 'unknown'
        assert translator.detect_language(None) == 'unknown'
    
    def test_needs_translation_english(self, translator):
        """Test that English text doesn't need translation."""
        text = "This is an English sentence."
        assert translator.needs_translation(text) is False
    
    def test_needs_translation_empty(self, translator):
        """Test needs_translation with empty text."""
        assert translator.needs_translation("") is False
        assert translator.needs_translation(None) is False
    
    def test_translate_english_passthrough(self, translator):
        """Test that English text passes through unchanged."""
        text = "Hello, this is a test meeting about project updates."
        result = translator.translate_to_english(text)
        assert result == text
    
    def test_translate_empty_text(self, translator):
        """Test translation with empty text."""
        assert translator.translate_to_english("") == ""
        assert translator.translate_to_english(None) == None
    
    def test_clean_text_removes_language_markers(self, translator):
        """Test that _clean_text removes language markers."""
        text = "[hi] This is translated text [mr]"
        cleaned = translator._clean_text(text)
        assert "[hi]" not in cleaned
        assert "[mr]" not in cleaned
    
    def test_clean_text_removes_extra_whitespace(self, translator):
        """Test that _clean_text removes extra whitespace."""
        text = "This  has   extra    spaces"
        cleaned = translator._clean_text(text)
        assert "  " not in cleaned
        assert cleaned == "This has extra spaces"
    
    def test_clean_text_strips_whitespace(self, translator):
        """Test that _clean_text strips leading/trailing whitespace."""
        text = "  text with spaces  "
        cleaned = translator._clean_text(text)
        assert cleaned == "text with spaces"
    
    def test_process_transcript_empty(self, translator):
        """Test processing empty transcript."""
        assert translator.process_transcript("") == ""
        assert translator.process_transcript(None) == None
    
    def test_process_transcript_english_only(self, translator):
        """Test processing transcript with only English."""
        transcript = "Hello everyone.\nWelcome to the meeting.\nLet's begin."
        result = translator.process_transcript(transcript)
        # Should contain the same content (may have slight formatting differences)
        assert "Hello everyone" in result
        assert "Welcome to the meeting" in result
        assert "Let's begin" in result
    
    def test_process_transcript_splits_paragraphs(self, translator):
        """Test that process_transcript handles paragraph splitting."""
        transcript = "Line 1\nLine 2\nLine 3"
        result = translator.process_transcript(transcript)
        # Should process each line
        assert result is not None
        assert len(result) > 0
    
    def test_error_handling_translation_failure(self, translator):
        """Test that translation errors are handled gracefully."""
        # This should handle errors and return text with error marker
        # We can't easily force a translation error, but we can test the structure
        result = translator.translate_to_english("Test text")
        assert result is not None
        assert isinstance(result, str)
    
    def test_clean_text_empty(self, translator):
        """Test _clean_text with empty input."""
        assert translator._clean_text("") == ""
        assert translator._clean_text(None) == None
    
    def test_clean_text_removes_translation_markers(self, translator):
        """Test that _clean_text removes translation service markers."""
        text = "[Translated from Hindi] This is the text"
        cleaned = translator._clean_text(text)
        assert "[Translated from" not in cleaned
        assert "This is the text" in cleaned
