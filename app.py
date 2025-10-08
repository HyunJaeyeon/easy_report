#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
안전보건 컨설팅 보고서 작성 애플리케이션
CustomTkinter 기반 데스크톱 애플리케이션
"""

import sys
import os

# Add src directory to path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.main_window import MainWindow

def main():
    """Main application entry point"""
    try:
        # Create and run main window
        app = MainWindow()
        app.run()

    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
