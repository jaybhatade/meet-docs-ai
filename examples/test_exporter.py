"""
Example usage of the Exporter module.
Demonstrates DOCX document creation from meeting summaries.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from exporter import DocxExporter


def main():
    """Demonstrate exporter functionality."""
    
    print("=" * 60)
    print("MeetDocs AI - Exporter Module Example")
    print("=" * 60)
    
    # Create sample meeting summary
    sample_summary = {
        'title': 'Q4 Product Planning Meeting',
        'participants': [
            'John Smith',
            'Sarah Johnson',
            'Michael Chen',
            'Emily Rodriguez'
        ],
        'key_points': [
            'Discussed new feature roadmap for Q4',
            'Reviewed customer feedback from recent surveys',
            'Analyzed competitor product launches',
            'Evaluated resource allocation for upcoming projects',
            'Discussed timeline for mobile app release'
        ],
        'action_items': [
            'John to prepare detailed feature specifications by Friday',
            'Sarah to schedule follow-up meeting with engineering team',
            'Michael to create budget proposal for Q4 initiatives',
            'Emily to conduct user research for new features'
        ],
        'decisions': [
            'Approved budget increase for mobile development',
            'Decided to prioritize user authentication improvements',
            'Agreed to postpone analytics dashboard to Q1 next year',
            'Confirmed launch date for beta release: November 15th'
        ],
        'follow_ups': [
            'Schedule technical architecture review next week',
            'Set up weekly sync meetings with product team',
            'Create project timeline with milestones',
            'Prepare presentation for stakeholder meeting'
        ]
    }
    
    # Initialize exporter
    print("\n1. Initializing DocxExporter...")
    exporter = DocxExporter(output_dir='./output')
    print("   ✓ Exporter initialized")
    
    # Create document
    print("\n2. Creating DOCX document...")
    try:
        filepath = exporter.create_document(sample_summary)
        print(f"   ✓ Document created successfully!")
        print(f"   📄 File saved to: {filepath}")
        
        # Verify file exists
        if Path(filepath).exists():
            file_size = Path(filepath).stat().st_size
            print(f"   📊 File size: {file_size:,} bytes")
        
    except Exception as e:
        print(f"   ✗ Error creating document: {e}")
        return
    
    # Test with minimal summary
    print("\n3. Testing with minimal summary...")
    minimal_summary = {
        'title': 'Quick Standup',
        'participants': [],
        'key_points': ['Brief status update'],
        'action_items': [],
        'decisions': [],
        'follow_ups': []
    }
    
    try:
        filepath2 = exporter.create_document(minimal_summary)
        print(f"   ✓ Minimal document created: {Path(filepath2).name}")
        
    except Exception as e:
        print(f"   ✗ Error creating minimal document: {e}")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
