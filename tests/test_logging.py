"""
Unit tests for logging system configuration.
Tests logging setup, multi-level logging, and error-specific log files.
"""

import logging
import pytest
from pathlib import Path
import tempfile
import shutil
from src.config import Config, setup_logging


class TestLoggingSystem:
    """Test suite for logging system configuration."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
        # Create temporary directory for logs
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up after each test."""
        # Clear all handlers from root logger first
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)
        
        # Small delay to ensure file handles are released on Windows
        import time
        time.sleep(0.1)
        
        # Remove temporary directory
        if Path(self.temp_dir).exists():
            try:
                shutil.rmtree(self.temp_dir)
            except PermissionError:
                # On Windows, sometimes files are still locked
                # Try again after a short delay
                time.sleep(0.5)
                try:
                    shutil.rmtree(self.temp_dir)
                except PermissionError:
                    # If still fails, just pass - temp files will be cleaned up by OS
                    pass
    
    def test_logging_configuration_creates_log_files(self):
        """Test that logging configuration creates required log files."""
        # Create config with test log directory
        config = Config(
            cookie_path='./cookies.pkl',
            audio_device_index=None,
            audio_dir='./audio',
            chunk_duration=30,
            whisper_model_size='base',
            transcript_dir='./transcripts',
            gemini_api_key='test_key',
            output_dir='./output',
            log_level='INFO',
            log_dir=str(self.log_dir)
        )
        
        # Setup logging
        setup_logging(config)
        
        # Verify log files are created
        main_log = self.log_dir / 'meetdocs.log'
        error_log = self.log_dir / 'meetdocs_errors.log'
        
        # Log some messages to trigger file creation
        logger = logging.getLogger('test_logger')
        logger.info("Test info message")
        logger.error("Test error message")
        
        # Force flush
        for handler in logging.getLogger().handlers:
            handler.flush()
        
        assert main_log.exists(), "Main log file should be created"
        assert error_log.exists(), "Error log file should be created"
    
    def test_log_format_includes_required_fields(self):
        """Test that log format includes timestamp, level, module, and function."""
        config = Config(
            cookie_path='./cookies.pkl',
            audio_device_index=None,
            audio_dir='./audio',
            chunk_duration=30,
            whisper_model_size='base',
            transcript_dir='./transcripts',
            gemini_api_key='test_key',
            output_dir='./output',
            log_level='DEBUG',
            log_dir=str(self.log_dir)
        )
        
        setup_logging(config)
        
        # Log a test message
        logger = logging.getLogger('test_module')
        logger.info("Test message for format validation")
        
        # Force flush and close handlers
        for handler in logging.getLogger().handlers:
            handler.flush()
            handler.close()
        
        # Read log file
        main_log = self.log_dir / 'meetdocs.log'
        with open(main_log, 'r') as f:
            log_content = f.read()
        
        # Verify format contains required fields
        assert '[INFO]' in log_content, "Log should contain level"
        # The module name in the log is from the file that called the logger (test_logging)
        assert '[test_logging]' in log_content, "Log should contain module name"
        assert '[test_log_format_includes_required_fields]' in log_content, "Log should contain function name"
        assert 'Test message for format validation' in log_content, "Log should contain message"
        # Timestamp format: [YYYY-MM-DD HH:MM:SS]
        assert log_content.count('[') >= 3, "Log should contain timestamp, level, and module in brackets"
    
    def test_error_log_contains_only_errors(self):
        """Test that error log file contains only ERROR and above messages."""
        config = Config(
            cookie_path='./cookies.pkl',
            audio_device_index=None,
            audio_dir='./audio',
            chunk_duration=30,
            whisper_model_size='base',
            transcript_dir='./transcripts',
            gemini_api_key='test_key',
            output_dir='./output',
            log_level='DEBUG',
            log_dir=str(self.log_dir)
        )
        
        setup_logging(config)
        
        # Log messages at different levels
        logger = logging.getLogger('test_error_logger')
        logger.debug("Debug message - should not be in error log")
        logger.info("Info message - should not be in error log")
        logger.warning("Warning message - should not be in error log")
        logger.error("Error message - should be in error log")
        logger.critical("Critical message - should be in error log")
        
        # Force flush
        for handler in logging.getLogger().handlers:
            handler.flush()
        
        # Read error log file
        error_log = self.log_dir / 'meetdocs_errors.log'
        with open(error_log, 'r') as f:
            error_content = f.read()
        
        # Verify only errors are in error log
        assert "Error message - should be in error log" in error_content
        assert "Critical message - should be in error log" in error_content
        assert "Debug message" not in error_content
        assert "Info message" not in error_content
        assert "Warning message" not in error_content
    
    def test_main_log_contains_all_levels(self):
        """Test that main log file contains all log levels."""
        config = Config(
            cookie_path='./cookies.pkl',
            audio_device_index=None,
            audio_dir='./audio',
            chunk_duration=30,
            whisper_model_size='base',
            transcript_dir='./transcripts',
            gemini_api_key='test_key',
            output_dir='./output',
            log_level='DEBUG',
            log_dir=str(self.log_dir)
        )
        
        setup_logging(config)
        
        # Log messages at different levels
        logger = logging.getLogger('test_all_levels')
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # Force flush
        for handler in logging.getLogger().handlers:
            handler.flush()
        
        # Read main log file
        main_log = self.log_dir / 'meetdocs.log'
        with open(main_log, 'r') as f:
            main_content = f.read()
        
        # Verify all levels are in main log
        assert "Debug message" in main_content
        assert "Info message" in main_content
        assert "Warning message" in main_content
        assert "Error message" in main_content
    
    def test_log_directory_created_if_not_exists(self):
        """Test that log directory is created if it doesn't exist."""
        # Use a non-existent directory
        new_log_dir = Path(self.temp_dir) / 'new_logs' / 'nested'
        
        assert not new_log_dir.exists(), "Directory should not exist initially"
        
        config = Config(
            cookie_path='./cookies.pkl',
            audio_device_index=None,
            audio_dir='./audio',
            chunk_duration=30,
            whisper_model_size='base',
            transcript_dir='./transcripts',
            gemini_api_key='test_key',
            output_dir='./output',
            log_level='INFO',
            log_dir=str(new_log_dir)
        )
        
        # Setup logging should create the directory
        setup_logging(config)
        
        assert new_log_dir.exists(), "Log directory should be created"
    
    def test_logging_respects_log_level_setting(self):
        """Test that logging respects the configured log level."""
        config = Config(
            cookie_path='./cookies.pkl',
            audio_device_index=None,
            audio_dir='./audio',
            chunk_duration=30,
            whisper_model_size='base',
            transcript_dir='./transcripts',
            gemini_api_key='test_key',
            output_dir='./output',
            log_level='WARNING',  # Set to WARNING
            log_dir=str(self.log_dir)
        )
        
        setup_logging(config)
        
        # Log messages at different levels
        logger = logging.getLogger('test_level')
        logger.debug("Debug message - should not appear")
        logger.info("Info message - should not appear")
        logger.warning("Warning message - should appear")
        logger.error("Error message - should appear")
        
        # Force flush
        for handler in logging.getLogger().handlers:
            handler.flush()
        
        # Read main log file
        main_log = self.log_dir / 'meetdocs.log'
        with open(main_log, 'r') as f:
            main_content = f.read()
        
        # Verify only WARNING and above are logged
        assert "Debug message" not in main_content
        assert "Info message" not in main_content
        assert "Warning message" in main_content
        assert "Error message" in main_content
