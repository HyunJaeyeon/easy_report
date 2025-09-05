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

        # UI components for stepper
        self.stepper_frame = None
        self.step_buttons = []

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
            font=ctk.CTkFont(size=18, weight="bold"),
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
                font=ctk.CTkFont(size=16),
                height=60,
                anchor="w",
                justify="left"
            )
            button.grid(row=i, column=0, padx=10, pady=5, sticky="ew")

            # Apply styling based on selection state
            if i == self.current_title1_index:
                button.configure(
                    fg_color="#FF6B35",  # High-contrast orange for selected
                    text_color="white",
                    border_width=2,
                    border_color="#CC5525"
                )
            else:
                button.configure(
                    fg_color="#F0F0F0",  # Light gray for unselected
                    text_color="#333333",
                    border_width=1,
                    border_color="#CCCCCC"
                )

    def update_main_content(self):
        """Update main content area"""
        # Clear existing content
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()

        if not self.title1_nodes:
            return

        current_title1 = self.title1_nodes[self.current_title1_index]

        # Header with progress
        self.create_header_with_progress(current_title1)

        # Stepper UI
        self.create_stepper(current_title1)

        # Placeholder for checklist
        content_label = ctk.CTkLabel(
            self.main_content_frame,
            text="Checklist area will be implemented in Phase 5",
            font=ctk.CTkFont(size=14)
        )
        content_label.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

    def create_header_with_progress(self, current_title1):
        """Create header with title and progress information"""
        # Header frame
        header_frame = ctk.CTkFrame(self.main_content_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        # Title label
        header_label = ctk.CTkLabel(
            header_frame,
            text=current_title1.label,
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        header_label.grid(row=0, column=0, sticky="w")

        # Progress information
        if self.state_manager:
            total_checked, total_items = self.state_manager.get_overall_progress(self.title1_nodes)
            progress_text = f"전체 진행률: {total_checked}/{total_items}"

            progress_label = ctk.CTkLabel(
                header_frame,
                text=progress_text,
                font=ctk.CTkFont(size=14),
                anchor="e"
            )
            progress_label.grid(row=0, column=1, sticky="e")

    def create_stepper(self, current_title1):
        """Create stepper UI with title2 buttons"""
        # Stepper frame
        self.stepper_frame = ctk.CTkFrame(self.main_content_frame, fg_color="transparent")
        self.stepper_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.stepper_frame.grid_columnconfigure(0, weight=1)

        # Clear previous step buttons
        self.step_buttons.clear()

        # Get title2 children
        title2_nodes = current_title1.get_title2_children()

        if not title2_nodes:
            return

        # Create step buttons
        for i, title2 in enumerate(title2_nodes):
            self.create_step_button(i, title2, len(title2_nodes))

    def create_step_button(self, index: int, title2, total_steps: int):
        """Create individual step button"""
        # Determine step status
        is_completed = title2.is_completed(self.state_manager) if self.state_manager else False
        is_current = index == self.current_title2_index

        # Step number and label
        step_number = index + 1
        step_text = f"{step_number}. {title2.label}"

        # Add completion indicator
        if is_completed:
            step_text = f"✓ {step_text}"

        # Button styling based on status
        if is_current:
            fg_color = "#FF6B35"  # High-contrast orange for current
            text_color = "white"
            border_width = 2
            border_color = "#CC5525"
        elif is_completed:
            fg_color = "#4CAF50"  # Green for completed
            text_color = "white"
            border_width = 1
            border_color = "#388E3C"
        else:
            fg_color = "#F0F0F0"  # Light gray for pending
            text_color = "#333333"
            border_width = 1
            border_color = "#CCCCCC"

        # Create button
        button = ctk.CTkButton(
            self.stepper_frame,
            text=step_text,
            command=lambda idx=index: self.select_title2(idx),
            font=ctk.CTkFont(size=14),
            height=50,
            fg_color=fg_color,
            text_color=text_color,
            border_width=border_width,
            border_color=border_color,
            anchor="w"
        )
        button.grid(row=index, column=0, padx=5, pady=2, sticky="ew")
        self.step_buttons.append(button)

    def select_title2(self, index: int):
        """Handle title2 selection from stepper"""
        # Auto-save current state before switching
        if self.state_manager:
            self.state_manager.save_state()

        self.current_title2_index = index

        # Update stepper UI to reflect new selection
        current_title1 = self.title1_nodes[self.current_title1_index]
        self.update_stepper_buttons(current_title1)

    def update_stepper_buttons(self, current_title1):
        """Update stepper button states after selection change"""
        title2_nodes = current_title1.get_title2_children()

        for i, (button, title2) in enumerate(zip(self.step_buttons, title2_nodes)):
            # Determine step status
            is_completed = title2.is_completed(self.state_manager) if self.state_manager else False
            is_current = i == self.current_title2_index

            # Step number and label
            step_number = i + 1
            step_text = f"{step_number}. {title2.label}"

            # Add completion indicator
            if is_completed:
                step_text = f"✓ {step_text}"

            # Update button styling and text
            if is_current:
                button.configure(
                    text=step_text,
                    fg_color="#FF6B35",
                    text_color="white",
                    border_width=2,
                    border_color="#CC5525"
                )
            elif is_completed:
                button.configure(
                    text=step_text,
                    fg_color="#4CAF50",
                    text_color="white",
                    border_width=1,
                    border_color="#388E3C"
                )
            else:
                button.configure(
                    text=step_text,
                    fg_color="#F0F0F0",
                    text_color="#333333",
                    border_width=1,
                    border_color="#CCCCCC"
                )

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
