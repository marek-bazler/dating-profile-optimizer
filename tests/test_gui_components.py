"""
Unit tests for GUI components
"""

import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch, Mock
import tempfile
import shutil
from pathlib import Path

from src.gui.model_loader import ModelLoader
from src.gui.profile_generator import ProfileGenerator


class TestModelLoader(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.root = tk.Tk()
        self.parent = tk.Frame(self.root)
        self.model_manager = MagicMock()
        self.logger = MagicMock()
        
    def tearDown(self):
        """Clean up test environment"""
        self.root.destroy()
    
    def test_init(self):
        """Test ModelLoader initialization"""
        loader = ModelLoader(self.parent, self.model_manager, self.logger)
        
        self.assertEqual(loader.parent, self.parent)
        self.assertEqual(loader.model_manager, self.model_manager)
        self.assertEqual(loader.logger, self.logger)
        
        # Check UI elements exist
        self.assertIsNotNone(loader.status_label)
        self.assertIsNotNone(loader.progress_bar)
        self.assertIsNotNone(loader.load_button)
    
    @patch('threading.Thread')
    def test_load_models(self, mock_thread):
        """Test load models method"""
        loader = ModelLoader(self.parent, self.model_manager, self.logger)
        
        loader.load_models()
        
        # Verify thread was created and started
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
    
    def test_update_progress(self):
        """Test progress update"""
        loader = ModelLoader(self.parent, self.model_manager, self.logger)
        
        loader.update_progress("Loading model...", 50.0)
        
        self.assertEqual(loader.progress_text.get(), "Loading model...")
        self.assertEqual(loader.progress_var.get(), 50.0)
    
    @patch('tkinter.messagebox.showinfo')
    def test_on_models_loaded(self, mock_showinfo):
        """Test successful model loading callback"""
        loader = ModelLoader(self.parent, self.model_manager, self.logger)
        
        loader.on_models_loaded()
        
        # Check UI updates
        self.assertIn("successfully", loader.status_label.cget("text"))
        self.assertEqual(loader.progress_var.get(), 100)
        self.assertEqual(str(loader.load_button.cget("state")), "disabled")
        
        # Check success message shown
        mock_showinfo.assert_called_once()
    
    @patch('tkinter.messagebox.showerror')
    def test_on_models_error(self, mock_showerror):
        """Test model loading error callback"""
        loader = ModelLoader(self.parent, self.model_manager, self.logger)
        
        loader.on_models_error("Test error message")
        
        # Check UI updates
        self.assertIn("Error", loader.status_label.cget("text"))
        self.assertEqual(loader.progress_var.get(), 0)
        self.assertEqual(str(loader.load_button.cget("state")), "normal")
        
        # Check error message shown
        mock_showerror.assert_called_once()


class TestProfileGenerator(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.root = tk.Tk()
        self.parent = tk.Frame(self.root)
        self.model_manager = MagicMock()
        self.logger = MagicMock()
        
    def tearDown(self):
        """Clean up test environment"""
        self.root.destroy()
    
    def test_init(self):
        """Test ProfileGenerator initialization"""
        generator = ProfileGenerator(self.parent, self.model_manager, self.logger)
        
        self.assertEqual(generator.parent, self.parent)
        self.assertEqual(generator.model_manager, self.model_manager)
        self.assertEqual(generator.logger, self.logger)
        self.assertEqual(generator.user_info, {})
        
        # Check UI elements exist
        self.assertIsNotNone(generator.age_var)
        self.assertIsNotNone(generator.occupation_var)
        self.assertIsNotNone(generator.interests_text)
        self.assertIsNotNone(generator.style_var)
    
    @patch('tkinter.messagebox.showerror')
    def test_save_info_missing_age(self, mock_showerror):
        """Test save info with missing age"""
        generator = ProfileGenerator(self.parent, self.model_manager, self.logger)
        
        generator.save_info()
        
        mock_showerror.assert_called_once()
        self.assertIn("age", mock_showerror.call_args[0][1])
    
    @patch('tkinter.messagebox.showerror')
    def test_save_info_invalid_age(self, mock_showerror):
        """Test save info with invalid age"""
        generator = ProfileGenerator(self.parent, self.model_manager, self.logger)
        
        generator.age_var.set("invalid")
        generator.occupation_var.set("Engineer")
        
        generator.save_info()
        
        mock_showerror.assert_called_once()
        self.assertIn("valid age", mock_showerror.call_args[0][1])
    
    @patch('tkinter.messagebox.showerror')
    def test_save_info_age_out_of_range(self, mock_showerror):
        """Test save info with age out of range"""
        generator = ProfileGenerator(self.parent, self.model_manager, self.logger)
        
        generator.age_var.set("15")  # Too young
        generator.occupation_var.set("Engineer")
        
        generator.save_info()
        
        mock_showerror.assert_called_once()
        self.assertIn("valid age", mock_showerror.call_args[0][1])
    
    @patch('tkinter.messagebox.showerror')
    def test_save_info_missing_occupation(self, mock_showerror):
        """Test save info with missing occupation"""
        generator = ProfileGenerator(self.parent, self.model_manager, self.logger)
        
        generator.age_var.set("25")
        # occupation left empty
        
        generator.save_info()
        
        mock_showerror.assert_called_once()
        self.assertIn("occupation", mock_showerror.call_args[0][1])
    
    @patch('tkinter.messagebox.showinfo')
    def test_save_info_success(self, mock_showinfo):
        """Test successful save info"""
        generator = ProfileGenerator(self.parent, self.model_manager, self.logger)
        
        # Fill in required fields
        generator.age_var.set("25")
        generator.occupation_var.set("Software Engineer")
        generator.location_var.set("New York")
        generator.interests_text.insert(1.0, "hiking, reading, coding")
        generator.personality_text.insert(1.0, "outgoing and friendly")
        generator.looking_text.insert(1.0, "meaningful relationship")
        generator.style_var.set("humorous")
        
        generator.save_info()
        
        # Check user info saved
        expected_info = {
            'age': 25,
            'occupation': 'Software Engineer',
            'location': 'New York',
            'interests': 'hiking, reading, coding',
            'personality': 'outgoing and friendly',
            'looking_for': 'meaningful relationship',
            'style': 'humorous'
        }
        
        self.assertEqual(generator.user_info, expected_info)
        self.assertIn("successfully", generator.status_var.get())
        mock_showinfo.assert_called_once()
    
    @patch('tkinter.messagebox.askyesno')
    def test_clear_form_confirmed(self, mock_askyesno):
        """Test clear form when confirmed"""
        mock_askyesno.return_value = True
        
        generator = ProfileGenerator(self.parent, self.model_manager, self.logger)
        
        # Set some values
        generator.age_var.set("25")
        generator.occupation_var.set("Engineer")
        generator.interests_text.insert(1.0, "test interests")
        generator.user_info = {'test': 'data'}
        
        generator.clear_form()
        
        # Check values cleared
        self.assertEqual(generator.age_var.get(), "")
        self.assertEqual(generator.occupation_var.get(), "")
        self.assertEqual(generator.interests_text.get(1.0, tk.END).strip(), "")
        self.assertEqual(generator.user_info, {})
        self.assertIn("cleared", generator.status_var.get())
    
    @patch('tkinter.messagebox.askyesno')
    def test_clear_form_cancelled(self, mock_askyesno):
        """Test clear form when cancelled"""
        mock_askyesno.return_value = False
        
        generator = ProfileGenerator(self.parent, self.model_manager, self.logger)
        
        # Set some values
        generator.age_var.set("25")
        generator.user_info = {'test': 'data'}
        
        generator.clear_form()
        
        # Check values not cleared
        self.assertEqual(generator.age_var.get(), "25")
        self.assertEqual(generator.user_info, {'test': 'data'})
    
    def test_get_user_info(self):
        """Test get user info"""
        generator = ProfileGenerator(self.parent, self.model_manager, self.logger)
        
        test_info = {'age': 25, 'occupation': 'Engineer'}
        generator.user_info = test_info
        
        result = generator.get_user_info()
        
        self.assertEqual(result, test_info)
        # Should return a copy, not the original
        self.assertIsNot(result, generator.user_info)
    
    def test_get_user_info_empty(self):
        """Test get user info when empty"""
        generator = ProfileGenerator(self.parent, self.model_manager, self.logger)
        
        result = generator.get_user_info()
        
        self.assertEqual(result, {})


class TestPhotoSelectorMethods(unittest.TestCase):
    """Test PhotoSelector methods that don't require full GUI setup"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('src.gui.photo_selector.tk.Tk')
    def test_photo_selector_init_components(self, mock_tk):
        """Test PhotoSelector initialization components"""
        from src.gui.photo_selector import PhotoSelector
        
        mock_parent = MagicMock()
        mock_model_manager = MagicMock()
        mock_logger = MagicMock()
        
        # Mock the tkinter components to avoid GUI creation
        with patch('src.gui.photo_selector.ttk.Frame'), \
             patch('src.gui.photo_selector.ttk.Label'), \
             patch('src.gui.photo_selector.ttk.Button'), \
             patch('src.gui.photo_selector.ttk.Progressbar'), \
             patch('src.gui.photo_selector.tk.Canvas'), \
             patch('src.gui.photo_selector.ttk.Scrollbar'), \
             patch('src.gui.photo_selector.tk.StringVar'), \
             patch('src.gui.photo_selector.tk.DoubleVar'):
            
            selector = PhotoSelector(mock_parent, mock_model_manager, mock_logger)
            
            self.assertEqual(selector.parent, mock_parent)
            self.assertEqual(selector.model_manager, mock_model_manager)
            self.assertEqual(selector.logger, mock_logger)
            self.assertEqual(selector.uploaded_photos, [])
            self.assertEqual(selector.analyzed_photos, [])


if __name__ == '__main__':
    unittest.main()