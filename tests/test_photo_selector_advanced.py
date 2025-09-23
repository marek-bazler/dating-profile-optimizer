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
    
    def _create_photo_selector_with_mocks(self):
        """Helper method to create PhotoSelector with all necessary mocks"""
        from src.gui.photo_selector import PhotoSelector
        
        with patch('src.gui.photo_selector.ttk.Frame'), \
             patch('src.gui.photo_selector.ttk.Label'), \
             patch('src.gui.photo_selector.ttk.Button'), \
             patch('src.gui.photo_selector.ttk.Progressbar'), \
             patch('src.gui.photo_selector.tk.Canvas'), \
             patch('src.gui.photo_selector.ttk.Scrollbar'), \
             patch('src.gui.photo_selector.tk.StringVar') as mock_stringvar, \
             patch('src.gui.photo_selector.tk.DoubleVar') as mock_doublevar:
            
            # Mock the StringVar and DoubleVar instances
            mock_stringvar_instance = MagicMock()
            mock_doublevar_instance = MagicMock()
            mock_stringvar.return_value = mock_stringvar_instance
            mock_doublevar.return_value = mock_doublevar_instance
            
            mock_parent = MagicMock()
            mock_model_manager = MagicMock()
            mock_logger = MagicMock()
            
            selector = PhotoSelector(mock_parent, mock_model_manager, mock_logger)
            
            # Manually set the mocked variables
            selector.upload_status = mock_stringvar_instance
            selector.analysis_status = mock_stringvar_instance
            selector.progress_var = mock_doublevar_instance
            
            return selector, mock_parent, mock_model_manager, mock_logger
    
    @patch('src.gui.photo_selector.filedialog.askopenfilenames')
    def test_upload_photos_success(self, mock_filedialog):
        """Test successful photo upload"""
        selector, mock_parent, mock_model_manager, mock_logger = self._create_photo_selector_with_mocks()
        
        # Mock file dialog to return test images
        mock_filedialog.return_value = self.test_images
        
        selector.upload_photos()
        
        # Verify photos uploaded
        self.assertEqual(selector.uploaded_photos, self.test_images)
        # Check that both status messages were set
        selector.upload_status.set.assert_any_call("3 photos uploaded")
        selector.analysis_status.set.assert_called_with("Photos uploaded - ready for analysis")
        mock_logger.info.assert_called_with("Uploaded 3 photos")
    
    @patch('src.gui.photo_selector.filedialog.askopenfilenames')
    def test_upload_photos_cancelled(self, mock_filedialog):
        """Test cancelled photo upload"""
        selector, mock_parent, mock_model_manager, mock_logger = self._create_photo_selector_with_mocks()
        
        # Mock file dialog to return empty (cancelled)
        mock_filedialog.return_value = []
        
        selector.upload_photos()
        
        # Verify no photos uploaded
        self.assertEqual(selector.uploaded_photos, [])
        selector.upload_status.set.assert_called_with("No photos selected")
    
    @patch('src.gui.photo_selector.messagebox.showerror')
    def test_analyze_photos_no_upload(self, mock_showerror):
        """Test analyze photos without upload"""
        selector, mock_parent, mock_model_manager, mock_logger = self._create_photo_selector_with_mocks()
        
        selector.analyze_photos()
        
        mock_showerror.assert_called_once()
        self.assertIn("upload photos first", mock_showerror.call_args[0][1])
    
    @patch('src.gui.photo_selector.messagebox.showerror')
    def test_analyze_photos_models_not_loaded(self, mock_showerror):
        """Test analyze photos when models not loaded"""
        selector, mock_parent, mock_model_manager, mock_logger = self._create_photo_selector_with_mocks()
        
        mock_model_manager.models_loaded = False
        selector.uploaded_photos = self.test_images
        
        selector.analyze_photos()
        
        mock_showerror.assert_called_once()
        self.assertIn("load AI models first", mock_showerror.call_args[0][1])
    
    @patch('src.gui.photo_selector.threading.Thread')
    def test_analyze_photos_success(self, mock_thread):
        """Test successful photo analysis"""
        selector, mock_parent, mock_model_manager, mock_logger = self._create_photo_selector_with_mocks()
        
        mock_model_manager.models_loaded = True
        selector.uploaded_photos = self.test_images
        
        selector.analyze_photos()
        
        # Verify thread was created and started
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
    
    def test_update_progress(self):
        """Test progress update functionality"""
        selector, mock_parent, mock_model_manager, mock_logger = self._create_photo_selector_with_mocks()
        
        selector.update_progress(75.0)
        
        # Verify progress bar updated
        selector.progress_var.set.assert_called_with(75.0)
        mock_parent.update_idletasks.assert_called_once()
    
    def test_get_analyzed_photos(self):
        """Test getting analyzed photos"""
        selector, mock_parent, mock_model_manager, mock_logger = self._create_photo_selector_with_mocks()
        
        test_analyzed_photos = [
            {'image_path': 'test1.jpg', 'attractiveness_score': 0.8},
            {'image_path': 'test2.jpg', 'attractiveness_score': 0.6}
        ]
        selector.analyzed_photos = test_analyzed_photos
        
        result = selector.get_analyzed_photos()
        
        self.assertEqual(result, test_analyzed_photos)
    
    def test_clear_results_display(self):
        """Test clearing results display"""
        selector, mock_parent, mock_model_manager, mock_logger = self._create_photo_selector_with_mocks()
        
        # Mock some child widgets
        mock_widget1 = MagicMock()
        mock_widget2 = MagicMock()
        selector.results_display = MagicMock()
        selector.results_display.winfo_children.return_value = [mock_widget1, mock_widget2]
        
        selector.clear_results_display()
        
        # Verify widgets destroyed
        mock_widget1.destroy.assert_called_once()
        mock_widget2.destroy.assert_called_once()


if __name__ == '__main__':
    unittest.main()