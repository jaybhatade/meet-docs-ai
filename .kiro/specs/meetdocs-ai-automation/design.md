# Design Document

## Overview

MeetDocs AI is a Python-based automation system that provides end-to-end meeting documentation. The system uses Selenium for browser automation, audio capture libraries for recording, OpenAI Whisper for transcription, Google Translate for language translation, Google Gemini for AI summarization, and python-docx for document generation. The architecture follows a modular pipeline design where each component operates independently and passes data to the next stage.

## Architecture

The system follows a linear pipeline architecture with six main components:

```
[Meet Joiner] → [Audio Capturer] → [Transcriber] → [Translator] → [Summarizer] → [Exporter]
```

### Component Flow

1. **Meet Joiner**: Launches Chrome via Selenium, authenticates using cookies, joins the meeting
2. **Audio Capturer**: Runs concurrently with the meeting, captures system audio in 30-second chunks
3. **Transcriber**: Processes audio chunks using Whisper, outputs raw multilingual text
4. **Translator**: Detects and translates Hindi/Marathi content to English
5. **Summarizer**: Sends transcript to Gemini API, receives structured summary
6. **Exporter**: Formats summary into professional DOCX document

### Technology Stack

- **Browser Automation**: Selenium WebDriver with ChromeDriver
- **Audio Capture**: sounddevice + soundfile (cross-platform compatibility)
- **Speech-to-Text**: OpenAI Whisper (whisper library)
- **Translation**: googletrans library
- **AI Summarization**: Google Gemini API (google-generativeai)
- **Document Export**: python-docx
- **Logging**: Python logging module
- **CLI**: argparse for command-line interface

## Components and Interfaces

### 1. Meet Joiner Module (`meet_joiner.py`)

**Purpose**: Automate Google Meet session joining using Selenium

**Key Classes**:
- `MeetJoiner`: Main class handling browser automation

**Key Methods**:
- `__init__(cookie_path: str)`: Initialize with path to saved cookies
- `load_cookies()`: Load authentication cookies from file
- `join_meeting(meet_url: str) -> bool`: Join the specified meeting
- `disable_av()`: Disable camera and microphone
- `click_join_button()`: Handle join/ask-to-join scenarios
- `is_in_meeting() -> bool`: Verify successful meeting entry
- `leave_meeting()`: Clean exit from meeting
- `close()`: Close browser and cleanup

**Dependencies**: selenium, webdriver_manager

**Error Handling**:
- Cookie file not found
- Invalid Meet URL
- Authentication failure
- Join button not found
- Network connectivity issues

### 2. Audio Capture Module (`audio_capture.py`)

**Purpose**: Capture system audio during the meeting

**Key Classes**:
- `AudioCapturer`: Manages audio recording

**Key Methods**:
- `__init__(output_dir: str, chunk_duration: int = 30)`: Initialize with output directory
- `list_audio_devices() -> list`: Display available audio devices
- `start_capture(device_index: int)`: Begin recording from specified device
- `stop_capture()`: Stop recording and finalize files
- `_save_chunk(audio_data: np.ndarray, chunk_number: int)`: Save individual chunk
- `get_audio_files() -> list`: Return list of captured audio files

**Dependencies**: sounddevice, soundfile, numpy

**Audio Format**:
- Sample Rate: 44100 Hz
- Channels: Stereo (2)
- Format: WAV (16-bit PCM)
- Chunk Size: 30 seconds

**Error Handling**:
- Audio device not available
- Insufficient disk space
- Audio buffer overflow
- Device disconnection during recording

### 3. Transcriber Module (`transcriber.py`)

**Purpose**: Convert audio to text using Whisper

**Key Classes**:
- `Transcriber`: Handles speech-to-text conversion

**Key Methods**:
- `__init__(model_size: str = "base", output_file: str = "transcript.txt")`: Initialize Whisper model
- `load_model()`: Load Whisper model into memory
- `transcribe_file(audio_path: str) -> dict`: Transcribe single audio file
- `transcribe_batch(audio_files: list) -> str`: Process multiple files
- `save_transcript(text: str)`: Append to consolidated transcript file
- `get_full_transcript() -> str`: Return complete transcript

