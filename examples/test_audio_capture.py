"""
Example script to test Audio Capture functionality.
This script demonstrates how to use the AudioCapturer class.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.audio_capture import AudioCapturer


def main():
    """Test audio capture functionality."""
    print("=" * 60)
    print("Audio Capture Test")
    print("=" * 60)
    
    # List available audio devices
    print("\n1. Listing available audio devices:")
    print("-" * 60)
    devices = AudioCapturer.list_audio_devices()
    
    output_devices = [d for d in devices if d['is_output']]
    if not output_devices:
        print("ERROR: No output audio devices found!")
        return
    
    print(f"\nFound {len(output_devices)} output device(s)")
    
    # Create capturer
    print("\n2. Creating AudioCapturer:")
    print("-" * 60)
    output_dir = Path("./audio")
    capturer = AudioCapturer(output_dir=str(output_dir), chunk_duration=5)
    print(f"Output directory: {output_dir.absolute()}")
    print(f"Chunk duration: {capturer.chunk_duration} seconds")
    print(f"Sample rate: {capturer.sample_rate} Hz")
    print(f"Channels: {capturer.channels}")
    
    # Test short capture
    print("\n3. Testing audio capture (10 seconds):")
    print("-" * 60)
    print("Starting capture...")
    
    # Use first output device
    device_index = output_devices[0]['index']
    print(f"Using device: {output_devices[0]['name']}")
    
    capturer.start_capture(device_index=device_index)
    
    # Capture for 10 seconds
    for i in range(10):
        time.sleep(1)
        print(f"  Capturing... {i+1}/10 seconds")
    
    print("Stopping capture...")
    capturer.stop_capture()
    
    # Show results
    print("\n4. Capture Results:")
    print("-" * 60)
    audio_files = capturer.get_audio_files()
    chunk_count = capturer.get_chunk_count()
    
    print(f"Total chunks captured: {chunk_count}")
    print(f"Audio files created: {len(audio_files)}")
    
    for i, filepath in enumerate(audio_files):
        file_path = Path(filepath)
        if file_path.exists():
            size_kb = file_path.stat().st_size / 1024
            print(f"  [{i}] {file_path.name} ({size_kb:.2f} KB)")
    
    print("\n" + "=" * 60)
    print("Audio capture test completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
