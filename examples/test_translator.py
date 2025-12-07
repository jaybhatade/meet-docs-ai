"""
Example script to test the Translator module.
Demonstrates language detection and translation capabilities.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from translator import Translator
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] - %(message)s'
)

def main():
    """Test the Translator with various text samples."""
    
    print("=" * 60)
    print("MeetDocs AI - Translator Module Test")
    print("=" * 60)
    
    # Initialize translator
    translator = Translator()
    print("\n✓ Translator initialized\n")
    
    # Test cases
    test_cases = [
        ("English text", "Hello, this is a test meeting about project updates."),
        ("Hindi text", "नमस्ते, यह परियोजना अद्यतन के बारे में एक परीक्षण बैठक है।"),
        ("Marathi text", "नमस्कार, ही प्रकल्प अद्यतनांबद्दल एक चाचणी बैठक आहे।"),
        ("Mixed content", "The meeting will discuss नई योजना और future plans."),
    ]
    
    for label, text in test_cases:
        print(f"\n{'='*60}")
        print(f"Test: {label}")
        print(f"{'='*60}")
        print(f"Original: {text}")
        
        # Detect language
        lang = translator.detect_language(text)
        print(f"Detected language: {lang}")
        
        # Check if translation needed
        needs_trans = translator.needs_translation(text)
        print(f"Needs translation: {needs_trans}")
        
        # Translate
        translated = translator.translate_to_english(text)
        print(f"Result: {translated}")
    
    # Test full transcript processing
    print(f"\n{'='*60}")
    print("Test: Full Transcript Processing")
    print(f"{'='*60}")
    
    sample_transcript = """Hello everyone, welcome to the meeting.
आज हम नई परियोजना पर चर्चा करेंगे।
We need to finalize the timeline.
कृपया अपने सुझाव दें।"""
    
    print(f"Original transcript:\n{sample_transcript}\n")
    
    processed = translator.process_transcript(sample_transcript)
    print(f"Processed transcript:\n{processed}")
    
    print("\n" + "="*60)
    print("✓ All tests completed!")
    print("="*60)

if __name__ == "__main__":
    main()