**Dependencies**: openai-whisper, torch

**Whisper Configuration**:
- Model: base (balance of speed and accuracy)
- Languages: Hindi (hi), Marathi (mr), English (en)
- Task: transcribe (not translate)
- Output: text with language detection

**Error Handling**:
- Whisper model not installed
- Insufficient GPU/CPU memory
- Corrupted audio files
- Unsupported audio format

### 4. Translator Module (`translator.py`)

**Purpose**: Translate non-English content to English

**Key Classes**:
- `Translator`: Manages translation operations

**Key Methods**:
- `__init__()`: Initialize translator
- `detect_language(text: str) -> str`: Identify text language
- `needs_translation(text: str) -> bool`: Check if translation required
- `translate_to_english(text: str) -> str`: Perform translation
- `process_transcript(transcript: str) -> str`: Process full transcript
- `_clean_text(text: str) -> str`: Remove artifacts and formatting issues

**Dependencies**: googletrans==4.0.0rc1

**Translation Logic**:
- Detect language for each paragraph/sentence
- Translate only Hindi/Marathi content
- Preserve English content as-is
- Handle mixed-language text

**Error Handling**:
- Network timeout during translation
- API rate limiting
- Unsupported language detection
- Translation service unavailable

### 5. Summarizer Module (`summarizer.py`)

**Purpose**: Generate structured meeting summary using Gemini AI

**Key Classes**:
- `Summarizer`: Interfaces with Gemini API

**Key Methods**:
- `__init__(api_key: str)`: Initialize with Gemini API key
- `generate_summary(transcript: str) -> dict`: Create structured summary
- `_build_prompt(transcript: str) -> str`: Construct Gemini prompt
- `_parse_response(response: str) -> dict`: Extract structured data
- `get_fallback_summary(transcript: str) -> dict`: Provide basic summary if API fails

**Dependencies**: google-generativeai

**Summary Structure**:
```python
{
    "title": str,
    "participants": list[str],
    "key_points": list[str],
    "action_items": list[str],
    "decisions": list[str],
    "follow_ups": list[str]
}
```

**Gemini Prompt Template**:
```
Analyze the following meeting transcript and provide a structured summary:

[TRANSCRIPT]

Please provide:
1. Meeting Title (infer from context)
2. Participants (list names mentioned)
3. Key Discussion Points (bullet points)
4. Action Items (who does what)
5. Decisions Taken (what was decided)
6. Follow-up Tasks (next steps)

Format as JSON.
```

**Error Handling**:
- API key invalid or missing
- API quota exceeded
- Network connectivity issues
- Malformed API response
- Transcript too long for API limits

### 6. Exporter Module (`exporter.py`)

**Purpose**: Create formatted DOCX document

**Key Classes**:
- `DocxExporter`: Handles document generation

**Key Methods**:
- `__init__(output_dir: str)`: Initialize with output directory
- `create_document(summary: dict) -> str`: Generate DOCX file
- `_add_title(doc, title: str)`: Add formatted title
- `_add_section(doc, heading: str, content: list)`: Add section with bullets
- `_generate_filename() -> str`: Create timestamped filename
- `_apply_formatting(doc)`: Apply professional styling

**Dependencies**: python-docx

**Document Formatting**:
- Title: Heading 1, Bold, 16pt
- Section Headers: Heading 2, Bold, 14pt
- Body Text: Normal, 11pt, Calibri
- Bullet Points: Standard bullets with 0.5" indent
- Spacing: 1.15 line spacing, 6pt after paragraphs

**Output Filename Format**: `meeting_summary_YYYYMMDD_HHMMSS.docx`

**Error Handling**:
- Output directory not writable
- Disk space insufficient
- Invalid summary structure
- Document corruption during save

### 7. Main Orchestrator (`main.py`)

**Purpose**: Coordinate pipeline execution

