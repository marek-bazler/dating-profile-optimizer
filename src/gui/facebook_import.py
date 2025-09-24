"""
Facebook Import GUI Component
Handles Facebook data export import and processing
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime

from ..data.facebook_parser import FacebookDataParser

class FacebookImport:
    def __init__(self, parent, model_manager, logger):
        self.parent = parent
        self.model_manager = model_manager
        self.logger = logger
        self.facebook_parser = FacebookDataParser()
        
        # Data storage
        self.facebook_data = {}
        self.dating_profile_data = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup Facebook import UI"""
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Facebook Data Import", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = """Import your Facebook data export to automatically populate your profile information and access your photos.

How to get your Facebook data:
1. Go to Facebook Settings & Privacy > Settings
2. Click "Your Facebook Information" > "Download Your Information"
3. Select JSON format and include: Profile Information, Photos and Videos, Posts, About You
4. Download and extract the ZIP file, then select it below"""
        
        instructions_label = ttk.Label(main_frame, text=instructions, wraplength=600, justify=tk.LEFT)
        instructions_label.pack(pady=(0, 20))
        
        # Import section
        import_frame = ttk.LabelFrame(main_frame, text="Import Facebook Data", padding=20)
        import_frame.pack(fill='x', pady=(0, 20))
        
        # File selection
        file_frame = ttk.Frame(import_frame)
        file_frame.pack(fill='x', pady=(0, 10))
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        file_entry.pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_facebook_file)
        browse_btn.pack(side=tk.RIGHT)
        
        # Import button
        button_frame = ttk.Frame(import_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        self.import_btn = ttk.Button(
            button_frame, 
            text="Import Facebook Data", 
            command=self.import_facebook_data,
            style='Accent.TButton'
        )
        self.import_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status
        self.import_status = tk.StringVar()
        self.import_status.set("No file selected")
        status_label = ttk.Label(button_frame, textvariable=self.import_status)
        status_label.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            import_frame, 
            variable=self.progress_var, 
            maximum=100,
            length=400
        )
        self.progress_bar.pack(fill='x', pady=(10, 0))
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Import Results", padding=10)
        results_frame.pack(fill='both', expand=True)
        
        # Create notebook for different data types
        self.results_notebook = ttk.Notebook(results_frame)
        self.results_notebook.pack(fill='both', expand=True)
        
        # Profile info tab
        self.profile_tab = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.profile_tab, text="Profile Info")
        
        self.profile_text = scrolledtext.ScrolledText(self.profile_tab, height=10, wrap=tk.WORD)
        self.profile_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Photos tab
        self.photos_tab = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.photos_tab, text="Photos")
        
        self.photos_text = scrolledtext.ScrolledText(self.photos_tab, height=10, wrap=tk.WORD)
        self.photos_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Interests tab
        self.interests_tab = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.interests_tab, text="Interests")
        
        self.interests_text = scrolledtext.ScrolledText(self.interests_tab, height=10, wrap=tk.WORD)
        self.interests_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Action buttons
        action_frame = ttk.Frame(results_frame)
        action_frame.pack(fill='x', pady=(10, 0))
        
        self.use_data_btn = ttk.Button(
            action_frame, 
            text="Use This Data for Profile", 
            command=self.use_facebook_data,
            state='disabled'
        )
        self.use_data_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        export_btn = ttk.Button(
            action_frame, 
            text="Export Processed Data", 
            command=self.export_processed_data,
            state='disabled'
        )
        export_btn.pack(side=tk.LEFT)
        
        self.export_btn = export_btn  # Store reference for enabling/disabling
    
    def browse_facebook_file(self):
        """Browse for Facebook data export file"""
        file_types = [
            ("Facebook Export", "*.zip *.json"),
            ("ZIP files", "*.zip"),
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select Facebook Data Export",
            filetypes=file_types
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.import_status.set("File selected - ready to import")
            self.logger.info(f"Facebook export file selected: {file_path}")
    
    def import_facebook_data(self):
        """Import and process Facebook data"""
        file_path = self.file_path_var.get().strip()
        
        if not file_path:
            messagebox.showerror("Error", "Please select a Facebook data export file first!")
            return
        
        if not Path(file_path).exists():
            messagebox.showerror("Error", "Selected file does not exist!")
            return
        
        def import_thread():
            try:
                self.import_btn.config(state='disabled')
                self.import_status.set("Processing Facebook data...")
                self.progress_var.set(10)
                
                # Parse Facebook data
                self.facebook_data = self.facebook_parser.parse_facebook_export(file_path)
                self.progress_var.set(50)
                
                # Extract dating profile data
                self.dating_profile_data = self.facebook_parser.extract_dating_profile_data(self.facebook_data)
                self.progress_var.set(80)
                
                # Update UI
                self.parent.after(0, self.display_import_results)
                self.progress_var.set(100)
                self.import_status.set("Import completed successfully!")
                
                self.logger.info("Facebook data import completed successfully")
                
            except Exception as e:
                self.logger.error(f"Error importing Facebook data: {str(e)}")
                self.parent.after(0, lambda: self.on_import_error(str(e)))
            finally:
                self.import_btn.config(state='normal')
        
        threading.Thread(target=import_thread, daemon=True).start()
    
    def display_import_results(self):
        """Display the imported Facebook data"""
        if not self.dating_profile_data:
            return
        
        # Display profile information
        profile_info = []
        profile_info.append("=== PROFILE INFORMATION ===\n")
        profile_info.append(f"Name: {self.dating_profile_data.get('name', 'Not found')}")
        profile_info.append(f"Age: {self.dating_profile_data.get('age', 'Not found')}")
        profile_info.append(f"Location: {self.dating_profile_data.get('location', 'Not found')}")
        profile_info.append(f"Hometown: {self.dating_profile_data.get('hometown', 'Not found')}")
        profile_info.append(f"Occupation: {self.dating_profile_data.get('occupation', 'Not found')}")
        profile_info.append(f"Education: {self.dating_profile_data.get('education', 'Not found')}")
        profile_info.append(f"Relationship Status: {self.dating_profile_data.get('relationship_status', 'Not found')}")
        
        # Add statistics about data found
        profile_info.append(f"\n=== DATA STATISTICS ===")
        profile_info.append(f"Posts analyzed: {self.dating_profile_data.get('posts_analyzed', 0)}")
        profile_info.append(f"Interests found: {self.dating_profile_data.get('interests_found', 0)}")
        
        if self.dating_profile_data.get('bio'):
            profile_info.append(f"\nBio: {self.dating_profile_data['bio']}")
        
        # Add note about Facebook export limitations
        profile_info.append(f"\n=== NOTE ===")
        profile_info.append("Facebook exports may not include all profile information.")
        profile_info.append("The app extracts what's available from your export file.")
        profile_info.append("You can manually add missing information in the Profile Info tab.")
        
        self.profile_text.delete(1.0, tk.END)
        self.profile_text.insert(1.0, "\n".join(profile_info))
        
        # Display photos information
        photos_info = []
        photos_info.append("=== PHOTOS INFORMATION ===\n")
        photos_info.append(f"Total photos found: {self.dating_profile_data.get('total_photos_found', 0)}")
        photos_info.append(f"Photos available for analysis: {self.dating_profile_data.get('available_photos_count', 0)}")
        
        photos = self.dating_profile_data.get('photos', [])
        if photos:
            photos_info.append("\nAvailable Photos:")
            for i, photo in enumerate(photos[:10], 1):  # Show first 10
                photos_info.append(f"{i}. {photo.get('title', 'Untitled')}")
                if photo.get('description'):
                    photos_info.append(f"   Description: {photo['description']}")
                photos_info.append(f"   Path: {photo.get('local_path', 'Not available')}")
                photos_info.append("")
            
            if len(photos) > 10:
                photos_info.append(f"... and {len(photos) - 10} more photos")
        
        self.photos_text.delete(1.0, tk.END)
        self.photos_text.insert(1.0, "\n".join(photos_info))
        
        # Display interests
        interests_info = []
        interests_info.append("=== INTERESTS & LIKES ===\n")
        
        interests = self.dating_profile_data.get('interests', '')
        if interests:
            interests_info.append("Extracted interests:")
            interests_info.append(interests)
        else:
            interests_info.append("No interests found in the data")
        
        # Show raw interests data if available
        if self.facebook_data.get('interests'):
            interests_info.append("\n\nAll liked pages/interests:")
            for interest in self.facebook_data['interests'][:20]:  # Show first 20
                interests_info.append(f"• {interest.get('name', 'Unknown')}")
                if interest.get('category'):
                    interests_info.append(f"  Category: {interest['category']}")
        
        self.interests_text.delete(1.0, tk.END)
        self.interests_text.insert(1.0, "\n".join(interests_info))
        
        # Enable action buttons
        self.use_data_btn.config(state='normal')
        self.export_btn.config(state='normal')
    
    def on_import_error(self, error_message: str):
        """Handle import errors"""
        self.import_status.set("Import failed")
        self.progress_var.set(0)
        messagebox.showerror("Import Error", f"Failed to import Facebook data:\n\n{error_message}")
    
    def use_facebook_data(self):
        """Use the imported Facebook data to populate the profile"""
        if not self.dating_profile_data:
            messagebox.showerror("Error", "No Facebook data available to use!")
            return
        
        try:
            # Get the main window instance and call integration method
            main_window = self.parent.master.master  # Navigate up to MainWindow
            if hasattr(main_window, 'integrate_facebook_data'):
                main_window.integrate_facebook_data()
            else:
                # Fallback message
                messagebox.showinfo(
                    "Success", 
                    "Facebook data is ready to use!\n\n"
                    "The profile information will be automatically populated in the Profile Info tab, "
                    "and photos will be available for analysis in the Photo Selection tab."
                )
            
            self.logger.info("Facebook data prepared for profile use")
            
        except Exception as e:
            self.logger.error(f"Error using Facebook data: {str(e)}")
            messagebox.showerror("Error", f"Error using Facebook data: {str(e)}")
    
    def export_processed_data(self):
        """Export the processed Facebook data"""
        if not self.dating_profile_data:
            messagebox.showerror("Error", "No data to export!")
            return
        
        try:
            # Ask user where to save
            file_path = filedialog.asksaveasfilename(
                title="Export Processed Facebook Data",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                # Prepare export data
                export_data = {
                    'dating_profile_data': self.dating_profile_data,
                    'raw_facebook_data': {
                        'profile_info': self.facebook_data.get('profile_info', {}),
                        'photos_count': len(self.facebook_data.get('photos', [])),
                        'interests_count': len(self.facebook_data.get('interests', [])),
                        'posts_count': len(self.facebook_data.get('posts', [])),
                        'friends_count': len(self.facebook_data.get('friends', []))
                    },
                    'export_timestamp': datetime.now().isoformat()
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Data exported successfully to:\n{file_path}")
                self.logger.info(f"Facebook data exported to: {file_path}")
                
        except Exception as e:
            self.logger.error(f"Error exporting data: {str(e)}")
            messagebox.showerror("Error", f"Error exporting data: {str(e)}")
    
    def get_dating_profile_data(self) -> Dict[str, Any]:
        """Get the processed dating profile data"""
        return self.dating_profile_data.copy() if self.dating_profile_data else {}
    
    def get_facebook_photos(self) -> list:
        """Get the list of available Facebook photos"""
        return self.dating_profile_data.get('photos', [])
    
    def has_data(self) -> bool:
        """Check if Facebook data has been imported"""
        return bool(self.dating_profile_data)