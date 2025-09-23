"""
Main GUI window for the Dating Profile Optimizer
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import logging
from pathlib import Path
from typing import List, Dict, Any
import json
from PIL import Image, ImageTk

from .photo_selector import PhotoSelector
from .profile_generator import ProfileGenerator
from .model_loader import ModelLoader

class MainWindow:
    def __init__(self, root, model_manager, logger):
        self.root = root
        self.model_manager = model_manager
        self.logger = logger
        
        # Data storage
        self.uploaded_photos = []
        self.analyzed_photos = []
        self.user_info = {}
        self.generated_profile = ""
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.setup_tab = ttk.Frame(self.notebook)
        self.photos_tab = ttk.Frame(self.notebook)
        self.profile_tab = ttk.Frame(self.notebook)
        self.results_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.setup_tab, text="Setup & Models")
        self.notebook.add(self.photos_tab, text="Photo Selection")
        self.notebook.add(self.profile_tab, text="Profile Info")
        self.notebook.add(self.results_tab, text="Results")
        
        # Setup each tab
        self.setup_setup_tab()
        self.setup_photos_tab()
        self.setup_profile_tab()
        self.setup_results_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_setup_tab(self):
        """Setup the models and configuration tab"""
        main_frame = ttk.Frame(self.setup_tab)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Dating Profile Optimizer", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_text = """This application helps optimize your dating profile using AI models.
        
Features:
• Upload and analyze your photos
• Generate attractive profile descriptions
• Select the best photos for dating apps
• All processing is done locally for privacy

