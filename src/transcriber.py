"""
Transcriber module for MeetDocs AI automation system.
Converts audio files to text using OpenAI Whisper with multilingual support.
"""

import logging
import os
from pathlib import Path
from typing import List, Dict, Optional

# Import whisper with error handling for environments where it's not available
try:
    import whisper
    WHISPER_AVAILABLE = True
except (ImportError, TypeError) as e:
    # TypeError can occur on Windows with certain configurations
    whisper = None
    WHISPER_AVAILABLE = False


logger = logging.getLogger(__name__)


class Transcriber:
    """
    Handles speech-to-text conversion using OpenAI Whisper.
    
    Supports multilingual transcription (Hindi, Marathi, English) with
    automatic language detection and chronological transcript assembly.
    """
    
    def __init__(self, model_size: str = "base", output_file: str = "transcript.txt"):
        """
        Initialize the Transcriber.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            output_file: Path to consolidated transcript file
        """
        self.model_size = model_size
        self.output_file = Path(output_file)
        self.model = None
        self._transcript_chunks: List[Dict] = []
        
        logger.info(f"Transcriber initialized with model size: {model_size}")
    
    def load_model(self) -> bool:
        """
        Load Whisper model into memory.
        
        Returns:
            bool: True if model loaded successfully, False otherwise
            
        Raises:
            RuntimeError: If Whisper model fails to load
        """
        if not WHISPER_AVAILABLE or whisper is None:
            error_msg = (
                "Whisper is not available in this environment.\n"
                "Please ensure Whisper is installed correctly:\n"
                "  pip install openai-whisper\n"
                "For GPU support, also install:\n"
                "  pip install torch torchvision torchaudio\n"
                "Note: On Windows, you may need to install Visual C++ redistributables."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            logger.info("Whisper model loaded successfully")
            return True
            
        except Exception as e:
            error_msg = (
                f"Failed to load Whisper model '{self.model_size}': {str(e)}\n"
                "Please ensure Whisper is installed correctly:\n"
                "  pip install openai-whisper\n"
                "For GPU support, also install:\n"
                "  pip install torch torchvision torchaudio\n"
                "If the model is not found, it will be downloaded automatically on first use."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def transcribe_file(self, audio_path: str) -> Dict:
        """
        Transcribe a single audio file.
        
        Args:
            audio_path: Path to audio file (WAV format)
            
        Returns:
            dict: Transcription result containing:
                - text: Transcribed text
                - language: Detected language code
                - segments: Detailed segment information
                
        Raises:
            RuntimeError: If model not loaded
            FileNotFoundError: If audio file doesn't exist
            Exception: If transcription fails
        """
        if self.model is None:
            raise RuntimeError("Whisper model not loaded. Call load_model() first.")
        
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            logger.info(f"Transcribing file: {audio_path.name}")
            
            # Transcribe with language detection
            # task='transcribe' means we want transcription in original language
            # (not translation to English)
            result = self.model.transcribe(
                str(audio_path),
                task='transcribe',
                language=None,  # Auto-detect language
                verbose=False
            )
            
            detected_language = result.get('language', 'unknown')
            text = result.get('text', '').strip()
            
            logger.info(
                f"Transcription complete: {audio_path.name} "
                f"(language: {detected_language}, length: {len(text)} chars)"
            )
            
            return {
                'text': text,
                'language': detected_language,
                'segments': result.get('segments', []),
                'file': str(audio_path)
            }
            
        except Exception as e:
            logger.error(f"Transcription failed for {audio_path}: {str(e)}")
            raise
    
    def transcribe_batch(self, audio_files: List[str]) -> str:
        """
        Process multiple audio files and return consolidated transcript.
        
        Args:
            audio_files: List of paths to audio files
            
        Returns:
            str: Complete consolidated transcript
            
        Raises:
            RuntimeError: If model not loaded
        """
        if self.model is None:
            raise RuntimeError("Whisper model not loaded. Call load_model() first.")
        
        if not audio_files:
            logger.warning("No audio files provided for batch transcription")
            return ""
        
        logger.info(f"Starting batch transcription of {len(audio_files)} files")
        
        # Clear previous chunks
        self._transcript_chunks = []
        
        # Process each file
        for idx, audio_file in enumerate(audio_files, 1):
            try:
                logger.info(f"Processing file {idx}/{len(audio_files)}: {Path(audio_file).name}")
                
                result = self.transcribe_file(audio_file)
                
                # Extract chunk number from filename (e.g., "chunk_001.wav" -> 1)
                chunk_number = self._extract_chunk_number(audio_file)
                
                self._transcript_chunks.append({
                    'chunk_number': chunk_number,
                    'text': result['text'],
                    'language': result['language'],
                    'file': audio_file
                })
                
            except Exception as e:
                logger.error(f"Failed to transcribe {audio_file}: {str(e)}")
                # Continue with remaining files
                continue
        
        # Assemble chronological transcript
        full_transcript = self._assemble_transcript()
        
        # Save to file
        self.save_transcript(full_transcript)
        
        logger.info(f"Batch transcription complete: {len(self._transcript_chunks)} files processed")
        
        return full_transcript
    
    def _extract_chunk_number(self, audio_path: str) -> int:
        """
        Extract chunk number from audio filename.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            int: Chunk number (defaults to 0 if not found)
        """
        try:
            filename = Path(audio_path).stem
            # Try to extract number from filename like "chunk_001" or "audio_001"
            parts = filename.split('_')
            for part in reversed(parts):
                if part.isdigit():
                    return int(part)
            return 0
        except Exception:
            return 0
    
    def _assemble_transcript(self) -> str:
        """
        Assemble transcript chunks in chronological order.
        
        Returns:
            str: Consolidated transcript with chunks in order
        """
        if not self._transcript_chunks:
            return ""
        
        # Sort by chunk number to ensure chronological order
        sorted_chunks = sorted(self._transcript_chunks, key=lambda x: x['chunk_number'])
        
        # Combine text from all chunks
        transcript_lines = []
        for chunk in sorted_chunks:
            if chunk['text']:
                transcript_lines.append(
                    f"[Chunk {chunk['chunk_number']:03d}] [{chunk['language']}]\n"
                    f"{chunk['text']}\n"
                )
        
        return "\n".join(transcript_lines)
    
    def save_transcript(self, text: str) -> None:
        """
        Append transcript text to consolidated transcript file.
        
        Args:
            text: Transcript text to save
        """
        try:
            # Ensure parent directory exists
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Append to file (or create if doesn't exist)
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(text)
                if not text.endswith('\n'):
                    f.write('\n')
            
            logger.info(f"Transcript saved to: {self.output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save transcript: {str(e)}")
            raise
    
    def get_full_transcript(self) -> str:
        """
        Return the complete transcript from file.
        
        Returns:
            str: Complete transcript content, or empty string if file doesn't exist
        """
        try:
            if self.output_file.exists():
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning(f"Transcript file not found: {self.output_file}")
                return ""
                
        except Exception as e:
            logger.error(f"Failed to read transcript: {str(e)}")
            return ""
    
    def get_transcript_chunks(self) -> List[Dict]:
        """
        Get list of processed transcript chunks.
        
        Returns:
            list: List of transcript chunk dictionaries
        """
        return self._transcript_chunks.copy()