**Key Functions**:
- `parse_arguments() -> argparse.Namespace`: Parse CLI arguments
- `validate_meet_url(url: str) -> bool`: Validate Google Meet URL format
- `setup_logging(log_level: str)`: Configure logging
- `run_pipeline(meet_url: str, config: dict) -> str`: Execute full pipeline
- `cleanup(joiner, capturer)`: Ensure proper resource cleanup

**CLI Arguments**:
- `meet_url` (required): Google Meet URL
- `--cookie-path`: Path to cookies file (default: ./cookies.pkl)
- `--audio-device`: Audio device index (default: auto-detect)
- `--model-size`: Whisper model size (default: base)
- `--gemini-key`: Gemini API key (default: from env var)
- `--output-dir`: Output directory (default: ./output)
- `--log-level`: Logging level (default: INFO)

**Pipeline Execution Flow**:
1. Validate inputs and configuration
2. Initialize all modules
3. Join meeting (Meet Joiner)
4. Start audio capture (Audio Capturer)
5. Wait for meeting to end or user interrupt
6. Stop audio capture
7. Transcribe audio chunks (Transcriber)
8. Translate to English (Translator)
9. Generate summary (Summarizer)
10. Export to DOCX (Exporter)
11. Cleanup resources
12. Report output file path

## Data Models

### Configuration Model
```python
@dataclass
class Config:
    cookie_path: str
    audio_device_index: int
    whisper_model_size: str
    gemini_api_key: str
    output_dir: str
    audio_dir: str
    transcript_dir: str
    log_level: str
```

### Audio Chunk Model
```python
@dataclass
class AudioChunk:
    chunk_number: int
    file_path: str
    duration: float
    sample_rate: int
    channels: int
```

### Transcription Model
```python
@dataclass
class Transcription:
    text: str
    language: str
    confidence: float
    chunk_number: int
```

### Summary Model
```python
@dataclass
class MeetingSummary:
    title: str
    participants: List[str]
    key_points: List[str]
    action_items: List[str]
    decisions: List[str]
    follow_ups: List[str]
    timestamp: datetime
```

## 
Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

After analyzing the acceptance criteria, I've identified the following properties that can be validated through property-based testing. Some criteria relate to documentation, code organization, or subjective quality measures which are not suitable for automated testing.

### Property Reflection

Before listing the properties, I've reviewed all testable criteria to eliminate redundancy:
- Properties 1.1 and 8.1 both relate to URL validation - these will be combined into a single comprehensive URL validation property
- Properties 2.2 and 2.3 both test audio file creation - these will be combined into a single property about audio chunk generation
- Properties 3.3 and 3.5 both test transcript file management - these will be combined into a single property about chronological transcript assembly
- Properties 6.3 and 6.4 both test filename generation - these will be combined into a single property about unique timestamped filenames

### Core Properties

**Property 1: URL validation and navigation**
*For any* valid Google Meet URL format, the Meet Joiner should successfully parse the URL and navigate the browser to that location
**Validates: Requirements 1.1, 8.1**

**Property 2: Cookie-based authentication**
*For any* saved cookie file with valid authentication data, the Meet Joiner should successfully authenticate without requiring credential input
**Validates: Requirements 1.2**

**Property 3: AV device state before join**
*For any* meeting join attempt, the camera and microphone elements should be in disabled state before the join button is clicked
**Validates: Requirements 1.3**

**Property 4: Conditional join behavior**
*For any* meeting room configuration, the Meet Joiner should either click "Join now" for open meetings or handle "Ask to join" for restricted meetings
**Validates: Requirements 1.4**

**Property 5: Session persistence**
*For any* successfully joined meeting, the browser session should remain active and connected until explicitly terminated
**Validates: Requirements 1.5**

**Property 6: Audio source selection**
*For any* audio capture session, the selected audio device should be a system output device, not an input/microphone device
**Validates: Requirements 2.1**

**Property 7: Audio chunk generation**
*For any* audio capture session, generated WAV files should be approximately 30 seconds in duration, stored in the audio directory with sequential naming
**Validates: Requirements 2.2, 2.3**

**Property 8: Audio device error recovery**
*For any* audio device error or disconnection, the system should log the error and attempt reconnection
**Validates: Requirements 2.4**

