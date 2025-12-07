# Summarizer Module Implementation

## Overview

The Summarizer module generates structured meeting summaries using Google's Gemini API. It processes meeting transcripts and extracts key information including title, participants, discussion points, action items, decisions, and follow-up tasks.

## Implementation Details

### Class: `Summarizer`

**Purpose**: Interface with Gemini API to generate AI-powered meeting summaries.

**Key Features**:
- Gemini API integration with proper configuration
- Structured prompt construction for consistent output
- Retry logic with exponential backoff for resilience
- JSON response parsing with fallback to text parsing
- Participant name extraction from transcripts
- Fallback summary generation when API is unavailable

### Methods

#### `__init__(api_key: str)`
Initializes the Summarizer with Gemini API credentials.

**Parameters**:
- `api_key`: Google Gemini API key (required)

**Raises**:
- `ValueError`: If API key is empty or None

**Example**:
```python
from summarizer import Summarizer
import os

api_key = os.getenv('GEMINI_API_KEY')
summarizer = Summarizer(api_key)
```

#### `generate_summary(transcript: str) -> Dict[str, any]`
Main method to generate structured meeting summary.

**Parameters**:
- `transcript`: Complete meeting transcript text

**Returns**:
Dictionary with structure:
```python
{
    'title': str,              # Meeting title (inferred)
    'participants': List[str], # Participant names
    'key_points': List[str],   # Key discussion points
    'action_items': List[str], # Action items with owners
    'decisions': List[str],    # Decisions made
    'follow_ups': List[str]    # Follow-up tasks
}
```

**Example**:
```python
transcript = """
John: Welcome to the project review.
Sarah: The authentication module is complete.
Mike: We need to schedule testing for next week.
"""

summary = summarizer.generate_summary(transcript)
print(f"Title: {summary['title']}")
print(f"Participants: {', '.join(summary['participants'])}")
```

#### `get_fallback_summary(transcript: str) -> Dict[str, any]`
Generates basic summary when API is unavailable.

**Parameters**:
- `transcript`: Original transcript text

**Returns**:
Basic summary dictionary with same structure as `generate_summary()`

**Use Case**:
- API quota exceeded
- Network connectivity issues
- API service outage

#### `_build_prompt(transcript: str) -> str`
Constructs the Gemini API prompt for summary generation.

**Internal Method**: Creates detailed instructions for the AI model to extract structured information.

#### `_call_api_with_retry(prompt: str, max_retries: int = 2) -> str`
Calls Gemini API with retry logic.

**Parameters**:
- `prompt`: The prompt to send
- `max_retries`: Maximum retry attempts (default: 2)

**Retry Strategy**:
- Initial delay: 5 seconds
- Exponential backoff: delay doubles after each retry
- Total attempts: 3 (initial + 2 retries)

#### `_parse_response(response_text: str) -> Dict[str, any]`
Parses Gemini API response to extract structured data.

**Features**:
- Handles JSON responses
- Removes markdown code blocks
- Validates required fields
- Falls back to text parsing if JSON fails

#### `_parse_text_response(response_text: str) -> Dict[str, any]`
Fallback parser for non-JSON responses.

**Strategy**:
- Detects section headers
- Extracts bullet points
- Builds structured summary from text

#### `_extract_participant_names(transcript: str) -> List[str]`
Extracts potential participant names from transcript.

**Heuristics**:
- Looks for patterns like "Name said", "Name mentioned"
- Filters common false positives
- Removes duplicates
- Limits to 10 names

## Configuration

### Environment Variables

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### Getting a Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add to your `.env` file

## Usage Examples

### Basic Usage

```python
from summarizer import Summarizer
import os

# Initialize
api_key = os.getenv('GEMINI_API_KEY')
summarizer = Summarizer(api_key)

# Generate summary
transcript = "Your meeting transcript here..."
summary = summarizer.generate_summary(transcript)

# Access results
print(f"Meeting: {summary['title']}")
for participant in summary['participants']:
    print(f"  - {participant}")
```

