"""
Integration example: Summarizer → Exporter pipeline.
Demonstrates the complete flow from transcript to DOCX document.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from summarizer import Summarizer
from exporter import DocxExporter


def main():
    """Demonstrate summarizer to exporter integration."""
    
    print("=" * 60)
    print("MeetDocs AI - Summarizer → Exporter Integration")
    print("=" * 60)
    
    # Sample transcript
    sample_transcript = """
    John: Good morning everyone. Let's start our Q4 planning meeting.
    
    Sarah: Thanks John. I've reviewed the customer feedback and we have 
    some clear priorities for the next quarter.
    
    Michael: I agree. The main themes I'm seeing are performance 
    improvements and mobile app enhancements.
    
    Emily: Yes, and we should also focus on the authentication system. 
    We've had several requests for SSO integration.
    
    John: Great points. Let's make a decision on the budget. I propose 
    we increase the mobile development budget by 20%.
    
    Sarah: I support that. We should also schedule weekly syncs with 
    the engineering team.
    
    Michael: Agreed. I'll prepare the budget proposal by Friday.
    
    Emily: I'll conduct user research for the new features next week.
    
    John: Perfect. Let's plan to launch the beta on November 15th.
    """
    
    print("\n1. Sample Transcript:")
    print("-" * 60)
    print(sample_transcript[:200] + "...")
    
    # Note: This example uses fallback summary since we don't have a real API key
    print("\n2. Generating Summary (using fallback)...")
    
    try:
        # Initialize summarizer with dummy key (will use fallback)
        summarizer = Summarizer(api_key='dummy_key_for_demo')
        
        # Generate summary (will use fallback since API key is invalid)
        summary = summarizer.get_fallback_summary(sample_transcript)
        
        print("   ✓ Summary generated")
        print(f"   Title: {summary['title']}")
        print(f"   Participants: {len(summary['participants'])} found")
        print(f"   Key Points: {len(summary['key_points'])} items")
        
    except Exception as e:
        print(f"   ✗ Error generating summary: {e}")
        return
    
    # Export to DOCX
    print("\n3. Exporting to DOCX...")
    
    try:
        exporter = DocxExporter('./output')
        filepath = exporter.create_document(summary)
        
        print(f"   ✓ Document created successfully!")
        print(f"   📄 File: {Path(filepath).name}")
        print(f"   📁 Location: {Path(filepath).parent}")
        
        # Verify file
        if Path(filepath).exists():
            file_size = Path(filepath).stat().st_size
            print(f"   📊 Size: {file_size:,} bytes")
        
    except Exception as e:
        print(f"   ✗ Error exporting document: {e}")
        return
    
    print("\n" + "=" * 60)
    print("Integration test completed successfully!")
    print("=" * 60)
    print("\nThe complete pipeline flow:")
    print("  Transcript → Summarizer → Summary → Exporter → DOCX")
    print("\nYou can now open the generated DOCX file to review the")
    print("formatted meeting documentation.")


if __name__ == '__main__':
    main()
