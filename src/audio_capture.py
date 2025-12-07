"""
Audio Capture module for MeetDocs AI automation system.
Captures system audio during meetings and saves in 30-second chunks.
"""

import logging
import threading
import time
from pathlib import Path
from typing import Optional, List
import numpy as np
import sounddevice as sd
import soundfile as sf


logger = logging.getLogger(__name__)


class AudioCapturer:
    """Manages audio recording during meetings."""
    
    def __init__(self, output_dir: str, chunk_duration: int = 30):
        """
        Initialize AudioCapturer.
        
        Args:
            output_dir: Directory to save audio chunks
            chunk_duration: Duration of each audio chunk in seconds (default: 30)
        """
        self.output_dir = Path(output_dir)
        self.chunk_duration = chunk_duration
        self.sample_rate = 44100  # CD quality
        self.channels = 2  # Stereo
        
        self.device_index: Optional[int] = None
        self.is_capturing = False
        self.capture_thread: Optional[threading.Thread] = None
        self.chunk_number = 0
        self.audio_files: List[str] = []
        
        # Audio buffer for current chunk
        self.current_chunk_data: List[np.ndarray] = []
        self.chunk_start_time: Optional[float] = None
        
        # Error recovery
        self.max_reconnect_attempts = 3
        self.reconnect_delay = 2  # seconds
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"AudioCapturer initialized: output_dir={output_dir}, chunk_duration={chunk_duration}s")
    
    @staticmethod
    def list_audio_devices() -> List[dict]:
        """
        List all available audio devices.
        
        Returns:
            List of device information dictionaries
        """
        devices = sd.query_devices()
        device_list = []
        
        logger.info("Available audio devices:")
        for idx, device in enumerate(devices):
            device_info = {
                'index': idx,
                'name': device['name'],
                'channels': device['max_output_channels'],
                'sample_rate': device['default_samplerate'],
                'is_output': device['max_output_channels'] > 0
            }
            device_list.append(device_info)
            
            if device['max_output_channels'] > 0:
                logger.info(f"  [{idx}] {device['name']} (Output: {device['max_output_channels']} channels)")
        
        return device_list
    
    def start_capture(self, device_index: Optional[int] = None):
        """
        Start audio capture in a separate thread.
        
        Args:
            device_index: Index of audio device to capture from (None for default)
        """
        if self.is_capturing:
            logger.warning("Audio capture already in progress")
            return
        
        self.device_index = device_index
        self.is_capturing = True
        self.chunk_number = 0
        self.audio_files = []
        
        # Start capture in separate thread for non-blocking operation
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        logger.info(f"Audio capture started on device {device_index}")
    
    def stop_capture(self):
        """Stop audio capture and finalize any partial chunks."""
        if not self.is_capturing:
            logger.warning("No audio capture in progress")
            return
        
        logger.info("Stopping audio capture...")
        self.is_capturing = False
        
        # Wait for capture thread to finish
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=5)
        
        # Finalize any remaining audio data
        self._finalize_partial_chunk()
        
        logger.info(f"Audio capture stopped. Total chunks: {self.chunk_number}")
    
    def _capture_loop(self):
        """Main capture loop running in separate thread."""
        attempt = 0
        
        while self.is_capturing and attempt < self.max_reconnect_attempts:
            try:
                self._capture_with_recovery()
                break  # Successful capture, exit loop
            except Exception as e:
                attempt += 1
                logger.error(f"Audio capture error (attempt {attempt}/{self.max_reconnect_attempts}): {e}")
                
                if attempt < self.max_reconnect_attempts and self.is_capturing:
                    logger.info(f"Attempting to reconnect in {self.reconnect_delay} seconds...")
                    time.sleep(self.reconnect_delay)
                else:
                    logger.error("Max reconnection attempts reached. Audio capture failed.")
                    self.is_capturing = False
    
    def _capture_with_recovery(self):
        """Capture audio with error recovery."""
        try:
            # Open audio stream
            with sd.InputStream(
                device=self.device_index,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=self._audio_callback,
                blocksize=int(self.sample_rate * 0.1)  # 100ms blocks
            ):
                logger.info("Audio stream opened successfully")
                self.chunk_start_time = time.time()
                
                # Keep stream open while capturing
                while self.is_capturing:
                    time.sleep(0.1)
                    
                    # Check if chunk duration reached
                    if self.chunk_start_time and time.time() - self.chunk_start_time >= self.chunk_duration:
                        self._save_current_chunk()
                        self.chunk_start_time = time.time()
        
        except sd.PortAudioError as e:
            logger.error(f"PortAudio error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in audio capture: {e}")
            raise
    
    def _audio_callback(self, indata, frames, time_info, status):
        """
        Callback function for audio stream.
        
        Args:
            indata: Input audio data
            frames: Number of frames
            time_info: Timing information
            status: Stream status
        """
        if status:
            logger.warning(f"Audio stream status: {status}")
        
        # Append audio data to current chunk buffer
        self.current_chunk_data.append(indata.copy())
    
    def _save_current_chunk(self):
        """Save the current audio chunk to file."""
        if not self.current_chunk_data:
            logger.warning("No audio data to save")
            return
        
        try:
            # Concatenate all audio blocks into single array
            audio_data = np.concatenate(self.current_chunk_data, axis=0)
            
            # Generate filename
            filename = self._generate_chunk_filename(self.chunk_number)
            filepath = self.output_dir / filename
            
            # Save as WAV file
            sf.write(filepath, audio_data, self.sample_rate)
            
            self.audio_files.append(str(filepath))
            logger.info(f"Saved audio chunk {self.chunk_number}: {filename} ({len(audio_data)/self.sample_rate:.2f}s)")
            
            # Reset for next chunk
            self.chunk_number += 1
            self.current_chunk_data = []
            
        except Exception as e:
            logger.error(f"Error saving audio chunk {self.chunk_number}: {e}")
    
    def _finalize_partial_chunk(self):
        """Save any remaining audio data as final chunk."""
        if self.current_chunk_data:
            logger.info("Finalizing partial audio chunk...")
            self._save_current_chunk()
    
    def _generate_chunk_filename(self, chunk_num: int) -> str:
        """
        Generate sequential filename for audio chunk.
        
        Args:
            chunk_num: Chunk number
            
        Returns:
            Filename string
        """
        return f"audio_chunk_{chunk_num:04d}.wav"
    
    def get_audio_files(self) -> List[str]:
        """
        Get list of captured audio files.
        
        Returns:
            List of audio file paths
        """
        return self.audio_files.copy()
    
    def get_chunk_count(self) -> int:
        """
        Get number of audio chunks captured.
        
        Returns:
            Number of chunks
        """
        return self.chunk_number
