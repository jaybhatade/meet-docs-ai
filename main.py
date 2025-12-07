#!/usr/bin/env python3
"""
MeetDocs AI - Main Orchestrator
Coordinates the complete pipeline for automated meeting documentation.
"""

import argparse
import logging
import os
import sys
import signal
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

# Import configuration and modules
from src.config import Config, setup_logging
from src.meet_joiner import MeetJoiner, MeetJoinerError
from src.audio_capture import AudioCapturer
from src.transcriber import Transcriber
from src.translator import Translator
from src.summarizer import Summarizer
from src.exporter import DocxExporter


logger = logging.getLogger(__name__)


class PipelineError(Exception):
    """Base exception for pipeline errors."""
    pass


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='MeetDocs AI - Automated meeting documentation system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py https://meet.google.com/abc-defg-hij
  python main.py https://meet.google.com/abc-defg-hij --audio-device 1
  python main.py https://meet.google.com/abc-defg-hij --model-size small

Environment Variables:
  GEMINI_API_KEY       Google Gemini API key (required)
  COOKIE_PATH          Path to cookies file (default: ./cookies.pkl)
  AUDIO_DEVICE_INDEX   Audio device index
  WHISPER_MODEL_SIZE   Whisper model size (default: base)
  OUTPUT_DIR           Output directory (default: ./output)
  LOG_LEVEL            Logging level (default: INFO)
        """
    )
    
    # Required arguments (unless --list-devices is used)
    parser.add_argument(
        'meet_url',
        type=str,
        nargs='?',  # Make optional
        help='Google Meet URL to join'
    )
    
    # Optional arguments
    parser.add_argument(
        '--cookie-path',
        type=str,
        default=None,
        help='Path to cookies file (default: from env or ./cookies.pkl)'
    )
    
    parser.add_argument(
        '--audio-device',
        type=int,
        default=None,
        help='Audio device index to capture from'
    )
    
    parser.add_argument(
        '--model-size',
        type=str,
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        default=None,
        help='Whisper model size (default: from env or base)'
    )
    
    parser.add_argument(
        '--gemini-key',
        type=str,
        default=None,
        help='Gemini API key (default: from env)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for documents (default: from env or ./output)'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default=None,
        help='Logging level (default: from env or INFO)'
    )
    
    parser.add_argument(
        '--list-devices',
        action='store_true',
        help='List available audio devices and exit'
    )
    
    return parser.parse_args()


def validate_meet_url(url: str) -> bool:
    """
    Validate Google Meet URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid Google Meet URL
        
    Raises:
        ValueError: If URL is invalid
    """
    try:
        parsed = urlparse(url)
        
        # Check if it's a Google Meet domain
        valid_domains = ['meet.google.com', 'meet.google.co.in']
        is_valid = (
            parsed.scheme in ['http', 'https'] and
            parsed.netloc in valid_domains and
            len(parsed.path) > 1
        )
        
        if not is_valid:
            raise ValueError(
                f"Invalid Google Meet URL: {url}\n"
                f"Expected format: https://meet.google.com/xxx-xxxx-xxx"
            )
        
        logger.info(f"URL validation successful: {url}")
        return True
        
    except Exception as e:
        logger.error(f"URL validation failed: {e}")
        raise ValueError(f"Invalid URL: {e}")


def load_configuration(args: argparse.Namespace) -> Config:
    """
    Load configuration from environment and command-line arguments.
    
    Command-line arguments override environment variables.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Configuration object
        
    Raises:
        ValueError: If configuration is invalid
    """
    logger.info("Loading configuration...")
    
    # Load base configuration from environment
    config = Config.from_env()
    
    # Override with command-line arguments if provided
    if args.cookie_path:
        config.cookie_path = args.cookie_path
    
    if args.audio_device is not None:
        config.audio_device_index = args.audio_device
    
    if args.model_size:
        config.whisper_model_size = args.model_size
    
    if args.gemini_key:
        config.gemini_api_key = args.gemini_key
    
    if args.output_dir:
        config.output_dir = args.output_dir
    
    if args.log_level:
        config.log_level = args.log_level
    
    # Validate configuration
    errors = config.validate()
    if errors:
        error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info("Configuration loaded successfully")
    return config


def run_pipeline(meet_url: str, config: Config) -> str:
    """
    Execute the complete MeetDocs pipeline.
    
    Pipeline stages:
    1. Join Google Meet session
    2. Capture audio in chunks
    3. Transcribe audio to text
    4. Translate to English
    5. Generate AI summary
    6. Export to DOCX
    
    Args:
        meet_url: Google Meet URL to join
        config: Configuration object
        
    Returns:
        Path to generated DOCX file
        
    Raises:
        PipelineError: If any stage fails critically
    """
    logger.info("=" * 80)
    logger.info("Starting MeetDocs AI Pipeline")
    logger.info("=" * 80)
    
    joiner = None
    capturer = None
    output_path = None
    
    try:
        # Ensure all directories exist
        config.ensure_directories()
        logger.info("Stage: Directory structure verified")
        
        # Stage 1: Join Meeting
        logger.info("=" * 80)
        logger.info("Stage 1: Joining Google Meet session")
        logger.info("=" * 80)
        
        joiner = MeetJoiner(config.cookie_path)
        if not joiner.join_meeting(meet_url):
            raise PipelineError("Failed to join meeting")
        
        logger.info("✓ Stage 1 complete: Successfully joined meeting")
        
        # Stage 2: Capture Audio
        logger.info("=" * 80)
        logger.info("Stage 2: Capturing audio")
        logger.info("=" * 80)
        
        capturer = AudioCapturer(config.audio_dir, config.chunk_duration)
        
        # List devices if no device specified
        if config.audio_device_index is None:
            logger.info("No audio device specified. Available devices:")
            devices = AudioCapturer.list_audio_devices()
            output_devices = [d for d in devices if d['is_output']]
            if output_devices:
                logger.info(f"Using default output device: {output_devices[0]['name']}")
        
        capturer.start_capture(config.audio_device_index)
        logger.info("✓ Stage 2 started: Audio capture in progress")
        
        # Wait for user to stop (Ctrl+C) or meeting to end
        logger.info("")
        logger.info("Recording in progress...")
        logger.info("Press Ctrl+C to stop recording and generate summary")
        logger.info("")
        
        # Keep the main thread alive while recording
        try:
            while joiner.is_in_meeting():
                import time
                time.sleep(5)
        except KeyboardInterrupt:
            logger.info("User requested stop")
        
        # Stop audio capture
        capturer.stop_capture()
        audio_files = capturer.get_audio_files()
        
        logger.info(f"✓ Stage 2 complete: Captured {len(audio_files)} audio chunks")
        
        # Leave meeting
        joiner.leave_meeting()
        joiner.close()
        joiner = None
        
        # Check if we have audio files
        if not audio_files:
            raise PipelineError("No audio files captured")
        
        # Stage 3: Transcribe Audio
        logger.info("=" * 80)
        logger.info("Stage 3: Transcribing audio")
        logger.info("=" * 80)
        
        transcript_file = Path(config.transcript_dir) / "meeting_transcript.txt"
        transcriber = Transcriber(config.whisper_model_size, str(transcript_file))
        
        transcriber.load_model()
        transcript = transcriber.transcribe_batch(audio_files)
        
        if not transcript or not transcript.strip():
            raise PipelineError("Transcription produced no text")
        
        logger.info(f"✓ Stage 3 complete: Transcription saved to {transcript_file}")
        
        # Stage 4: Translate to English
        logger.info("=" * 80)
        logger.info("Stage 4: Translating to English")
        logger.info("=" * 80)
        
        translator = Translator()
        english_transcript = translator.process_transcript(transcript)
        
        # Save translated transcript
        translated_file = Path(config.transcript_dir) / "meeting_transcript_english.txt"
        translated_file.parent.mkdir(parents=True, exist_ok=True)
        with open(translated_file, 'w', encoding='utf-8') as f:
            f.write(english_transcript)
        
        logger.info(f"✓ Stage 4 complete: Translation saved to {translated_file}")
        
        # Stage 5: Generate Summary
        logger.info("=" * 80)
        logger.info("Stage 5: Generating AI summary")
        logger.info("=" * 80)
        
        summarizer = Summarizer(config.gemini_api_key)
        summary = summarizer.generate_summary(english_transcript)
        
        logger.info("✓ Stage 5 complete: Summary generated")
        
        # Stage 6: Export to DOCX
        logger.info("=" * 80)
        logger.info("Stage 6: Exporting to DOCX")
        logger.info("=" * 80)
        
        exporter = DocxExporter(config.output_dir)
        output_path = exporter.create_document(summary)
        
        logger.info(f"✓ Stage 6 complete: Document exported to {output_path}")
        
        # Pipeline complete
        logger.info("=" * 80)
        logger.info("Pipeline completed successfully!")
        logger.info("=" * 80)
        
        return output_path
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        raise
    
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise PipelineError(f"Pipeline execution failed: {e}") from e
    
    finally:
        # Cleanup resources
        cleanup(joiner, capturer)


def cleanup(joiner: Optional[MeetJoiner], capturer: Optional[AudioCapturer]):
    """
    Clean up resources on exit.
    
    Ensures browser is closed and audio capture is stopped,
    even if errors occurred during pipeline execution.
    
    Args:
        joiner: MeetJoiner instance (may be None)
        capturer: AudioCapturer instance (may be None)
    """
    logger.info("Cleaning up resources...")
    
    try:
        if capturer and capturer.is_capturing:
            logger.info("Stopping audio capture...")
            capturer.stop_capture()
    except Exception as e:
        logger.error(f"Error stopping audio capture: {e}")
    
    try:
        if joiner:
            logger.info("Closing browser...")
            joiner.close()
    except Exception as e:
        logger.error(f"Error closing browser: {e}")
    
    logger.info("Cleanup complete")


def main():
    """Main entry point for MeetDocs AI."""
    # Parse arguments
    args = parse_arguments()
    
    # Handle --list-devices flag
    if args.list_devices:
        print("\nAvailable Audio Devices:")
        print("-" * 60)
        devices = AudioCapturer.list_audio_devices()
        for device in devices:
            if device['is_output']:
                print(f"[{device['index']}] {device['name']}")
                print(f"    Channels: {device['channels']}, Sample Rate: {device['sample_rate']}")
        print("-" * 60)
        return 0
    
    # Check if meet_url is provided
    if not args.meet_url:
        print("Error: meet_url is required", file=sys.stderr)
        print("Use --help for usage information", file=sys.stderr)
        return 1
    
    # Validate URL before loading configuration
    try:
        validate_meet_url(args.meet_url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    # Load configuration
    try:
        config = load_configuration(args)
    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        return 1
    
    # Setup logging
    setup_logging(config)
    
    logger.info("MeetDocs AI starting...")
    logger.info(f"Meet URL: {args.meet_url}")
    logger.info(f"Output directory: {config.output_dir}")
    
    # Run pipeline
    try:
        output_path = run_pipeline(args.meet_url, config)
        
        # Report success
        print("\n" + "=" * 80)
        print("SUCCESS!")
        print("=" * 80)
        print(f"\nMeeting documentation generated successfully!")
        print(f"Output file: {output_path}")
        print("\n" + "=" * 80)
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        print("\nOperation cancelled by user")
        return 130  # Standard exit code for Ctrl+C
    
    except PipelineError as e:
        logger.error(f"Pipeline error: {e}")
        print(f"\nError: {e}", file=sys.stderr)
        return 1
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
