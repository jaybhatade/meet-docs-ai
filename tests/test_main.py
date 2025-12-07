"""
Tests for main orchestrator module.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path to import main
sys.path.insert(0, str(Path(__file__).parent.parent))

import main
from src.config import Config


class TestURLValidation:
    """Test URL validation functionality."""
    
    def test_valid_meet_url(self):
        """Test that valid Google Meet URLs are accepted."""
        valid_urls = [
            "https://meet.google.com/abc-defg-hij",
            "http://meet.google.com/xyz-1234-abc",
            "https://meet.google.co.in/test-meet-url"
        ]
        
        for url in valid_urls:
            assert main.validate_meet_url(url) is True
    
    def test_invalid_meet_url_domain(self):
        """Test that non-Google Meet URLs are rejected."""
        invalid_urls = [
            "https://zoom.us/j/123456789",
            "https://teams.microsoft.com/meeting",
            "https://example.com/meet"
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError):
                main.validate_meet_url(url)
    
    def test_invalid_meet_url_format(self):
        """Test that malformed URLs are rejected."""
        invalid_urls = [
            "not-a-url",
            "meet.google.com/abc",  # Missing scheme
            "https://meet.google.com",  # Missing path
            "ftp://meet.google.com/abc"  # Wrong scheme
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError):
                main.validate_meet_url(url)


class TestConfigurationLoading:
    """Test configuration loading functionality."""
    
    def test_load_configuration_from_env(self):
        """Test loading configuration from environment variables."""
        args = Mock()
        args.cookie_path = None
        args.audio_device = None
        args.model_size = None
        args.gemini_key = "test-api-key"
        args.output_dir = None
        args.log_level = None
        
        with patch.dict('os.environ', {
            'GEMINI_API_KEY': 'test-api-key',
            'COOKIE_PATH': './test_cookies.pkl'
        }):
            with patch('pathlib.Path.exists', return_value=True):
                config = main.load_configuration(args)
                
                assert config.gemini_api_key == 'test-api-key'
                assert config.cookie_path == './test_cookies.pkl'
    
    def test_load_configuration_cli_override(self):
        """Test that CLI arguments override environment variables."""
        args = Mock()
        args.cookie_path = './cli_cookies.pkl'
        args.audio_device = 5
        args.model_size = 'small'
        args.gemini_key = 'cli-api-key'
        args.output_dir = './cli_output'
        args.log_level = 'DEBUG'
        
        with patch.dict('os.environ', {
            'GEMINI_API_KEY': 'env-api-key',
            'COOKIE_PATH': './env_cookies.pkl'
        }):
            with patch('pathlib.Path.exists', return_value=True):
                config = main.load_configuration(args)
                
                assert config.cookie_path == './cli_cookies.pkl'
                assert config.audio_device_index == 5
                assert config.whisper_model_size == 'small'
                assert config.gemini_api_key == 'cli-api-key'
                assert config.output_dir == './cli_output'
                assert config.log_level == 'DEBUG'
    
    def test_load_configuration_validation_error(self):
        """Test that invalid configuration raises ValueError."""
        args = Mock()
        args.cookie_path = './nonexistent.pkl'
        args.audio_device = None
        args.model_size = None
        args.gemini_key = None  # Missing required API key
        args.output_dir = None
        args.log_level = None
        
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError):
                main.load_configuration(args)


class TestCleanup:
    """Test cleanup functionality."""
    
    def test_cleanup_with_active_resources(self):
        """Test cleanup stops capture and closes browser."""
        mock_joiner = Mock()
        mock_capturer = Mock()
        mock_capturer.is_capturing = True
        
        main.cleanup(mock_joiner, mock_capturer)
        
        mock_capturer.stop_capture.assert_called_once()
        mock_joiner.close.assert_called_once()
    
    def test_cleanup_with_none_resources(self):
        """Test cleanup handles None resources gracefully."""
        # Should not raise any exceptions
        main.cleanup(None, None)
    
    def test_cleanup_with_inactive_capturer(self):
        """Test cleanup with inactive capturer."""
        mock_joiner = Mock()
        mock_capturer = Mock()
        mock_capturer.is_capturing = False
        
        main.cleanup(mock_joiner, mock_capturer)
        
        # Should not call stop_capture if not capturing
        mock_capturer.stop_capture.assert_not_called()
        mock_joiner.close.assert_called_once()
    
    def test_cleanup_handles_exceptions(self):
        """Test cleanup continues even if errors occur."""
        mock_joiner = Mock()
        mock_joiner.close.side_effect = Exception("Close error")
        
        mock_capturer = Mock()
        mock_capturer.is_capturing = True
        mock_capturer.stop_capture.side_effect = Exception("Stop error")
        
        # Should not raise exceptions
        main.cleanup(mock_joiner, mock_capturer)


class TestArgumentParsing:
    """Test command-line argument parsing."""
    
    def test_parse_required_argument(self):
        """Test parsing with only required argument."""
        test_args = ['main.py', 'https://meet.google.com/abc-defg-hij']
        
        with patch('sys.argv', test_args):
            args = main.parse_arguments()
            assert args.meet_url == 'https://meet.google.com/abc-defg-hij'
    
    def test_parse_optional_arguments(self):
        """Test parsing with optional arguments."""
        test_args = [
            'main.py',
            'https://meet.google.com/abc-defg-hij',
            '--audio-device', '1',
            '--model-size', 'small',
            '--log-level', 'DEBUG'
        ]
        
        with patch('sys.argv', test_args):
            args = main.parse_arguments()
            assert args.meet_url == 'https://meet.google.com/abc-defg-hij'
            assert args.audio_device == 1
            assert args.model_size == 'small'
            assert args.log_level == 'DEBUG'
    
    def test_parse_list_devices_flag(self):
        """Test parsing --list-devices flag."""
        test_args = ['main.py', '--list-devices']
        
        with patch('sys.argv', test_args):
            args = main.parse_arguments()
            assert args.list_devices is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
