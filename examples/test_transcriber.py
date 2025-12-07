"""
Example script to test the Transcriber module.

This script demonstrates how to use the Transcriber to:
1. Load the Whisper model
2. Transcribe individual audio files
3. Process multiple audio files in batch
4. Save and retrieve transcripts

Usage:
    python examples/test_transcriber.py
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from transcriber import Transcriber
from config import setup_logging, Config


def main():
    """Test the Transcriber module."""
    
    # Setup logging
    config = Config.from_env()
    setup_logging(config)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Transcriber test")
    
    # Initialize transcriber
    transcript_file = Path(config.transcript_dir) / "test_transcript.txt"
    transcriber = Transcriber(
        model_size=config.whisper_model_size,
        output_file=str(transcript_file)
    )
    
    try:
        # Load Whisper model
        logger.info("Loading Whisper model...")
        transcriber.load_model()
        logger.info("Model loaded successfully!")
        
        # Check for audio files
        audio_dir = Path(config.audio_dir)
        audio_files = sorted(audio_dir.glob("*.wav"))
        
        if not audio_files:
            logger.warning(f"No audio files found in {audio_dir}")
            logger.info("Please run the audio capture test first to generate audio files")
            return
        
        logger.info(f"Found {len(audio_files)} audio files")
        
        # Test single file transcription
        if audio_files:
            logger.info("\n=== Testing single file transcription ===")
            first_file = audio_files[0]
            result = transcriber.transcribe_file(str(first_file))
            
            logger.info(f"File: {first_file.name}")
            logger.info(f"Language: {result['language']}")
            logger.info(f"Text length: {len(result['text'])} characters")
            logger.info(f"Text preview: {result['text'][:200]}...")
        
        # Test batch transcription
        logger.info("\n=== Testing batch transcription ===")
        full_transcript = transcriber.transcribe_batch([str(f) for f in audio_files])
        
        logger.info(f"Batch transcription complete!")
        logger.info(f"Total transcript length: {len(full_transcript)} characters")
        logger.info(f"Transcript saved to: {transcript_file}")
        
        # Retrieve and display transcript
        logger.info("\n=== Retrieving saved transcript ===")
        saved_transcript = transcriber.get_full_transcript()
        logger.info(f"Retrieved transcript length: {len(saved_transcript)} characters")
        
        # Display chunk information
        chunks = transcriber.get_transcript_chunks()
        logger.info(f"\n=== Processed {len(chunks)} chunks ===")
        for chunk in chunks:
            logger.info(
                f"Chunk {chunk['chunk_number']:03d}: "
                f"{chunk['language']} - {len(chunk['text'])} chars"
            )
        
        logger.info("\n✓ Transcriber test completed successfully!")
        
    except RuntimeError as e:
        logger.error(f"Model loading failed: {e}")
        logger.info("\nTo install Whisper:")
        logger.info("  pip install openai-whisper")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