### With Error Handling

```python
from summarizer import Summarizer
import os

try:
    summarizer = Summarizer(os.getenv('GEMINI_API_KEY'))
    summary = summarizer.generate_summary(transcript)
    
    # Process summary
    print(f"Generated summary for: {summary['title']}")
    
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Summary generation failed: {e}")
    # Use fallback
    summary = summarizer.get_fallback_summary(transcript)
```

### Testing Without API Key

```python
from summarizer import Summarizer

# For testing fallback functionality
summarizer = Summarizer("dummy_key")  # Will fail on API call
transcript = "Test transcript..."

# This will use fallback summary
summary = summarizer.get_fallback_summary(transcript)
```

## Error Handling

### Common Errors

1. **Empty API Key**
   - Error: `ValueError: Gemini API key cannot be empty`
   - Solution: Set `GEMINI_API_KEY` environment variable

2. **API Quota Exceeded**
   - Behavior: Falls back to basic summary
   - Log: "All API retry attempts exhausted"

3. **Network Timeout**
   - Behavior: Retries with exponential backoff
   - Max retries: 2 (total 3 attempts)

4. **Invalid JSON Response**
   - Behavior: Falls back to text parsing
   - Log: "Failed to parse JSON response"

### Logging

The module logs at various levels:

- **INFO**: Initialization, successful operations
- **WARNING**: Fallback activations, missing fields
- **ERROR**: API failures, parsing errors
- **DEBUG**: Detailed execution flow

## Testing

### Run Unit Tests

```bash
# Run all summarizer tests
pytest tests/test_summarizer.py -v

# Run with coverage
pytest tests/test_summarizer.py --cov=src.summarizer --cov-report=html
```

### Run Example Script

```bash
# Set API key
export GEMINI_API_KEY="your_key_here"

# Run example
python examples/test_summarizer.py
```

## Integration with Pipeline

The Summarizer integrates into the MeetDocs pipeline after translation:

```
[Transcriber] → [Translator] → [Summarizer] → [Exporter]
```

**Input**: English transcript (from Translator)
**Output**: Structured summary dictionary (to Exporter)

## Performance Considerations

### API Call Timing
- Average response time: 3-10 seconds
- Retry delays: 5s, 10s (exponential backoff)
- Total max time: ~30 seconds with retries

### Transcript Length
- Recommended max: 10,000 words
- Gemini API limit: ~30,000 tokens
- Long transcripts may need chunking (future enhancement)

### Rate Limiting
- Free tier: 60 requests per minute
- Consider implementing request throttling for batch processing

## Future Enhancements

1. **Custom Summary Templates**: Allow user-defined summary formats
2. **Multi-language Summaries**: Generate summaries in original language
3. **Sentiment Analysis**: Add meeting sentiment/tone analysis
4. **Topic Clustering**: Group related discussion points
5. **Speaker Statistics**: Track speaking time and contributions
6. **Confidence Scores**: Add confidence metrics for extracted information
7. **Streaming Summaries**: Generate summaries in real-time during meetings

## Troubleshooting

### Issue: "API key cannot be empty"
**Solution**: Ensure `GEMINI_API_KEY` is set in environment or `.env` file

### Issue: "All API retry attempts exhausted"
**Solution**: 
- Check internet connectivity
- Verify API key is valid
- Check Gemini API status
- Review API quota limits

### Issue: Summary has empty sections
**Solution**:
- Transcript may lack relevant information
- Try with more detailed transcript
- Review fallback summary for basic structure

### Issue: Participant names not extracted
**Solution**:
- Ensure transcript uses format: "Name: dialogue" or "Name said..."
- Names must be capitalized
- Check transcript quality and formatting

## Dependencies

```
google-generativeai==0.3.2
```

## References

- [Gemini API Documentation](https://ai.google.dev/docs)
- [Google AI Studio](https://makersuite.google.com/)
- [Gemini API Pricing](https://ai.google.dev/pricing)
