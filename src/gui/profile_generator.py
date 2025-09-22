"""
Profile information input interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any

class ProfileGenerator:
    def __init__(self, parent, model_manager, logger):
        self.parent = parent
        self.model_manager = model_manager
        self.logger = logger
        
        self.user_info = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup profile information UI"""
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Profile Information", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = """Fill in your information below. This will be used to generate your dating profile description.
The more details you provide, the better the AI can create a personalized profile for you."""
        
        instructions_label = ttk.Label(main_frame, text=instructions, wraplength=600, justify=tk.LEFT)
        instructions_label.pack(pady=(0, 20))
        
        # Create form
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill='x', pady=(0, 20))
        
        # Basic Information
        basic_frame = ttk.LabelFrame(form_frame, text="Basic Information", padding=20)
        basic_frame.pack(fill='x', pady=(0, 20))
        
        # Age
        age_frame = ttk.Frame(basic_frame)
        age_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(age_frame, text="Age:", width=15).pack(side=tk.LEFT)
        self.age_var = tk.StringVar()
        age_entry = ttk.Entry(age_frame, textvariable=self.age_var, width=10)
        age_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Occupation
        occupation_frame = ttk.Frame(basic_frame)
        occupation_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(occupation_frame, text="Occupation:", width=15).pack(side=tk.LEFT)
        self.occupation_var = tk.StringVar()
        occupation_entry = ttk.Entry(occupation_frame, textvariable=self.occupation_var, width=40)
        occupation_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Location
        location_frame = ttk.Frame(basic_frame)
        location_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(location_frame, text="Location:", width=15).pack(side=tk.LEFT)
        self.location_var = tk.StringVar()
        location_entry = ttk.Entry(location_frame, textvariable=self.location_var, width=40)
        location_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Interests and Hobbies
        interests_frame = ttk.LabelFrame(form_frame, text="Interests & Hobbies", padding=20)
        interests_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(interests_frame, text="List your interests, hobbies, and activities (comma-separated):").pack(anchor='w', pady=(0, 10))
        self.interests_text = tk.Text(interests_frame, height=4, wrap=tk.WORD)
        self.interests_text.pack(fill='x')
        
        # Personality
        personality_frame = ttk.LabelFrame(form_frame, text="Personality & Lifestyle", padding=20)
        personality_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(personality_frame, text="Describe your personality, lifestyle, or what makes you unique:").pack(anchor='w', pady=(0, 10))
        self.personality_text = tk.Text(personality_frame, height=4, wrap=tk.WORD)
        self.personality_text.pack(fill='x')
        
        # What you're looking for
        looking_frame = ttk.LabelFrame(form_frame, text="What You're Looking For", padding=20)
        looking_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(looking_frame, text="What are you looking for in a partner or relationship?").pack(anchor='w', pady=(0, 10))
        self.looking_text = tk.Text(looking_frame, height=3, wrap=tk.WORD)
        self.looking_text.pack(fill='x')
        
        # Profile Style
        style_frame = ttk.LabelFrame(form_frame, text="Profile Style Preferences", padding=20)
        style_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(style_frame, text="Choose your preferred profile style:").pack(anchor='w', pady=(0, 10))
        
        self.style_var = tk.StringVar(value="balanced")
        styles = [
            ("balanced", "Balanced - Mix of fun and serious"),
            ("humorous", "Humorous - Light-hearted and funny"),
            ("adventurous", "Adventurous - Focus on activities and experiences"),
            ("romantic", "Romantic - Emphasis on connection and relationships"),
            ("professional", "Professional - Career-focused and ambitious")
        ]
        
        for value, text in styles:
            ttk.Radiobutton(style_frame, text=text, variable=self.style_var, value=value).pack(anchor='w', pady=2)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=20)
        
        save_btn = ttk.Button(button_frame, text="Save Information", command=self.save_info)
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(button_frame, text="Clear All", command=self.clear_form)
        clear_btn.pack(side=tk.LEFT)
        
        # Status
        self.status_var = tk.StringVar()
        self.status_var.set("Fill in your information above")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(pady=(10, 0))
    
    def save_info(self):
        """Save the user information"""
        try:
            # Validate required fields
            if not self.age_var.get().strip():
                messagebox.showerror("Error", "Please enter your age")
                return
            
            try:
                age = int(self.age_var.get().strip())
                if age < 18 or age > 100:
                    messagebox.showerror("Error", "Please enter a valid age (18-100)")
                    return
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid age")
                return
            
            if not self.occupation_var.get().strip():
                messagebox.showerror("Error", "Please enter your occupation")
                return
            
            # Collect all information
            self.user_info = {
                'age': age,
                'occupation': self.occupation_var.get().strip(),
                'location': self.location_var.get().strip(),
                'interests': self.interests_text.get(1.0, tk.END).strip(),
                'personality': self.personality_text.get(1.0, tk.END).strip(),
                'looking_for': self.looking_text.get(1.0, tk.END).strip(),
                'style': self.style_var.get()
            }
            
            self.status_var.set("✓ Information saved successfully!")
            self.logger.info("User profile information saved")
            
            messagebox.showinfo("Success", "Your profile information has been saved!\nYou can now proceed to generate your optimized profile.")
            
        except Exception as e:
            self.logger.error(f"Error saving profile info: {str(e)}")
            messagebox.showerror("Error", f"Error saving information: {str(e)}")
    
    def clear_form(self):
        """Clear all form fields"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all information?"):
            self.age_var.set("")
            self.occupation_var.set("")
            self.location_var.set("")
            self.interests_text.delete(1.0, tk.END)
            self.personality_text.delete(1.0, tk.END)
            self.looking_text.delete(1.0, tk.END)
            self.style_var.set("balanced")
            
            self.user_info = {}
            self.status_var.set("Form cleared - fill in your information above")
            self.logger.info("Profile form cleared")
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get the saved user information"""
        return self.user_info.copy() if self.user_info else {}