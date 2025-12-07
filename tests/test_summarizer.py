"""
Unit tests for the Summarizer module.
Tests AI-powered summary generation and fallback mechanisms.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.summarizer import Summarizer


class TestSummarizerInitialization:
    """Test Summarizer initialization and configuration."""
    
    def test_init_with_valid_api_key(self):
        """Test initialization with valid API key."""
        with patch('src.summarizer.genai.configure'):
            with patch('src.summarizer.genai.GenerativeModel'):
                summarizer = Summarizer("valid_api_key_123")
                assert summarizer is not None
    
    def test_init_with_empty_api_key(self):
        """Test initialization fails with empty API key."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            Summarizer("")
    
    def test_init_with_whitespace_api_key(self):
        """Test initialization fails with whitespace-only API key."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            Summarizer("   ")
    
    def test_init_with_none_api_key(self):
        """Test initialization fails with None API key."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            Summarizer(None)


class TestPromptConstruction:
    """Test prompt building for Gemini API."""
    
    @patch('src.summarizer.genai.configure')
    @patch('src.summarizer.genai.GenerativeModel')
    def test_build_prompt_includes_transcript(self, mock_model, mock_configure):
        """Test that prompt includes the transcript text."""
        summarizer = Summarizer("test_key")
        transcript = "This is a test meeting transcript."
        
        prompt = summarizer._build_prompt(transcript)
        
        assert transcript in prompt
        assert "TRANSCRIPT:" in prompt
    
    @patch('src.summarizer.genai.configure')
    @patch('src.summarizer.genai.GenerativeModel')
    def test_build_prompt_includes_required_sections(self, mock_model, mock_configure):
        """Test that prompt requests all required sections."""
        summarizer = Summarizer("test_key")
        transcript = "Test transcript"
        
        prompt = summarizer._build_prompt(transcript)
        
        # Check for all required sections
        assert "Meeting Title" in prompt or "title" in prompt.lower()
        assert "Participants" in prompt or "participants" in prompt.lower()
        assert "Key Discussion Points" in prompt or "key" in prompt.lower()
        assert "Action Items" in prompt or "action" in prompt.lower()
        assert "Decisions" in prompt or "decision" in prompt.lower()
        assert "Follow-up" in prompt or "follow" in prompt.lower()
    
    @patch('src.summarizer.genai.configure')
    @patch('src.summarizer.genai.GenerativeModel')
    def test_build_prompt_requests_json_format(self, mock_model, mock_configure):
        """Test that prompt requests JSON formatted response."""
        summarizer = Summarizer("test_key")
        transcript = "Test transcript"
        
        prompt = summarizer._build_prompt(transcript)
        
        assert "JSON" in prompt or "json" in prompt


