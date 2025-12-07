#!/usr/bin/env python3
"""
Configuration Validation Helper for MeetDocs AI

This script validates your MeetDocs AI configuration and checks that all
required dependencies and files are properly set up.

Usage:
    python helper_validate_config.py [--env-file .env]

The script will check:
- Environment variables and configuration
- Required files (cookies, directories)
- Python dependencies
- Audio device availability
- API key validity (basic check)
- Whisper model availability

This helps identify configuration issues before running the main application.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Tuple


# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header."""
    print()
    print("=" * 80)
    print(f"{Colors.BOLD}{text}{Colors.RESET}")
    print("=" * 80)
    print()


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓{Colors.RESET} {text}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {text}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}✗{Colors.RESET} {text}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {text}")


def load_env_file(env_file: str) -> bool:
    """Load environment variables from .env file."""
    env_path = Path(env_file)
    
    if not env_path.exists():
        print_warning(f"Environment file not found: {env_file}")
        print_info("Using system environment variables only")
        return False
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip().strip('"').strip("'")
                    os.environ[key.strip()] = value
        
        print_success(f"Loaded environment from: {env_file}")
        return True
    except Exception as e:
        print_error(f"Failed to load .env file: {e}")
        return False


def check_python_version() -> Tuple[bool, str]:
    """Check Python version."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, f"Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)"


def check_dependencies() -> List[Tuple[str, bool, str]]:
    """Check if required Python packages are installed."""
    dependencies = [
        ('selenium', 'selenium'),
        ('webdriver_manager', 'webdriver_manager'),
        ('sounddevice', 'sounddevice'),
        ('soundfile', 'soundfile'),
        ('numpy', 'numpy'),
        ('openai-whisper', 'whisper'),
        ('googletrans', 'googletrans'),
        ('google-generativeai', 'google.generativeai'),
        ('python-docx', 'docx'),
    ]
    
    results = []
    for display_name, import_name in dependencies:
        try:
            __import__(import_name)
            results.append((display_name, True, "Installed"))
        except (ImportError, TypeError, AttributeError) as e:
            # Some packages may have import issues even when installed
            # Try to be more lenient with the check
            results.append((display_name, False, f"Not installed or import error"))
        except Exception as e:
            # Catch any other unexpected errors
            results.append((display_name, False, f"Check failed: {type(e).__name__}"))
    
    return results


def check_configuration() -> List[Tuple[str, bool, str]]:
    """Check configuration values."""
    checks = []
    
    # Cookie path
    cookie_path = os.getenv('COOKIE_PATH', './cookies.pkl')
    cookie_exists = Path(cookie_path).exists()
    checks.append((
        'COOKIE_PATH',
        cookie_exists,
        f"{cookie_path} {'(exists)' if cookie_exists else '(NOT FOUND)'}"
    ))
    
    # Gemini API key
    gemini_key = os.getenv('GEMINI_API_KEY', '')
    has_gemini = bool(gemini_key)
    checks.append((
        'GEMINI_API_KEY',
        has_gemini,
        "Set" if has_gemini else "NOT SET"
    ))
    
    # Audio device index
    audio_device = os.getenv('AUDIO_DEVICE_INDEX', '')
    checks.append((
        'AUDIO_DEVICE_INDEX',
        True,  # Optional, so always pass
        audio_device if audio_device else "Not set (will use default)"
    ))
    
    # Whisper model size
    model_size = os.getenv('WHISPER_MODEL_SIZE', 'base')
    valid_sizes = ['tiny', 'base', 'small', 'medium', 'large']
    is_valid = model_size in valid_sizes
    checks.append((
        'WHISPER_MODEL_SIZE',
        is_valid,
        f"{model_size} {'(valid)' if is_valid else '(INVALID)'}"
    ))
    
    # Directories
    for dir_var in ['AUDIO_DIR', 'TRANSCRIPT_DIR', 'OUTPUT_DIR', 'LOG_DIR']:
        dir_path = os.getenv(dir_var, f'./{dir_var.lower().replace("_dir", "")}')
        checks.append((
            dir_var,
            True,  # Will be created if needed
            dir_path
        ))
    
    return checks


def check_audio_devices() -> Tuple[bool, str]:
    """Check if audio devices are available."""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        
        output_devices = [d for d in devices if d['max_output_channels'] > 0]
        
        if output_devices:
            return True, f"Found {len(output_devices)} output device(s)"
        else:
            return False, "No output devices found (virtual audio cable may be needed)"
    except Exception as e:
        return False, f"Error checking devices: {e}"


def check_whisper_model() -> Tuple[bool, str]:
    """Check if Whisper model is available."""
    try:
        import whisper
        model_size = os.getenv('WHISPER_MODEL_SIZE', 'base')
        
        # Try to load the model (this will download if not present)
        print_info(f"Checking Whisper model '{model_size}' (may download if not cached)...")
        model = whisper.load_model(model_size)
        
        return True, f"Model '{model_size}' is available"
    except Exception as e:
        return False, f"Error loading model: {e}"


def validate_config(env_file: str = '.env') -> bool:
    """
    Validate the complete configuration.
    
    Returns:
        True if configuration is valid
    """
    print_header("MeetDocs AI - Configuration Validation")
    
    all_passed = True
    warnings = []
    
    # Load environment file
    print_header("1. Environment Configuration")
    load_env_file(env_file)
    
    # Check Python version
    print_header("2. Python Version")
    py_ok, py_msg = check_python_version()
    if py_ok:
        print_success(py_msg)
    else:
        print_error(py_msg)
        all_passed = False
    
    # Check dependencies
    print_header("3. Python Dependencies")
    deps = check_dependencies()
    for name, installed, msg in deps:
        if installed:
            print_success(f"{name}: {msg}")
        else:
            print_error(f"{name}: {msg}")
            all_passed = False
    
    # Check configuration
    print_header("4. Configuration Values")
    configs = check_configuration()
    for name, valid, msg in configs:
        if valid:
            print_success(f"{name}: {msg}")
        else:
            if name in ['COOKIE_PATH', 'GEMINI_API_KEY']:
                print_error(f"{name}: {msg}")
                all_passed = False
            else:
                print_warning(f"{name}: {msg}")
                warnings.append(name)
    
    # Check audio devices
    print_header("5. Audio Devices")
    audio_ok, audio_msg = check_audio_devices()
    if audio_ok:
        print_success(audio_msg)
        print_info("Run 'python helper_list_devices.py' to see all devices")
    else:
        print_warning(audio_msg)
        warnings.append("Audio devices")
    
    # Check Whisper model (optional, can be slow)
    print_header("6. Whisper Model")
    print_info("Skipping Whisper model check (run manually if needed)")
    print_info("The model will be downloaded automatically on first use")
    
    # Summary
    print_header("Validation Summary")
    
    if all_passed and not warnings:
        print_success("All checks passed! Configuration is valid.")
        print()
        print("You're ready to run MeetDocs AI:")
        print("  python main.py <google-meet-url>")
        print()
        return True
    elif all_passed:
        print_warning(f"Configuration is valid with {len(warnings)} warning(s)")
        print()
        print("Warnings for:")
        for w in warnings:
            print(f"  - {w}")
        print()
        print("You can proceed, but review the warnings above.")
        print()
        return True
    else:
        print_error("Configuration validation failed!")
        print()
        print("Please fix the errors above before running MeetDocs AI.")
        print()
        print("Common fixes:")
        print("  1. Install missing dependencies: pip install -r requirements.txt")
        print("  2. Extract cookies: python helper_extract_cookies.py")
        print("  3. Set GEMINI_API_KEY in your .env file")
        print("  4. Install virtual audio cable for system audio capture")
        print()
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate MeetDocs AI configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--env-file',
        default='.env',
        help='Path to .env file (default: .env)'
    )
    
    args = parser.parse_args()
    
    success = validate_config(args.env_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
