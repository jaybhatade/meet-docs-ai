"""
Unit tests for the Transcriber module.

Tests core functionality including model loading, file transcription,
batch processing, and transcript assembly.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Mock whisper module before importing transcriber
sys.modules['whisper'] = MagicMock()

from transcriber import Transcriber


class TestTranscriberInitialization:
    """Test Transcriber initialization."""
    
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        transcriber = Transcriber()
        assert transcriber.model_size == "base"
        assert transcriber.output_file == Path("transcript.txt")
        assert transcriber.model is None
        assert transcriber._transcript_chunks == []
    
    def test_init_with_custom_params(self):
        """Test initialization with custom parameters."""
        transcriber = Transcriber(model_size="small", output_file="custom.txt")
        assert transcriber.model_size == "small"
        assert transcriber.output_file == Path("custom.txt")


class TestModelLoading:
    """Test Whisper model loading."""
    
    @patch('transcriber.WHISPER_AVAILABLE', True)
    @patch('transcriber.whisper')
    def test_load_model_success(self, mock_whisper):
        """Test successful model loading."""
        mock_model = Mock()
        mock_whisper.load_model.return_value = mock_model
        
        transcriber = Transcriber(model_size="base")
        result = transcriber.load_model()
        
        assert result is True
        assert transcriber.model == mock_model
        mock_whisper.load_model.assert_called_once_with("base")
    
    @patch('transcriber.WHISPER_AVAILABLE', True)
    @patch('transcriber.whisper')
    def test_load_model_failure(self, mock_whisper):
        """Test model loading failure with proper error message."""
        mock_whisper.load_model.side_effect = Exception("Model not found")
        
        transcriber = Transcriber(model_size="base")
        
        with pytest.raises(RuntimeError) as exc_info:
            transcriber.load_model()
        
        error_msg = str(exc_info.value)
        assert "Failed to load Whisper model" in error_msg
        assert "pip install openai-whisper" in error_msg
    
    @patch('transcriber.WHISPER_AVAILABLE', False)
    @patch('transcriber.whisper', None)
    def test_load_model_whisper_not_available(self):
        """Test model loading when Whisper is not available."""
        transcriber = Transcriber(model_size="base")
        
        with pytest.raises(RuntimeError) as exc_info:
            transcriber.load_model()
        
        error_msg = str(exc_info.value)
        assert "Whisper is not available" in error_msg
        assert "pip install openai-whisper" in error_msg


class TestSingleFileTranscription:
    """Test single file transcription."""
    
    def test_transcribe_file_without_model(self):
        """Test transcription fails if model not loaded."""
        transcriber = Transcriber()
        
        with pytest.raises(RuntimeError) as exc_info:
            transcriber.transcribe_file("test.wav")
        
        assert "model not loaded" in str(exc_info.value).lower()
    
    def test_transcribe_file_not_found(self):
        """Test transcription fails for non-existent file."""
        transcriber = Transcriber()
        transcriber.model = Mock()  # Fake model
        
        with pytest.raises(FileNotFoundError):
            transcriber.transcribe_file("nonexistent.wav")
    
    @patch('transcriber.WHISPER_AVAILABLE', True)
    @patch('transcriber.whisper')
    def test_transcribe_file_success(self, mock_whisper):
        """Test successful file transcription."""
        # Setup mock model
        mock_model = Mock()
        mock_model.transcribe.return_value = {
            'text': 'This is a test transcription',
            'language': 'en',
            'segments': []
        }
        mock_whisper.load_model.return_value = mock_model
        
        # Create temporary audio file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            transcriber = Transcriber()
            transcriber.load_model()
            
            result = transcriber.transcribe_file(tmp_path)
            
            assert result['text'] == 'This is a test transcription'
            assert result['language'] == 'en'
            assert 'segments' in result
            assert 'file' in result
            
        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestBatchTranscription:
    """Test batch transcription processing."""
    
    def test_batch_without_model(self):
        """Test batch transcription fails if model not loaded."""
        transcriber = Transcriber()
        
        with pytest.raises(RuntimeError) as exc_info:
            transcriber.transcribe_batch(["test.wav"])
        
        assert "model not loaded" in str(exc_info.value).lower()
    
    def test_batch_empty_list(self):
        """Test batch transcription with empty file list."""
        transcriber = Transcriber()
        transcriber.model = Mock()
        
        result = transcriber.transcribe_batch([])
        
        assert result == ""
    
    @patch('transcriber.WHISPER_AVAILABLE', True)
    @patch('transcriber.whisper')
    def test_batch_transcription_success(self, mock_whisper):
        """Test successful batch transcription."""
        # Setup mock model
        mock_model = Mock()
        mock_model.transcribe.side_effect = [
            {'text': 'First chunk', 'language': 'en', 'segments': []},
            {'text': 'Second chunk', 'language': 'en', 'segments': []},
        ]
        mock_whisper.load_model.return_value = mock_model
        
        # Create temporary directory and files
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create test audio files
            file1 = tmpdir_path / "chunk_001.wav"
            file2 = tmpdir_path / "chunk_002.wav"
            file1.touch()
            file2.touch()
            
            # Create transcriber with temp output
            output_file = tmpdir_path / "transcript.txt"
            transcriber = Transcriber(output_file=str(output_file))
            transcriber.load_model()
            
            # Transcribe batch
            result = transcriber.transcribe_batch([str(file1), str(file2)])
            
            # Verify result
            assert "First chunk" in result
            assert "Second chunk" in result
            assert len(transcriber._transcript_chunks) == 2
            
            # Verify chunks are in order
            chunks = transcriber.get_transcript_chunks()
            assert chunks[0]['chunk_number'] == 1
            assert chunks[1]['chunk_number'] == 2


class TestChunkNumberExtraction:
    """Test chunk number extraction from filenames."""
    
    def test_extract_chunk_number_standard(self):
        """Test extraction from standard filename format."""
        transcriber = Transcriber()
        
        assert transcriber._extract_chunk_number("chunk_001.wav") == 1
        assert transcriber._extract_chunk_number("chunk_042.wav") == 42
        assert transcriber._extract_chunk_number("audio_123.wav") == 123
    
    def test_extract_chunk_number_no_number(self):
        """Test extraction when no number in filename."""
        transcriber = Transcriber()
        
        assert transcriber._extract_chunk_number("audio.wav") == 0
        assert transcriber._extract_chunk_number("test.wav") == 0


class TestTranscriptAssembly:
    """Test chronological transcript assembly."""
    
    def test_assemble_empty_chunks(self):
        """Test assembly with no chunks."""
        transcriber = Transcriber()
        result = transcriber._assemble_transcript()
        assert result == ""
    
    def test_assemble_chronological_order(self):
        """Test chunks are assembled in chronological order."""
        transcriber = Transcriber()
        
        # Add chunks out of order
        transcriber._transcript_chunks = [
            {'chunk_number': 3, 'text': 'Third', 'language': 'en', 'file': 'c3.wav'},
            {'chunk_number': 1, 'text': 'First', 'language': 'en', 'file': 'c1.wav'},
            {'chunk_number': 2, 'text': 'Second', 'language': 'en', 'file': 'c2.wav'},
        ]
        
        result = transcriber._assemble_transcript()
        
        # Verify order
        assert result.index('First') < result.index('Second')
        assert result.index('Second') < result.index('Third')
        assert '[Chunk 001]' in result
        assert '[Chunk 002]' in result
        assert '[Chunk 003]' in result


class TestTranscriptFileOperations:
    """Test transcript file saving and retrieval."""
    
    def test_save_transcript(self):
        """Test saving transcript to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "test_transcript.txt"
            transcriber = Transcriber(output_file=str(output_file))
            
            transcriber.save_transcript("Test content")
            
            assert output_file.exists()
            content = output_file.read_text(encoding='utf-8')
            assert "Test content" in content
    
    def test_save_transcript_creates_directory(self):
        """Test that save_transcript creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "subdir" / "transcript.txt"
            transcriber = Transcriber(output_file=str(output_file))
            
            transcriber.save_transcript("Test content")
            
            assert output_file.exists()
            assert output_file.parent.exists()
    
    def test_get_full_transcript_exists(self):
        """Test retrieving existing transcript."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "transcript.txt"
            output_file.write_text("Existing content", encoding='utf-8')
            
            transcriber = Transcriber(output_file=str(output_file))
            result = transcriber.get_full_transcript()
            
            assert result == "Existing content"
    
    def test_get_full_transcript_not_exists(self):
        """Test retrieving non-existent transcript returns empty string."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "nonexistent.txt"
            transcriber = Transcriber(output_file=str(output_file))
            
            result = transcriber.get_full_transcript()
            
            assert result == ""


class TestGetTranscriptChunks:
    """Test getting transcript chunks."""
    
    def test_get_transcript_chunks_empty(self):
        """Test getting chunks when none exist."""
        transcriber = Transcriber()
        chunks = transcriber.get_transcript_chunks()
        assert chunks == []
    
    def test_get_transcript_chunks_returns_copy(self):
        """Test that get_transcript_chunks returns a copy."""
        transcriber = Transcriber()
        transcriber._transcript_chunks = [
            {'chunk_number': 1, 'text': 'Test', 'language': 'en', 'file': 'test.wav'}
        ]
        
        chunks = transcriber.get_transcript_chunks()
        chunks.append({'chunk_number': 2, 'text': 'New', 'language': 'en', 'file': 'new.wav'})
        
        # Original should not be modified
        assert len(transcriber._transcript_chunks) == 1
