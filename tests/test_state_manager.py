#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import ChecklistParser
from state_manager import StateManager

def test_state_manager():
    """Test state manager functionality"""

    # Load checklist
    checklist_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'checklist.json')
    title1_nodes = ChecklistParser.load_from_file(checklist_file)

    # Create state manager
    state_manager = StateManager(company_name="Test Company")

    print("🧪 Testing State Manager...")

    # Test initial state
    print("\n📊 Initial Progress:")
    total_checked, total_items = state_manager.get_overall_progress(title1_nodes)
    print(f"  Overall: {total_checked}/{total_items}")

    # Test checking some items
    print("\n✅ Checking some items...")
    first_title1 = title1_nodes[0]
    first_title2 = first_title1.get_title2_children()[0]
    first_section = first_title2.get_sections()[0]

    # Check first item
    first_item = first_section.items[0]
    state_manager.set_item_checked(first_section.id, first_item, True)
    print(f"  Checked: {first_item}")

    # Test section progress
    checked, total = state_manager.get_section_progress(first_section.id, first_section.items)
    print(f"  Section progress: {checked}/{total}")

    # Test overall progress
    total_checked, total_items = state_manager.get_overall_progress(title1_nodes)
    print(f"  Overall progress: {total_checked}/{total_items}")

    # Test toggle
    print("\n🔄 Testing toggle...")
    state_manager.toggle_item(first_section.id, first_item)
    checked, total = state_manager.get_section_progress(first_section.id, first_section.items)
    print(f"  After toggle: {checked}/{total}")

    # Test check all / uncheck all
    print("\n📋 Testing bulk operations...")
    state_manager.check_all_section(first_section.id, first_section.items)
    checked, total = state_manager.get_section_progress(first_section.id, first_section.items)
    print(f"  After check all: {checked}/{total}")

    state_manager.uncheck_all_section(first_section.id, first_section.items)
    checked, total = state_manager.get_section_progress(first_section.id, first_section.items)
    print(f"  After uncheck all: {checked}/{total}")

    # Test export summary
    print("\n📄 Testing export summary...")
    state_manager.set_item_checked(first_section.id, first_item, True)
    summary = state_manager.export_summary(title1_nodes)
    print("Summary preview:")
    print(summary[:200] + "..." if len(summary) > 200 else summary)

    print("\n🎉 State Manager test completed successfully!")

if __name__ == "__main__":
    test_state_manager()
