# MeetDocs AI - Automated Meeting Documentation

An end-to-end Python automation tool that automatically joins Google Meet sessions, captures and transcribes audio in multiple languages (Hindi, Marathi, English), translates content to English, generates AI-powered meeting summaries, and exports professional documentation in DOCX format.

## Table of Contents

- [Project Structure](#project-structure)
- [System Requirements](#system-requirements)
- [Installation](#installation)
  - [Python Setup](#python-setup)
  - [ChromeDriver Setup](#chromedriver-setup)
  - [Virtual Audio Cable Setup](#virtual-audio-cable-setup)
  - [Cookie Extraction](#cookie-extraction)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Command-Line Options](#command-line-options)
  - [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [Features](#features)
- [Testing](#testing)

## Project Structure

```
meetdocs-ai/
├── src/                    # Source code modules
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── meet_joiner.py     # Google Meet automation
│   ├── audio_capture.py   # Audio recording
│   ├── transcriber.py     # Speech-to-text
│   ├── translator.py      # Language translation
│   ├── summarizer.py      # AI summarization
│   └── exporter.py        # DOCX export
├── audio/                  # Captured audio chunks
├── transcripts/            # Generated transcripts
├── output/                 # Final DOCX documents
├── logs/                   # Application logs
├── tests/                  # Test suite
├── examples/               # Example scripts
├── main.py                 # Main orchestrator
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
└── README.md              # This file
```

## System Requirements

- **Python**: 3.10 or higher
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: Minimum 8GB (16GB recommended for larger Whisper models)
- **Storage**: At least 5GB free space for models and recordings
- **Browser**: Google Chrome (latest version)
- **Internet**: Stable connection for Google Meet and API calls

## Installation

### Python Setup

1. **Install Python 3.10 or higher**

   - **Windows**: Download from [python.org](https://www.python.org/downloads/)
   - **macOS**: `brew install python@3.10`
   - **Linux**: `sudo apt install python3.10 python3.10-venv`

2. **Clone the repository and navigate to the project directory**
   ```bash
   git clone <repository-url>
   cd meetdocs-ai
   ```

3. **Create a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   This will install all required packages including:
   - Selenium for browser automation
   - OpenAI Whisper for transcription
   - Google Generative AI for summarization
   - sounddevice and soundfile for audio capture
   - python-docx for document generation

### ChromeDriver Setup

ChromeDriver is automatically managed by `webdriver-manager`, but you need Google Chrome installed.

#### Windows

1. **Install Google Chrome**
   - Download from [google.com/chrome](https://www.google.com/chrome/)
   - Run the installer

2. **Verify Chrome installation**
   ```cmd
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --version
   ```

3. **ChromeDriver will be automatically downloaded** on first run by webdriver-manager

#### macOS

1. **Install Google Chrome**
   ```bash
   brew install --cask google-chrome
   ```

2. **Verify Chrome installation**
   ```bash
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version
   ```

3. **ChromeDriver will be automatically downloaded** on first run

#### Linux

1. **Install Google Chrome**
   ```bash
   # Ubuntu/Debian
   wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
   sudo dpkg -i google-chrome-stable_current_amd64.deb
   sudo apt-get install -f

   # Fedora
   sudo dnf install google-chrome-stable
   ```

2. **Verify Chrome installation**
   ```bash
   google-chrome --version
   ```

3. **For headless servers, install Xvfb**
   ```bash
   sudo apt-get install xvfb
   ```

   Run with Xvfb:
   ```bash
   xvfb-run python main.py <meet-url>
   ```

### Virtual Audio Cable Setup

Virtual audio cables route system audio output back as an input device for recording.

#### Windows - VB-Audio Virtual Cable

1. **Download VB-Audio Virtual Cable**
   - Visit [vb-audio.com/Cable](https://vb-audio.com/Cable/)
   - Download "VBCABLE_Driver_Pack43.zip"

2. **Install the driver**
   - Extract the ZIP file
   - Right-click `VBCABLE_Setup_x64.exe` (or x86 for 32-bit)
   - Select "Run as administrator"
   - Follow installation prompts
   - Restart your computer

3. **Configure audio routing**
   - Right-click the speaker icon in system tray
   - Select "Open Sound settings"
   - Under "Output", select "CABLE Input (VB-Audio Virtual Cable)"
   - This routes all system audio through the virtual cable

4. **Find the audio device index**
   ```bash
   python -c "import sounddevice as sd; print(sd.query_devices())"
   ```
   Look for "CABLE Output" in the list and note its index number

5. **Optional: Hear audio while recording**
   - Open "Sound settings" → "Sound Control Panel"
   - Go to "Recording" tab
   - Right-click "CABLE Output" → Properties
   - Go to "Listen" tab
   - Check "Listen to this device"
   - Select your speakers/headphones from dropdown

#### macOS - BlackHole

1. **Install BlackHole using Homebrew**
   ```bash
   brew install blackhole-2ch
   ```

   Or download manually from [existential.audio/blackhole](https://existential.audio/blackhole/)

2. **Create Multi-Output Device (to hear audio while recording)**
   - Open "Audio MIDI Setup" (Applications → Utilities)
   - Click the "+" button at bottom left
   - Select "Create Multi-Output Device"
   - Check both "BlackHole 2ch" and your output device (e.g., "MacBook Pro Speakers")
   - Right-click the Multi-Output Device → "Use This Device For Sound Output"

3. **Find the audio device index**
   ```bash
   python -c "import sounddevice as sd; print(sd.query_devices())"
   ```
   Look for "BlackHole 2ch" and note its index number

4. **Set system output**
   - Go to System Preferences → Sound → Output
   - Select the "Multi-Output Device" you created

#### Linux - PulseAudio Loopback

1. **Install PulseAudio (usually pre-installed)**
   ```bash
   sudo apt-get install pulseaudio pavucontrol
   ```

2. **Create a loopback device**
   ```bash
   pactl load-module module-loopback latency_msec=1
   ```

3. **Make it permanent** (optional)
   - Edit `/etc/pulse/default.pa`
   - Add line: `load-module module-loopback latency_msec=1`

4. **Configure audio routing with pavucontrol**
   ```bash
   pavucontrol
   ```
   - Go to "Recording" tab
   - Find your application and set input to "Monitor of [your output device]"

5. **Find the audio device index**
   ```bash
   python -c "import sounddevice as sd; print(sd.query_devices())"
   ```
   Look for devices with "monitor" in the name

### Cookie Extraction

MeetDocs AI uses saved browser cookies to authenticate with Google Meet without hardcoded credentials.

#### Method 1: Manual Cookie Extraction (Recommended)

1. **Open Google Chrome and log into Google Meet**
   - Visit [meet.google.com](https://meet.google.com)
   - Sign in with your Google account
   - Join any test meeting to verify login works

2. **Open Chrome DevTools**
   - Press `F12` or `Ctrl+Shift+I` (Windows/Linux)
   - Press `Cmd+Option+I` (macOS)

3. **Navigate to Application/Storage tab**
   - Click "Application" tab (or "Storage" in some versions)
   - Expand "Cookies" in left sidebar
   - Click on "https://meet.google.com"

4. **Export cookies manually**
   - You'll see a list of cookies
   - Important cookies to note: `SID`, `HSID`, `SSID`, `APISID`, `SAPISID`

5. **Create cookies file using Python**
   
   Create a file `extract_cookies.py`:
   ```python
   import pickle
   from selenium import webdriver
   from selenium.webdriver.chrome.service import Service
   from webdriver_manager.chrome import ChromeDriverManager
   
   # Start Chrome
   service = Service(ChromeDriverManager().install())
   driver = webdriver.Chrome(service=service)
   
   # Navigate to Google Meet
   driver.get("https://meet.google.com")
   
   # Wait for manual login
   input("Please log in to Google Meet, then press Enter here...")
   
   # Save cookies
   cookies = driver.get_cookies()
   pickle.dump(cookies, open("cookies.pkl", "wb"))
   print("Cookies saved to cookies.pkl")
   
   driver.quit()
   ```

   Run it:
   ```bash
   python extract_cookies.py
   ```

#### Method 2: Using Browser Extension

1. **Install "Get cookies.txt" extension**
   - Chrome Web Store: Search for "Get cookies.txt"
   - Install the extension

2. **Export cookies**
   - Visit [meet.google.com](https://meet.google.com) while logged in
   - Click the extension icon
   - Click "Export" → Save as `cookies.txt`

3. **Convert to pickle format**
   ```python
   # convert_cookies.py
   import pickle
   import http.cookiejar
   
   # Read Netscape format cookies
   cj = http.cookiejar.MozillaCookieJar('cookies.txt')
   cj.load()
   
   # Convert to Selenium format
   cookies = []
   for cookie in cj:
       cookies.append({
           'name': cookie.name,
           'value': cookie.value,
           'domain': cookie.domain,
           'path': cookie.path,
           'secure': cookie.secure
       })
   
   # Save as pickle
   pickle.dump(cookies, open("cookies.pkl", "wb"))
   print("Converted cookies.txt to cookies.pkl")
   ```

#### Verifying Cookie File

Test your cookies:
```python
import pickle

cookies = pickle.load(open("cookies.pkl", "rb"))
print(f"Loaded {len(cookies)} cookies")
for cookie in cookies:
    print(f"  - {cookie['name']}: {cookie['domain']}")
```

## Configuration

### Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# Required: Google Gemini API Key
GEMINI_API_KEY=your_api_key_here

# Optional: Override default paths
COOKIE_PATH=./cookies.pkl
AUDIO_DEVICE_INDEX=1
WHISPER_MODEL_SIZE=base
OUTPUT_DIR=./output
LOG_LEVEL=INFO
```

### Configuration Options

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `GEMINI_API_KEY` | Google Gemini API key (required) | None | Get from [ai.google.dev](https://ai.google.dev/) |
| `COOKIE_PATH` | Path to saved cookies file | `./cookies.pkl` | Any valid file path |
| `AUDIO_DEVICE_INDEX` | Audio device index for recording | Auto-detect | Run helper script to find |
| `WHISPER_MODEL_SIZE` | Whisper model size | `base` | `tiny`, `base`, `small`, `medium`, `large` |
| `OUTPUT_DIR` | Directory for output files | `./output` | Any valid directory path |
| `LOG_LEVEL` | Logging verbosity | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

### Getting a Gemini API Key

1. Visit [Google AI Studio](https://ai.google.dev/)
2. Sign in with your Google account
3. Click "Get API Key"
4. Create a new API key or use existing one
5. Copy the key to your `.env` file

## Usage

### Basic Usage

```bash
python main.py <google_meet_url>
```

The system will:
1. Join the Google Meet session
2. Capture audio in 30-second chunks
3. Transcribe audio using Whisper
4. Translate non-English content to English
5. Generate AI summary using Gemini
6. Export formatted DOCX document
7. Display the output file path

### Command-Line Options

```bash
python main.py <meet_url> [options]
```

#### Required Arguments

- `meet_url`: Google Meet URL (e.g., `https://meet.google.com/abc-defg-hij`)

#### Optional Arguments

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--cookie-path PATH` | Path to cookies file | `./cookies.pkl` | `--cookie-path /path/to/cookies.pkl` |
| `--audio-device INDEX` | Audio device index | Auto-detect | `--audio-device 2` |
| `--model-size SIZE` | Whisper model size | `base` | `--model-size small` |
| `--gemini-key KEY` | Gemini API key | From `.env` | `--gemini-key YOUR_KEY` |
| `--output-dir DIR` | Output directory | `./output` | `--output-dir /path/to/output` |
| `--log-level LEVEL` | Logging level | `INFO` | `--log-level DEBUG` |
| `--duration MINUTES` | Recording duration | Until manual stop | `--duration 60` |
| `--no-translate` | Skip translation step | Enabled | `--no-translate` |
| `--help` | Show help message | - | `--help` |

### Usage Examples

#### Example 1: Basic Meeting Recording

```bash
python main.py https://meet.google.com/abc-defg-hij
```

Uses default settings from `.env` file.

#### Example 2: Custom Audio Device

```bash
# First, list available devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Then use the device index
python main.py https://meet.google.com/abc-defg-hij --audio-device 3
```

#### Example 3: High-Quality Transcription

```bash
python main.py https://meet.google.com/abc-defg-hij --model-size medium
```

Uses the `medium` Whisper model for better accuracy (requires more RAM/GPU).

#### Example 4: Custom Output Directory

```bash
python main.py https://meet.google.com/abc-defg-hij --output-dir ~/Documents/Meetings
```

Saves the output DOCX to a specific directory.

#### Example 5: Debug Mode

```bash
python main.py https://meet.google.com/abc-defg-hij --log-level DEBUG
```

Enables detailed logging for troubleshooting.

#### Example 6: Timed Recording

```bash
python main.py https://meet.google.com/abc-defg-hij --duration 30
```

Automatically stops recording after 30 minutes.

#### Example 7: Skip Translation

```bash
python main.py https://meet.google.com/abc-defg-hij --no-translate
```

Useful for English-only meetings to save processing time.

#### Example 8: Complete Custom Configuration

```bash
python main.py https://meet.google.com/abc-defg-hij \
  --cookie-path ~/my-cookies.pkl \
  --audio-device 2 \
  --model-size small \
  --output-dir ~/Meetings/2024 \
  --log-level INFO
```

### Helper Scripts

MeetDocs AI includes three helper utilities to simplify setup and configuration:

#### 1. List Audio Devices (`helper_list_devices.py`)

Lists all available audio devices on your system and identifies which ones are suitable for system audio capture.

```bash
python helper_list_devices.py
```

**Output includes**:
- Device index (use this in your configuration)
- Device name
- Number of output channels
- Default sample rate
- Whether it's suitable for system audio capture

**Example output**:
```
[0] Microphone (Realtek Audio)
    Type: Input
    Output Channels: 0
    Input Channels: 2

[1] CABLE Output (VB-Audio Virtual Cable)
    Type: Output
    Output Channels: 2
    Input Channels: 0
    ✓ Suitable for system audio capture

RECOMMENDATIONS:
For system audio capture, use one of these device indices:
  - Device [1]: CABLE Output (VB-Audio Virtual Cable)

To use a device, set AUDIO_DEVICE_INDEX in your .env file:
  AUDIO_DEVICE_INDEX=1
```

#### 2. Extract Cookies (`helper_extract_cookies.py`)

Interactive script that helps you extract Google authentication cookies from Chrome.

```bash
python helper_extract_cookies.py [--output cookies.pkl]
```

**What it does**:
1. Launches Chrome browser
2. Navigates to Google accounts page
3. Waits for you to log in (if not already logged in)
4. Extracts and saves authentication cookies
5. Saves cookies to the specified file

**Usage**:
```bash
# Save to default location (cookies.pkl)
python helper_extract_cookies.py

# Save to custom location
python helper_extract_cookies.py --output my_cookies.pkl
```

**Security Note**: The cookie file contains sensitive authentication data. Never commit it to version control and keep it secure.

#### 3. Validate Configuration (`helper_validate_config.py`)

Validates your complete MeetDocs AI configuration and checks that all required dependencies and files are properly set up.

```bash
python helper_validate_config.py [--env-file .env]
```

**What it checks**:
- Python version (3.8+)
- Required Python packages
- Environment variables and configuration
- Cookie file existence
- Gemini API key
- Audio device availability
- Directory structure

**Example output**:
```
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
...

================================================================================
4. Configuration Values
================================================================================
✓ COOKIE_PATH: ./cookies.pkl (exists)
✓ GEMINI_API_KEY: Set
✓ AUDIO_DEVICE_INDEX: 1
✓ WHISPER_MODEL_SIZE: base (valid)
...

================================================================================
Validation Summary
================================================================================
✓ All checks passed! Configuration is valid.

You're ready to run MeetDocs AI:
  python main.py <google-meet-url>
```

**Usage with custom .env file**:
```bash
python helper_validate_config.py --env-file production.env
```

#### Quick Setup Workflow

For first-time setup, run the helper scripts in this order:

```bash
# 1. List audio devices and note the correct index
python helper_list_devices.py

# 2. Extract Google authentication cookies
python helper_extract_cookies.py

# 3. Configure your .env file with the information from steps 1-2
# Edit .env and set:
#   - AUDIO_DEVICE_INDEX=<index from step 1>
#   - COOKIE_PATH=cookies.pkl
#   - GEMINI_API_KEY=<your API key>

# 4. Validate your configuration
python helper_validate_config.py

# 5. If validation passes, you're ready to run MeetDocs AI!
python main.py <google-meet-url>
```

#### Test Audio Recording

```bash
python examples/test_audio_capture.py
```

Records a 10-second test clip to verify audio setup.

## Troubleshooting

### Common Issues and Solutions

#### 1. ChromeDriver Issues

**Problem**: `SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version X`

**Solution**:
- Update Google Chrome to the latest version
- Delete cached ChromeDriver: `rm -rf ~/.wdm/` (Linux/macOS) or `rmdir /s %USERPROFILE%\.wdm\` (Windows)
- Run the script again to download matching ChromeDriver

**Problem**: `WebDriverException: Message: 'chromedriver' executable needs to be in PATH`

**Solution**:
- The `webdriver-manager` package should handle this automatically
- Ensure you have internet connection for first-time download
- Try manual installation: `pip install --upgrade webdriver-manager`

#### 2. Audio Capture Issues

**Problem**: No audio is being recorded / Empty audio files

**Solution**:
- Verify virtual audio cable is installed and configured
- Check system audio output is routed through virtual cable
- List devices: `python -c "import sounddevice as sd; print(sd.query_devices())"`
- Ensure you're using the correct device index (look for "CABLE Output", "BlackHole", or "monitor")
- Test with: `python examples/test_audio_capture.py`

**Problem**: `PortAudioError: Error opening audio device`

**Solution**:
- The device index may be incorrect
- Run device listing script to find correct index
- Try different device indices
- Restart the virtual audio cable driver
- On Linux, check PulseAudio is running: `pulseaudio --check`

**Problem**: Audio is choppy or has gaps

**Solution**:
- Increase buffer size in `audio_capture.py`
- Close other audio applications
- Check CPU usage (Whisper transcription is CPU-intensive)
- Use a smaller Whisper model (`tiny` or `base`)

#### 3. Authentication Issues

**Problem**: `Unable to join meeting - authentication failed`

**Solution**:
- Cookies may have expired - extract fresh cookies
- Ensure you're logged into the correct Google account
- Try logging into Google Meet manually in Chrome first
- Verify `cookies.pkl` file exists and is not empty
- Check cookie file path in `.env` is correct

**Problem**: Meeting requires approval but bot doesn't join

**Solution**:
- The meeting host needs to approve the join request
- Check logs for "Waiting for approval" message
- Ensure the account has permission to join the meeting
- Try joining with a different Google account

#### 4. Whisper/Transcription Issues

**Problem**: `ModuleNotFoundError: No module named 'whisper'`

**Solution**:
```bash
pip install openai-whisper
```

**Problem**: `RuntimeError: Couldn't load Whisper model`

**Solution**:
- First run downloads the model (can take several minutes)
- Ensure stable internet connection
- Check available disk space (models are 100MB-3GB)
- Try a smaller model: `--model-size tiny`
- Manual download: `python -c "import whisper; whisper.load_model('base')"`

**Problem**: Transcription is very slow

**Solution**:
- Use a smaller model: `--model-size tiny` or `base`
- Enable GPU acceleration (requires CUDA-capable GPU)
- Install PyTorch with CUDA: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`
- Close other applications to free up RAM

**Problem**: Transcription is inaccurate

**Solution**:
- Use a larger model: `--model-size medium` or `large`
- Ensure audio quality is good (check virtual audio cable setup)
- Verify correct language is being detected
- Check for background noise in recordings

#### 5. Translation Issues

**Problem**: `AttributeError: 'NoneType' object has no attribute 'text'`

**Solution**:
- Translation service may be temporarily unavailable
- Check internet connection
- The system will fall back to original text
- Try again after a few minutes

**Problem**: Translation is incorrect or garbled

**Solution**:
- This is a limitation of the free googletrans library
- Consider upgrading to Google Cloud Translation API
- Check source language detection is correct
- For English-only meetings, use `--no-translate`

#### 6. Gemini API Issues

**Problem**: `google.api_core.exceptions.PermissionDenied: 403 API key not valid`

**Solution**:
- Verify API key in `.env` file is correct
- Ensure no extra spaces or quotes around the key
- Generate a new API key at [ai.google.dev](https://ai.google.dev/)
- Check API key has Gemini API enabled

**Problem**: `ResourceExhausted: 429 Quota exceeded`

**Solution**:
- You've hit the free tier limit
- Wait for quota to reset (usually daily)
- Upgrade to paid tier for higher limits
- The system will provide raw transcript as fallback

**Problem**: Summary is incomplete or poorly formatted

**Solution**:
- Transcript may be too long for API limits
- Try shorter meetings or split processing
- Check transcript quality (improve audio/transcription first)
- Adjust prompt in `summarizer.py` for better results

#### 7. DOCX Export Issues

**Problem**: `PermissionError: [Errno 13] Permission denied`

**Solution**:
- Output file may be open in Word/another program
- Close the file and try again
- Check write permissions on output directory
- Try a different output directory: `--output-dir ~/Documents`

**Problem**: DOCX file is corrupted or won't open

**Solution**:
- Check logs for errors during export
- Ensure `python-docx` is installed: `pip install python-docx`
- Verify summary structure is valid
- Try opening with different programs (LibreOffice, Google Docs)

#### 8. General Issues

**Problem**: `ImportError: No module named 'X'`

**Solution**:
```bash
pip install -r requirements.txt
```

**Problem**: Script crashes with no error message

**Solution**:
- Run with debug logging: `--log-level DEBUG`
- Check logs in `logs/meetdocs_errors.log`
- Ensure all prerequisites are installed
- Check system resources (RAM, disk space)

**Problem**: Process hangs or becomes unresponsive

**Solution**:
- Press `Ctrl+C` to stop gracefully
- Check if Whisper is processing (CPU-intensive)
- Monitor system resources
- Try with smaller Whisper model
- Check network connectivity for API calls

#### 9. Platform-Specific Issues

**Windows**:
- Use forward slashes in paths or raw strings: `r"C:\path\to\file"`
- Run Command Prompt as Administrator if permission issues occur
- Disable antivirus temporarily if it blocks ChromeDriver

**macOS**:
- Grant accessibility permissions: System Preferences → Security & Privacy → Accessibility
- Allow Chrome in Security settings if blocked
- Use `brew` for easier dependency management

**Linux**:
- Install Chrome dependencies: `sudo apt-get install -f`
- For headless servers, use Xvfb: `xvfb-run python main.py <url>`
- Check PulseAudio is running: `pulseaudio --start`

### Getting Help

If you encounter issues not covered here:

1. Check the logs in `logs/meetdocs.log` and `logs/meetdocs_errors.log`
2. Run with debug logging: `--log-level DEBUG`
3. Search existing issues on GitHub
4. Create a new issue with:
   - Error message and full traceback
   - Your OS and Python version
   - Steps to reproduce
   - Relevant log excerpts

## Features

- ✅ Automated Google Meet joining with cookie-based authentication
- ✅ System audio capture in 30-second chunks
- ✅ Multi-language transcription (Hindi, Marathi, English) using Whisper
- ✅ Automatic translation to English
- ✅ AI-powered meeting summaries with structured sections
- ✅ Professional DOCX export with formatting
- ✅ Comprehensive error handling and logging
- ✅ Cross-platform support (Windows, macOS, Linux)
- ✅ Modular architecture for easy customization
- ✅ Property-based testing for correctness

## Testing

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/test_*.py -v

# Property-based tests only
pytest tests/test_properties_*.py -v

# With coverage report
pytest --cov=src --cov-report=html tests/
```

### Run Example Scripts

```bash
# Test individual modules
python examples/test_audio_capture.py
python examples/test_transcriber.py
python examples/test_translator.py
python examples/test_summarizer.py
python examples/test_exporter.py

# Test full pipeline
python examples/test_summarizer_to_exporter.py
```

## Architecture

MeetDocs AI follows a modular pipeline architecture:

```
Meet Joiner → Audio Capturer → Transcriber → Translator → Summarizer → Exporter
```

Each module is independent and can be tested/used separately. See individual module documentation in `docs/` for details.

## Performance Notes

- **Whisper Models**: 
  - `tiny`: Fastest, lowest accuracy (~1GB RAM)
  - `base`: Balanced, recommended default (~1GB RAM)
  - `small`: Better accuracy (~2GB RAM)
  - `medium`: High accuracy (~5GB RAM, GPU recommended)
  - `large`: Best accuracy (~10GB RAM, GPU required)

- **Processing Time**: 
  - Real-time audio capture (no overhead)
  - Transcription: ~1-2x meeting duration (depends on model)
  - Translation: ~10-30 seconds
  - Summarization: ~5-15 seconds
  - Export: <1 second

- **Resource Usage**:
  - Audio files: ~10MB per minute
  - Whisper model: 100MB-3GB (one-time download)
  - Peak RAM: 2-10GB (depends on Whisper model)

## Security and Privacy

- **Credentials**: Never hardcoded; uses cookie-based authentication
- **API Keys**: Stored in `.env` file (not committed to git)
- **Data Storage**: All data stored locally by default
- **Network**: Only connects to Google Meet, Google Translate, and Gemini API
- **Cookies**: Stored in `cookies.pkl` (add to `.gitignore`)

**Important**: 
- Do not commit `.env` or `cookies.pkl` to version control
- Rotate API keys regularly
- Use separate Google account for automation if concerned about security
- Review generated summaries before sharing (may contain sensitive information)

## Limitations

- Requires stable internet connection
- Google Meet session must remain active
- Translation quality depends on googletrans service
- Gemini API has rate limits on free tier
- Whisper accuracy varies by audio quality and language
- Cannot capture video, only audio
- Requires manual cookie extraction initially

## Future Enhancements

- Real-time transcription display
- Speaker diarization (identify different speakers)
- Custom summary templates
- Multiple meeting support
- Cloud storage integration (Google Drive, Dropbox)
- Slack/Email integration for auto-sending summaries
- Meeting analytics (duration, speaker time, sentiment)
- Video recording capability
- Calendar integration for auto-joining scheduled meetings
- Mobile app for notifications

## License

[To be determined]

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## Acknowledgments

- OpenAI Whisper for speech recognition
- Google Gemini for AI summarization
- Selenium for browser automation
- All open-source contributors

## Support

For questions, issues, or feature requests, please open an issue on GitHub.