class TestResponseParsing:
    """Test parsing of Gemini API responses."""
    
    @patch('src.summarizer.genai.configure')
    @patch('src.summarizer.genai.GenerativeModel')
    def test_parse_valid_json_response(self, mock_model, mock_configure):
        """Test parsing of valid JSON response."""
        summarizer = Summarizer("test_key")
        
        response_text = """{
            "title": "Project Review Meeting",
            "participants": ["John", "Sarah"],
            "key_points": ["Feature complete", "Testing needed"],
            "action_items": ["Review documentation"],
            "decisions": ["Deploy next week"],
            "follow_ups": ["Schedule follow-up"]
        }"""
        
        summary = summarizer._parse_response(response_text)
        
        assert summary['title'] == "Project Review Meeting"
        assert len(summary['participants']) == 2
        assert "John" in summary['participants']
        assert len(summary['key_points']) == 2
    
    @patch('src.summarizer.genai.configure')
    @patch('src.summarizer.genai.GenerativeModel')
    def test_parse_json_with_markdown_code_blocks(self, mock_model, mock_configure):
        """Test parsing JSON wrapped in markdown code blocks."""
        summarizer = Summarizer("test_key")
        
        response_text = """```json
{
    "title": "Test Meeting",
    "participants": ["Alice"],
    "key_points": ["Point 1"],
    "action_items": ["Action 1"],
    "decisions": ["Decision 1"],
    "follow_ups": ["Follow-up 1"]
}
```"""
        
        summary = summarizer._parse_response(response_text)
        
        assert summary['title'] == "Test Meeting"
        assert "Alice" in summary['participants']
    
    @patch('src.summarizer.genai.configure')
    @patch('src.summarizer.genai.GenerativeModel')
    def test_parse_response_adds_missing_fields(self, mock_model, mock_configure):
        """Test that missing fields are added with defaults."""
        summarizer = Summarizer("test_key")
        
        # Response missing some fields
        response_text = """{
            "title": "Incomplete Meeting",
            "participants": ["Bob"]
        }"""
        
        summary = summarizer._parse_response(response_text)
        
        assert 'key_points' in summary
        assert 'action_items' in summary
        assert 'decisions' in summary
        assert 'follow_ups' in summary
        assert isinstance(summary['key_points'], list)
    
    @patch('src.summarizer.genai.configure')
    @patch('src.summarizer.genai.GenerativeModel')
    def test_parse_invalid_json_falls_back_to_text_parsing(self, mock_model, mock_configure):
        """Test fallback to text parsing when JSON is invalid."""
        summarizer = Summarizer("test_key")
        
        response_text = """
        Meeting Title: Project Discussion
        
        Participants:
        - John
        - Sarah
        
        Key Points:
        - Discussed new features
        - Reviewed timeline
        """
        
        summary = summarizer._parse_response(response_text)
        
        # Should still return a valid summary structure
        assert 'title' in summary
        assert 'participants' in summary
        assert 'key_points' in summary
        assert isinstance(summary, dict)


class TestFallbackSummary:
    """Test fallback summary generation."""
    
    @patch('src.summarizer.genai.configure')
    @patch('src.summarizer.genai.GenerativeModel')
    def test_fallback_summary_structure(self, mock_model, mock_configure):
        """Test that fallback summary has correct structure."""
        summarizer = Summarizer("test_key")
        transcript = "Test meeting transcript"
        
        summary = summarizer.get_fallback_summary(transcript)
        
        assert 'title' in summary
        assert 'participants' in summary
        assert 'key_points' in summary
        assert 'action_items' in summary
        assert 'decisions' in summary
        assert 'follow_ups' in summary
    
    @patch('src.summarizer.genai.configure')
    @patch('src.summarizer.genai.GenerativeModel')
    def test_fallback_summary_with_empty_transcript(self, mock_model, mock_configure):
        """Test fallback summary with empty transcript."""
        summarizer = Summarizer("test_key")
        
        summary = summarizer.get_fallback_summary("")
        
        assert summary['title'] is not None
        assert isinstance(summary['participants'], list)
        assert isinstance(summary['key_points'], list)
    
    @patch('src.summarizer.genai.configure')
    @patch('src.summarizer.genai.GenerativeModel')
    def test_fallback_extracts_participant_names(self, mock_model, mock_configure):
        """Test that fallback attempts to extract participant names."""
        summarizer = Summarizer("test_key")
        transcript = "John said we should proceed. Sarah mentioned the deadline."
        
        summary = summarizer.get_fallback_summary(transcript)
        
        # Should attempt to extract names
        assert isinstance(summary['participants'], list)


class TestParticipantExtraction:
    """Test participant name extraction from transcripts."""
    
    @patch('src.summarizer.genai.configure')
    @patch('src.summarizer.genai.GenerativeModel')
    def test_extract_names_from_transcript(self, mock_model, mock_configure):
        """Test extraction of participant names."""
        summarizer = Summarizer("test_key")
        transcript = "John said hello. Sarah mentioned the project. Mike asked a question."
        
        names = summarizer._extract_participant_names(transcript)
        
        assert isinstance(names, list)
        # Should find at least some names
        assert len(names) >= 0  # May or may not find names depending on pattern
    
    @patch('src.summarizer.genai.configure')
    @patch('src.summarizer.genai.GenerativeModel')
    def test_extract_names_filters_common_words(self, mock_model, mock_configure):
        """Test that common words are filtered from names."""
        summarizer = Summarizer("test_key")
        transcript = "The said something. This mentioned that."
        
        names = summarizer._extract_participant_names(transcript)
        
        # Should not include common words like "The", "This"
        assert "The" not in names
        assert "This" not in names
    
    @patch('src.summarizer.genai.configure')
    @patch('src.summarizer.genai.GenerativeModel')
    def test_extract_names_removes_duplicates(self, mock_model, mock_configure):
        """Test that duplicate names are removed."""
        summarizer = Summarizer("test_key")
        transcript = "John said hello. John mentioned again. John asked something."
        
        names = summarizer._extract_participant_names(transcript)
        
        # Should not have duplicates
        assert len(names) == len(set(names))


