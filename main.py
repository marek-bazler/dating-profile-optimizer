#!/usr/bin/env python3
"""
Dating Profile Optimizer
A comprehensive application to optimize dating profiles using local AI models
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import logging
import os
from datetime import datetime
import threading
from pathlib import Path

from src.gui.main_window import MainWindow
from src.utils.logger import setup_logger
from src.models.model_manager import ModelManager

class DatingProfileApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dating Profile Optimizer")
        self.root.geometry("1200x800")
        
        # Setup logging
        self.logger = setup_logger()
        self.logger.info("Starting Dating Profile Optimizer")
        
        # Initialize model manager
        self.model_manager = ModelManager()
        
        # Create main window
        self.main_window = MainWindow(self.root, self.model_manager, self.logger)
        
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Application error: {str(e)}")
            messagebox.showerror("Error", f"Application error: {str(e)}")

if __name__ == "__main__":
    app = DatingProfileApp()
    app.run()