**Property 9: Partial chunk finalization**
*For any* audio capture session that ends mid-chunk, the remaining audio data should be saved as a final chunk file
**Validates: Requirements 2.5**

**Property 10: Whisper model invocation**
*For any* set of audio files, the Transcriber should invoke Whisper processing on each file exactly once
**Validates: Requirements 3.1**

**Property 11: Multilingual transcription**
*For any* audio content in Hindi, Marathi, or English, the Transcriber should produce text output in the detected language
**Validates: Requirements 3.2**

**Property 12: Chronological transcript assembly**
*For any* sequence of audio chunks processed in any order, the consolidated transcript file should contain transcriptions in chronological order by chunk number
**Validates: Requirements 3.3, 3.5**

**Property 13: Language detection accuracy**
*For any* text containing Hindi or Marathi characters, the Translator should correctly detect the presence of non-English content
**Validates: Requirements 4.1**

**Property 14: Translation invocation**
*For any* text detected as Hindi or Marathi, the Translator should invoke the translation API
**Validates: Requirements 4.2**

**Property 15: Translation output cleanliness**
*For any* translated text, the output should not contain language detection markers, translation artifacts, or formatting remnants
**Validates: Requirements 4.3**

**Property 16: English text identity**
*For any* text that is entirely in English, the Translator output should be identical to the input
**Validates: Requirements 4.4**

**Property 17: Gemini API invocation**
*For any* complete transcript, the Summarizer should send the text to the Gemini API for processing
**Validates: Requirements 5.1**

**Property 18: Summary structure completeness**
*For any* generated summary, the output should contain all required sections: Meeting Title, Participants, Key Discussion Points, Action Items, Decisions Taken, and Follow-up Tasks
**Validates: Requirements 5.2**

**Property 19: Participant extraction**
*For any* transcript containing person names, the generated summary should include those names in the Participants section
**Validates: Requirements 5.4**

**Property 20: DOCX document creation**
*For any* meeting summary, the Exporter should create a valid DOCX file that can be opened by document readers
**Validates: Requirements 6.1**

**Property 21: Document style application**
*For any* generated DOCX document, the meeting title should have Heading 1 style, section headers should have Heading 2 style, and list items should be formatted as bullets
**Validates: Requirements 6.2**

**Property 22: Unique timestamped filenames**
*For any* two summaries generated at different times, the filenames should be unique and include timestamps in the format meeting_summary_YYYYMMDD_HHMMSS.docx
**Validates: Requirements 6.3, 6.4**

**Property 23: Output directory creation**
*For any* export operation where the output directory does not exist, the Exporter should create the directory before saving the file
**Validates: Requirements 6.5**

**Property 24: Directory structure maintenance**
*For any* pipeline execution, the system should maintain separate directories for audio files, transcripts, and output documents
**Validates: Requirements 7.2**

**Property 25: Error logging completeness**
*For any* module error, the log entry should contain the module name, error type, and timestamp
**Validates: Requirements 7.3**

**Property 26: Pipeline execution sequence**
*For any* pipeline run, modules should execute in the order: join meeting, capture audio, transcribe, translate, summarize, export
**Validates: Requirements 8.2**

**Property 27: Stage completion logging**
*For any* completed pipeline stage, a log entry should be created before proceeding to the next stage
**Validates: Requirements 8.3**

**Property 28: Pipeline error handling**
*For any* pipeline stage failure, the system should log the failure and notify the user
**Validates: Requirements 8.4**

**Property 29: Output path reporting**
*For any* successful pipeline completion, the system should output the absolute path to the generated DOCX file
**Validates: Requirements 8.5**

### Edge Case Examples

The following are specific edge cases that should be tested with example-based tests:

**Example 1: Missing Whisper model**
When the Whisper model is not installed, the system should display installation instructions
**Validates: Requirements 3.4**

**Example 2: Translation network failure**
When translation fails due to network errors, the system should retain original text with a warning marker
**Validates: Requirements 4.5**

