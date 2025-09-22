"""
Integration tests for the Dating Profile Optimizer
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.model_manager import ModelManager
from utils.logger import setup_logger


class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('models.model_manager.torch.cuda.is_available')
    def test_model_manager_initialization_flow(self, mock_cuda):
        """Test complete model manager initialization flow"""
        mock_cuda.return_value = False
        
        # Test initialization
        manager = ModelManager()
        
        self.assertFalse(manager.models_loaded)
        self.assertEqual(manager.device, "cpu")
        self.assertEqual(len(manager.model_configs), 3)
        
        # Test model configuration structure
        for model_key, config in manager.model_configs.items():
            self.assertIn('name', config)
            self.assertIn('type', config)
            self.assertIsInstance(config['name'], str)
            self.assertIsInstance(config['type'], str)
    
    @patch('utils.logger.Path.cwd')
    def test_logger_integration_with_model_manager(self, mock_cwd):
        """Test logger integration with model manager"""
        mock_cwd.return_value = Path(self.test_dir)
        
        with patch('utils.logger.Path.mkdir'):
            # Setup logger
            logger = setup_logger()
            
            # Create model manager (should use the logger)
            with patch('models.model_manager.torch.cuda.is_available', return_value=False):
                manager = ModelManager()
                
                # Verify logger is accessible
                self.assertIsNotNone(manager.logger)
                self.assertEqual(manager.logger.name, 'models.model_manager')
    
    def test_profile_context_generation_integration(self):
        """Test profile context generation with various inputs"""
        with patch('models.model_manager.torch.cuda.is_available', return_value=False):
            manager = ModelManager()
            
            # Test with complete user info
            complete_user_info = {
                'age': 28,
                'interests': 'photography, hiking, cooking',
                'occupation': 'graphic designer',
                'location': 'San Francisco',
                'personality': 'creative and adventurous'
            }
            
            image_descriptions = [
                'person taking photos outdoors',
                'person hiking in mountains',
                'person cooking in kitchen'
            ]
            
            context = manager._prepare_profile_context(complete_user_info, image_descriptions)
            
            # Verify all information is included
            self.assertIn('Age: 28', context)
            self.assertIn('photography, hiking, cooking', context)
            self.assertIn('graphic designer', context)
            self.assertIn('person taking photos', context)
            self.assertIn('Create an attractive dating profile', context)
            
            # Test with minimal info
            minimal_user_info = {'age': 25}
            minimal_context = manager._prepare_profile_context(minimal_user_info, [])
            
            self.assertIn('Age: 25', minimal_context)
            self.assertIn('Create an attractive dating profile', minimal_context)
    
    def test_attractiveness_score_calculation_scenarios(self):
        """Test attractiveness score calculation with various scenarios"""
        with patch('models.model_manager.torch.cuda.is_available', return_value=False):
            manager = ModelManager()
            
            # Test highly positive scenario
            positive_caption = "beautiful person with confident smile and attractive features"
            positive_sentiment = {'label': 'POSITIVE', 'score': 0.95}
            
            positive_score = manager._calculate_attractiveness_score(positive_caption, positive_sentiment)
            self.assertGreater(positive_score, 0.8)
            
            # Test negative scenario
            negative_caption = "blurry photo of person looking away"
            negative_sentiment = {'label': 'NEGATIVE', 'score': 0.8}
            
            negative_score = manager._calculate_attractiveness_score(negative_caption, negative_sentiment)
            self.assertLess(negative_score, 0.4)
            
            # Test neutral scenario
            neutral_caption = "person standing in room"
            neutral_sentiment = {'label': 'NEUTRAL', 'score': 0.5}
            
            neutral_score = manager._calculate_attractiveness_score(neutral_caption, neutral_sentiment)
            self.assertAlmostEqual(neutral_score, 0.5, delta=0.2)
    
    def test_description_cleaning_edge_cases(self):
        """Test description cleaning with various edge cases"""
        with patch('models.model_manager.torch.cuda.is_available', return_value=False):
            manager = ModelManager()
            
            # Test empty description
            empty_result = manager._clean_description("")
            self.assertEqual(empty_result, "")
            
            # Test single line
            single_line = "This is a single line description that should remain unchanged."
            single_result = manager._clean_description(single_line)
            self.assertEqual(single_result, single_line)
            
            # Test with newlines and duplicates
            messy_description = """
            Great person who loves adventure.
            
            Great person who loves adventure.
            Enjoys hiking and photography.
            Short.
            Very short line.
            Enjoys hiking and photography.
            Another unique line here.
            """
            
            cleaned = manager._clean_description(messy_description)
            
            # Should remove duplicates
            lines = cleaned.split(' ')
            unique_phrases = set()
            for line in cleaned.split('.'):
                line = line.strip()
                if line:
                    self.assertNotIn(line, unique_phrases, f"Duplicate found: {line}")
                    unique_phrases.add(line)
    
    @patch('models.model_manager.torch.cuda.is_available')
    def test_error_handling_integration(self, mock_cuda):
        """Test error handling across components"""
        mock_cuda.return_value = False
        
        manager = ModelManager()
        
        # Test profile generation without loaded models
        with self.assertRaises(RuntimeError) as context:
            manager.generate_profile_description({}, [])
        
        self.assertIn("Models not loaded", str(context.exception))
        
        # Test image analysis with invalid path
        result = manager.analyze_image("nonexistent_file.jpg")
        
        self.assertEqual(result['caption'], 'Error analyzing image')
        self.assertEqual(result['sentiment']['label'], 'NEUTRAL')
        self.assertEqual(result['attractiveness_score'], 0.5)
        self.assertEqual(result['image_path'], "nonexistent_file.jpg")


class TestDataFlow(unittest.TestCase):
    """Test data flow between components"""
    
    def test_user_info_data_structure(self):
        """Test user info data structure consistency"""
        # This would be the structure from ProfileGenerator
        user_info = {
            'age': 25,
            'occupation': 'Software Engineer',
            'location': 'New York',
            'interests': 'hiking, reading, coding',
            'personality': 'outgoing and friendly',
            'looking_for': 'meaningful relationship',
            'style': 'humorous'
        }
        
        # Test that ModelManager can handle this structure
        with patch('models.model_manager.torch.cuda.is_available', return_value=False):
            manager = ModelManager()
            
            # Should not raise any errors
            context = manager._prepare_profile_context(user_info, [])
            
            # Verify expected fields are included
            self.assertIn(str(user_info['age']), context)
            self.assertIn(user_info['interests'], context)
            self.assertIn(user_info['occupation'], context)
    
    def test_photo_analysis_data_structure(self):
        """Test photo analysis data structure consistency"""
        with patch('models.model_manager.torch.cuda.is_available', return_value=False):
            manager = ModelManager()
            
            # Mock the expected structure from analyze_image
            expected_structure = {
                'caption': 'A person smiling outdoors',
                'sentiment': {'label': 'POSITIVE', 'score': 0.8},
                'attractiveness_score': 0.75,
                'image_path': '/path/to/image.jpg'
            }
            
            # Test that this structure works with other methods
            descriptions = [expected_structure['caption']]
            context = manager._prepare_profile_context({'age': 25}, descriptions)
            
            self.assertIn(expected_structure['caption'], context)
    
    def test_export_data_structure(self):
        """Test export data structure"""
        # This would be the structure for export
        export_data = {
            "recommended_photos": [
                {
                    "path": "/path/to/photo1.jpg",
                    "score": 0.85,
                    "caption": "Person smiling confidently"
                },
                {
                    "path": "/path/to/photo2.jpg", 
                    "score": 0.78,
                    "caption": "Person enjoying outdoor activity"
                }
            ]
        }
        
        # Test JSON serialization
        json_str = json.dumps(export_data, indent=2)
        parsed_data = json.loads(json_str)
        
        self.assertEqual(parsed_data, export_data)
        self.assertEqual(len(parsed_data["recommended_photos"]), 2)
        
        for photo in parsed_data["recommended_photos"]:
            self.assertIn("path", photo)
            self.assertIn("score", photo)
            self.assertIn("caption", photo)
            self.assertIsInstance(photo["score"], (int, float))


if __name__ == '__main__':
    unittest.main()