"""
Unit tests for model manager
"""

import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path
import torch
from PIL import Image
import numpy as np

from src.models.model_manager import ModelManager


class TestModelManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('src.models.model_manager.torch.cuda.is_available')
    def test_init_cuda_available(self, mock_cuda):
        """Test initialization when CUDA is available"""
        mock_cuda.return_value = True
        
        manager = ModelManager()
        
        self.assertEqual(manager.device, "cuda")
        self.assertFalse(manager.models_loaded)
        self.assertEqual(len(manager.model_configs), 3)
        self.assertIn('text_generator', manager.model_configs)
        self.assertIn('image_captioner', manager.model_configs)
        self.assertIn('sentiment_analyzer', manager.model_configs)
    
    @patch('src.models.model_manager.torch.cuda.is_available')
    def test_init_cuda_not_available(self, mock_cuda):
        """Test initialization when CUDA is not available"""
        mock_cuda.return_value = False
        
        manager = ModelManager()
        
        self.assertEqual(manager.device, "cpu")
    
    @patch('src.models.model_manager.torch.cuda.is_available')
    @patch('src.models.model_manager.AutoTokenizer')
    @patch('src.models.model_manager.AutoModelForCausalLM')
    @patch('src.models.model_manager.BlipProcessor')
    @patch('src.models.model_manager.BlipForConditionalGeneration')
    @patch('src.models.model_manager.pipeline')
    def test_load_models_success(self, mock_pipeline, mock_blip_model, mock_blip_processor, 
                                mock_auto_model, mock_tokenizer, mock_cuda):
        """Test successful model loading"""
        mock_cuda.return_value = False
        
        # Setup mocks
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        mock_processor_instance = MagicMock()
        mock_blip_instance = MagicMock()
        mock_pipeline_instance = MagicMock()
        
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        mock_auto_model.from_pretrained.return_value = mock_model_instance
        mock_blip_processor.from_pretrained.return_value = mock_processor_instance
        mock_blip_model.from_pretrained.return_value = mock_blip_instance
        mock_pipeline.return_value = mock_pipeline_instance
        
        manager = ModelManager()
        
        # Mock progress callback
        progress_callback = MagicMock()
        
        manager.load_models(progress_callback)
        
        # Verify models loaded
        self.assertTrue(manager.models_loaded)
        self.assertEqual(len(manager.models), 3)
        self.assertEqual(len(manager.tokenizers), 1)
        self.assertEqual(len(manager.processors), 1)
        
        # Verify progress callback called
        self.assertTrue(progress_callback.called)
    
    @patch('src.models.model_manager.torch.cuda.is_available')
    def test_load_models_without_callback(self, mock_cuda):
        """Test model loading without progress callback"""
        mock_cuda.return_value = False
        
        with patch.object(ModelManager, '_load_single_model') as mock_load:
            manager = ModelManager()
            manager.load_models()
            
            # Should call _load_single_model for each model
            self.assertEqual(mock_load.call_count, 3)
    
    @patch('src.models.model_manager.torch.cuda.is_available')
    def test_load_models_failure(self, mock_cuda):
        """Test model loading failure"""
        mock_cuda.return_value = False
        
        with patch.object(ModelManager, '_load_single_model', side_effect=Exception("Load failed")):
            manager = ModelManager()
            
            with self.assertRaises(Exception):
                manager.load_models()
    
    @patch('src.models.model_manager.torch.cuda.is_available')
    @patch('src.models.model_manager.AutoTokenizer')
    @patch('src.models.model_manager.AutoModelForCausalLM')
    def test_load_single_model_text_generation(self, mock_auto_model, mock_tokenizer, mock_cuda):
        """Test loading text generation model"""
        mock_cuda.return_value = False
        
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        mock_auto_model.from_pretrained.return_value = mock_model_instance
        
        manager = ModelManager()
        config = {'name': 'test-model', 'type': 'text_generation'}
        
        manager._load_single_model('test_key', config)
        
        self.assertIn('test_key', manager.tokenizers)
        self.assertIn('test_key', manager.models)
    
    @patch('src.models.model_manager.torch.cuda.is_available')
    @patch('src.models.model_manager.BlipProcessor')
    @patch('src.models.model_manager.BlipForConditionalGeneration')
    def test_load_single_model_image_captioning(self, mock_blip_model, mock_blip_processor, mock_cuda):
        """Test loading image captioning model"""
        mock_cuda.return_value = False
        
        mock_processor_instance = MagicMock()
        mock_model_instance = MagicMock()
        mock_blip_processor.from_pretrained.return_value = mock_processor_instance
        mock_blip_model.from_pretrained.return_value = mock_model_instance
        
        manager = ModelManager()
        config = {'name': 'test-model', 'type': 'image_captioning'}
        
        manager._load_single_model('test_key', config)
        
        self.assertIn('test_key', manager.processors)
        self.assertIn('test_key', manager.models)
    
    @patch('src.models.model_manager.torch.cuda.is_available')
    @patch('src.models.model_manager.pipeline')
    def test_load_single_model_sentiment(self, mock_pipeline, mock_cuda):
        """Test loading sentiment analysis model"""
        mock_cuda.return_value = False
        
        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        manager = ModelManager()
        config = {'name': 'test-model', 'type': 'sentiment'}
        
        manager._load_single_model('test_key', config)
        
        self.assertIn('test_key', manager.models)
    
    def test_generate_profile_description_models_not_loaded(self):
        """Test profile generation when models not loaded"""
        manager = ModelManager()
        manager.models_loaded = False
        
        with self.assertRaises(RuntimeError):
            manager.generate_profile_description({}, [])
    
    @patch('src.models.model_manager.torch.cuda.is_available')
    def test_generate_profile_description_success(self, mock_cuda):
        """Test successful profile description generation"""
        mock_cuda.return_value = False
        
        manager = ModelManager()
        manager.models_loaded = True
        
        # Mock tokenizer and model
        mock_tokenizer = MagicMock()
        mock_model = MagicMock()
        
        mock_tokenizer.pad_token = None
        mock_tokenizer.eos_token = "<eos>"
        mock_tokenizer.eos_token_id = 1
        mock_tokenizer.encode.return_value = torch.tensor([[1, 2, 3]])
        mock_tokenizer.decode.return_value = "Test context. Generated description here."
        
        mock_outputs = MagicMock()
        mock_outputs.__getitem__.return_value = torch.tensor([1, 2, 3, 4, 5])
        mock_model.generate.return_value = [mock_outputs]
        
        manager.tokenizers['text_generator'] = mock_tokenizer
        manager.models['text_generator'] = mock_model
        
        user_info = {'age': 25, 'interests': 'hiking', 'occupation': 'engineer'}
        image_descriptions = ['person smiling', 'outdoor activity']
        
        with patch.object(manager, '_prepare_profile_context', return_value="Test context."):
            with patch.object(manager, '_clean_description', return_value="Clean description"):
                result = manager.generate_profile_description(user_info, image_descriptions)
                
                self.assertEqual(result, "Clean description")
    
    @patch('src.models.model_manager.torch.cuda.is_available')
    def test_generate_profile_description_error(self, mock_cuda):
        """Test profile generation error handling"""
        mock_cuda.return_value = False
        
        manager = ModelManager()
        manager.models_loaded = True
        manager.tokenizers['text_generator'] = None  # This will cause an error
        
        result = manager.generate_profile_description({}, [])
        
        self.assertEqual(result, "Error generating description. Please try again.")
    
    @patch('src.models.model_manager.torch.cuda.is_available')
    @patch('src.models.model_manager.Image')
    def test_analyze_image_success(self, mock_image, mock_cuda):
        """Test successful image analysis"""
        mock_cuda.return_value = False
        
        manager = ModelManager()
        
        # Mock image
        mock_img = MagicMock()
        mock_image.open.return_value = mock_img
        mock_img.convert.return_value = mock_img
        
        # Mock processor and model
        mock_processor = MagicMock()
        mock_model = MagicMock()
        mock_sentiment_pipeline = MagicMock()
        
        # Mock processor to return proper tensor format
        mock_inputs = MagicMock()
        mock_inputs.__getitem__ = MagicMock(return_value=torch.tensor([1, 2, 3]))
        mock_inputs.to = MagicMock(return_value=mock_inputs)  # Mock the .to() method
        mock_processor.return_value = mock_inputs
        
        mock_model.generate.return_value = torch.tensor([[1, 2, 3]])
        mock_processor.decode.return_value = "A person smiling"
        mock_sentiment_pipeline.return_value = [{'label': 'POSITIVE', 'score': 0.8}]
        
        manager.processors['image_captioner'] = mock_processor
        manager.models['image_captioner'] = mock_model
        manager.models['sentiment_analyzer'] = mock_sentiment_pipeline
        
        with patch.object(manager, '_calculate_attractiveness_score', return_value=0.75):
            result = manager.analyze_image("test_image.jpg")
            
            self.assertEqual(result['caption'], "A person smiling")
            self.assertEqual(result['sentiment']['label'], 'POSITIVE')
            self.assertEqual(result['attractiveness_score'], 0.75)
            self.assertEqual(result['image_path'], "test_image.jpg")
    
    @patch('src.models.model_manager.torch.cuda.is_available')
    @patch('src.models.model_manager.Image')
    def test_analyze_image_error(self, mock_image, mock_cuda):
        """Test image analysis error handling"""
        mock_cuda.return_value = False
        mock_image.open.side_effect = Exception("File not found")
        
        manager = ModelManager()
        
        result = manager.analyze_image("nonexistent.jpg")
        
        self.assertEqual(result['caption'], 'Error analyzing image')
        self.assertEqual(result['sentiment']['label'], 'NEUTRAL')
        self.assertEqual(result['attractiveness_score'], 0.5)
    
    def test_prepare_profile_context(self):
        """Test profile context preparation"""
        manager = ModelManager()
        
        user_info = {
            'age': 25,
            'interests': 'hiking, reading',
            'occupation': 'software engineer'
        }
        image_descriptions = ['person hiking', 'person reading', 'person smiling', 'extra description']
        
        context = manager._prepare_profile_context(user_info, image_descriptions)
        
        self.assertIn("Age: 25", context)
        self.assertIn("Interests: hiking, reading", context)
        self.assertIn("Occupation: software engineer", context)
        self.assertIn("person hiking", context)
        self.assertIn("person reading", context)
        self.assertIn("person smiling", context)
        self.assertNotIn("extra description", context)  # Should limit to 3
    
    def test_prepare_profile_context_minimal(self):
        """Test profile context with minimal information"""
        manager = ModelManager()
        
        user_info = {'age': 30}
        image_descriptions = []
        
        context = manager._prepare_profile_context(user_info, image_descriptions)
        
        self.assertIn("Age: 30", context)
        self.assertIn("Create an attractive dating profile", context)
    
    def test_clean_description(self):
        """Test description cleaning"""
        manager = ModelManager()
        
        # Test with repetitive and messy text
        messy_description = "Great person.\nGreat person.\nLoves hiking and reading.\n\nShort.\nLoves hiking and reading.\nAnother line here."
        
        cleaned = manager._clean_description(messy_description)
        
        # Should remove duplicates and short lines
        self.assertNotIn("Short.", cleaned)
        # Should not have duplicate "Great person."
        self.assertEqual(cleaned.count("Great person."), 1)
    
    def test_clean_description_long_text(self):
        """Test description cleaning with long text"""
        manager = ModelManager()
        
        long_description = "A" * 600  # Longer than 500 chars
        
        cleaned = manager._clean_description(long_description)
        
        self.assertTrue(len(cleaned) <= 503)  # 500 + "..."
        self.assertTrue(cleaned.endswith("..."))
    
    def test_calculate_attractiveness_score_positive(self):
        """Test attractiveness score calculation with positive sentiment"""
        manager = ModelManager()
        
        caption = "A beautiful person with a confident smile"
        sentiment = {'label': 'POSITIVE', 'score': 0.9}
        
        score = manager._calculate_attractiveness_score(caption, sentiment)
        
        # Should be higher than base score due to positive sentiment and keywords
        self.assertGreater(score, 0.5)
        self.assertLessEqual(score, 1.0)
    
    def test_calculate_attractiveness_score_negative(self):
        """Test attractiveness score calculation with negative sentiment"""
        manager = ModelManager()
        
        caption = "A sad looking person"
        sentiment = {'label': 'NEGATIVE', 'score': 0.8}
        
        score = manager._calculate_attractiveness_score(caption, sentiment)
        
        # Should be lower than base score due to negative sentiment
        self.assertLess(score, 0.5)
        self.assertGreaterEqual(score, 0.0)
    
    def test_calculate_attractiveness_score_neutral(self):
        """Test attractiveness score calculation with neutral sentiment"""
        manager = ModelManager()
        
        caption = "A person standing"
        sentiment = {'label': 'NEUTRAL', 'score': 0.5}
        
        score = manager._calculate_attractiveness_score(caption, sentiment)
        
        # Should be close to base score
        self.assertAlmostEqual(score, 0.5, delta=0.1)


if __name__ == '__main__':
    unittest.main()