**Example 3: Gemini API unavailable**
When the Gemini API is unavailable, the system should provide the raw transcript as fallback
**Validates: Requirements 5.5**

## Error Handling

### Error Categories

1. **Setup Errors**: Missing dependencies, invalid configuration, authentication failures
2. **Runtime Errors**: Network issues, device disconnections, API failures
3. **Data Errors**: Corrupted audio files, invalid transcripts, malformed API responses
4. **Resource Errors**: Insufficient disk space, memory limitations, file permission issues

### Error Handling Strategy

**Graceful Degradation**:
- If Gemini API fails, provide raw transcript
- If translation fails, keep original text with warning
- If audio chunk fails, continue with remaining chunks

**Retry Logic**:
- Audio device reconnection: 3 attempts with exponential backoff
- API calls: 2 retries with 5-second delay
- Network operations: 3 retries with increasing timeout

**User Notification**:
- Critical errors: Immediate console output + log entry
- Warnings: Log entry only
- Info: Optional verbose logging

**Cleanup Guarantees**:
- Browser always closed on exit
- Audio capture always stopped
- Temporary files always cleaned up
- Partial results always saved

### Logging Strategy

**Log Levels**:
- DEBUG: Detailed execution flow, variable values
- INFO: Pipeline stage transitions, file operations
- WARNING: Recoverable errors, fallback activations
- ERROR: Unrecoverable errors, pipeline failures
- CRITICAL: System-level failures requiring immediate attention

**Log Format**:
```
[TIMESTAMP] [LEVEL] [MODULE] [FUNCTION] - MESSAGE
```

**Log Locations**:
- Console: INFO and above
- File (meetdocs.log): DEBUG and above
- Error file (meetdocs_errors.log): ERROR and above

## Testing Strategy

### Unit Testing

The system will use pytest for unit testing. Unit tests will focus on:

**Module Initialization**:
- Configuration loading and validation
- Dependency availability checks
- Resource initialization

**Core Functions**:
- URL validation logic
- Audio chunk file naming
- Language detection algorithms
- Filename generation with timestamps
- Directory creation logic

**Error Handling**:
- Exception raising for invalid inputs
- Fallback behavior activation
- Cleanup execution on failures

**Integration Points**:
- Module communication interfaces
- Data format conversions
- File I/O operations

### Property-Based Testing

The system will use Hypothesis for property-based testing in Python. Each property-based test will:

- Run a minimum of 100 iterations with randomly generated inputs
- Be tagged with a comment explicitly referencing the correctness property from this design document
- Use the format: `# Feature: meetdocs-ai-automation, Property X: [property text]`
- Test one correctness property per test function

**Property Test Coverage**:

Each of the 29 correctness properties listed above will be implemented as a separate property-based test. The tests will use Hypothesis strategies to generate:

- Random valid Google Meet URLs
- Various audio file configurations
- Text samples in Hindi, Marathi, and English
- Different meeting summary structures
- Various error conditions

**Example Property Test Structure**:
```python
from hypothesis import given, strategies as st

# Feature: meetdocs-ai-automation, Property 16: English text identity
@given(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=10))
def test_english_text_passthrough(english_text):
    """For any text that is entirely in English, 
    the Translator output should be identical to the input"""
    translator = Translator()
    result = translator.translate_to_english(english_text)
    assert result == english_text
```

**Property Test Configuration**:
- Minimum iterations: 100 per test
- Timeout: 60 seconds per test
- Shrinking: Enabled for failure case minimization
- Seed: Randomized (logged for reproducibility)

### Test Organization

```
tests/
├── unit/
│   ├── test_meet_joiner.py
│   ├── test_audio_capture.py
│   ├── test_transcriber.py
│   ├── test_translator.py
│   ├── test_summarizer.py
│   └── test_exporter.py
├── property/
│   ├── test_properties_meet_joiner.py
│   ├── test_properties_audio.py
│   ├── test_properties_transcription.py
│   ├── test_properties_translation.py
│   ├── test_properties_summary.py
│   ├── test_properties_export.py
│   └── test_properties_pipeline.py
├── fixtures/
│   ├── sample_audio/
│   ├── sample_transcripts/
│   └── sample_cookies/
└── conftest.py
```

