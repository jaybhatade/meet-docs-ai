# Transcriber Module Implementation

## Overview

The Transcriber module converts audio files to text using OpenAI Whisper with support for multilingual transcription (Hindi, Marathi, English). It handles batch processing, chronological transcript assembly, and consolidated transcript file management.

## Features

- **Whisper Model Loading**: Automatic model loading with comprehensive error handling
- **Single File Transcription**: Process individual audio files with language detection
- **Batch Processing**: Handle multiple audio chunks efficiently
- **Chronological Assembly**: Maintain correct order of transcriptions
- **Progress Logging**: Detailed logging for long transcription operations
- **Error Recovery**: Graceful handling of corrupted or missing files

## Class: Transcriber

### Initialization

```python
from transcriber import Transcriber

transcriber = Transcriber(
    model_size="base",  # tiny, base, small, medium, large
    output_file="transcripts/transcript.txt"
)
```

### Methods

#### `load_model() -> bool`

Loads the Whisper model into memory. Must be called before transcription.

```python
try:
    transcriber.load_model()
    print("Model loaded successfully")
except RuntimeError as e:
    print(f"Failed to load model: {e}")
```

**Returns**: `True` if successful

**Raises**: `RuntimeError` if model fails to load with installation instructions

#### `transcribe_file(audio_path: str) -> Dict`

Transcribes a single audio file with automatic language detection.

```python
result = transcriber.transcribe_file("audio/chunk_001.wav")

print(f"Text: {result['text']}")
print(f"Language: {result['language']}")
print(f"Segments: {len(result['segments'])}")
```

**Parameters**:
- `audio_path`: Path to WAV audio file

**Returns**: Dictionary containing:
- `text`: Transcribed text
- `language`: Detected language code (hi, mr, en, etc.)
- `segments`: Detailed segment information
- `file`: Original file path

**Raises**:
- `RuntimeError`: If model not loaded
- `FileNotFoundError`: If audio file doesn't exist
- `Exception`: If transcription fails

#### `transcribe_batch(audio_files: List[str]) -> str`

Processes multiple audio files and returns consolidated transcript.

```python
audio_files = [
    "audio/chunk_001.wav",
    "audio/chunk_002.wav",
    "audio/chunk_003.wav"
]

full_transcript = transcriber.transcribe_batch(audio_files)
print(f"Complete transcript: {full_transcript}")
```

**Parameters**:
- `audio_files`: List of paths to audio files

**Returns**: Complete consolidated transcript as string

**Features**:
- Automatically extracts chunk numbers from filenames
- Sorts chunks chronologically
- Continues processing even if individual files fail
- Saves transcript to output file

#### `save_transcript(text: str) -> None`

Appends transcript text to the consolidated transcript file.

```python
transcriber.save_transcript("Additional transcript text...")
```

**Parameters**:
- `text`: Transcript text to save

**Features**:
- Creates parent directories if needed
- Appends to existing file
- Ensures proper line endings

#### `get_full_transcript() -> str`

Retrieves the complete transcript from the output file.

```python
transcript = transcriber.get_full_transcript()
print(f"Total length: {len(transcript)} characters")
```

**Returns**: Complete transcript content, or empty string if file doesn't exist

#### `get_transcript_chunks() -> List[Dict]`

Returns list of processed transcript chunks with metadata.

```python
chunks = transcriber.get_transcript_chunks()
for chunk in chunks:
    print(f"Chunk {chunk['chunk_number']}: {chunk['language']}")
```

**Returns**: List of dictionaries containing:
- `chunk_number`: Sequential chunk number
- `text`: Transcribed text
- `language`: Detected language
- `file`: Source audio file path

## Whisper Model Sizes

| Model | Speed | Accuracy | Memory | Use Case |
|-------|-------|----------|--------|----------|
| tiny | Fastest | Lowest | ~1 GB | Testing, quick drafts |
| base | Fast | Good | ~1 GB | **Recommended default** |
| small | Medium | Better | ~2 GB | Higher accuracy needed |
| medium | Slow | High | ~5 GB | Professional use (GPU) |
| large | Slowest | Best | ~10 GB | Maximum accuracy (GPU) |

## Supported Languages

The transcriber automatically detects and transcribes:
- **Hindi** (hi)
- **Marathi** (mr)
- **English** (en)

Whisper supports 99+ languages, but these three are the primary focus for MeetDocs AI.

## Transcript Format

The consolidated transcript file uses this format:

```
[Chunk 001] [en]
This is the transcribed text from the first audio chunk.

[Chunk 002] [hi]
यह दूसरे ऑडियो चंक से ट्रांसक्राइब किया गया टेक्स्ट है।

[Chunk 003] [mr]
हा तिसऱ्या ऑडिओ चंकमधून लिप्यंतरित मजकूर आहे।
```

