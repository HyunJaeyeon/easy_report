import json
import os
from typing import Dict, Set, List
from datetime import datetime


class StateManager:
    """Manages checklist state (checked items, progress, etc.)"""

    def __init__(self, data_dir: str = "data", company_name: str = ""):
        self.data_dir = data_dir
        self.company_name = company_name
        self.checked_items: Set[str] = set()
        self.state_file = self._get_state_file_path()

        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)

        # Load existing state if available
        self.load_state()

    def _get_state_file_path(self) -> str:
        """Get path for state file based on company name"""
        if self.company_name:
            safe_name = "".join(c for c in self.company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            return os.path.join(self.data_dir, f"state_{safe_name}.json")
        return os.path.join(self.data_dir, "state_default.json")

    def _generate_item_key(self, section_id: str, item_text: str) -> str:
        """Generate unique key for checklist item"""
        return f"{section_id}::{item_text}"

    def is_item_checked(self, section_id: str, item_text: str) -> bool:
        """Check if an item is checked"""
        key = self._generate_item_key(section_id, item_text)
        return key in self.checked_items

    def set_item_checked(self, section_id: str, item_text: str, checked: bool):
        """Set checked state for an item and save"""
        key = self._generate_item_key(section_id, item_text)
        if checked:
            self.checked_items.add(key)
        else:
            self.checked_items.discard(key)

        # Auto-save after state change
        self.save_state()

    def set_item_checked_no_save(self, section_id: str, item_text: str, checked: bool):
        """Set checked state for an item without saving (performance optimization)"""
        key = self._generate_item_key(section_id, item_text)
        if checked:
            self.checked_items.add(key)
        else:
            self.checked_items.discard(key)

    def toggle_item(self, section_id: str, item_text: str):
        """Toggle checked state for an item"""
        current_state = self.is_item_checked(section_id, item_text)
        self.set_item_checked(section_id, item_text, not current_state)

    def check_all_section(self, section_id: str, items: List[str]):
        """Check all items in a section"""
        for item in items:
            self.set_item_checked(section_id, item, True)

    def uncheck_all_section(self, section_id: str, items: List[str]):
        """Uncheck all items in a section"""
        for item in items:
            self.set_item_checked(section_id, item, False)

    def get_section_progress(self, section_id: str, items: List[str]) -> tuple[int, int]:
        """Get progress for a section (checked_count, total_count)"""
        checked_count = sum(1 for item in items if self.is_item_checked(section_id, item))
        return checked_count, len(items)

    def get_overall_progress(self, title1_nodes) -> tuple[int, int]:
        """Get overall progress across all title1 nodes"""
        total_checked = 0
        total_items = 0

        for title1 in title1_nodes:
            for title2 in title1.get_title2_children():
                for section in title2.get_sections():
                    checked, total = self.get_section_progress(section.id, section.items)
                    total_checked += checked
                    total_items += total

        return total_checked, total_items

    def save_state(self):
        """Save current state to file"""
        state_data = {
            "company_name": self.company_name,
            "checked_items": list(self.checked_items),
            "last_saved": datetime.now().isoformat(),
            "version": "1.0"
        }

        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving state: {e}")

    def load_state(self):
        """Load state from file"""
        if not os.path.exists(self.state_file):
            return

        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)

            self.checked_items = set(state_data.get('checked_items', []))
            loaded_company = state_data.get('company_name', '')

            # If company name doesn't match, this might be an old state file
            if loaded_company and loaded_company != self.company_name:
                print(f"Warning: State file company '{loaded_company}' doesn't match current '{self.company_name}'")

        except Exception as e:
            print(f"Error loading state: {e}")
            self.checked_items = set()

    def clear_state(self):
        """Clear all checked items"""
        self.checked_items.clear()
        self.save_state()

    def export_summary(self, title1_nodes) -> str:
        """Export hierarchical summary of checked items"""
        lines = []
        total_checked, total_items = self.get_overall_progress(title1_nodes)

        lines.append(f"체크리스트 완료 현황: {total_checked}/{total_items}")
        lines.append("=" * 50)

        for title1 in title1_nodes:
            title1_checked, title1_total = self.get_overall_progress([title1])

            if title1_checked > 0:
                lines.append(f"\n📋 {title1.label}")
                lines.append("-" * 30)

                for title2 in title1.get_title2_children():
                    title2_checked = title2.get_checked_items_count(self)
                    title2_total = title2.get_total_items_count()

                    if title2_checked > 0:
                        status = "✓" if title2.is_completed(self) else f"{title2_checked}/{title2_total}"
                        lines.append(f"  {status} {title2.label}")

                        for section in title2.get_sections():
                            section_checked = section.get_checked_count(self)

                            if section_checked > 0:
                                lines.append(f"    📂 {section.label}")

                                for item in section.items:
                                    if self.is_item_checked(section.id, item):
                                        lines.append(f"      • {item}")

        return "\n".join(lines)