### Testing Dependencies

- pytest: Test framework
- pytest-cov: Coverage reporting
- hypothesis: Property-based testing
- pytest-mock: Mocking support for external dependencies
- pytest-timeout: Test timeout management

### Continuous Testing

- All tests run before commits (pre-commit hook)
- Property tests run with 100 iterations in CI/CD
- Coverage target: 80% for core modules
- Critical path coverage: 100%

## Implementation Notes

### ChromeDriver Management

Use webdriver-manager to automatically download and manage ChromeDriver versions:
```python
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
```

### Cookie Management

Cookies should be saved using pickle after manual login:
```python
import pickle

# Save cookies after manual login
pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))

# Load cookies for automation
cookies = pickle.load(open("cookies.pkl", "rb"))
for cookie in cookies:
    driver.add_cookie(cookie)
```

### Audio Device Selection

Provide helper function to list available devices:
```python
import sounddevice as sd

def list_audio_devices():
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if device['max_output_channels'] > 0:
            print(f"{idx}: {device['name']}")
```

### Whisper Model Selection

Model size recommendations:
- tiny: Fastest, lowest accuracy (good for testing)
- base: Balanced (recommended default)
- small: Better accuracy, slower
- medium: High accuracy, requires GPU
- large: Best accuracy, requires powerful GPU

### Gemini API Configuration

```python
import google.generativeai as genai

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')
```

### Directory Structure

```
meetdocs-ai/
├── src/
│   ├── __init__.py
│   ├── meet_joiner.py
│   ├── audio_capture.py
│   ├── transcriber.py
│   ├── translator.py
│   ├── summarizer.py
│   ├── exporter.py
│   └── config.py
├── tests/
│   ├── unit/
│   ├── property/
│   └── fixtures/
├── audio/
├── transcripts/
├── output/
├── logs/
├── main.py
├── requirements.txt
├── README.md
├── .env.example
└── cookies.pkl (user-generated)
```

### Configuration Management

Use environment variables and .env file:
```
GEMINI_API_KEY=your_api_key_here
COOKIE_PATH=./cookies.pkl
AUDIO_DEVICE_INDEX=1
WHISPER_MODEL_SIZE=base
OUTPUT_DIR=./output
LOG_LEVEL=INFO
```

### Performance Considerations

- Audio capture runs in separate thread to avoid blocking
- Transcription processes chunks as they're created (streaming)
- Translation batches multiple paragraphs for efficiency
- DOCX generation uses streaming write for large documents
- Implement progress indicators for long-running operations

### Security Considerations

- Never commit cookies.pkl or .env files
- Store API keys in environment variables only
- Validate all user inputs before processing
- Sanitize filenames to prevent path traversal
- Use HTTPS for all API communications
- Clear sensitive data from memory after use

### Platform-Specific Notes

**Windows**:
- Use VB-Audio Virtual Cable for system audio capture
- ChromeDriver path may need explicit setting
- Use forward slashes in paths or raw strings

**macOS**:
- Use BlackHole for system audio routing
- May require accessibility permissions for Selenium
- Use Homebrew for dependency installation

**Linux**:
- Use PulseAudio loopback for audio capture
- May require xvfb for headless operation
- Ensure Chrome/Chromium is installed

## Future Enhancements

1. **Real-time Transcription**: Display transcription during meeting
2. **Speaker Diarization**: Identify different speakers in transcript
3. **Custom Summary Templates**: Allow user-defined summary formats
4. **Multiple Meeting Support**: Join and record multiple meetings simultaneously
5. **Cloud Storage Integration**: Auto-upload to Google Drive/Dropbox
6. **Slack/Email Integration**: Auto-send summaries to team channels
7. **Meeting Analytics**: Track meeting duration, speaker time, sentiment
8. **Video Recording**: Capture screen alongside audio
9. **Calendar Integration**: Auto-join scheduled meetings
10. **Mobile App**: iOS/Android companion app for notifications
