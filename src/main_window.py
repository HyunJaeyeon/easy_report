import customtkinter as ctk
from typing import Optional
import sys
import os

# Add src directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

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
            checklist_path = get_resource_path("data/checklist.json")
            self.title1_nodes = ChecklistParser.load_from_file(checklist_path)

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
        # Determine step status (완료 표시 제거)
        is_current = index == self.current_title2_index

        # Step number and label (깔끔하게)
        step_number = index + 1
        step_text = f"{step_number}. {title2.label}"

        # Button styling based on current selection only
        if is_current:
            fg_color = "#007ACC"  # 현재 선택된 단계는 파란색
            text_color = "white"
            border_width = 0
        else:
            fg_color = "#F5F5F5"  # 선택되지 않은 단계는 연한 회색
            text_color = "#555555"
            border_width = 0

        # Create button (현대적 스타일)
        button = ctk.CTkButton(
            self.stepper_frame,
            text=step_text,
            command=lambda idx=index: self.select_title2(idx),
            font=ctk.CTkFont(size=12, weight="bold"),
            height=50,
            corner_radius=6,
            fg_color=fg_color,
            text_color=text_color,
            border_width=border_width,
            hover_color="#005A9F" if is_current else "#E8E8E8",
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
        # Section container frame (현대적 디자인)
        section_frame = ctk.CTkFrame(
            self.checklist_frame,
            corner_radius=8,
            fg_color="#FAFAFA",
            border_width=1,
            border_color="#E0E0E0"
        )
        section_frame.grid(row=section_idx, column=0, padx=12, pady=8, sticky="ew")
        section_frame.grid_columnconfigure(0, weight=1)
        
        # Section header with title and bulk select button
        header_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=16, pady=(16, 12), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Section title (더 세련된 스타일)
        section_title = ctk.CTkLabel(
            header_frame,
            text=section.label,
            font=ctk.CTkFont(size=17, weight="bold"),
            anchor="w",
            text_color="#1A1A1A"
        )
        section_title.grid(row=0, column=0, sticky="w")
        
        # Bulk select button (깔끔한 디자인)
        bulk_button = ctk.CTkButton(
            header_frame,
            text="전체 선택/해제",
            command=lambda s=section: self.toggle_section_items(s),
            font=ctk.CTkFont(size=13),
            height=32,
            width=110,
            corner_radius=6,
            fg_color="#f0f0f0",
            text_color="#333333",
            hover_color="#e0e0e0"
        )
        bulk_button.grid(row=0, column=1, sticky="e", padx=(10, 0))
        
        # Items container (여백 조정)
        items_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        items_frame.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="ew")
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

        # Create checkbox frame (깔끔한 디자인)
        checkbox_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        checkbox_frame.grid(row=item_idx, column=0, padx=8, pady=4, sticky="ew")
        checkbox_frame.grid_columnconfigure(1, weight=1)

        # Checkbox (현대적 스타일)
        checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="",
            command=lambda: self.toggle_item(section.id, item),
            font=ctk.CTkFont(size=15),
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=4,
            border_width=2,
            fg_color="#007ACC",
            hover_color="#005A9F",
            checkmark_color="white"
        )
        checkbox.grid(row=0, column=0, padx=(8, 12), pady=6, sticky="nw")

        # Set initial state
        if is_checked:
            checkbox.select()
        else:
            checkbox.deselect()

        # Item text label (텍스트 줄바꿈 지원)
        item_label = ctk.CTkLabel(
            checkbox_frame,
            text=item,
            font=ctk.CTkFont(size=15),
            anchor="w",
            justify="left",
            text_color="#2D2D2D"
        )
        item_label.grid(row=0, column=1, padx=(0, 12), pady=6, sticky="ew")

        # 위젯이 화면에 배치된 후 실제 너비를 계산하여 wraplength 설정
        def update_wraplength(event):
            # 실제 Label이 차지할 수 있는 너비 계산 (여백 제외)
            available_width = event.width - 30  # 좌우 여백 고려
            if available_width > 50:  # 최소 너비 확보
                item_label.configure(wraplength=available_width)

        item_label.bind("<Configure>", update_wraplength)

    def toggle_item(self, section_id: str, item: str):
        """Toggle individual item checkbox state"""
        if not self.state_manager:
            return
            
        # Toggle state (메모리에서만 변경, 저장하지 않음)
        current_state = self.state_manager.is_item_checked(section_id, item)
        self.state_manager.set_item_checked_no_save(section_id, item, not current_state)
        
        # UI 업데이트는 하지 않음 (성능 최적화)

    def toggle_section_items(self, section):
        """Toggle all items in a section"""
        if not self.state_manager:
            return
            
        # Check if all items are currently checked
        checked_count = section.get_checked_count(self.state_manager)
        total_count = section.get_total_count()
        
        # If all are checked, uncheck all. Otherwise, check all.
        new_state = not (checked_count == total_count)
        
        # Update all items in the section (메모리에서만, 저장하지 않음)
        for item in section.items:
            self.state_manager.set_item_checked_no_save(section.id, item, new_state)
        
        # UI 업데이트 (전체 선택 시 체크박스 상태 반영)
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
        
        # Determine if this is the very last step across all title1s
        is_final_step = (self.current_title1_index == len(self.title1_nodes) - 1) and is_last_step
        
        # Next button text and behavior
        if is_final_step:
            next_button_text = "완료 ▶"
            next_command = self.go_to_final_review
            next_color = "#28A745"  # Green for completion
        elif is_last_step:
            # Last step of current title1, but not final
            next_title1 = self.title1_nodes[self.current_title1_index + 1]
            next_button_text = f"다음: {next_title1.label[:10]}... ▶"
            next_command = self.go_to_next_step
            next_color = "#FF6B35"  # Orange for title1 transition
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
        """Navigate to next title2 step or next title1"""
        current_title1 = self.title1_nodes[self.current_title1_index]
        title2_nodes = current_title1.get_title2_children()
        
        # Auto-save current state
        if self.state_manager:
            self.state_manager.save_state()
        
        if self.current_title2_index < len(title2_nodes) - 1:
            # Move to next title2 within current title1
            self.current_title2_index += 1
        else:
            # Current title1 is complete, move to next title1
            if self.current_title1_index < len(self.title1_nodes) - 1:
                self.current_title1_index += 1
                self.current_title2_index = 0  # Reset to first title2
            else:
                # All title1s complete, go to final review
                self.show_final_review()
                return
        
        self.update_sidebar()
        self.update_main_content()
        self.update_navigation_buttons()

    def go_to_final_review(self):
        """Navigate to final review page (Phase 7)"""
        self.show_final_review()

    def show_final_review(self):
        """Show final review page with hierarchical summary"""
        # Auto-save current state
        if self.state_manager:
            self.state_manager.save_state()

        # Clear current content
        for widget in self.winfo_children():
            widget.destroy()

        # Configure layout for final review (풀스크린, 단일 컬럼)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header fixed
        self.grid_rowconfigure(1, weight=1)  # Content area expands
        self.grid_rowconfigure(2, weight=0)  # Button area fixed

        # Header
        header_label = ctk.CTkLabel(
            self,
            text=f"{self.company_name} - 최종 검토 및 보고서 생성",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Create scrollable summary area
        self.create_hierarchical_summary(self)

        # Bottom button frame (여백 최소화)
        button_frame = ctk.CTkFrame(self, height=80)
        button_frame.grid(row=2, column=0, padx=0, pady=0, sticky="ew")
        button_frame.grid_propagate(False)
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)
        button_frame.grid_rowconfigure(0, weight=1)

        # Back to checklist button
        back_button = ctk.CTkButton(
            button_frame,
            text="◀ 체크리스트로 돌아가기",
            command=self.return_to_checklist,
            font=ctk.CTkFont(size=14),
            height=50,
            width=160,
            fg_color="#6C757D",
            text_color="white"
        )
        back_button.grid(row=0, column=0, padx=10, pady=15, sticky="w")

        # HWP conversion button
        hwp_button = ctk.CTkButton(
            button_frame,
            text="📄 HWP 파일로 변환",
            command=self.convert_to_hwp,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=200,
            fg_color="#28A745",
            text_color="white"
        )
        hwp_button.grid(row=0, column=2, padx=10, pady=15, sticky="e")

    def create_hierarchical_summary(self, parent_frame):
        """Create modern, readable hierarchical summary of all checked items"""
        # Create enhanced scrollable frame with modern styling
        summary_frame = ctk.CTkScrollableFrame(
            parent_frame,
            fg_color="#FAFAFA",
            corner_radius=12,
            border_width=1,
            border_color="#E0E0E0"
        )
        summary_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")
        summary_frame.grid_columnconfigure(0, weight=1)

        # Store reference for later use
        self.summary_scrollable_frame = summary_frame

        if not self.state_manager or not self.title1_nodes:
            no_data_frame = ctk.CTkFrame(
                summary_frame,
                fg_color="white",
                corner_radius=10,
                border_width=1,
                border_color="#E8E8E8"
            )
            no_data_frame.grid(row=0, column=0, padx=10, pady=20, sticky="ew")
            no_data_frame.grid_columnconfigure(0, weight=1)
            
            no_data_label = ctk.CTkLabel(
                no_data_frame,
                text="📝 체크된 항목이 없습니다.",
                font=ctk.CTkFont(size=16),
                text_color="#666666"
            )
            no_data_label.grid(row=0, column=0, pady=30)
            return

        # Content sections with modern card design (완료 현황 통계 제거)
        row_idx = 0
        for title1_idx, title1 in enumerate(self.title1_nodes):
            # Main section card
            section_card = ctk.CTkFrame(
                summary_frame,
                fg_color="white",
                corner_radius=12,
                border_width=1,
                border_color="#E8E8E8"
            )
            section_card.grid(row=row_idx, column=0, padx=10, pady=(0, 15), sticky="ew")
            section_card.grid_columnconfigure(0, weight=1)
            
            # Section header with numbering
            section_header = ctk.CTkFrame(
                section_card,
                fg_color="#F8F9FA",
                corner_radius=10
            )
            section_header.grid(row=0, column=0, padx=12, pady=(12, 8), sticky="ew")
            section_header.grid_columnconfigure(0, weight=1)
            
            title1_label = ctk.CTkLabel(
                section_header,
                text=f"{title1_idx + 1}. {title1.label}",
                font=ctk.CTkFont(size=18, weight="bold"),
                anchor="w",
                text_color="#1A1A1A"
            )
            title1_label.grid(row=0, column=0, padx=15, pady=12, sticky="w")
            
            content_row = 1
            
            # Title2 subsections with improved layout
            for title2_idx, title2 in enumerate(title1.get_title2_children()):
                # Title2 header with modern styling
                title2_header = ctk.CTkLabel(
                    section_card,
                    text=f"📂 {title2_idx + 1}.{title1_idx + 1} {title2.label}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    anchor="w",
                    text_color="#333333"
                )
                title2_header.grid(row=content_row, column=0, padx=25, pady=(8, 4), sticky="w")
                content_row += 1

                # Process sections with enhanced display
                has_content = False
                for section in title2.get_sections():
                    checked_items = []
                    for item in section.items:
                        if self.state_manager.is_item_checked(section.id, item):
                            checked_items.append(item)
                    
                    if checked_items:
                        has_content = True
                        # Section container with subtle background
                        section_container = ctk.CTkFrame(
                            section_card,
                            fg_color="#F8F9FA",
                            corner_radius=8,
                            border_width=1,
                            border_color="#E8E8E8"
                        )
                        section_container.grid(row=content_row, column=0, padx=25, pady=(2, 8), sticky="ew")
                        section_container.grid_columnconfigure(0, weight=1)

                        # Section title
                        section_title = ctk.CTkLabel(
                            section_container,
                            text=f"📝 {section.label}",
                            font=ctk.CTkFont(size=14, weight="bold"),
                            anchor="w",
                            justify="left",
                            text_color="#444444",
                            wraplength=1000
                        )
                        section_title.grid(row=0, column=0, padx=15, pady=(10, 6), sticky="ew")

                        # Items with bullet points and left alignment
                        for idx, item in enumerate(checked_items, 1):
                            item_container = ctk.CTkFrame(
                                section_container,
                                fg_color="transparent"
                            )
                            item_container.grid(row=idx, column=0, padx=10, pady=1, sticky="ew")
                            item_container.grid_columnconfigure(1, weight=1)

                            # Bullet point
                            bullet_label = ctk.CTkLabel(
                                item_container,
                                text="•",
                                font=ctk.CTkFont(size=13, weight="bold"),
                                text_color="#007ACC",
                                width=15
                            )
                            bullet_label.grid(row=0, column=0, sticky="nw", pady=(2, 0), padx=(5, 0))

                            # Item text with word wrapping and left alignment
                            item_label = ctk.CTkLabel(
                                item_container,
                                text=item,
                                font=ctk.CTkFont(size=13),
                                anchor="w",
                                justify="left",
                                text_color="#28A745"
                            )
                            item_label.grid(row=0, column=1, sticky="ew", padx=(5, 10), pady=2)

                            # 위젯이 화면에 배치된 후 실제 너비를 계산하여 wraplength 설정
                            def update_summary_wraplength(event, label=item_label):
                                available_width = event.width - 30
                                if available_width > 50:
                                    label.configure(wraplength=available_width)

                            item_label.bind("<Configure>", update_summary_wraplength)
                        
                        # Bottom padding for section
                        ctk.CTkLabel(section_container, text="", height=8).grid(row=len(checked_items)+1, column=0)
                        content_row += 1

                if not has_content:
                    # Styled "no content" message
                    no_content_frame = ctk.CTkFrame(
                        section_card,
                        fg_color="#F5F5F5",
                        corner_radius=6
                    )
                    no_content_frame.grid(row=content_row, column=0, padx=35, pady=(2, 8), sticky="ew")
                    
                    no_content_label = ctk.CTkLabel(
                        no_content_frame,
                        text="체크된 항목이 없습니다",
                        font=ctk.CTkFont(size=13),
                        text_color="#999999"
                    )
                    no_content_label.grid(row=0, column=0, pady=8)
                    content_row += 1
            
            # Card bottom padding
            ctk.CTkLabel(section_card, text="", height=8).grid(row=content_row, column=0)
            row_idx += 1

    def return_to_checklist(self):
        """Return to main checklist screen"""
        # Go back to the last step we were on
        self.show_main_screen()

    def convert_to_hwp(self):
        """Convert checklist to HWP file"""
        if not self.hwp_file_path:
            self.show_error_dialog("HWP 변환 실패", "원본 HWP 파일이 설정되지 않았습니다.\n첫 화면에서 HWP 파일을 선택해주세요.")
            return

        # 변환 중 표시할 다이얼로그
        progress_window = self.create_progress_dialog()
        
        # 별도 스레드에서 변환 실행
        import threading
        
        def perform_conversion():
            try:
                from hwp_converter import HWPConverter, check_hwp_available
                
                if not check_hwp_available():
                    self.after(0, lambda: self.handle_conversion_error(progress_window, 
                        "한글(HWP) 프로그램이 설치되어 있지 않습니다."))
                    return
                
                converter = HWPConverter()
                
                # 체크된 항목 수집
                checked_items_data = {
                    'checked_items': list(self.state_manager.checked_items) if self.state_manager else []
                }
                
                # HWP 변환 실행
                success, message = converter.convert_checklist_to_hwp(
                    self.hwp_file_path,
                    self.company_name,
                    checked_items_data,
                    self.title1_nodes
                )
                
                # UI 스레드에서 결과 표시
                self.after(0, lambda: self.handle_conversion_result(progress_window, success, message))
                
            except Exception as e:
                error_msg = f"변환 중 예상치 못한 오류가 발생했습니다:\n{str(e)}"
                self.after(0, lambda: self.handle_conversion_error(progress_window, error_msg))
        
        threading.Thread(target=perform_conversion, daemon=True).start()

    def create_progress_dialog(self):
        """변환 진행 중 표시할 다이얼로그 생성"""
        progress_window = ctk.CTkToplevel(self)
        progress_window.title("HWP 변환 중...")
        progress_window.geometry("400x150")
        progress_window.resizable(False, False)
        
        # Center the window
        progress_window.transient(self)
        progress_window.grab_set()
        
        progress_label = ctk.CTkLabel(
            progress_window,
            text="체크리스트를 HWP 파일로 변환하고 있습니다...\n잠시만 기다려주세요.",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        progress_label.pack(expand=True, pady=20)
        
        # Progress bar (indeterminate)
        import tkinter as tk
        from tkinter import ttk
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(pady=(0, 20), padx=20, fill='x')
        progress_bar.start(10)
        
        return progress_window

    def handle_conversion_result(self, progress_window, success: bool, message: str):
        """변환 결과 처리"""
        progress_window.destroy()
        
        if success:
            self.show_success_dialog("HWP 변환 완료", message)
        else:
            self.show_error_dialog("HWP 변환 실패", message)

    def handle_conversion_error(self, progress_window, error_message: str):
        """변환 오류 처리"""
        progress_window.destroy()
        self.show_error_dialog("HWP 변환 오류", error_message)

    def show_success_dialog(self, title: str, message: str):
        """성공 다이얼로그 표시"""
        result_window = ctk.CTkToplevel(self)
        result_window.title(title)
        result_window.geometry("500x250")
        result_window.resizable(False, False)
        
        result_window.transient(self)
        result_window.grab_set()
        
        result_label = ctk.CTkLabel(
            result_window,
            text=message,
            font=ctk.CTkFont(size=12),
            justify="left",
            wraplength=450
        )
        result_label.pack(expand=True, pady=20, padx=20)
        
        close_button = ctk.CTkButton(
            result_window,
            text="확인",
            command=result_window.destroy,
            width=100,
            height=35,
            fg_color="#28A745"
        )
        close_button.pack(pady=(0, 20))

    def show_error_dialog(self, title: str, message: str):
        """오류 다이얼로그 표시"""
        result_window = ctk.CTkToplevel(self)
        result_window.title(title)
        result_window.geometry("500x200")
        result_window.resizable(False, False)
        
        result_window.transient(self)
        result_window.grab_set()
        
        result_label = ctk.CTkLabel(
            result_window,
            text=message,
            font=ctk.CTkFont(size=12),
            justify="left",
            wraplength=450
        )
        result_label.pack(expand=True, pady=20, padx=20)
        
        close_button = ctk.CTkButton(
            result_window,
            text="확인",
            command=result_window.destroy,
            width=100,
            height=35,
            fg_color="#DC3545"
        )
        close_button.pack(pady=(0, 20))

    def run(self):
        """Start the application"""
        self.mainloop()
