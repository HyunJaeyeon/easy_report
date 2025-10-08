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

            print(f"[OK] Loaded {len(self.title1_nodes)} title1 nodes")

        except Exception as e:
            print(f"[ERROR] Error loading checklist: {e}")
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
        self.update_navigation_buttons()

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
        self.main_content_frame.grid_rowconfigure(0, weight=0)  # Header - fixed height
        self.main_content_frame.grid_rowconfigure(1, weight=0)  # Stepper - fixed height
        self.main_content_frame.grid_rowconfigure(2, weight=1)  # Checklist - expands

    def create_navigation(self):
        """Create bottom navigation area"""
        self.navigation_frame = ctk.CTkFrame(self, height=60)
        self.navigation_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        self.navigation_frame.grid_propagate(False)  # Don't shrink

        # Configure navigation layout
        self.navigation_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.navigation_frame.grid_rowconfigure(0, weight=1)

        # Create navigation buttons
        self.update_navigation_buttons()

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
                anchor="w"
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

        # Checklist content area
        self.create_checklist_area(current_title1)

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
        self.stepper_frame = ctk.CTkFrame(self.main_content_frame, fg_color="transparent", height=70)
        self.stepper_frame.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")
        self.stepper_frame.grid_propagate(False)  # Don't shrink

        # Clear previous step buttons
        self.step_buttons.clear()

        # Get title2 children
        title2_nodes = current_title1.get_title2_children()

        if not title2_nodes:
            return

        # Configure stepper grid for horizontal layout
        total_steps = len(title2_nodes)
        for i in range(total_steps):
            self.stepper_frame.grid_columnconfigure(i, weight=1)
        self.stepper_frame.grid_rowconfigure(0, weight=1)

        # Create step buttons horizontally
        for i, title2 in enumerate(title2_nodes):
            self.create_step_button(i, title2, total_steps)

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
            font=ctk.CTkFont(size=12, weight="bold"),
            height=50,
            fg_color=fg_color,
            text_color=text_color,
            border_width=border_width,
            border_color=border_color,
            anchor="center"
        )
        button.grid(row=0, column=index, padx=3, pady=5, sticky="nsew")
        self.step_buttons.append(button)


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
        self.update_navigation_buttons()

    def select_title2(self, index: int):
        """Handle title2 selection"""
        # Auto-save current state before switching
        if self.state_manager:
            self.state_manager.save_state()
            
        self.current_title2_index = index
        
        # Update UI
        self.update_main_content()
        self.update_navigation_buttons()

    def create_checklist_area(self, current_title1):
        """Create checklist area showing sections and items for current title2"""
        # Get current title2
        title2_nodes = current_title1.get_title2_children()
        if not title2_nodes or self.current_title2_index >= len(title2_nodes):
            return
            
        current_title2 = title2_nodes[self.current_title2_index]
        
        # Create scrollable checklist frame
        self.checklist_frame = ctk.CTkScrollableFrame(
            self.main_content_frame,
            fg_color="transparent"
        )
        self.checklist_frame.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="nsew")
        self.checklist_frame.grid_columnconfigure(0, weight=1)
        
        # Get all sections under current title2
        sections = current_title2.get_sections()
        
        if not sections:
            # No sections, show message
            no_content_label = ctk.CTkLabel(
                self.checklist_frame,
                text="이 단계에는 체크리스트 항목이 없습니다.",
                font=ctk.CTkFont(size=16)
            )
            no_content_label.grid(row=0, column=0, padx=20, pady=40, sticky="ew")
            return
        
        # Create section frames
        for section_idx, section in enumerate(sections):
            self.create_section_frame(section, section_idx)

    def create_section_frame(self, section, section_idx: int):
        """Create a frame for a single section with its items"""
        # Section container frame
        section_frame = ctk.CTkFrame(self.checklist_frame)
        section_frame.grid(row=section_idx, column=0, padx=10, pady=10, sticky="ew")
        section_frame.grid_columnconfigure(0, weight=1)
        
        # Section header with title and bulk select button
        header_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Section title
        section_title = ctk.CTkLabel(
            header_frame,
            text=section.label,
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        section_title.grid(row=0, column=0, sticky="w")
        
        # Progress display
        if self.state_manager:
            checked_count = section.get_checked_count(self.state_manager)
            total_count = section.get_total_count()
            progress_text = f"({checked_count}/{total_count})"
            
            progress_label = ctk.CTkLabel(
                header_frame,
                text=progress_text,
                font=ctk.CTkFont(size=14),
                anchor="e"
            )
            progress_label.grid(row=0, column=1, sticky="e", padx=(10, 0))
        
        # Bulk select button
        bulk_button = ctk.CTkButton(
            header_frame,
            text="전체 선택/해제",
            command=lambda s=section: self.toggle_section_items(s),
            font=ctk.CTkFont(size=14),
            height=35,
            width=120
        )
        bulk_button.grid(row=0, column=2, sticky="e", padx=(10, 0))
        
        # Items container
        items_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        items_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        items_frame.grid_columnconfigure(0, weight=1)
        
        # Create checkboxes for each item
        for item_idx, item in enumerate(section.items):
            self.create_item_checkbox(items_frame, section, item, item_idx)

    def create_item_checkbox(self, parent_frame, section, item: str, item_idx: int):
        """Create a checkbox for a single checklist item"""
        # Check if item is currently checked
        is_checked = False
        if self.state_manager:
            is_checked = self.state_manager.is_item_checked(section.id, item)
        
        # Create checkbox frame
        checkbox_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        checkbox_frame.grid(row=item_idx, column=0, padx=5, pady=3, sticky="ew")
        checkbox_frame.grid_columnconfigure(1, weight=1)
        
        # Checkbox
        checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="",
            command=lambda: self.toggle_item(section.id, item),
            font=ctk.CTkFont(size=16),
            checkbox_width=24,
            checkbox_height=24
        )
        checkbox.grid(row=0, column=0, padx=(5, 10), pady=5, sticky="w")
        
        # Set initial state
        if is_checked:
            checkbox.select()
        else:
            checkbox.deselect()
        
        # Item text label
        item_label = ctk.CTkLabel(
            checkbox_frame,
            text=item,
            font=ctk.CTkFont(size=16),
            anchor="w",
            justify="left"
        )
        item_label.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="ew")

    def toggle_item(self, section_id: str, item: str):
        """Toggle individual item checkbox state"""
        if not self.state_manager:
            return
            
        # Toggle state
        current_state = self.state_manager.is_item_checked(section_id, item)
        self.state_manager.set_item_checked(section_id, item, not current_state)
        
        # Save state
        self.state_manager.save_state()
        
        # Update UI to reflect changes
        self.update_main_content()

    def toggle_section_items(self, section):
        """Toggle all items in a section"""
        if not self.state_manager:
            return
            
        # Check if all items are currently checked
        checked_count = section.get_checked_count(self.state_manager)
        total_count = section.get_total_count()
        
        # If all are checked, uncheck all. Otherwise, check all.
        new_state = not (checked_count == total_count)
        
        # Update all items in the section
        for item in section.items:
            self.state_manager.set_item_checked(section.id, item, new_state)
        
        # Save state
        self.state_manager.save_state()
        
        # Update UI to reflect changes
        self.update_main_content()

    def update_navigation_buttons(self):
        """Update navigation buttons based on current state"""
        # Clear existing buttons
        for widget in self.navigation_frame.winfo_children():
            widget.destroy()
        
        if not self.title1_nodes:
            return
            
        current_title1 = self.title1_nodes[self.current_title1_index]
        title2_nodes = current_title1.get_title2_children()
        
        if not title2_nodes:
            return
        
        total_steps = len(title2_nodes)
        is_first_step = self.current_title2_index == 0
        is_last_step = self.current_title2_index == total_steps - 1
        
        # Previous button
        prev_button = ctk.CTkButton(
            self.navigation_frame,
            text="◀ 이전",
            command=self.go_to_previous_step,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            width=120,
            fg_color="#6C757D" if is_first_step else "#007BFF",
            text_color="white",
            state="disabled" if is_first_step else "normal"
        )
        prev_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Step info in the center
        step_info = ctk.CTkLabel(
            self.navigation_frame,
            text=f"{self.current_title2_index + 1} / {total_steps}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        step_info.grid(row=0, column=1, pady=10)
        
        # Next button (or Complete button for last step)
        if is_last_step:
            next_button_text = "완료 ▶"
            next_command = self.go_to_final_review
            next_color = "#28A745"  # Green for completion
        else:
            next_button_text = "다음 ▶"
            next_command = self.go_to_next_step
            next_color = "#007BFF"  # Blue for next
        
        next_button = ctk.CTkButton(
            self.navigation_frame,
            text=next_button_text,
            command=next_command,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            width=120,
            fg_color=next_color,
            text_color="white"
        )
        next_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")

    def go_to_previous_step(self):
        """Navigate to previous title2 step"""
        if self.current_title2_index > 0:
            # Auto-save current state
            if self.state_manager:
                self.state_manager.save_state()
            
            self.current_title2_index -= 1
            self.update_main_content()
            self.update_navigation_buttons()

    def go_to_next_step(self):
        """Navigate to next title2 step"""
        current_title1 = self.title1_nodes[self.current_title1_index]
        title2_nodes = current_title1.get_title2_children()
        
        if self.current_title2_index < len(title2_nodes) - 1:
            # Auto-save current state
            if self.state_manager:
                self.state_manager.save_state()
            
            self.current_title2_index += 1
            self.update_main_content()
            self.update_navigation_buttons()

    def go_to_final_review(self):
        """Navigate to final review page (Phase 7)"""
        # Auto-save current state
        if self.state_manager:
            self.state_manager.save_state()
        
        # TODO: Implement final review page in Phase 7
        print("[INFO] Final review page will be implemented in Phase 7")

    def run(self):
        """Start the application"""
        self.mainloop()
