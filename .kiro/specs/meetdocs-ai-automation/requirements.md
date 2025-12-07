# Requirements Document

## Introduction

MeetDocs AI is an end-to-end Python automation tool that automatically joins Google Meet sessions, captures and transcribes audio in multiple languages (Hindi, Marathi, English), translates content to English, generates AI-powered meeting summaries, and exports professional documentation in DOCX format. The system provides a complete hands-free solution for meeting documentation and follow-up.

## Glossary

- **MeetDocs System**: The complete Python automation tool including all modules for meeting joining, recording, transcription, translation, summarization, and export
- **Meet Joiner**: The Selenium-based component that automates Google Meet session joining
- **Audio Capturer**: The component that captures system audio during meetings
- **Transcriber**: The Whisper-based component that converts audio to text
- **Translator**: The component that translates non-English text to English
- **Summarizer**: The Gemini API-based component that generates structured meeting summaries
- **Exporter**: The component that creates formatted DOCX documents
- **Audio Chunk**: A 30-second segment of captured audio saved as a WAV file
- **Raw Transcription**: The unprocessed text output from speech-to-text conversion
- **Meeting Summary**: A structured document containing title, participants, discussion points, action items, decisions, and follow-up tasks

## Requirements

### Requirement 1

**User Story:** As a meeting participant, I want the system to automatically join Google Meet sessions, so that I can focus on the meeting content without manual setup.

#### Acceptance Criteria

1. WHEN the user provides a Google Meet link as a command-line argument, THE Meet Joiner SHALL open a Google Chrome browser window and navigate to the provided URL
2. WHEN the Meet Joiner accesses Google Meet, THE Meet Joiner SHALL authenticate using saved browser cookies without requiring hardcoded credentials
3. WHEN the Meet Joiner enters a meeting room, THE Meet Joiner SHALL automatically disable both camera and microphone before joining
4. WHEN the meeting requires approval to join, THE Meet Joiner SHALL click the "Join now" button, and WHERE the meeting allows direct entry, THE Meet Joiner SHALL bypass the approval step
5. WHEN the Meet Joiner successfully enters the meeting, THE Meet Joiner SHALL remain active in the session until the meeting ends or the user terminates the process

### Requirement 2

**User Story:** As a meeting participant, I want the system to capture system audio during the meeting, so that all spoken content is recorded for transcription.

#### Acceptance Criteria

1. WHEN the meeting is active, THE Audio Capturer SHALL capture system audio output without recording microphone input
2. WHEN capturing audio, THE Audio Capturer SHALL save audio data in 30-second chunks as WAV files
3. WHEN an audio chunk is complete, THE Audio Capturer SHALL store the file in the designated audio directory with sequential naming
4. IF the audio device is unavailable or encounters an error, THEN THE Audio Capturer SHALL log the error and attempt to reconnect to the audio source
5. WHEN the meeting ends, THE Audio Capturer SHALL finalize and save any remaining audio data

### Requirement 3

**User Story:** As a meeting participant, I want the system to transcribe audio in multiple languages, so that content spoken in Hindi, Marathi, or English is converted to text.

#### Acceptance Criteria

1. WHEN an audio chunk is available, THE Transcriber SHALL process the audio file using the OpenAI Whisper local model
2. WHEN transcribing audio, THE Transcriber SHALL detect and transcribe content in Hindi, Marathi, and English languages
3. WHEN transcription is complete for a chunk, THE Transcriber SHALL append the raw transcription text to a single consolidated transcript file
4. IF the Whisper model is not found or fails to load, THEN THE Transcriber SHALL log the error and notify the user with specific installation instructions
5. WHEN processing multiple chunks, THE Transcriber SHALL maintain chronological order of transcriptions in the output file

### Requirement 4

**User Story:** As a meeting participant, I want non-English content automatically translated to English, so that I have a unified English transcript for documentation.

#### Acceptance Criteria

1. WHEN the Translator receives transcribed text, THE Translator SHALL detect the presence of Hindi or Marathi content
2. WHEN Hindi or Marathi content is detected, THE Translator SHALL translate the text to English using the googletrans module
3. WHEN translation is complete, THE Translator SHALL output clean English text without language markers or formatting artifacts
4. WHEN the transcribed text is already in English, THE Translator SHALL pass the text through without modification
5. IF translation fails due to network or API errors, THEN THE Translator SHALL log the error and retain the original text with a warning marker

