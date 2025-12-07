# Helper Utilities Documentation

MeetDocs AI includes three helper utilities to simplify setup and configuration. These scripts help you identify audio devices, extract authentication cookies, and validate your configuration before running the main application.

## Overview

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `helper_list_devices.py` | List audio devices | Before first run, when changing audio setup |
| `helper_extract_cookies.py` | Extract Google cookies | Before first run, when cookies expire |
| `helper_validate_config.py` | Validate configuration | Before first run, when troubleshooting |

## 1. Audio Device Listing (`helper_list_devices.py`)

### Purpose

Lists all available audio devices on your system and identifies which ones are suitable for system audio capture.

### Usage

```bash
python helper_list_devices.py
```

### Output

The script displays:
- Device index (use this in your configuration)
- Device name
- Device type (Input/Output)
- Number of output and input channels
- Default sample rate
- Whether it's suitable for system audio capture

### Example Output

```
================================================================================
MeetDocs AI - Audio Device Listing Helper
================================================================================

Found 16 audio device(s):

[0] Microphone (Realtek Audio)
    Type: Input
    Output Channels: 0
    Input Channels: 2
    Default Sample Rate: 44100.0 Hz

[1] CABLE Output (VB-Audio Virtual Cable)
    Type: Output
    Output Channels: 2
    Input Channels: 0
    Default Sample Rate: 44100.0 Hz
    ✓ Suitable for system audio capture

[2] Speakers (Realtek Audio)
    Type: Output
    Output Channels: 2
    Input Channels: 0
    Default Sample Rate: 44100.0 Hz
    ✓ Suitable for system audio capture

================================================================================
RECOMMENDATIONS:
================================================================================

For system audio capture, use one of these device indices:
  - Device [1]: CABLE Output (VB-Audio Virtual Cable)
  - Device [2]: Speakers (Realtek Audio)

Common device names to look for:
  - Windows: 'Stereo Mix', 'CABLE Output (VB-Audio Virtual Cable)'
  - macOS: 'BlackHole 2ch', 'Multi-Output Device'
  - Linux: 'Monitor of ...', 'pulse'

To use a device, set AUDIO_DEVICE_INDEX in your .env file:
  AUDIO_DEVICE_INDEX=1
```

### What to Look For

**Windows:**
- "Stereo Mix" (built-in, may need to be enabled)
- "CABLE Output (VB-Audio Virtual Cable)" (requires VB-Audio installation)

**macOS:**
- "BlackHole 2ch" (requires BlackHole installation)
- "Multi-Output Device" (created in Audio MIDI Setup)

**Linux:**
- Devices with "Monitor of" in the name
- "pulse" devices

### Next Steps

1. Note the device index of your preferred audio device
2. Add it to your `.env` file:
   ```
   AUDIO_DEVICE_INDEX=1
   ```
3. Test audio capture with: `python examples/test_audio_capture.py`

## 2. Cookie Extraction (`helper_extract_cookies.py`)

### Purpose

Interactive script that helps you extract Google authentication cookies from Chrome for automated Google Meet login.

### Usage

```bash
# Save to default location (cookies.pkl)
python helper_extract_cookies.py

# Save to custom location
python helper_extract_cookies.py --output my_cookies.pkl
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--output`, `-o` | Output path for cookie file | `cookies.pkl` |

### How It Works

1. Launches Chrome browser
2. Navigates to Google accounts page
3. Waits for you to log in (if not already logged in)
4. Prompts you to press ENTER when ready
5. Extracts all cookies from the browser
6. Saves cookies to the specified file
7. Closes the browser

### Interactive Process

```
================================================================================
MeetDocs AI - Cookie Extraction Helper
================================================================================

Initializing Chrome browser...
✓ Browser launched successfully

Navigating to Google accounts page...
✓ Loaded Google accounts page

================================================================================
INSTRUCTIONS:
================================================================================

1. If you're not logged in, please log in to your Google account now
2. Make sure you're logged into the account you want to use for Meet
3. Once logged in, return to this terminal
4. Press ENTER when you're ready to extract cookies...

Press ENTER to continue...

Extracting cookies...
✓ Found 42 cookie(s)
✓ Cookies saved to: F:\path\to\cookies.pkl
✓ Cookie file created successfully (8456 bytes)

================================================================================
SUCCESS!
================================================================================

Next steps:
1. Update your .env file with: COOKIE_PATH=cookies.pkl
2. Keep this file secure and private
3. Add cookies.pkl to your .gitignore file
4. You can now run MeetDocs AI with these cookies

Note: Cookies may expire after some time. If authentication fails,
      run this script again to refresh your cookies.
```

