#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import ChecklistParser

def test_parser():
    """Test checklist parser functionality"""

    # Load checklist from file
    checklist_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'checklist.json')
    print(f"Loading checklist from: {checklist_file}")

    try:
        title1_nodes = ChecklistParser.load_from_file(checklist_file)

        print(f"\n✅ Successfully loaded {len(title1_nodes)} title1 nodes")

        # Validate structure
        is_valid = ChecklistParser.validate_structure(title1_nodes)
        print(f"✅ Structure validation: {'PASS' if is_valid else 'FAIL'}")

        # Print structure summary
        print("\n📋 Checklist Structure:")
        for title1 in title1_nodes:
            print(f"  📁 {title1.label} ({title1.id})")
            for title2 in title1.get_title2_children():
                print(f"    📄 {title2.label} ({title2.id})")
                for section in title2.get_sections():
                    print(f"      📝 {section.label} ({section.id}) - {len(section.items)} items")
                    for item in section.items:
                        print(f"        • {item}")

        print("\n🎉 Parser test completed successfully!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

    return True

if __name__ == "__main__":
    test_parser()