### Requirement 5

**User Story:** As a meeting participant, I want an AI-generated summary of the meeting, so that I can quickly review key points, decisions, and action items.

#### Acceptance Criteria

1. WHEN the Summarizer receives the complete English transcript, THE Summarizer SHALL send the text to the Gemini API for processing
2. WHEN generating the summary, THE Summarizer SHALL extract and structure the following sections: Meeting Title, Participants, Key Discussion Points, Action Items, Decisions Taken, and Follow-up Tasks
3. WHEN the summary is generated, THE Summarizer SHALL format the output in a clear and professional structure suitable for business documentation
4. IF participant names are mentioned in the transcript, THEN THE Summarizer SHALL include them in the Participants section
5. IF the Gemini API fails or is unavailable, THEN THE Summarizer SHALL log the error and provide the raw transcript as fallback output

### Requirement 6

**User Story:** As a meeting participant, I want the meeting summary exported as a formatted DOCX file, so that I can easily share and archive the documentation.

#### Acceptance Criteria

1. WHEN the Exporter receives the meeting summary, THE Exporter SHALL create a DOCX document using the python-docx library
2. WHEN formatting the document, THE Exporter SHALL apply Heading 1 style to the meeting title, Heading 2 style to section headers, and bullet points to list items
3. WHEN the document is formatted, THE Exporter SHALL save the file as "meeting_summary.docx" in the designated output directory
4. WHEN saving the file, THE Exporter SHALL include a timestamp in the filename to prevent overwriting previous summaries
5. IF the output directory does not exist, THEN THE Exporter SHALL create the directory before saving the file

### Requirement 7

**User Story:** As a developer, I want a modular codebase with clear separation of concerns, so that the system is maintainable and extensible.

#### Acceptance Criteria

1. THE MeetDocs System SHALL organize code into separate modules: meet_joiner.py, audio_capture.py, transcriber.py, translator.py, summarizer.py, and exporter.py
2. THE MeetDocs System SHALL maintain separate directories for audio files, transcripts, and output documents
3. WHEN any module encounters an error, THE MeetDocs System SHALL log detailed error information including module name, error type, and timestamp
4. THE MeetDocs System SHALL include TODO comments at configuration points requiring user input such as cookie paths, audio device indices, and API keys
5. THE MeetDocs System SHALL provide a main.py orchestrator that coordinates the execution of all modules in the correct sequence

### Requirement 8

**User Story:** As a user, I want a single command to run the entire pipeline, so that I can start the automation with minimal effort.

#### Acceptance Criteria

1. WHEN the user executes main.py with a Google Meet link, THE MeetDocs System SHALL validate the URL format before proceeding
2. WHEN the pipeline starts, THE MeetDocs System SHALL execute modules in sequence: join meeting, capture audio, transcribe, translate, summarize, and export
3. WHEN each pipeline stage completes, THE MeetDocs System SHALL log the completion status and proceed to the next stage
4. IF any pipeline stage fails, THEN THE MeetDocs System SHALL log the failure, attempt recovery where possible, and notify the user of the issue
5. WHEN the pipeline completes successfully, THE MeetDocs System SHALL output the path to the generated DOCX file

### Requirement 9

**User Story:** As a new user, I want clear installation and setup instructions, so that I can configure the system correctly on my machine.

#### Acceptance Criteria

1. THE MeetDocs System SHALL provide a requirements.txt file listing all Python dependencies with version specifications
2. THE MeetDocs System SHALL include a README.md file with step-by-step instructions for ChromeDriver setup, virtual audio cable configuration, and Google login cookie extraction
3. THE MeetDocs System SHALL document the command-line syntax for running the tool with example Google Meet URLs
4. THE MeetDocs System SHALL specify system requirements including Python version, operating system compatibility, and hardware prerequisites
5. THE MeetDocs System SHALL provide troubleshooting guidance for common setup issues including audio device selection and browser driver configuration
