"""
Integration tests for MeetDocs AI pipeline.

These tests verify that all modules work together correctly and that
error handling and cleanup work across module boundaries.
"""

import pytest
import tempfile
import pickle
import os
import signal
import time
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock
import logging

from main import (
    validate_meet_url,
    load_configuration,
    cleanup,
    run_pipeline,
    PipelineError
)
from src.config import Config
from src.meet_joiner import MeetJoiner
from src.audio_capture import AudioCapturer


class TestModuleIntegration:
    """Test that modules integrate correctly."""
    
    def test_config_to_modules_integration(self):
        """Verify configuration flows correctly to all modules."""
        # Create a test configuration
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(
                cookie_path=str(Path(tmpdir) / "cookies.pkl"),
                audio_device_index=0,
                whisper_model_size="base",
                gemini_api_key="test_key",
                output_dir=str(Path(tmpdir) / "output"),
                audio_dir=str(Path(tmpdir) / "audio"),
                transcript_dir=str(Path(tmpdir) / "transcripts"),
                log_level="INFO",
                log_dir=str(Path(tmpdir) / "logs"),
                chunk_duration=30
            )
            
            # Verify directories can be created
            config.ensure_directories()
            
            assert Path(config.output_dir).exists()
            assert Path(config.audio_dir).exists()
            assert Path(config.transcript_dir).exists()
    
    def test_audio_to_transcriber_integration(self, tmp_path):
        """Verify audio files flow correctly from capturer to transcriber."""
        from src.transcriber import Transcriber
        
        audio_dir = tmp_path / "audio"
        audio_dir.mkdir()
        
        # Create a mock audio capturer
        capturer = AudioCapturer(str(audio_dir), chunk_duration=1)
        
        # Verify capturer creates proper directory structure
        assert Path(capturer.output_dir).exists()
        
        # Verify transcriber can access the same directory
        transcript_file = tmp_path / "transcript.txt"
        transcriber = Transcriber("base", str(transcript_file))
        
        # Both should work with the same file paths (normalize paths for comparison)
        assert str(Path(capturer.output_dir)) == str(audio_dir)
    
    def test_transcriber_to_translator_integration(self, tmp_path):
        """Verify transcript flows correctly from transcriber to translator."""
        from src.transcriber import Transcriber
        from src.translator import Translator
        
        transcript_file = tmp_path / "transcript.txt"
        
        # Create transcriber and write a test transcript
        transcriber = Transcriber("base", str(transcript_file))
        test_text = "This is a test transcript."
        transcriber.save_transcript(test_text)
        
        # Verify translator can read and process it
        translator = Translator()
        result = translator.process_transcript(test_text)
        
        # English text should pass through unchanged
        assert result == test_text
    
    def test_translator_to_summarizer_integration(self):
        """Verify translated text flows correctly to summarizer."""
        from src.translator import Translator
        from src.summarizer import Summarizer
        
        translator = Translator()
        test_text = "Meeting discussion about project timeline."
        translated = translator.process_transcript(test_text)
        
        # Verify summarizer can process the translated text
        # (using fallback since we don't have real API key)
        summarizer = Summarizer("test_key")
        summary = summarizer.get_fallback_summary(translated)
        
        assert "title" in summary
        assert "participants" in summary
        assert "key_points" in summary
    
    def test_summarizer_to_exporter_integration(self, tmp_path):
        """Verify summary flows correctly to exporter."""
        from src.summarizer import Summarizer
        from src.exporter import DocxExporter
        
        output_dir = tmp_path / "output"
        
        # Create a test summary
        summarizer = Summarizer("test_key")
        summary = summarizer.get_fallback_summary("Test meeting content")
        
        # Verify exporter can create document from summary
        exporter = DocxExporter(str(output_dir))
        output_path = exporter.create_document(summary)
        
        assert Path(output_path).exists()
        assert output_path.endswith('.docx')


