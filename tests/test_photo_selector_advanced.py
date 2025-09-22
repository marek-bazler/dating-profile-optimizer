"""
Advanced tests for PhotoSelector functionality
"""

import unittest
import tempfile
import shutil
from unittest.mock import MagicMock, patch, Mock, call
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestPhotoSelectorAdvanced(unittest.TestCase):
    """Advanced tests for PhotoSelector methods"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        
        # Create test image files
        self.test_images = []
        for i in range(3):
            img_path = Path(self.test_dir) / f"test_image_{i}.jpg"
            img_path.write_text(f"fake image data {i}")
            self.test_images.append(str(img_path))
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('src.gui.photo_selector.tk.Tk')
    @patch('src.gui.photo_selector.filedialog.askopenfilenames')
    def test_upload_photos_success(self, mock_filedialog, mock_tk):
        """Test successful photo upload"""
        from src.gui.photo_selector import PhotoSelector
        
        # Mock GUI components
        with patch('src.gui.photo_selector.ttk.Frame'), \
             patch('src.gui.photo_selector.ttk.Label'), \
             patch('src.gui.photo_selector.ttk.Button'), \
             patch('src.gui.photo_selector.ttk.Progressbar'), \
             patch('src.gui.photo_selector.tk.Canvas'), \
             patch('src.gui.photo_selector.ttk.Scrollbar'):
            
            mock_parent = MagicMock()
            mock_model_manager = MagicMock()
            mock_logger = MagicMock()
            
            selector = PhotoSelector(mock_parent, mock_model_manager, mock_logger)
            
            # Mock file dialog to return test images
            mock_filedialog.return_value = self.test_images
            
            selector.upload_photos()
            
            # Verify photos uploaded
            self.assertEqual(selector.uploaded_photos, self.test_images)
            self.assertIn("3 photos uploaded", selector.upload_status.get())
            mock_logger.info.assert_called_with("Uploaded 3 photos")
    
    @patch('src.gui.photo_selector.tk.Tk')
    @patch('src.gui.photo_selector.filedialog.askopenfilenames')
    def test_upload_photos_cancelled(self, mock_filedialog, mock_tk):
        """Test cancelled photo upload"""
        from src.gui.photo_selector import PhotoSelector
        
        with patch('src.gui.photo_selector.ttk.Frame'), \
             patch('src.gui.photo_selector.ttk.Label'), \
             patch('src.gui.photo_selector.ttk.Button'), \
             patch('src.gui.photo_selector.ttk.Progressbar'), \
             patch('src.gui.photo_selector.tk.Canvas'), \
             patch('src.gui.photo_selector.ttk.Scrollbar'):
            
            mock_parent = MagicMock()
            mock_model_manager = MagicMock()
            mock_logger = MagicMock()
            
            selector = PhotoSelector(mock_parent, mock_model_manager, mock_logger)
            
            # Mock file dialog to return empty (cancelled)
            mock_filedialog.return_value = []
            
            selector.upload_photos()
            
            # Verify no photos uploaded
            self.assertEqual(selector.uploaded_photos, [])
            self.assertEqual(selector.upload_status.get(), "No photos selected")
    
    @patch('src.gui.photo_selector.tk.Tk')
    @patch('src.gui.photo_selector.messagebox.showerror')
    def test_analyze_photos_no_upload(self, mock_showerror, mock_tk):
        """Test analyze photos without upload"""
        from src.gui.photo_selector import PhotoSelector
        
        with patch('src.gui.photo_selector.ttk.Frame'), \
             patch('src.gui.photo_selector.ttk.Label'), \
             patch('src.gui.photo_selector.ttk.Button'), \
             patch('src.gui.photo_selector.ttk.Progressbar'), \
             patch('src.gui.photo_selector.tk.Canvas'), \
             patch('src.gui.photo_selector.ttk.Scrollbar'):
            
            mock_parent = MagicMock()
            mock_model_manager = MagicMock()
            mock_logger = MagicMock()
            
            selector = PhotoSelector(mock_parent, mock_model_manager, mock_logger)
            
            selector.analyze_photos()
            
            mock_showerror.assert_called_once()
            self.assertIn("upload photos first", mock_showerror.call_args[0][1])
    
    @patch('src.gui.photo_selector.tk.Tk')
    @patch('src.gui.photo_selector.messagebox.showerror')
    def test_analyze_photos_models_not_loaded(self, mock_showerror, mock_tk):
        """Test analyze photos when models not loaded"""
        from src.gui.photo_selector import PhotoSelector
        
        with patch('src.gui.photo_selector.ttk.Frame'), \
             patch('src.gui.photo_selector.ttk.Label'), \
             patch('src.gui.photo_selector.ttk.Button'), \
             patch('src.gui.photo_selector.ttk.Progressbar'), \
             patch('src.gui.photo_selector.tk.Canvas'), \
             patch('src.gui.photo_selector.ttk.Scrollbar'):
            
            mock_parent = MagicMock()
            mock_model_manager = MagicMock()
            mock_model_manager.models_loaded = False
            mock_logger = MagicMock()
            
            selector = PhotoSelector(mock_parent, mock_model_manager, mock_logger)
            selector.uploaded_photos = self.test_images
            
            selector.analyze_photos()
            
            mock_showerror.assert_called_once()
            self.assertIn("load AI models first", mock_showerror.call_args[0][1])
    
    @patch('src.gui.photo_selector.tk.Tk')
    @patch('src.gui.photo_selector.threading.Thread')
    def test_analyze_photos_success(self, mock_thread, mock_tk):
        """Test successful photo analysis"""
        from src.gui.photo_selector import PhotoSelector
        
        with patch('src.gui.photo_selector.ttk.Frame'), \
             patch('src.gui.photo_selector.ttk.Label'), \
             patch('src.gui.photo_selector.ttk.Button'), \
             patch('src.gui.photo_selector.ttk.Progressbar'), \
             patch('src.gui.photo_selector.tk.Canvas'), \
             patch('src.gui.photo_selector.ttk.Scrollbar'):
            
            mock_parent = MagicMock()
            mock_model_manager = MagicMock()
            mock_model_manager.models_loaded = True
            mock_logger = MagicMock()
            
            selector = PhotoSelector(mock_parent, mock_model_manager, mock_logger)
            selector.uploaded_photos = self.test_images
            
            selector.analyze_photos()
            
            # Verify thread was created and started
            mock_thread.assert_called_once()
            mock_thread.return_value.start.assert_called_once()
    
    def test_update_progress(self):
        """Test progress update functionality"""
        from src.gui.photo_selector import PhotoSelector
        
        with patch('src.gui.photo_selector.tk.Tk'), \
             patch('src.gui.photo_selector.ttk.Frame'), \
             patch('src.gui.photo_selector.ttk.Label'), \
             patch('src.gui.photo_selector.ttk.Button'), \
             patch('src.gui.photo_selector.ttk.Progressbar'), \
             patch('src.gui.photo_selector.tk.Canvas'), \
             patch('src.gui.photo_selector.ttk.Scrollbar'):
            
            mock_parent = MagicMock()
            mock_model_manager = MagicMock()
            mock_logger = MagicMock()
            
            selector = PhotoSelector(mock_parent, mock_model_manager, mock_logger)
            
            selector.update_progress(75.0)
            
            # Verify progress bar updated
            selector.progress_var.set.assert_called_with(75.0)
            mock_parent.update_idletasks.assert_called_once()
    
    def test_get_analyzed_photos(self):
        """Test getting analyzed photos"""
        from src.gui.photo_selector import PhotoSelector
        
        with patch('src.gui.photo_selector.tk.Tk'), \
             patch('src.gui.photo_selector.ttk.Frame'), \
             patch('src.gui.photo_selector.ttk.Label'), \
             patch('src.gui.photo_selector.ttk.Button'), \
             patch('src.gui.photo_selector.ttk.Progressbar'), \
             patch('src.gui.photo_selector.tk.Canvas'), \
             patch('src.gui.photo_selector.ttk.Scrollbar'):
            
            mock_parent = MagicMock()
            mock_model_manager = MagicMock()
            mock_logger = MagicMock()
            
            selector = PhotoSelector(mock_parent, mock_model_manager, mock_logger)
            
            test_analyzed_photos = [
                {'image_path': 'test1.jpg', 'attractiveness_score': 0.8},
                {'image_path': 'test2.jpg', 'attractiveness_score': 0.6}
            ]
            selector.analyzed_photos = test_analyzed_photos
            
            result = selector.get_analyzed_photos()
            
            self.assertEqual(result, test_analyzed_photos)
    
    @patch('src.gui.photo_selector.tk.Tk')
    def test_clear_results_display(self, mock_tk):
        """Test clearing results display"""
        from src.gui.photo_selector import PhotoSelector
        
        with patch('src.gui.photo_selector.ttk.Frame'), \
             patch('src.gui.photo_selector.ttk.Label'), \
             patch('src.gui.photo_selector.ttk.Button'), \
             patch('src.gui.photo_selector.ttk.Progressbar'), \
             patch('src.gui.photo_selector.tk.Canvas'), \
             patch('src.gui.photo_selector.ttk.Scrollbar'):
            
            mock_parent = MagicMock()
            mock_model_manager = MagicMock()
            mock_logger = MagicMock()
            
            selector = PhotoSelector(mock_parent, mock_model_manager, mock_logger)
            
            # Mock some child widgets
            mock_widget1 = MagicMock()
            mock_widget2 = MagicMock()
            selector.results_display.winfo_children.return_value = [mock_widget1, mock_widget2]
            
            selector.clear_results_display()
            
            # Verify widgets destroyed
            mock_widget1.destroy.assert_called_once()
            mock_widget2.destroy.assert_called_once()


if __name__ == '__main__':
    unittest.main()