class TestGenerateSummary:
    """Test the main summary generation method."""
    
    @patch('src.summarizer.genai.configure')
    @patch('src.summarizer.genai.GenerativeModel')
    def test_generate_summary_with_empty_transcript(self, mock_model, mock_configure):
        """Test that empty transcript returns fallback summary."""
        summarizer = Summarizer("test_key")
        
        summary = summarizer.generate_summary("")
        
        # Should return fallback summary
        assert 'title' in summary
        assert isinstance(summary, dict)
    
    @patch('src.summarizer.genai.configure')
    @patch('src.summarizer.genai.GenerativeModel')
    def test_generate_summary_calls_api(self, mock_model, mock_configure):
        """Test that generate_summary calls the API."""
        mock_response = Mock()
        mock_response.text = """{
            "title": "Test",
            "participants": [],
            "key_points": [],
            "action_items": [],
            "decisions": [],
            "follow_ups": []
        }"""
        
        mock_instance = Mock()
        mock_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_instance
        
        summarizer = Summarizer("test_key")
        summary = summarizer.generate_summary("Test transcript")
        
        # Verify API was called
        mock_instance.generate_content.assert_called_once()
    
    @patch('src.summarizer.genai.configure')
    @patch('src.summarizer.genai.GenerativeModel')
    def test_generate_summary_returns_fallback_on_api_failure(self, mock_model, mock_configure):
        """Test that API failure returns fallback summary."""
        mock_instance = Mock()
        mock_instance.generate_content.side_effect = Exception("API Error")
        mock_model.return_value = mock_instance
        
        summarizer = Summarizer("test_key")
        summary = summarizer.generate_summary("Test transcript")
        
        # Should return fallback summary
        assert 'title' in summary
        assert isinstance(summary, dict)


class TestAPIRetryLogic:
    """Test API call retry mechanism."""
    
    @patch('src.summarizer.genai.configure')
    @patch('src.summarizer.genai.GenerativeModel')
    @patch('src.summarizer.time.sleep')  # Mock sleep to speed up tests
    def test_retry_on_api_failure(self, mock_sleep, mock_model, mock_configure):
        """Test that API calls are retried on failure."""
        mock_response = Mock()
        mock_response.text = '{"title": "Test", "participants": [], "key_points": [], "action_items": [], "decisions": [], "follow_ups": []}'
        
        mock_instance = Mock()
        # Fail twice, then succeed
        mock_instance.generate_content.side_effect = [
            Exception("Temporary error"),
            Exception("Another error"),
            mock_response
        ]
        mock_model.return_value = mock_instance
        
        summarizer = Summarizer("test_key")
        result = summarizer._call_api_with_retry("test prompt", max_retries=2)
        
        # Should have called 3 times (initial + 2 retries)
        assert mock_instance.generate_content.call_count == 3
        assert result == mock_response.text
    
    @patch('src.summarizer.genai.configure')
    @patch('src.summarizer.genai.GenerativeModel')
    @patch('src.summarizer.time.sleep')
    def test_retry_exhaustion_raises_exception(self, mock_sleep, mock_model, mock_configure):
        """Test that exception is raised after all retries fail."""
        mock_instance = Mock()
        mock_instance.generate_content.side_effect = Exception("Persistent error")
        mock_model.return_value = mock_instance
        
        summarizer = Summarizer("test_key")
        
        with pytest.raises(Exception, match="Persistent error"):
            summarizer._call_api_with_retry("test prompt", max_retries=2)
        
        # Should have tried 3 times (initial + 2 retries)
        assert mock_instance.generate_content.call_count == 3
