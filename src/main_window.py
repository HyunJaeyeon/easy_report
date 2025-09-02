import customtkinter as ctk
from typing import Optional
import sys
import os

# Add src directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from ui_first_screen import FirstScreen
from models import ChecklistParser
from state_manager import StateManager


class MainWindow(ctk.CTk):
    """Main application window"""

    def __init__(self):
        super().__init__()

        # Configure window
        self.title("안전보건 컨설팅 보고서 작성")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        # Set appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Application state
        self.company_name = ""
        self.hwp_file_path = ""
        self.title1_nodes = []
        self.state_manager = None
        self.current_title1_index = 0
        self.current_title2_index = 0

        # UI components
        self.first_screen = None
        self.sidebar_frame = None
        self.main_content_frame = None
        self.navigation_frame = None

        # Load checklist data
        self.load_checklist_data()

        # Show first screen initially
        self.show_first_screen()

    def load_checklist_data(self):
        """Load checklist data from JSON file"""
        try:
            self.title1_nodes = ChecklistParser.load_from_file("data/checklist.json")

            # Validate structure
            if not ChecklistParser.validate_structure(self.title1_nodes):
                raise ValueError("Invalid checklist structure")

            print(f"✅ Loaded {len(self.title1_nodes)} title1 nodes")

        except Exception as e:
            print(f"❌ Error loading checklist: {e}")
            # Create empty list as fallback
            self.title1_nodes = []

    def show_first_screen(self):
        """Show the first screen for company input and file upload"""
        # Clear current content
        for widget in self.winfo_children():
            widget.destroy()

        # Create first screen
        self.first_screen = FirstScreen(
            self,
            on_confirm_callback=self.on_first_screen_confirm
        )
        self.first_screen.pack(fill="both", expand=True)

    def on_first_screen_confirm(self, company_name: str, hwp_file_path: str):
        """Handle confirmation from first screen"""
        self.company_name = company_name
        self.hwp_file_path = hwp_file_path

        # Initialize state manager
        self.state_manager = StateManager(company_name=self.company_name)

        # Switch to main checklist screen
        self.show_main_screen()

    def show_main_screen(self):
        """Show the main checklist screen"""
        # Clear current content
        for widget in self.winfo_children():
            widget.destroy()

        # Configure main layout
        self.grid_columnconfigure(1, weight=1)  # Main content expands
        self.grid_rowconfigure(0, weight=1)     # Content row expands

        # Create sidebar
        self.create_sidebar()

        # Create main content area
        self.create_main_content()

        # Create navigation
        self.create_navigation()

        # Load initial content
        self.update_sidebar()
        self.update_main_content()

    def create_sidebar(self):
        """Create left sidebar"""
        self.sidebar_frame = ctk.CTkFrame(self, width=300)
        self.sidebar_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)  # Don't shrink

        # Configure sidebar layout
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        self.sidebar_frame.grid_rowconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            self.sidebar_frame,
            text=f"{self.company_name}\n3차 보고서",
            font=ctk.CTkFont(size=16, weight="bold"),
            justify="center"
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Scrollable frame for title1 buttons
        self.sidebar_scrollable = ctk.CTkScrollableFrame(self.sidebar_frame)
        self.sidebar_scrollable.grid(row=1, column=0, padx=10, pady=(0, 20), sticky="nsew")
        self.sidebar_scrollable.grid_columnconfigure(0, weight=1)

    def create_main_content(self):
        """Create right main content area"""
        self.main_content_frame = ctk.CTkFrame(self)
        self.main_content_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")

        # Configure main content layout
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure((0, 1, 2), weight=0)  # Header, stepper, checklist
        self.main_content_frame.grid_rowconfigure(1, weight=1)  # Checklist expands

    def create_navigation(self):
        """Create bottom navigation area"""
        self.navigation_frame = ctk.CTkFrame(self, height=60)
        self.navigation_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        self.navigation_frame.grid_propagate(False)  # Don't shrink

        # Configure navigation layout
        self.navigation_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.navigation_frame.grid_rowconfigure(0, weight=1)

    def update_sidebar(self):
        """Update sidebar with title1 buttons"""
        # Clear existing buttons
        for widget in self.sidebar_scrollable.winfo_children():
            widget.destroy()

        # Create buttons for each title1
        for i, title1 in enumerate(self.title1_nodes):
            button = ctk.CTkButton(
                self.sidebar_scrollable,
                text=title1.label,
                command=lambda idx=i: self.select_title1(idx),
                font=ctk.CTkFont(size=14),
                height=50,
                anchor="w",
                justify="left"
            )
            button.grid(row=i, column=0, padx=10, pady=5, sticky="ew")

            # Highlight current selection
            if i == self.current_title1_index:
                button.configure(fg_color="#3B8ED0")

    def update_main_content(self):
        """Update main content area"""
        # Clear existing content
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()

        if not self.title1_nodes:
            return

        current_title1 = self.title1_nodes[self.current_title1_index]

        # Header
        header_label = ctk.CTkLabel(
            self.main_content_frame,
            text=current_title1.label,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Placeholder for stepper and checklist
        content_label = ctk.CTkLabel(
            self.main_content_frame,
            text="Main content area - Stepper and checklist will be implemented in next phases",
            font=ctk.CTkFont(size=14)
        )
        content_label.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

    def select_title1(self, index: int):
        """Handle title1 selection"""
        self.current_title1_index = index
        self.current_title2_index = 0  # Reset to first title2

        # Update UI
        self.update_sidebar()
        self.update_main_content()

    def run(self):
        """Start the application"""
        self.mainloop()