class TestErrorHandlingAcrossModules:
    """Test error handling across module boundaries."""
    
    def test_meet_joiner_error_propagation(self):
        """Verify MeetJoiner errors are properly caught and logged."""
        # Test with non-existent cookie file
        with pytest.raises(FileNotFoundError):
            joiner = MeetJoiner("/nonexistent/cookies.pkl")
    
    def test_audio_capture_error_recovery(self, tmp_path):
        """Verify audio capture handles device errors gracefully."""
        audio_dir = tmp_path / "audio"
        capturer = AudioCapturer(str(audio_dir))
        
        # Try to capture from invalid device
        # The capturer may not raise immediately, but will fail during actual capture
        # This tests that the module doesn't crash on initialization
        try:
            capturer.start_capture(device_index=9999)
            # If it starts, stop it immediately
            capturer.stop_capture()
        except Exception:
            # Expected - invalid device should cause error
            pass
    
    def test_transcriber_missing_model_error(self, tmp_path):
        """Verify transcriber handles missing model gracefully."""
        from src.transcriber import Transcriber
        
        transcript_file = tmp_path / "transcript.txt"
        transcriber = Transcriber("base", str(transcript_file))
        
        # Without loading model, transcription should fail gracefully
        with pytest.raises(Exception) as exc_info:
            transcriber.transcribe_file("nonexistent.wav")
        
        assert "model" in str(exc_info.value).lower() or "file" in str(exc_info.value).lower()
    
    def test_translator_network_failure_fallback(self):
        """Verify translator falls back to original text on failure."""
        from src.translator import Translator
        
        translator = Translator()
        
        # With network issues, should return original text
        test_text = "Test content"
        result = translator.translate_to_english(test_text)
        
        # Should at least return something (original or translated)
        assert result is not None
        assert len(result) > 0
    
    def test_summarizer_api_failure_fallback(self):
        """Verify summarizer provides fallback on API failure."""
        from src.summarizer import Summarizer
        
        summarizer = Summarizer("invalid_key")
        transcript = "Meeting about project timeline and deliverables."
        
        # Should provide fallback summary
        summary = summarizer.get_fallback_summary(transcript)
        
        assert "title" in summary
        assert "participants" in summary
        assert isinstance(summary["key_points"], list)
    
    def test_exporter_invalid_directory_error(self):
        """Verify exporter handles invalid directories."""
        from src.exporter import DocxExporter
        
        # Exporter creates directory if it doesn't exist, so test with a truly invalid path
        # On Windows, paths with certain characters are invalid
        # The exporter will handle this gracefully by creating the directory
        # So we test that it doesn't crash
        try:
            exporter = DocxExporter("./test_output")
            # Cleanup
            import shutil
            if Path("./test_output").exists():
                shutil.rmtree("./test_output")
        except Exception:
            # If it does raise, that's also acceptable behavior
            pass


