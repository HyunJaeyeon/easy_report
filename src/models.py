import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ChecklistNode:
    """Base class for all checklist nodes"""
    id: str
    label: str
    type: str
    children: List['ChecklistNode'] = field(default_factory=list)
    parent: Optional['ChecklistNode'] = None

    def __post_init__(self):
        # Set parent reference for all children
        for child in self.children:
            child.parent = self

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary"""
        result = {
            "id": self.id,
            "label": self.label,
            "type": self.type
        }
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
        return result


@dataclass
class Title1(ChecklistNode):
    """Top-level title node (shown in sidebar)"""
    type: str = "title1"

    def get_title2_children(self) -> List['Title2']:
        """Get all title2 children"""
        return [child for child in self.children if isinstance(child, Title2)]


@dataclass
class Title2(ChecklistNode):
    """Mid-level title node (shown in stepper)"""
    type: str = "title2"

    def get_sections(self) -> List['Section']:
        """Get all section children"""
        return [child for child in self.children if isinstance(child, Section)]

    def get_total_items_count(self) -> int:
        """Get total number of checklist items under this title2"""
        return sum(len(section.items) for section in self.get_sections())

    def get_checked_items_count(self, state_manager) -> int:
        """Get number of checked items under this title2"""
        count = 0
        for section in self.get_sections():
            count += sum(1 for item in section.items
                        if state_manager.is_item_checked(section.id, item))
        return count

    def is_completed(self, state_manager) -> bool:
        """Check if all items under this title2 are completed"""
        return self.get_checked_items_count(state_manager) == self.get_total_items_count()


@dataclass
class Section(ChecklistNode):
    """Section node containing checklist items"""
    type: str = "section"
    items: List[str] = field(default_factory=list)

    def get_checked_count(self, state_manager) -> int:
        """Get number of checked items in this section"""
        return sum(1 for item in self.items
                  if state_manager.is_item_checked(self.id, item))

    def get_total_count(self) -> int:
        """Get total number of items in this section"""
        return len(self.items)

    def is_completed(self, state_manager) -> bool:
        """Check if all items in this section are completed"""
        return self.get_checked_count(state_manager) == self.get_total_count()


class ChecklistParser:
    """Parser for checklist.json files"""

    @staticmethod
    def load_from_file(file_path: str) -> List[Title1]:
        """Load checklist from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return ChecklistParser.parse_nodes(data)

    @staticmethod
    def parse_nodes(data: List[Dict[str, Any]]) -> List[Title1]:
        """Parse JSON data into node objects"""
        nodes = []
        for item in data:
            node = ChecklistParser._create_node(item)
            if node:
                nodes.append(node)
        return nodes

    @staticmethod
    def _create_node(data: Dict[str, Any]) -> Optional[ChecklistNode]:
        """Create appropriate node type from dictionary data"""
        node_type = data.get('type')
        if node_type == 'title1':
            return Title1(
                id=data['id'],
                label=data['label'],
                children=[ChecklistParser._create_node(child)
                         for child in data.get('children', [])]
            )
        elif node_type == 'title2':
            return Title2(
                id=data['id'],
                label=data['label'],
                children=[ChecklistParser._create_node(child)
                         for child in data.get('children', [])]
            )
        elif node_type == 'section':
            return Section(
                id=data['id'],
                label=data['label'],
                items=data.get('items', [])
            )
        return None

    @staticmethod
    def validate_structure(nodes: List[Title1]) -> bool:
        """Validate the checklist structure"""
        for title1 in nodes:
            if not isinstance(title1, Title1):
                return False
            for title2 in title1.get_title2_children():
                if not isinstance(title2, Title2):
                    return False
                for section in title2.get_sections():
                    if not isinstance(section, Section):
                        return False
        return True
