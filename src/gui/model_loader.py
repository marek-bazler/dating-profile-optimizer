"""
Model loading interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

class ModelLoader:
    def __init__(self, parent, model_manager, logger):
        self.parent = parent
        self.model_manager = model_manager
        self.logger = logger
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup model loading UI"""
        # Model status
        self.status_label = ttk.Label(self.parent, text="Models not loaded")
        self.status_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.parent, 
            variable=self.progress_var, 
            maximum=100,
            length=400
        )
        self.progress_bar.pack(pady=(0, 10))
        
        # Progress text
        self.progress_text = tk.StringVar()
        self.progress_text.set("Ready to load models")
        self.progress_label = ttk.Label(self.parent, textvariable=self.progress_text)
        self.progress_label.pack(pady=(0, 10))
        
        # Load button
        self.load_button = ttk.Button(
            self.parent, 
            text="Load AI Models", 
            command=self.load_models,
            style='Accent.TButton'
        )
        self.load_button.pack(pady=(0, 10))
        
        # Model info
        info_text = """Models to be loaded:
• Text Generator: For creating profile descriptions
• Image Analyzer: For analyzing photo attractiveness
• Sentiment Analyzer: For optimizing content tone

Note: First-time loading will download models (~2-3 GB total)"""
        
        info_label = ttk.Label(self.parent, text=info_text, justify=tk.LEFT)
        info_label.pack()
    
    def load_models(self):
        """Load all AI models"""
        def load_thread():
            try:
                self.load_button.config(state='disabled')
                self.status_label.config(text="Loading models...")
                
                def progress_callback(message, progress):
                    self.parent.after(0, lambda: self.update_progress(message, progress))
                
                self.model_manager.load_models(progress_callback)
                
                self.parent.after(0, lambda: self.on_models_loaded())
                
            except Exception as e:
                self.logger.error(f"Error loading models: {str(e)}")
                self.parent.after(0, lambda: self.on_models_error(str(e)))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def update_progress(self, message, progress):
        """Update progress display"""
        self.progress_text.set(message)
        self.progress_var.set(progress)
        self.parent.update_idletasks()
    
    def on_models_loaded(self):
        """Called when models are successfully loaded"""
        self.status_label.config(text="✓ All models loaded successfully!")
        self.progress_text.set("Ready to optimize your dating profile!")
        self.progress_var.set(100)
        self.load_button.config(text="Models Loaded", state='disabled')
        
        messagebox.showinfo("Success", "All AI models loaded successfully!\nYou can now proceed to the other tabs.")
    
    def on_models_error(self, error_message):
        """Called when model loading fails"""
        self.status_label.config(text="❌ Error loading models")
        self.progress_text.set("Error occurred during loading")
        self.progress_var.set(0)
        self.load_button.config(state='normal')
        
        messagebox.showerror("Error", f"Failed to load models:\n{error_message}")