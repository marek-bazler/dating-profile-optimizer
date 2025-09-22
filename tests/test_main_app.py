"""
Unit tests for main application
"""

import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch, Mock
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import DatingProfileApp


class TestDatingProfileApp(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        # Mock tkinter to avoid GUI creation during tests
        self.tk_patcher = patch('main.tk.Tk')
        self.mock_tk = self.tk_patcher.start()
        self.mock_root = MagicMock()
        self.mock_tk.return_value = self.mock_root
        
    def tearDown(self):
        """Clean up test environment"""
        self.tk_patcher.stop()
    
    @patch('main.setup_logger')
    @patch('main.ModelManager')
    @patch('main.MainWindow')
    def test_init(self, mock_main_window, mock_model_manager, mock_setup_logger):
        """Test DatingProfileApp initialization"""
        mock_logger = MagicMock()
        mock_setup_logger.return_value = mock_logger
        mock_manager = MagicMock()
        mock_model_manager.return_value = mock_manager
        mock_window = MagicMock()
        mock_main_window.return_value = mock_window
        
        app = DatingProfileApp()
        
        # Verify root window setup
        self.mock_root.title.assert_called_with("Dating Profile Optimizer")
        self.mock_root.geometry.assert_called_with("1200x800")
        
        # Verify logger setup
        mock_setup_logger.assert_called_once()
        mock_logger.info.assert_called_with("Starting Dating Profile Optimizer")
        
        # Verify model manager creation
        mock_model_manager.assert_called_once()
        
        # Verify main window creation
        mock_main_window.assert_called_once_with(self.mock_root, mock_manager, mock_logger)
        
        # Verify attributes
        self.assertEqual(app.root, self.mock_root)
        self.assertEqual(app.logger, mock_logger)
        self.assertEqual(app.model_manager, mock_manager)
        self.assertEqual(app.main_window, mock_window)
    
    @patch('main.setup_logger')
    @patch('main.ModelManager')
    @patch('main.MainWindow')
    def test_run_success(self, mock_main_window, mock_model_manager, mock_setup_logger):
        """Test successful app run"""
        app = DatingProfileApp()
        
        app.run()
        
        self.mock_root.mainloop.assert_called_once()
    
    @patch('main.setup_logger')
    @patch('main.ModelManager')
    @patch('main.MainWindow')
    @patch('main.messagebox.showerror')
    def test_run_with_exception(self, mock_showerror, mock_main_window, mock_model_manager, mock_setup_logger):
        """Test app run with exception"""
        mock_logger = MagicMock()
        mock_setup_logger.return_value = mock_logger
        
        # Make mainloop raise an exception
        self.mock_root.mainloop.side_effect = Exception("Test error")
        
        app = DatingProfileApp()
        app.run()
        
        # Verify error handling
        mock_logger.error.assert_called_with("Application error: Test error")
        mock_showerror.assert_called_with("Error", "Application error: Test error")


if __name__ == '__main__':
    unittest.main()