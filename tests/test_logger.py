"""
Unit tests for logger utility
"""

import unittest
import tempfile
import shutil
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.utils.logger import setup_logger


class TestLogger(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    @patch('src.utils.logger.Path.cwd')
    def test_setup_logger_default(self, mock_cwd):
        """Test logger setup with default parameters"""
        mock_cwd.return_value = Path(self.test_dir)
        
        with patch('src.utils.logger.Path.mkdir') as mock_mkdir:
            logger = setup_logger()
            
            # Verify logger creation
            self.assertIsInstance(logger, logging.Logger)
            self.assertEqual(logger.name, "dating_profile_optimizer")
            self.assertEqual(logger.level, logging.INFO)
            
            # Verify logs directory creation
            mock_mkdir.assert_called_once_with(exist_ok=True)
            
            # Verify handlers
            self.assertEqual(len(logger.handlers), 2)  # File and console handlers
    
    @patch('src.utils.logger.Path.cwd')
    def test_setup_logger_custom_name_level(self, mock_cwd):
        """Test logger setup with custom name and level"""
        mock_cwd.return_value = Path(self.test_dir)
        
        with patch('src.utils.logger.Path.mkdir'):
            logger = setup_logger(name="test_logger", level=logging.DEBUG)
            
            self.assertEqual(logger.name, "test_logger")
            self.assertEqual(logger.level, logging.DEBUG)
    
    @patch('src.utils.logger.Path.cwd')
    def test_logger_handlers_configuration(self, mock_cwd):
        """Test that handlers are properly configured"""
        mock_cwd.return_value = Path(self.test_dir)
        
        with patch('src.utils.logger.Path.mkdir'):
            with patch('src.utils.logger.logging.FileHandler') as mock_file_handler:
                with patch('src.utils.logger.logging.StreamHandler') as mock_stream_handler:
                    mock_file_instance = MagicMock()
                    mock_stream_instance = MagicMock()
                    mock_file_handler.return_value = mock_file_instance
                    mock_stream_handler.return_value = mock_stream_instance
                    
                    # Mock the level attribute for handlers
                    mock_file_instance.level = logging.DEBUG
                    mock_stream_instance.level = logging.INFO
                    
                    # Mock the logger.info call to avoid actual logging during test
                    with patch.object(logging.Logger, 'info'):
                        logger = setup_logger()
                    
                    # Verify file handler setup
                    mock_file_handler.assert_called_once()
                    mock_file_instance.setLevel.assert_called_with(logging.DEBUG)
                    mock_file_instance.setFormatter.assert_called_once()
                    
                    # Verify stream handler setup
                    mock_stream_handler.assert_called_once()
                    mock_stream_instance.setLevel.assert_called_with(logging.INFO)
                    mock_stream_instance.setFormatter.assert_called_once()
    
    @patch('src.utils.logger.Path.cwd')
    def test_logger_clears_existing_handlers(self, mock_cwd):
        """Test that existing handlers are cleared"""
        mock_cwd.return_value = Path(self.test_dir)
        
        with patch('src.utils.logger.Path.mkdir'):
            # Create logger with existing handler
            existing_logger = logging.getLogger("test_clear")
            existing_handler = logging.StreamHandler()
            existing_logger.addHandler(existing_handler)
            
            # Setup logger should clear existing handlers
            logger = setup_logger(name="test_clear")
            
            # Should have exactly 2 handlers (file + console)
            self.assertEqual(len(logger.handlers), 2)


if __name__ == '__main__':
    unittest.main()