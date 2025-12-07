"""
Example script to test the Summarizer module.
Demonstrates AI-powered meeting summary generation using Gemini API.
"""

import sys
from pathlib import Path
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from summarizer import Summarizer
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] - %(message)s'
)

def main():
    """Test the Summarizer with sample transcripts."""
    
    print("=" * 60)
    print("MeetDocs AI - Summarizer Module Test")
    print("=" * 60)
    
    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("\n⚠ GEMINI_API_KEY not found in environment variables")
        print("Please set GEMINI_API_KEY to test the summarizer")
        print("\nTesting fallback summary generation instead...\n")
        
        # Test with empty API key to trigger fallback
        try:
            summarizer = Summarizer("")
        except ValueError:
            print("✓ Correctly rejected empty API key")
            print("\nGenerating fallback summary...\n")
            
            # Create a dummy summarizer for fallback testing
            sample_transcript = """
            John: Welcome everyone to today's project review meeting.
            Sarah: Thanks John. I'd like to discuss the progress on the new feature.
            Mike: We've completed the authentication module and it's ready for testing.
            Sarah: Great! What about the database migration?
            Mike: That's scheduled for next week. We need to coordinate with the DevOps team.
            John: Okay, let's make sure we have a backup plan. Sarah, can you follow up with DevOps?
            Sarah: Yes, I'll send them an email today.
            John: Perfect. Any other concerns?
            Mike: We should also review the API documentation before the release.
            John: Good point. Let's schedule a documentation review for Friday.
            Sarah: Sounds good. I'll send out calendar invites.
            John: Excellent. Thanks everyone for the updates.
            """
            
            # We can't test the full summarizer without API key, but we can show the transcript
            print("Sample transcript:")
            print(sample_transcript)
            print("\n" + "="*60)
            print("⚠ Cannot generate AI summary without valid API key")
            print("="*60)
        return
    
    # Initialize summarizer
    try:
        summarizer = Summarizer(api_key)
        print("\n✓ Summarizer initialized with Gemini API\n")
    except Exception as e:
        print(f"\n✗ Failed to initialize summarizer: {e}")
        return
    
    # Sample transcript
    sample_transcript = """
    John: Welcome everyone to today's project review meeting.
    Sarah: Thanks John. I'd like to discuss the progress on the new feature.
    Mike: We've completed the authentication module and it's ready for testing.
    Sarah: Great! What about the database migration?
    Mike: That's scheduled for next week. We need to coordinate with the DevOps team.
    John: Okay, let's make sure we have a backup plan. Sarah, can you follow up with DevOps?
    Sarah: Yes, I'll send them an email today.
    John: Perfect. Any other concerns?
    Mike: We should also review the API documentation before the release.
    John: Good point. Let's schedule a documentation review for Friday.
    Sarah: Sounds good. I'll send out calendar invites.
    John: Excellent. Thanks everyone for the updates.
    """
    
    print("Sample transcript:")
    print(sample_transcript)
    print("\n" + "="*60)
    print("Generating AI-powered summary...")
    print("="*60 + "\n")
    
    # Generate summary
    try:
        summary = summarizer.generate_summary(sample_transcript)
        
        # Display summary
        print(f"Meeting Title: {summary['title']}\n")
        
        print("Participants:")
        for participant in summary['participants']:
            print(f"  • {participant}")
        print()
        
        print("Key Discussion Points:")
        for point in summary['key_points']:
            print(f"  • {point}")
        print()
        
        print("Action Items:")
        for item in summary['action_items']:
            print(f"  • {item}")
        print()
        
        print("Decisions Taken:")
        for decision in summary['decisions']:
            print(f"  • {decision}")
        print()
        
        print("Follow-up Tasks:")
        for task in summary['follow_ups']:
            print(f"  • {task}")
        print()
        
        print("="*60)
        print("✓ Summary generated successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"✗ Failed to generate summary: {e}")
        print("\nTesting fallback summary...\n")
        
        fallback = summarizer.get_fallback_summary(sample_transcript)
        print(f"Fallback Title: {fallback['title']}")
        print(f"Participants: {fallback['participants']}")
        print(f"Key Points: {fallback['key_points']}")

if __name__ == "__main__":
    main()
