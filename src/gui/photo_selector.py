"""
Photo selection and analysis interface
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from PIL import Image, ImageTk
from typing import List, Dict

class PhotoSelector:
    def __init__(self, parent, model_manager, logger):
        self.parent = parent
        self.model_manager = model_manager
        self.logger = logger
        
        self.uploaded_photos = []
        self.analyzed_photos = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup photo selection UI"""
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Photo Selection & Analysis", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Upload section
        upload_frame = ttk.LabelFrame(main_frame, text="Upload Photos", padding=20)
        upload_frame.pack(fill='x', pady=(0, 20))
        
        upload_btn = ttk.Button(
            upload_frame, 
            text="Select Photos", 
            command=self.upload_photos,
            style='Accent.TButton'
        )
        upload_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.upload_status = tk.StringVar()
        self.upload_status.set("No photos uploaded")
        upload_status_label = ttk.Label(upload_frame, textvariable=self.upload_status)
        upload_status_label.pack(side=tk.LEFT)
        
        # Analysis section
        analysis_frame = ttk.LabelFrame(main_frame, text="Photo Analysis", padding=20)
        analysis_frame.pack(fill='x', pady=(0, 20))
        
        analyze_btn = ttk.Button(
            analysis_frame, 
            text="Analyze Photos", 
            command=self.analyze_photos,
            style='Accent.TButton'
        )
        analyze_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.analysis_status = tk.StringVar()
        self.analysis_status.set("No analysis performed")
        analysis_status_label = ttk.Label(analysis_frame, textvariable=self.analysis_status)
        analysis_status_label.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            analysis_frame, 
            variable=self.progress_var, 
            maximum=100,
            length=200
        )
        self.progress_bar.pack(side=tk.RIGHT)
        
        # Results display
        results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding=10)
        results_frame.pack(fill='both', expand=True)
        
        # Create scrollable frame for photos
        canvas = tk.Canvas(results_frame)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.results_display = self.scrollable_frame
    
    def upload_photos(self):
        """Upload photos for analysis"""
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select photos for dating profile",
            filetypes=file_types
        )
        
        if files:
            self.uploaded_photos = list(files)
            self.upload_status.set(f"{len(files)} photos uploaded")
            self.logger.info(f"Uploaded {len(files)} photos")
            
            # Clear previous analysis
            self.analyzed_photos = []
            self.analysis_status.set("Photos uploaded - ready for analysis")
            self.clear_results_display()
        else:
            self.upload_status.set("No photos selected")
    
    def analyze_photos(self):
        """Analyze uploaded photos"""
        if not self.uploaded_photos:
            messagebox.showerror("Error", "Please upload photos first!")
            return
            
        if not self.model_manager.models_loaded:
            messagebox.showerror("Error", "Please load AI models first!")
            return
        
        def analyze_thread():
            try:
                self.analyzed_photos = []
                total_photos = len(self.uploaded_photos)
                
                for i, photo_path in enumerate(self.uploaded_photos):
                    # Update progress
                    progress = (i / total_photos) * 100
                    self.parent.after(0, lambda p=progress: self.update_progress(p))
                    self.parent.after(0, lambda: self.analysis_status.set(f"Analyzing photo {i+1}/{total_photos}"))
                    
                    # Analyze photo
                    analysis_result = self.model_manager.analyze_image(photo_path)
                    self.analyzed_photos.append(analysis_result)
                
                # Update UI
                self.parent.after(0, lambda: self.update_progress(100))
                self.parent.after(0, lambda: self.analysis_status.set(f"Analysis complete - {len(self.analyzed_photos)} photos analyzed"))
                self.parent.after(0, self.display_results)
                
            except Exception as e:
                self.logger.error(f"Error analyzing photos: {str(e)}")
                self.parent.after(0, lambda: messagebox.showerror("Error", f"Error analyzing photos: {str(e)}"))
                self.parent.after(0, lambda: self.analysis_status.set("Analysis failed"))
        
        threading.Thread(target=analyze_thread, daemon=True).start()
    
    def update_progress(self, progress):
        """Update progress bar"""
        self.progress_var.set(progress)
        self.parent.update_idletasks()
    
    def display_results(self):
        """Display analysis results"""
        self.clear_results_display()
        
        if not self.analyzed_photos:
            return
        
        # Sort by attractiveness score
        sorted_photos = sorted(self.analyzed_photos, key=lambda x: x['attractiveness_score'], reverse=True)
        
        for i, photo_data in enumerate(sorted_photos):
            self.create_photo_result_widget(photo_data, i + 1)
    
    def create_photo_result_widget(self, photo_data, rank):
        """Create widget to display photo analysis result"""
        # Main frame for this photo
        photo_frame = ttk.Frame(self.results_display)
        photo_frame.pack(fill='x', pady=10, padx=10)
        
        # Left side - thumbnail
        left_frame = ttk.Frame(photo_frame)
        left_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        try:
            # Load and display thumbnail
            img = Image.open(photo_data['image_path'])
            img.thumbnail((150, 150))
            photo_img = ImageTk.PhotoImage(img)
            
            photo_label = ttk.Label(left_frame, image=photo_img)
            photo_label.image = photo_img  # Keep reference
            photo_label.pack()
            
            # Rank label
            rank_label = ttk.Label(left_frame, text=f"Rank #{rank}", font=('Arial', 10, 'bold'))
            rank_label.pack(pady=(5, 0))
            
        except Exception as e:
            self.logger.error(f"Error loading thumbnail for {photo_data['image_path']}: {str(e)}")
            error_label = ttk.Label(left_frame, text="Error loading image")
            error_label.pack()
        
        # Right side - analysis details
        right_frame = ttk.Frame(photo_frame)
        right_frame.pack(side=tk.LEFT, fill='x', expand=True)
        
        # File name
        file_name = Path(photo_data['image_path']).name
        name_label = ttk.Label(right_frame, text=f"File: {file_name}", font=('Arial', 10, 'bold'))
        name_label.pack(anchor='w')
        
        # Attractiveness score
        score = photo_data['attractiveness_score']
        score_color = 'green' if score > 0.7 else 'orange' if score > 0.5 else 'red'
        score_label = ttk.Label(right_frame, text=f"Attractiveness Score: {score:.2f}", foreground=score_color)
        score_label.pack(anchor='w', pady=(5, 0))
        
        # Caption
        caption_label = ttk.Label(right_frame, text=f"AI Description: {photo_data['caption']}", wraplength=400)
        caption_label.pack(anchor='w', pady=(5, 0))
        
        # Sentiment
        sentiment = photo_data['sentiment']
        sentiment_text = f"Sentiment: {sentiment['label']} ({sentiment['score']:.2f})"
        sentiment_label = ttk.Label(right_frame, text=sentiment_text)
        sentiment_label.pack(anchor='w', pady=(5, 0))
        
        # Separator
        separator = ttk.Separator(self.results_display, orient='horizontal')
        separator.pack(fill='x', pady=10)
    
    def clear_results_display(self):
        """Clear the results display"""
        for widget in self.results_display.winfo_children():
            widget.destroy()
    
    def get_analyzed_photos(self) -> List[Dict]:
        """Get the analyzed photos data"""
        return self.analyzed_photos
    
    def load_facebook_photos(self, facebook_photos: List[Dict]):
        """Load photos from Facebook data"""
        try:
            # Filter photos that have local paths
            available_photos = [
                photo['local_path'] for photo in facebook_photos 
                if photo.get('local_path') and Path(photo['local_path']).exists()
            ]
            
            if available_photos:
                self.uploaded_photos = available_photos
                self.upload_status.set(f"{len(available_photos)} Facebook photos loaded")
                self.analysis_status.set("Facebook photos loaded - ready for analysis")
                self.logger.info(f"Loaded {len(available_photos)} Facebook photos")
                
                # Clear previous analysis
                self.analyzed_photos = []
                self.clear_results_display()
            else:
                self.upload_status.set("No accessible Facebook photos found")
                self.logger.warning("No accessible Facebook photos found")
                
        except Exception as e:
            self.logger.error(f"Error loading Facebook photos: {str(e)}")
            self.upload_status.set("Error loading Facebook photos")