### Security Considerations

⚠️ **Important Security Notes:**

- The cookie file contains sensitive authentication data
- Never commit `cookies.pkl` to version control
- Add `cookies.pkl` to your `.gitignore` file
- Keep the file secure and private
- Cookies may expire and need to be refreshed periodically
- Use a separate Google account for automation if concerned about security

### Troubleshooting

**Problem:** Browser doesn't launch

**Solution:**
- Ensure Chrome is installed
- Check internet connection
- Close other Chrome instances
- Update Chrome to latest version

**Problem:** No cookies found

**Solution:**
- Make sure you're logged into Google
- Wait for the page to fully load before pressing ENTER
- Try logging out and back in
- Clear browser cache and try again

**Problem:** Authentication still fails with cookies

**Solution:**
- Cookies may have expired - run the script again
- Ensure you're using the correct Google account
- Check that the cookie file path in `.env` is correct
- Try extracting cookies again after logging out and back in

## 3. Configuration Validation (`helper_validate_config.py`)

### Purpose

Validates your complete MeetDocs AI configuration and checks that all required dependencies and files are properly set up.

### Usage

```bash
# Validate default .env file
python helper_validate_config.py

# Validate custom .env file
python helper_validate_config.py --env-file production.env
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--env-file` | Path to .env file | `.env` |

### What It Checks

The script performs comprehensive validation of:

1. **Environment Configuration**
   - Loads and validates `.env` file
   - Falls back to system environment variables if file not found

2. **Python Version**
   - Checks Python version is 3.8 or higher
   - Displays current version

3. **Python Dependencies**
   - Verifies all required packages are installed
   - Lists each package with installation status

4. **Configuration Values**
   - `COOKIE_PATH`: Checks if cookie file exists
   - `GEMINI_API_KEY`: Verifies API key is set
   - `AUDIO_DEVICE_INDEX`: Shows configured device (optional)
   - `WHISPER_MODEL_SIZE`: Validates model size is valid
   - Directory paths: Shows configured directories

5. **Audio Devices**
   - Checks if audio devices are available
   - Counts output devices suitable for capture

6. **Whisper Model**
   - Notes that model will be downloaded on first use
   - Skips actual model check to save time

### Example Output

```
================================================================================
MeetDocs AI - Configuration Validation
================================================================================

================================================================================
1. Environment Configuration
================================================================================
✓ Loaded environment from: .env

================================================================================
2. Python Version
================================================================================
✓ Python 3.10.5

================================================================================
3. Python Dependencies
================================================================================
✓ selenium: Installed
✓ webdriver_manager: Installed
✓ sounddevice: Installed
✓ soundfile: Installed
✓ numpy: Installed
✓ openai-whisper: Installed
✓ googletrans: Installed
✓ google-generativeai: Installed
✓ python-docx: Installed

================================================================================
4. Configuration Values
================================================================================
✓ COOKIE_PATH: ./cookies.pkl (exists)
✓ GEMINI_API_KEY: Set
✓ AUDIO_DEVICE_INDEX: 1
✓ WHISPER_MODEL_SIZE: base (valid)
✓ AUDIO_DIR: ./audio
✓ TRANSCRIPT_DIR: ./transcripts
✓ OUTPUT_DIR: ./output
✓ LOG_DIR: ./logs

================================================================================
5. Audio Devices
================================================================================
✓ Found 6 output device(s)
ℹ Run 'python helper_list_devices.py' to see all devices

================================================================================
6. Whisper Model
================================================================================
ℹ Skipping Whisper model check (run manually if needed)
ℹ The model will be downloaded automatically on first use

================================================================================
Validation Summary
================================================================================
✓ All checks passed! Configuration is valid.

You're ready to run MeetDocs AI:
  python main.py <google-meet-url>
```

### Status Indicators