First, load the AI models (this may take a few minutes):"""
        
        desc_label = ttk.Label(main_frame, text=desc_text, justify=tk.LEFT)
        desc_label.pack(pady=(0, 20))
        
        # Model loading section
        model_frame = ttk.LabelFrame(main_frame, text="AI Models", padding=20)
        model_frame.pack(fill='x', pady=(0, 20))
        
        self.model_loader = ModelLoader(model_frame, self.model_manager, self.logger)
        
        # Log viewer
        log_frame = ttk.LabelFrame(main_frame, text="Application Logs", padding=10)
        log_frame.pack(fill='both', expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state='disabled')
        self.log_text.pack(fill='both', expand=True)
        
        # Setup log handler to display in GUI
        self.setup_log_handler()
    
    def setup_photos_tab(self):
        """Setup the photo selection tab"""
        self.photo_selector = PhotoSelector(self.photos_tab, self.model_manager, self.logger)
        
    def setup_profile_tab(self):
        """Setup the profile information tab"""
        self.profile_generator = ProfileGenerator(self.profile_tab, self.model_manager, self.logger)
        
    def setup_results_tab(self):
        """Setup the results display tab"""
        main_frame = ttk.Frame(self.results_tab)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Generate final results button
        generate_btn = ttk.Button(
            main_frame, 
            text="Generate Final Results", 
            command=self.generate_final_results,
            style='Accent.TButton'
        )
        generate_btn.pack(pady=(0, 20))
        
        # Results display
        results_frame = ttk.LabelFrame(main_frame, text="Optimized Dating Profile", padding=20)
        results_frame.pack(fill='both', expand=True)
        
        # Selected photos frame
        photos_frame = ttk.LabelFrame(results_frame, text="Selected Photos (Top 5)", padding=10)
        photos_frame.pack(fill='x', pady=(0, 20))
        
        self.photos_display_frame = ttk.Frame(photos_frame)
        self.photos_display_frame.pack(fill='x')
        
        # Generated profile frame
        profile_frame = ttk.LabelFrame(results_frame, text="Generated Profile Description", padding=10)
        profile_frame.pack(fill='both', expand=True)
        
        self.profile_text = scrolledtext.ScrolledText(profile_frame, height=10, wrap=tk.WORD)
        self.profile_text.pack(fill='both', expand=True)
        
        # Export button
        export_btn = ttk.Button(results_frame, text="Export Results", command=self.export_results)
        export_btn.pack(pady=(10, 0))
    
    def setup_log_handler(self):
        """Setup log handler to display logs in GUI"""
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                
            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.config(state='normal')
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.config(state='disabled')
                    self.text_widget.see(tk.END)
                self.text_widget.after(0, append)
        
        gui_handler = GUILogHandler(self.log_text)
        gui_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        gui_handler.setFormatter(formatter)
        
        # Add to root logger
        logging.getLogger().addHandler(gui_handler)
    
    def generate_final_results(self):
        """Generate the final optimized dating profile"""
        if not self.model_manager.models_loaded:
            messagebox.showerror("Error", "Please load the AI models first!")
            return
        
        def generate():
            try:
                self.status_var.set("Generating final results...")
                
                # Get data from other tabs
                photos = self.photo_selector.get_analyzed_photos()
                user_info = self.profile_generator.get_user_info()
                
                if not photos:
                    messagebox.showerror("Error", "Please upload and analyze photos first!")
                    return
                
                if not user_info:
                    messagebox.showerror("Error", "Please fill in your profile information!")
                    return
                
                # Select top 5 photos
                top_photos = sorted(photos, key=lambda x: x['attractiveness_score'], reverse=True)[:5]
                
                # Generate profile description
                image_descriptions = [photo['caption'] for photo in top_photos]
                profile_description = self.model_manager.generate_profile_description(user_info, image_descriptions)
                
                # Update UI
                self.root.after(0, lambda: self.display_results(top_photos, profile_description))
                self.status_var.set("Results generated successfully!")
                
            except Exception as e:
                self.logger.error(f"Error generating results: {str(e)}")
                messagebox.showerror("Error", f"Error generating results: {str(e)}")
                self.status_var.set("Error generating results")
        
        threading.Thread(target=generate, daemon=True).start()
    
    def display_results(self, top_photos: List[Dict], profile_description: str):
        """Display the final results"""
        # Clear previous results
        for widget in self.photos_display_frame.winfo_children():
            widget.destroy()
        
        # Display top photos
        for i, photo in enumerate(top_photos):
            photo_frame = ttk.Frame(self.photos_display_frame)
            photo_frame.pack(side=tk.LEFT, padx=5)
            
            # Load and display thumbnail
            try:
                img = Image.open(photo['image_path'])
                img.thumbnail((100, 100))
                photo_img = ImageTk.PhotoImage(img)
                
                photo_label = ttk.Label(photo_frame, image=photo_img)
                photo_label.image = photo_img  # Keep reference
                photo_label.pack()
                
                # Score label
                score_label = ttk.Label(photo_frame, text=f"Score: {photo['attractiveness_score']:.2f}")
                score_label.pack()
                
            except Exception as e:
                self.logger.error(f"Error displaying photo {photo['image_path']}: {str(e)}")
        
        # Display profile description
        self.profile_text.delete(1.0, tk.END)
        self.profile_text.insert(1.0, profile_description)
    
    def export_results(self):
        """Export results to files"""
        try:
            # Create export directory
            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)
            
            # Get current results
            profile_text = self.profile_text.get(1.0, tk.END).strip()
            
            if not profile_text:
                messagebox.showwarning("Warning", "No results to export!")
                return
            
            # Export profile description
            with open(export_dir / "profile_description.txt", "w", encoding="utf-8") as f:
                f.write(profile_text)
            
            # Export photo recommendations
            photos = self.photo_selector.get_analyzed_photos()
            if photos:
                top_photos = sorted(photos, key=lambda x: x['attractiveness_score'], reverse=True)[:5]
                
                recommendations = {
                    "recommended_photos": [
                        {
                            "path": photo['image_path'],
                            "score": photo['attractiveness_score'],
                            "caption": photo['caption']
                        }
                        for photo in top_photos
                    ]
                }
                
                with open(export_dir / "photo_recommendations.json", "w", encoding="utf-8") as f:
                    json.dump(recommendations, f, indent=2)
            
            messagebox.showinfo("Success", f"Results exported to {export_dir}")
            self.logger.info(f"Results exported to {export_dir}")
            
        except Exception as e:
            self.logger.error(f"Error exporting results: {str(e)}")
            messagebox.showerror("Error", f"Error exporting results: {str(e)}")