## Error Handling

### Model Loading Errors

If Whisper is not installed or fails to load:

```python
try:
    transcriber.load_model()
except RuntimeError as e:
    print(e)  # Includes installation instructions
```

Error message includes:
- Specific error details
- Installation command: `pip install openai-whisper`
- GPU support instructions
- Model download information

### Transcription Errors

The batch processor continues even if individual files fail:

```python
# If chunk_002.wav is corrupted, processing continues with remaining files
audio_files = ["chunk_001.wav", "chunk_002.wav", "chunk_003.wav"]
transcript = transcriber.transcribe_batch(audio_files)
# Result includes chunks 001 and 003
```

### File Not Found

```python
try:
    result = transcriber.transcribe_file("missing.wav")
except FileNotFoundError as e:
    print(f"Audio file not found: {e}")
```

## Integration Example

Complete workflow integration:

```python
from pathlib import Path
from transcriber import Transcriber
from config import Config

# Load configuration
config = Config.from_env()

# Initialize transcriber
transcriber = Transcriber(
    model_size=config.whisper_model_size,
    output_file=Path(config.transcript_dir) / "meeting_transcript.txt"
)

# Load model
transcriber.load_model()

# Get audio files from audio capture
audio_dir = Path(config.audio_dir)
audio_files = sorted(audio_dir.glob("chunk_*.wav"))

# Transcribe all chunks
full_transcript = transcriber.transcribe_batch([str(f) for f in audio_files])

# Pass to translator
from translator import Translator
translator = Translator()
english_transcript = translator.process_transcript(full_transcript)
```

## Performance Considerations

### Processing Time

Approximate transcription speed (base model on CPU):
- 1 minute of audio ≈ 30-60 seconds processing time
- 30-second chunk ≈ 15-30 seconds processing time

### Memory Usage

- **tiny/base**: ~1 GB RAM
- **small**: ~2 GB RAM
- **medium**: ~5 GB RAM (GPU recommended)
- **large**: ~10 GB RAM (GPU required)

### GPU Acceleration

For faster processing, install PyTorch with CUDA:

```bash
# For CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Whisper automatically uses GPU if available.

## Logging

The transcriber provides detailed logging:

```
[2024-01-15 10:30:00] [INFO] [transcriber] [load_model] - Loading Whisper model: base
[2024-01-15 10:30:05] [INFO] [transcriber] [load_model] - Whisper model loaded successfully
[2024-01-15 10:30:05] [INFO] [transcriber] [transcribe_batch] - Starting batch transcription of 5 files
[2024-01-15 10:30:05] [INFO] [transcriber] [transcribe_batch] - Processing file 1/5: chunk_001.wav
[2024-01-15 10:30:15] [INFO] [transcriber] [transcribe_file] - Transcription complete: chunk_001.wav (language: en, length: 245 chars)
[2024-01-15 10:30:15] [INFO] [transcriber] [transcribe_batch] - Processing file 2/5: chunk_002.wav
...
[2024-01-15 10:31:30] [INFO] [transcriber] [save_transcript] - Transcript saved to: transcripts/meeting_transcript.txt
[2024-01-15 10:31:30] [INFO] [transcriber] [transcribe_batch] - Batch transcription complete: 5 files processed
```

## Testing

Run the example script:

```bash
python examples/test_transcriber.py
```

This will:
1. Load the Whisper model
2. Find audio files in the audio directory
3. Transcribe a single file
4. Process all files in batch
5. Display chunk information
6. Save consolidated transcript

## Requirements

Add to `requirements.txt`:

```
openai-whisper>=20231117
torch>=2.0.0
torchaudio>=2.0.0
```

## Troubleshooting

### "No module named 'whisper'"

```bash
pip install openai-whisper
```

### "Model not found"

Whisper downloads models automatically on first use. Ensure internet connection.

### "CUDA out of memory"

Use a smaller model size or switch to CPU:

```python
transcriber = Transcriber(model_size="tiny")  # or "base"
```

### Slow transcription

- Use GPU acceleration (install CUDA-enabled PyTorch)
- Use smaller model (tiny or base)
- Process fewer files at once

### Incorrect language detection

Whisper's language detection is generally accurate, but for short audio clips it may misidentify. The translator module handles this by detecting language in the text itself.

## Next Steps

After transcription, the transcript is passed to:
1. **Translator** - Converts Hindi/Marathi to English
2. **Summarizer** - Generates structured meeting summary
3. **Exporter** - Creates formatted DOCX document
