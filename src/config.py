"""
Configuration management for MeetDocs AI automation system.
Centralizes all configuration settings and environment variables.
"""

import os
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    """Central configuration for MeetDocs AI system."""
    
    # Authentication
    cookie_path: str
    
    # Audio settings
    audio_device_index: Optional[int]
    audio_dir: str
    chunk_duration: int
    
    # Transcription settings
    whisper_model_size: str
    transcript_dir: str
    
    # Translation settings
    # (googletrans doesn't require API key)
    
    # Summarization settings
    gemini_api_key: str
    
    # Export settings
    output_dir: str
    
    # Logging settings
    log_level: str
    log_dir: str
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        return cls(
            cookie_path=os.getenv('COOKIE_PATH', './cookies.pkl'),
            audio_device_index=cls._get_int_env('AUDIO_DEVICE_INDEX'),
            audio_dir=os.getenv('AUDIO_DIR', './audio'),
            chunk_duration=int(os.getenv('CHUNK_DURATION', '30')),
            whisper_model_size=os.getenv('WHISPER_MODEL_SIZE', 'base'),
            transcript_dir=os.getenv('TRANSCRIPT_DIR', './transcripts'),
            gemini_api_key=os.getenv('GEMINI_API_KEY', ''),
            output_dir=os.getenv('OUTPUT_DIR', './output'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            log_dir=os.getenv('LOG_DIR', './logs')
        )
    
    @staticmethod
    def _get_int_env(key: str) -> Optional[int]:
        """Get integer environment variable, return None if not set."""
        value = os.getenv(key)
        return int(value) if value else None
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not self.gemini_api_key:
            errors.append("GEMINI_API_KEY is required")
        
        if not Path(self.cookie_path).exists():
            errors.append(f"Cookie file not found: {self.cookie_path}")
        
        if self.whisper_model_size not in ['tiny', 'base', 'small', 'medium', 'large']:
            errors.append(f"Invalid Whisper model size: {self.whisper_model_size}")
        
        return errors
    
    def ensure_directories(self):
        """Create all required directories if they don't exist."""
        directories = [
            self.audio_dir,
            self.transcript_dir,
            self.output_dir,
            self.log_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)


def setup_logging(config: Config):
    """Configure logging for the application."""
    log_format = '[%(asctime)s] [%(levelname)s] [%(module)s] [%(funcName)s] - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Ensure log directory exists
    Path(config.log_dir).mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.log_level.upper()))
    
    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (DEBUG and above)
    file_handler = logging.FileHandler(
        Path(config.log_dir) / 'meetdocs.log',
        mode='a',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler (ERROR and above)
    error_handler = logging.FileHandler(
        Path(config.log_dir) / 'meetdocs_errors.log',
        mode='a',
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    logging.info("Logging configured successfully")
