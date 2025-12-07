"""
Unit tests for Audio Capture module.
"""

import pytest
import time
import numpy as np
from pathlib import Path
from src.audio_capture import AudioCapturer


class TestAudioCapturer:
    """Test suite for AudioCapturer class."""
    
    def test_initialization(self, tmp_path):
        """Test AudioCapturer initialization."""
        capturer = AudioCapturer(output_dir=str(tmp_path), chunk_duration=30)
        
        assert capturer.output_dir == tmp_path
        assert capturer.chunk_duration == 30
        assert capturer.sample_rate == 44100
        assert capturer.channels == 2
        assert not capturer.is_capturing
        assert capturer.chunk_number == 0
        assert len(capturer.audio_files) == 0
    
    def test_output_directory_creation(self, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        output_dir = tmp_path / "audio_output"
        assert not output_dir.exists()
        
        capturer = AudioCapturer(output_dir=str(output_dir))
        
        assert output_dir.exists()
        assert output_dir.is_dir()
    
    def test_list_audio_devices(self):
        """Test audio device listing."""
        devices = AudioCapturer.list_audio_devices()
        
        assert isinstance(devices, list)
        assert len(devices) > 0
        
        # Check device structure
        for device in devices:
            assert 'index' in device
            assert 'name' in device
            assert 'channels' in device
            assert 'sample_rate' in device
            assert 'is_output' in device
    
    def test_chunk_filename_generation(self, tmp_path):
        """Test sequential chunk filename generation."""
        capturer = AudioCapturer(output_dir=str(tmp_path))
        
        filename_0 = capturer._generate_chunk_filename(0)
        filename_1 = capturer._generate_chunk_filename(1)
        filename_99 = capturer._generate_chunk_filename(99)
        filename_1000 = capturer._generate_chunk_filename(1000)
        
        assert filename_0 == "audio_chunk_0000.wav"
        assert filename_1 == "audio_chunk_0001.wav"
        assert filename_99 == "audio_chunk_0099.wav"
        assert filename_1000 == "audio_chunk_1000.wav"
    
    def test_get_audio_files_empty(self, tmp_path):
        """Test getting audio files when none captured."""
        capturer = AudioCapturer(output_dir=str(tmp_path))
        
        files = capturer.get_audio_files()
        
        assert isinstance(files, list)
        assert len(files) == 0
    
    def test_get_chunk_count_initial(self, tmp_path):
        """Test chunk count is initially zero."""
        capturer = AudioCapturer(output_dir=str(tmp_path))
        
        count = capturer.get_chunk_count()
        
        assert count == 0
    
    def test_stop_capture_when_not_capturing(self, tmp_path):
        """Test stopping capture when not capturing doesn't raise error."""
        capturer = AudioCapturer(output_dir=str(tmp_path))
        
        # Should not raise exception
        capturer.stop_capture()
    
    def test_start_capture_sets_flags(self, tmp_path):
        """Test that start_capture sets appropriate flags."""
        capturer = AudioCapturer(output_dir=str(tmp_path))
        
        # Find a valid output device
        devices = AudioCapturer.list_audio_devices()
        output_device = next((d for d in devices if d['is_output']), None)
        
        if output_device:
            capturer.start_capture(device_index=output_device['index'])
            
            # Give it a moment to start
            time.sleep(0.2)
            
            assert capturer.is_capturing
            assert capturer.device_index == output_device['index']
            assert capturer.capture_thread is not None
            
            # Clean up
            capturer.stop_capture()
    
    def test_save_chunk_with_data(self, tmp_path):
        """Test saving audio chunk with data."""
        capturer = AudioCapturer(output_dir=str(tmp_path), chunk_duration=1)
        
        # Create fake audio data (1 second of silence)
        fake_audio = np.zeros((44100, 2), dtype=np.float32)
        capturer.current_chunk_data = [fake_audio]
        
        capturer._save_current_chunk()
        
        # Check file was created
        expected_file = tmp_path / "audio_chunk_0000.wav"
        assert expected_file.exists()
        assert capturer.chunk_number == 1
        assert len(capturer.audio_files) == 1
        assert capturer.audio_files[0] == str(expected_file)
    
    def test_finalize_partial_chunk(self, tmp_path):
        """Test finalizing partial chunk on stop."""
        capturer = AudioCapturer(output_dir=str(tmp_path))
        
        # Add some fake data
        fake_audio = np.zeros((22050, 2), dtype=np.float32)  # 0.5 seconds
        capturer.current_chunk_data = [fake_audio]
        
        capturer._finalize_partial_chunk()
        
        # Check file was created
        expected_file = tmp_path / "audio_chunk_0000.wav"
        assert expected_file.exists()
        assert len(capturer.audio_files) == 1
