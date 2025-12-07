"""
Summarizer module for MeetDocs AI automation system.
Generates structured meeting summaries using Google Gemini API.
"""

import logging
import json
import time
from typing import Dict, List, Optional
import google.generativeai as genai


logger = logging.getLogger(__name__)


class Summarizer:
    """
    Manages AI-powered meeting summary generation using Gemini API.
    
    Processes transcripts to extract structured information including
    meeting title, participants, key points, action items, decisions,
    and follow-up tasks.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the Summarizer with Gemini API credentials.
        
        Args:
            api_key: Google Gemini API key
            
        Raises:
            ValueError: If API key is empty or invalid
        """
        if not api_key or not api_key.strip():
            logger.error("Gemini API key is required")
            raise ValueError("Gemini API key cannot be empty")
        
        try:
            # Configure Gemini API
            genai.configure(api_key=api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel('gemini-pro')
            
            logger.info("Summarizer initialized with Gemini API")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}")
            raise
    
    def generate_summary(self, transcript: str) -> Dict[str, any]:
        """
        Generate a structured meeting summary from transcript.
        
        Uses Gemini API with retry logic to create a comprehensive
        summary with all required sections.
        
        Args:
            transcript: Complete meeting transcript text
            
        Returns:
            Dictionary containing structured summary with keys:
            - title: Meeting title (inferred from context)
            - participants: List of participant names
            - key_points: List of key discussion points
            - action_items: List of action items
            - decisions: List of decisions taken
            - follow_ups: List of follow-up tasks
        """
        if not transcript or not transcript.strip():
            logger.warning("Empty transcript provided for summarization")
            return self.get_fallback_summary(transcript)
        
        logger.info("Generating meeting summary with Gemini API")
        
        # Build the prompt
        prompt = self._build_prompt(transcript)
        
        # Call API with retry logic
        try:
            response_text = self._call_api_with_retry(prompt)
            
            # Parse the response
            summary = self._parse_response(response_text)
            
            logger.info("Meeting summary generated successfully")
            return summary
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            logger.warning("Falling back to basic summary")
            return self.get_fallback_summary(transcript)
    
    def _build_prompt(self, transcript: str) -> str:
        """
        Construct the Gemini API prompt for summary generation.
        
        Creates a detailed prompt that instructs the model to extract
        structured information from the transcript.
        
        Args:
            transcript: Meeting transcript text
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Analyze the following meeting transcript and provide a structured summary.

TRANSCRIPT:
{transcript}

Please provide a comprehensive summary with the following sections:

1. Meeting Title: Infer an appropriate title based on the discussion topics
2. Participants: List all names mentioned in the transcript (if any)
3. Key Discussion Points: Main topics and themes discussed (bullet points)
4. Action Items: Specific tasks assigned with responsible parties (if mentioned)
5. Decisions Taken: Key decisions made during the meeting
6. Follow-up Tasks: Next steps and future actions needed

Format your response as JSON with the following structure:
{{
    "title": "Meeting title here",
    "participants": ["Name 1", "Name 2"],
    "key_points": ["Point 1", "Point 2"],
    "action_items": ["Action 1", "Action 2"],
    "decisions": ["Decision 1", "Decision 2"],
    "follow_ups": ["Follow-up 1", "Follow-up 2"]
}}

If any section has no information, use an empty list [] or appropriate placeholder.
Ensure the JSON is valid and properly formatted."""

        logger.debug("Prompt constructed for Gemini API")
        return prompt
    
    def _call_api_with_retry(self, prompt: str, max_retries: int = 2) -> str:
        """
        Call Gemini API with retry logic for resilience.
        
        Implements exponential backoff for transient failures.
        
        Args:
            prompt: The prompt to send to the API
            max_retries: Maximum number of retry attempts
            
        Returns:
            API response text
            
        Raises:
            Exception: If all retry attempts fail
        """
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries + 1):
            try:
                logger.debug(f"API call attempt {attempt + 1}/{max_retries + 1}")
                
                # Generate content
                response = self.model.generate_content(prompt)
                
                # Check if response is valid
                if not response or not response.text:
                    raise ValueError("Empty response from Gemini API")
                
                logger.info("API call successful")
                return response.text
                
            except Exception as e:
                logger.warning(f"API call attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("All API retry attempts exhausted")
                    raise
    
    def _parse_response(self, response_text: str) -> Dict[str, any]:
        """
        Parse Gemini API response to extract structured summary.
        
        Attempts to parse JSON response and validates required fields.
        Falls back to text parsing if JSON parsing fails.
        
        Args:
            response_text: Raw response text from API
            
        Returns:
            Structured summary dictionary
        """
        logger.debug("Parsing API response")
        
        try:
            # Try to extract JSON from response
            # Sometimes the model includes markdown code blocks
            json_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if json_text.startswith('```'):
                # Find the actual JSON content
                lines = json_text.split('\n')
                json_lines = []
                in_code_block = False
                
                for line in lines:
                    if line.strip().startswith('```'):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block or (not line.strip().startswith('```')):
                        json_lines.append(line)
                
                json_text = '\n'.join(json_lines).strip()
            
            # Parse JSON
            summary = json.loads(json_text)
            
            # Validate required fields
            required_fields = ['title', 'participants', 'key_points', 
                             'action_items', 'decisions', 'follow_ups']
            
            for field in required_fields:
                if field not in summary:
                    logger.warning(f"Missing field in response: {field}")
                    summary[field] = [] if field != 'title' else "Meeting Summary"
            
            # Ensure lists are actually lists
            for field in required_fields:
                if field != 'title' and not isinstance(summary[field], list):
                    summary[field] = [str(summary[field])]
            
            logger.info("Response parsed successfully")
            return summary
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response_text[:500]}...")
            
            # Attempt text-based parsing as fallback
            return self._parse_text_response(response_text)
        
        except Exception as e:
            logger.error(f"Unexpected error parsing response: {e}")
            raise
    
    def _parse_text_response(self, response_text: str) -> Dict[str, any]:
        """
        Parse non-JSON response text to extract summary information.
        
        Fallback parser for when API doesn't return valid JSON.
        
        Args:
            response_text: Raw response text
            
        Returns:
            Structured summary dictionary
        """
        logger.info("Attempting text-based parsing of response")
        
        summary = {
            'title': 'Meeting Summary',
            'participants': [],
            'key_points': [],
            'action_items': [],
            'decisions': [],
            'follow_ups': []
        }
        
        # Simple text parsing logic
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers
            lower_line = line.lower()
            if 'title' in lower_line or 'meeting title' in lower_line:
                current_section = 'title'
            elif 'participant' in lower_line:
                current_section = 'participants'
            elif 'key' in lower_line and ('point' in lower_line or 'discussion' in lower_line):
                current_section = 'key_points'
            elif 'action' in lower_line:
                current_section = 'action_items'
            elif 'decision' in lower_line:
                current_section = 'decisions'
            elif 'follow' in lower_line:
                current_section = 'follow_ups'
            elif current_section and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                # This is a bullet point
                content = line.lstrip('-•* ').strip()
                if content and current_section != 'title':
                    summary[current_section].append(content)
            elif current_section == 'title' and ':' in line:
                # Extract title after colon
                summary['title'] = line.split(':', 1)[1].strip()
        
        logger.info("Text-based parsing completed")
        return summary
    
    def get_fallback_summary(self, transcript: str) -> Dict[str, any]:
        """
        Generate a basic fallback summary when API is unavailable.
        
        Creates a minimal summary structure with the raw transcript
        included for manual review.
        
        Args:
            transcript: Original transcript text
            
        Returns:
            Basic summary dictionary
        """
        logger.info("Generating fallback summary")
        
        # Extract potential participant names (simple heuristic)
        participants = self._extract_participant_names(transcript)
        
        summary = {
            'title': 'Meeting Summary (Auto-generated)',
            'participants': participants,
            'key_points': [
                'Full transcript available below',
                'AI summarization was unavailable',
                'Please review transcript manually'
            ],
            'action_items': ['Review transcript and extract action items manually'],
            'decisions': ['Review transcript and extract decisions manually'],
            'follow_ups': ['Review transcript and identify follow-up tasks']
        }
        
        logger.info("Fallback summary generated")
        return summary
    
    def _extract_participant_names(self, transcript: str) -> List[str]:
        """
        Extract potential participant names from transcript.
        
        Uses simple heuristics to identify names mentioned in the text.
        This is a basic implementation that looks for capitalized words.
        
        Args:
            transcript: Meeting transcript text
            
        Returns:
            List of potential participant names
        """
        import re
        
        # Look for patterns like "Name said" or "Name mentioned"
        # This is a simple heuristic and may not be perfect
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:said|mentioned|asked|stated|replied|responded)'
        
        matches = re.findall(name_pattern, transcript)
        
        # Remove duplicates and common false positives
        names = list(set(matches))
        
        # Filter out common words that might be capitalized
        common_words = {'The', 'This', 'That', 'These', 'Those', 'What', 'When', 
                       'Where', 'Why', 'How', 'Who', 'Which', 'There', 'Here'}
        
        names = [name for name in names if name not in common_words]
        
        logger.debug(f"Extracted {len(names)} potential participant names")
        return names[:10]  # Limit to 10 names to avoid noise