- ✓ (Green checkmark): Check passed
- ⚠ (Yellow warning): Non-critical issue, can proceed with caution
- ✗ (Red X): Critical error, must be fixed
- ℹ (Blue info): Informational message

### Exit Codes

- `0`: Configuration is valid (all checks passed or only warnings)
- `1`: Configuration validation failed (critical errors found)

### Common Fixes

The script provides helpful suggestions when issues are found:

```
Common fixes:
  1. Install missing dependencies: pip install -r requirements.txt
  2. Extract cookies: python helper_extract_cookies.py
  3. Set GEMINI_API_KEY in your .env file
  4. Install virtual audio cable for system audio capture
```

## Quick Setup Workflow

For first-time setup, run the helper scripts in this recommended order:

### Step 1: List Audio Devices

```bash
python helper_list_devices.py
```

Note the device index you want to use for system audio capture.

### Step 2: Extract Cookies

```bash
python helper_extract_cookies.py
```

Follow the interactive prompts to log in and extract cookies.

### Step 3: Configure Environment

Create or edit your `.env` file:

```bash
cp .env.example .env
```

Update with your settings:

```env
# Required
GEMINI_API_KEY=your_api_key_here

# From Step 1
AUDIO_DEVICE_INDEX=1

# From Step 2
COOKIE_PATH=cookies.pkl

# Optional (defaults shown)
WHISPER_MODEL_SIZE=base
OUTPUT_DIR=./output
LOG_LEVEL=INFO
```

### Step 4: Validate Configuration

```bash
python helper_validate_config.py
```

Fix any errors reported by the validation script.

### Step 5: Run MeetDocs AI

If validation passes, you're ready to go:

```bash
python main.py <google-meet-url>
```

## Troubleshooting

### All Scripts

**Problem:** `ModuleNotFoundError: No module named 'X'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Audio Device Listing

**Problem:** No output devices found

**Solution:**
- Install virtual audio cable (VB-Audio, BlackHole, or PulseAudio loopback)
- Restart audio service
- Check audio drivers are installed

### Cookie Extraction

**Problem:** Browser doesn't launch

**Solution:**
- Install Google Chrome
- Update Chrome to latest version
- Check internet connection

**Problem:** Cookies expire quickly

**Solution:**
- This is normal behavior for security
- Re-run the script when authentication fails
- Consider using a dedicated Google account for automation

### Configuration Validation

**Problem:** Many dependencies show as "Not installed"

**Solution:**
- Activate your virtual environment
- Run: `pip install -r requirements.txt`
- Verify installation: `pip list`

**Problem:** Validation fails but everything seems correct

**Solution:**
- Check `.env` file syntax (no spaces around `=`)
- Ensure file paths use forward slashes or raw strings
- Verify API key has no extra spaces or quotes
- Try running with `--env-file` to specify path explicitly

## Best Practices

1. **Run validation before every major change** to your configuration
2. **Keep helper scripts updated** with the main application
3. **Document your audio device index** in comments in `.env`
4. **Refresh cookies periodically** (every few weeks)
5. **Use version control** for helper scripts but not for cookies or `.env`
6. **Test audio setup** with `examples/test_audio_capture.py` after configuration

## Integration with Main Application

The helper utilities are designed to work seamlessly with the main MeetDocs AI application:

- **Audio device indices** from `helper_list_devices.py` → `AUDIO_DEVICE_INDEX` in `.env`
- **Cookie files** from `helper_extract_cookies.py` → `COOKIE_PATH` in `.env`
- **Validation results** from `helper_validate_config.py` → Confirms readiness to run `main.py`

## Additional Resources

- Main README: `README.md`
- Configuration guide: `.env.example`
- Audio setup guide: `README.md` → "Virtual Audio Cable Setup"
- Cookie extraction guide: `README.md` → "Cookie Extraction"
- Troubleshooting: `README.md` → "Troubleshooting"

## Support

If you encounter issues with the helper utilities:

1. Check the troubleshooting section above
2. Review the main README troubleshooting section
3. Check logs in `logs/` directory
4. Run with debug output if available
5. Open an issue on GitHub with:
   - Script name and command used
   - Error message and full output
   - Your OS and Python version
   - Steps to reproduce
