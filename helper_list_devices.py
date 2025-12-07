#!/usr/bin/env python3
"""
Audio Device Listing Helper for MeetDocs AI

This script lists all available audio devices on your system and helps you
identify the correct device index for system audio capture.

Usage:
    python helper_list_devices.py

The script will display:
- Device index (use this in your configuration)
- Device name
- Number of output channels
- Default sample rate
- Whether it's an output device (suitable for system audio capture)
"""

import sys
import sounddevice as sd


def list_audio_devices():
    """List all available audio devices with detailed information."""
    print("=" * 80)
    print("MeetDocs AI - Audio Device Listing Helper")
    print("=" * 80)
    print()
    
    try:
        devices = sd.query_devices()
        
        print(f"Found {len(devices)} audio device(s):\n")
        
        output_devices = []
        
        for idx, device in enumerate(devices):
            is_output = device['max_output_channels'] > 0
            is_input = device['max_input_channels'] > 0
            
            # Determine device type
            device_type = []
            if is_input:
                device_type.append("Input")
            if is_output:
                device_type.append("Output")
            
            type_str = "/".join(device_type) if device_type else "Unknown"
            
            # Print device information
            print(f"[{idx}] {device['name']}")
            print(f"    Type: {type_str}")
            print(f"    Output Channels: {device['max_output_channels']}")
            print(f"    Input Channels: {device['max_input_channels']}")
            print(f"    Default Sample Rate: {device['default_samplerate']} Hz")
            
            # Mark suitable devices for system audio capture
            if is_output:
                output_devices.append(idx)
                print(f"    ✓ Suitable for system audio capture")
            
            print()
        
        # Provide recommendations
        print("=" * 80)
        print("RECOMMENDATIONS:")
        print("=" * 80)
        print()
        
        if output_devices:
            print("For system audio capture, use one of these device indices:")
            for idx in output_devices:
                device = devices[idx]
                print(f"  - Device [{idx}]: {device['name']}")
            
            print()
            print("Common device names to look for:")
            print("  - Windows: 'Stereo Mix', 'CABLE Output (VB-Audio Virtual Cable)'")
            print("  - macOS: 'BlackHole 2ch', 'Multi-Output Device'")
            print("  - Linux: 'Monitor of ...', 'pulse'")
            print()
            print("To use a device, set AUDIO_DEVICE_INDEX in your .env file:")
            print(f"  AUDIO_DEVICE_INDEX={output_devices[0]}")
        else:
            print("⚠ WARNING: No output devices found!")
            print()
            print("You may need to install a virtual audio cable:")
            print("  - Windows: VB-Audio Virtual Cable (https://vb-audio.com/Cable/)")
            print("  - macOS: BlackHole (https://github.com/ExistentialAudio/BlackHole)")
            print("  - Linux: PulseAudio loopback module")
        
        print()
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to list audio devices: {e}", file=sys.stderr)
        print()
        print("Troubleshooting:")
        print("  1. Ensure sounddevice is installed: pip install sounddevice")
        print("  2. Check that your audio drivers are properly installed")
        print("  3. Try restarting your audio service/system")
        return False


def main():
    """Main entry point."""
    success = list_audio_devices()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