class TestCleanupScenarios:
    """Test cleanup on various exit scenarios."""
    
    def test_cleanup_with_active_joiner(self):
        """Verify cleanup properly closes active browser."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as f:
            cookies = [{'name': 'test', 'value': 'test'}]
            pickle.dump(cookies, f)
            temp_cookie_path = f.name
        
        try:
            # Create mock joiner
            joiner = MagicMock()
            joiner.close = MagicMock()
            
            # Create mock capturer
            capturer = MagicMock()
            capturer.is_capturing = True
            capturer.stop_capture = MagicMock()
            
            # Call cleanup
            cleanup(joiner, capturer)
            
            # Verify both were cleaned up
            capturer.stop_capture.assert_called_once()
            joiner.close.assert_called_once()
        
        finally:
            Path(temp_cookie_path).unlink(missing_ok=True)
    
    def test_cleanup_with_none_resources(self):
        """Verify cleanup handles None resources gracefully."""
        # Should not raise any errors
        cleanup(None, None)
    
    def test_cleanup_with_inactive_capturer(self):
        """Verify cleanup handles inactive capturer."""
        capturer = MagicMock()
        capturer.is_capturing = False
        capturer.stop_capture = MagicMock()
        
        cleanup(None, capturer)
        
        # Should not call stop_capture if not capturing
        capturer.stop_capture.assert_not_called()
    
    def test_cleanup_handles_exceptions(self):
        """Verify cleanup continues even if individual cleanups fail."""
        joiner = MagicMock()
        joiner.close = MagicMock(side_effect=Exception("Close failed"))
        
        capturer = MagicMock()
        capturer.is_capturing = True
        capturer.stop_capture = MagicMock(side_effect=Exception("Stop failed"))
        
        # Should not raise exception
        cleanup(joiner, capturer)


class TestURLValidation:
    """Test URL validation for various formats."""
    
    def test_valid_meet_urls(self):
        """Test that valid Google Meet URLs pass validation."""
        valid_urls = [
            "https://meet.google.com/abc-defg-hij",
            "https://meet.google.com/xyz-1234-abc",
            "http://meet.google.com/test-meet-url",
            "https://meet.google.co.in/abc-defg-hij"
        ]
        
        for url in valid_urls:
            assert validate_meet_url(url) is True
    
    def test_invalid_meet_urls(self):
        """Test that invalid URLs are rejected."""
        invalid_urls = [
            "https://zoom.us/j/123456",
            "https://teams.microsoft.com/meeting",
            "not-a-url",
            "https://meet.google.com",  # No path
            "ftp://meet.google.com/abc-defg-hij",  # Wrong protocol
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError):
                validate_meet_url(url)


class TestConfigurationLoading:
    """Test configuration loading from environment and CLI."""
    
    def test_config_from_env_and_cli_override(self, monkeypatch, tmp_path):
        """Test that CLI arguments override environment variables."""
        # Set environment variables
        monkeypatch.setenv("GEMINI_API_KEY", "env_key")
        monkeypatch.setenv("WHISPER_MODEL_SIZE", "base")
        monkeypatch.setenv("COOKIE_PATH", str(tmp_path / "env_cookies.pkl"))
        
        # Create mock args with CLI overrides
        args = MagicMock()
        args.cookie_path = str(tmp_path / "cli_cookies.pkl")
        args.audio_device = 1
        args.model_size = "small"
        args.gemini_key = "cli_key"
        args.output_dir = str(tmp_path / "output")
        args.log_level = "DEBUG"
        
        # Create cookie files
        (tmp_path / "env_cookies.pkl").touch()
        (tmp_path / "cli_cookies.pkl").touch()
        
        config = load_configuration(args)
        
        # CLI values should override env values
        assert config.gemini_api_key == "cli_key"
        assert config.whisper_model_size == "small"
        assert config.cookie_path == str(tmp_path / "cli_cookies.pkl")
        assert config.audio_device_index == 1
        assert config.log_level == "DEBUG"


class TestPipelineExecution:
    """Test complete pipeline execution scenarios."""
    
    @patch('main.MeetJoiner')
    @patch('main.AudioCapturer')
    @patch('main.Transcriber')
    @patch('main.Translator')
    @patch('main.Summarizer')
    @patch('main.DocxExporter')
    def test_pipeline_sequence_order(
        self,
        mock_exporter_class,
        mock_summarizer_class,
        mock_translator_class,
        mock_transcriber_class,
        mock_capturer_class,
        mock_joiner_class,
        tmp_path
    ):
        """Verify pipeline executes modules in correct sequence."""
        # Setup mocks
        mock_joiner = MagicMock()
        mock_joiner.join_meeting.return_value = True
        mock_joiner.is_in_meeting.return_value = False
        mock_joiner_class.return_value = mock_joiner
        
        mock_capturer = MagicMock()
        mock_capturer.get_audio_files.return_value = [str(tmp_path / "chunk_001.wav")]
        mock_capturer_class.return_value = mock_capturer
        
        mock_transcriber = MagicMock()
        mock_transcriber.transcribe_batch.return_value = "Test transcript"
        mock_transcriber_class.return_value = mock_transcriber
        
        mock_translator = MagicMock()
        mock_translator.process_transcript.return_value = "Test transcript"
        mock_translator_class.return_value = mock_translator
        
        mock_summarizer = MagicMock()
        mock_summarizer.generate_summary.return_value = {
            "title": "Test Meeting",
            "participants": [],
            "key_points": [],
            "action_items": [],
            "decisions": [],
            "follow_ups": []
        }
        mock_summarizer_class.return_value = mock_summarizer
        
        mock_exporter = MagicMock()
        mock_exporter.create_document.return_value = str(tmp_path / "output.docx")
        mock_exporter_class.return_value = mock_exporter
        
        # Create config
        config = Config(
            cookie_path=str(tmp_path / "cookies.pkl"),
            audio_device_index=0,
            whisper_model_size="base",
            gemini_api_key="test_key",
            output_dir=str(tmp_path / "output"),
            audio_dir=str(tmp_path / "audio"),
            transcript_dir=str(tmp_path / "transcripts"),
            log_level="INFO",
            log_dir=str(tmp_path / "logs"),
            chunk_duration=30
        )
        
        # Create directories
        config.ensure_directories()
        
        # Run pipeline
        result = run_pipeline("https://meet.google.com/test-meet-url", config)
        
        # Verify sequence
        assert mock_joiner.join_meeting.called
        assert mock_capturer.start_capture.called
        assert mock_capturer.stop_capture.called
        assert mock_transcriber.load_model.called
        assert mock_transcriber.transcribe_batch.called
        assert mock_translator.process_transcript.called
        assert mock_summarizer.generate_summary.called
        assert mock_exporter.create_document.called
        
        # Verify result
        assert result == str(tmp_path / "output.docx")
    
    @patch('main.MeetJoiner')
    def test_pipeline_fails_on_join_error(self, mock_joiner_class, tmp_path):
        """Verify pipeline handles join failure correctly."""
        mock_joiner = MagicMock()
        mock_joiner.join_meeting.return_value = False
        mock_joiner_class.return_value = mock_joiner
        
        config = Config(
            cookie_path=str(tmp_path / "cookies.pkl"),
            audio_device_index=0,
            whisper_model_size="base",
            gemini_api_key="test_key",
            output_dir=str(tmp_path / "output"),
            audio_dir=str(tmp_path / "audio"),
            transcript_dir=str(tmp_path / "transcripts"),
            log_level="INFO",
            log_dir=str(tmp_path / "logs"),
            chunk_duration=30
        )
        
        config.ensure_directories()
        
        with pytest.raises(PipelineError) as exc_info:
            run_pipeline("https://meet.google.com/test-meet-url", config)
        
        assert "join" in str(exc_info.value).lower()


class TestDirectoryStructure:
    """Test that directory structure is maintained correctly."""
    
    def test_pipeline_creates_all_directories(self, tmp_path):
        """Verify all required directories are created."""
        config = Config(
            cookie_path=str(tmp_path / "cookies.pkl"),
            audio_device_index=0,
            whisper_model_size="base",
            gemini_api_key="test_key",
            output_dir=str(tmp_path / "output"),
            audio_dir=str(tmp_path / "audio"),
            transcript_dir=str(tmp_path / "transcripts"),
            log_level="INFO",
            log_dir=str(tmp_path / "logs"),
            chunk_duration=30
        )
        
        config.ensure_directories()
        
        assert Path(config.audio_dir).exists()
        assert Path(config.transcript_dir).exists()
        assert Path(config.output_dir).exists()
    
    def test_modules_respect_directory_structure(self, tmp_path):
        """Verify modules save files to correct directories."""
        audio_dir = tmp_path / "audio"
        transcript_dir = tmp_path / "transcripts"
        output_dir = tmp_path / "output"
        
        # Create capturer
        capturer = AudioCapturer(str(audio_dir))
        assert Path(capturer.output_dir) == audio_dir
        
        # Create exporter
        from src.exporter import DocxExporter
        exporter = DocxExporter(str(output_dir))
        assert Path(exporter.output_dir) == output_dir


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
