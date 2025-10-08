import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from typing import Optional, Callable


class FirstScreen(ctk.CTkFrame):
    """First screen for company name input and HWP file upload"""

    def __init__(self, master, on_confirm_callback: Callable[[str, str], None], **kwargs):
        super().__init__(master, **kwargs)

        self.on_confirm_callback = on_confirm_callback
        self.company_name = ""
        self.hwp_file_path = ""

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface"""

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="안전보건 컨설팅 보고서 작성",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(40, 20))

        # Company name input section
        company_frame = ctk.CTkFrame(main_frame)
        company_frame.grid(row=1, column=0, padx=40, pady=20, sticky="ew")
        company_frame.grid_columnconfigure(1, weight=1)

        company_label = ctk.CTkLabel(
            company_frame,
            text="회사명:",
            font=ctk.CTkFont(size=16)
        )
        company_label.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="w")

        self.company_entry = ctk.CTkEntry(
            company_frame,
            placeholder_text="회사명을 입력하세요",
            font=ctk.CTkFont(size=16),
            height=45
        )
        self.company_entry.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="ew")

        # HWP file upload section
        hwp_frame = ctk.CTkFrame(main_frame)
        hwp_frame.grid(row=2, column=0, padx=40, pady=20, sticky="ew")
        hwp_frame.grid_columnconfigure((0, 1), weight=1)

        hwp_label = ctk.CTkLabel(
            hwp_frame,
            text="HWP 파일:",
            font=ctk.CTkFont(size=16)
        )
        hwp_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.file_label = ctk.CTkLabel(
            hwp_frame,
            text="파일을 선택해주세요",
            font=ctk.CTkFont(size=14),
            text_color="gray",
            wraplength=300
        )
        self.file_label.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="w")

        upload_button = ctk.CTkButton(
            hwp_frame,
            text="파일 선택",
            command=self.select_hwp_file,
            font=ctk.CTkFont(size=14),
            height=40,
            width=120
        )
        upload_button.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="e")

        # Confirm button
        confirm_button = ctk.CTkButton(
            main_frame,
            text="확인",
            command=self.confirm_and_proceed,
            font=ctk.CTkFont(size=18, weight="bold"),
            height=50,
            width=200
        )
        confirm_button.grid(row=3, column=0, pady=(20, 40))

        # Bind Enter key to confirm
        self.company_entry.bind("<Return>", lambda e: self.confirm_and_proceed())
        self.master.bind("<Return>", lambda e: self.confirm_and_proceed())

    def select_hwp_file(self):
        """Open file dialog to select HWP file"""
        file_path = filedialog.askopenfilename(
            title="HWP 파일 선택",
            filetypes=[("HWP files", "*.hwp"), ("HWPX files", "*.hwpx"), ("All files", "*.*")]
        )

        if file_path:
            self.hwp_file_path = file_path
            file_name = os.path.basename(file_path)
            self.file_label.configure(text=f"선택된 파일: {file_name}", text_color="black")
            
            # HWP 필드 검증 (백그라운드에서 실행)
            self.validate_hwp_fields_async(file_path)
        else:
            self.file_label.configure(text="파일을 선택해주세요", text_color="gray")

    def validate_hwp_fields_async(self, file_path: str):
        """HWP 파일의 필드를 비동기적으로 검증"""
        # 별도 스레드에서 실행하여 UI 블로킹 방지
        import threading
        
        def validate_fields():
            try:
                # HWP 변환기 임포트 (필요 시에만)
                import sys
                current_dir = os.path.dirname(os.path.abspath(__file__))
                if current_dir not in sys.path:
                    sys.path.insert(0, current_dir)
                
                from hwp_converter import HWPConverter, check_hwp_available
                
                if not check_hwp_available():
                    self.after(0, lambda: self.show_hwp_warning("한글(HWP) 프로그램이 설치되어 있지 않습니다."))
                    return
                
                converter = HWPConverter()
                fields = converter.detect_hwp_fields(file_path)
                
                # UI 스레드에서 결과 표시
                self.after(0, lambda: self.display_field_validation_result(fields))
                
            except Exception as e:
                error_msg = f"HWP 필드 검증 중 오류: {str(e)}"
                self.after(0, lambda: self.show_hwp_warning(error_msg))
        
        threading.Thread(target=validate_fields, daemon=True).start()

    def display_field_validation_result(self, detected_fields: list):
        """필드 검증 결과를 표시"""
        try:
            if detected_fields:
                field_count = len(detected_fields)
                message = f"HWP 필드 {field_count}개 감지됨 ✓"
                current_text = self.file_label.cget('text')
                self.file_label.configure(
                    text=f"{current_text}\n{message}", 
                    text_color="green"
                )
            else:
                message = "감지된 HWP 필드가 없습니다"
                current_text = self.file_label.cget('text')
                self.file_label.configure(
                    text=f"{current_text}\n{message}", 
                    text_color="orange"
                )
        except:
            # UI가 이미 파괴된 경우 무시
            pass

    def show_hwp_warning(self, message: str):
        """HWP 관련 경고 메시지 표시"""
        try:
            current_text = self.file_label.cget('text')
            self.file_label.configure(
                text=f"{current_text}\n⚠️ {message}", 
                text_color="red"
            )
        except:
            # UI가 이미 파괴된 경우 무시
            pass

    def confirm_and_proceed(self):
        """Validate inputs and proceed to next screen"""
        self.company_name = self.company_entry.get().strip()

        if not self.company_name:
            messagebox.showerror("입력 오류", "회사명을 입력해주세요.")
            self.company_entry.focus()
            return

        if not self.hwp_file_path:
            messagebox.showerror("파일 오류", "HWP 파일을 선택해주세요.")
            return

        # Validate file exists
        if not os.path.exists(self.hwp_file_path):
            messagebox.showerror("파일 오류", "선택한 파일이 존재하지 않습니다.")
            return

        # Call callback with company name and file path
        self.on_confirm_callback(self.company_name, self.hwp_file_path)

    def get_company_name(self) -> str:
        """Get current company name"""
        return self.company_name

    def get_hwp_file_path(self) -> str:
        """Get current HWP file path"""
        return self.hwp_file_path
