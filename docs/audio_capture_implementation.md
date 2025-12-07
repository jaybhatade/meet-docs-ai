# Audio Capture Module Implementation

## Overview
The Audio Capture module has been successfully implemented for the MeetDocs AI automation system. This module captures system audio during meetings and saves it in 30-second chunks as WAV files.

## Implementation Details

### File Created
- `src/audio_capture.py` - Main AudioCapturer class implementation

### Key Features Implemented

#### 1. AudioCapturer Class
- **Initialization**: Configurable output directory and chunk duration (default 30 seconds)
- **Audio Format**: 44.1kHz sample rate, stereo (2 channels), WAV format (16-bit PCM)

#### 2. Audio Device Management
- `list_audio_devices()`: Static method to list all available audio devices
- Filters and displays output devices (system audio sources)
- Returns device information including index, name, channels, and sample rate

#### 3. Capture Control
- `start_capture(device_index)`: Starts audio capture in a separate thread
- `stop_capture()`: Stops capture and finalizes any partial chunks
- Non-blocking operation using threading

#### 4. Chunk Management
- Automatic 30-second chunk creation
- Sequential naming: `audio_chunk_0000.wav`, `audio_chunk_0001.wav`, etc.
- Saves chunks to designated output directory
- Tracks all created audio files

#### 5. Error Recovery
- Automatic reconnection on audio device errors
- Maximum 3 reconnection attempts with 2-second delays
- Comprehensive error logging
- Graceful degradation on failures

#### 6. Partial Chunk Finalization
- Saves remaining audio data when capture stops mid-chunk
- Ensures no audio data is lost

#### 7. Thread Safety
- Runs capture in separate daemon thread
- Non-blocking operation allows concurrent processing
- Proper cleanup on stop

## Testing

### Unit Tests Created
- `tests/test_audio_capture.py` - Comprehensive unit test suite
- 10 test cases covering all major functionality
- All tests passing ✅

### Test Coverage
- Initialization and configuration
- Output directory creation
- Audio device listing
- Chunk filename generation
- Audio file tracking
- Chunk saving with data
- Partial chunk finalization
- Start/stop capture flow

### Example Script
- `examples/test_audio_capture.py` - Demonstration script
- Shows device listing, capture initialization, and 10-second test capture

## Requirements Validation

### Requirement 2.1 ✅
**WHEN the meeting is active, THE Audio Capturer SHALL capture system audio output without recording microphone input**
- Implemented: Uses `sd.InputStream` with configurable device index
- Filters for output devices only in `list_audio_devices()`

### Requirement 2.2 ✅
**WHEN capturing audio, THE Audio Capturer SHALL save audio data in 30-second chunks as WAV files**
- Implemented: Configurable `chunk_duration` (default 30 seconds)
- Saves as WAV using soundfile library

### Requirement 2.3 ✅
**WHEN an audio chunk is complete, THE Audio Capturer SHALL store the file in the designated audio directory with sequential naming**
- Implemented: `_generate_chunk_filename()` creates sequential names
- Files saved to `output_dir` with format `audio_chunk_XXXX.wav`

### Requirement 2.4 ✅
**IF the audio device is unavailable or encounters an error, THEN THE Audio Capturer SHALL log the error and attempt to reconnect to the audio source**
- Implemented: `_capture_loop()` with retry logic
- Maximum 3 attempts with exponential backoff
- Comprehensive error logging

### Requirement 2.5 ✅
**WHEN the meeting ends, THE Audio Capturer SHALL finalize and save any remaining audio data**
- Implemented: `_finalize_partial_chunk()` called in `stop_capture()`
- Saves partial chunks automatically

## API Reference

### AudioCapturer Class

```python
class AudioCapturer:
    def __init__(self, output_dir: str, chunk_duration: int = 30)
    
    @staticmethod
    def list_audio_devices() -> List[dict]
    
    def start_capture(self, device_index: Optional[int] = None)
    def stop_capture(self)
    
    def get_audio_files() -> List[str]
    def get_chunk_count() -> int
```

### Usage Example

```python
from src.audio_capture import AudioCapturer

# List available devices
devices = AudioCapturer.list_audio_devices()
output_device = next(d for d in devices if d['is_output'])

# Create capturer
capturer = AudioCapturer(output_dir="./audio", chunk_duration=30)

# Start capture
capturer.start_capture(device_index=output_device['index'])

# ... meeting happens ...

# Stop capture
capturer.stop_capture()

# Get captured files
audio_files = capturer.get_audio_files()
print(f"Captured {len(audio_files)} audio chunks")
```

## Dependencies
- `sounddevice==0.4.6` - Audio capture
- `soundfile==0.12.1` - WAV file I/O
- `numpy==1.26.2` - Audio data arrays

## Next Steps
The Audio Capture module is complete and ready for integration with:
1. Meet Joiner module (already implemented)
2. Transcriber module (next task)
3. Main orchestrator pipeline

## Notes
- The module uses system audio output devices, not microphone input
- On Windows, may require virtual audio cable (e.g., VB-Audio Virtual Cable)
- On macOS, may require BlackHole for audio routing
- On Linux, may require PulseAudio loopback configuration
