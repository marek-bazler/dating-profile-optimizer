"""
Unit tests for Facebook data parser
"""

import unittest
import tempfile
import shutil
import json
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.facebook_parser import FacebookDataParser


class TestFacebookDataParser(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.parser = FacebookDataParser()
        
        # Create sample Facebook data
        self.sample_profile_data = {
            "profile_v2": {
                "name": {"full_name": "John Doe"},
                "birthday": {"year": 1990, "month": 5, "day": 15},
                "gender": {"pronoun": "he/him"},
                "current_city": {"name": "San Francisco, CA"},
                "hometown": {"name": "New York, NY"},
                "relationship": {"status": "Single"},
                "bio": {"text": "Love hiking and photography"},
                "website": "https://johndoe.com",
                "email": "john@example.com"
            }
        }
        
        self.sample_photos_data = {
            "other_photos_v2": [
                {
                    "uri": "your_facebook_activity/posts/media/your_posts/profile.jpg",
                    "creation_timestamp": 1640995200,  # 2022-01-01
                    "media_metadata": {"photo_metadata": {"taken_timestamp": 1640995200}}
                }
            ]
        }
        
        self.sample_album_data = {
            "name": "Mobile uploads",
            "photos": [
                {
                    "title": "Mobile uploads",
                    "uri": "your_facebook_activity/posts/media/Mobileuploads/photo1.jpg",
                    "creation_timestamp": 1640995200,
                    "media_metadata": {"photo_metadata": {"taken_timestamp": 1640995200}}
                }
            ]
        }
        
        self.sample_interests_data = {
            "page_likes_v2": [
                {"name": "Photography", "category": "Hobby", "timestamp": 1640995200},
                {"name": "Hiking Club", "category": "Sports", "timestamp": 1640995300}
            ]
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_init(self):
        """Test FacebookDataParser initialization"""
        parser = FacebookDataParser()
        
        self.assertIsNotNone(parser.logger)
        self.assertEqual(parser.supported_formats, ['.json', '.zip'])
    
    def test_parse_json_export(self):
        """Test parsing JSON export file"""
        # Create test JSON file
        test_file = Path(self.test_dir) / "facebook_data.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(self.sample_profile_data, f)
        
        result = self.parser._parse_json_export(test_file)
        
        self.assertIsInstance(result, dict)
        self.assertIn('profile_info', result)
        self.assertIn('photos', result)
        self.assertIn('posts', result)
    
    def test_parse_profile_info(self):
        """Test parsing profile information"""
        # Create test JSON file
        test_file = Path(self.test_dir) / "profile.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(self.sample_profile_data, f)
        
        result = self.parser._parse_profile_info(test_file)
        
        self.assertEqual(result['name'], 'John Doe')
        self.assertEqual(result['birthday'], '1990-05-15')
        self.assertEqual(result['gender'], 'he/him')
        self.assertEqual(result['location'], 'San Francisco, CA')
        self.assertEqual(result['hometown'], 'New York, NY')
        self.assertEqual(result['relationship_status'], 'Single')
        self.assertEqual(result['bio'], 'Love hiking and photography')
        self.assertEqual(result['website'], 'https://johndoe.com')
        self.assertEqual(result['email'], 'john@example.com')
    
    def test_parse_new_photos(self):
        """Test parsing photos data in new format"""
        # Create test JSON file
        test_file = Path(self.test_dir) / "your_uncategorized_photos.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(self.sample_photos_data, f)
        
        # Create fake photo file structure
        photo_dir = Path(self.test_dir) / "your_facebook_activity" / "posts" / "media" / "your_posts"
        photo_dir.mkdir(parents=True)
        photo_file = photo_dir / "profile.jpg"
        photo_file.write_text("fake image data")
        
        result = self.parser._parse_new_photos(test_file, Path(self.test_dir))
        
        self.assertEqual(len(result), 1)
        photo = result[0]
        self.assertEqual(photo['title'], 'Uncategorized Photo')
        self.assertEqual(photo['description'], '')
        self.assertEqual(photo['uri'], 'your_facebook_activity/posts/media/your_posts/profile.jpg')
        self.assertIsNotNone(photo['local_path'])
        self.assertEqual(len(photo['comments']), 0)
        self.assertEqual(len(photo['reactions']), 0)
    
    def test_parse_interests(self):
        """Test parsing interests data"""
        # Create test JSON file
        test_file = Path(self.test_dir) / "interests.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(self.sample_interests_data, f)
        
        result = self.parser._parse_interests(test_file)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Photography')
        self.assertEqual(result[0]['category'], 'Hobby')
        self.assertEqual(result[1]['name'], 'Hiking Club')
        self.assertEqual(result[1]['category'], 'Sports')
    
    def test_parse_birthday(self):
        """Test birthday parsing"""
        # Valid birthday
        birthday_data = {"year": 1990, "month": 5, "day": 15}
        result = self.parser._parse_birthday(birthday_data)
        self.assertEqual(result, "1990-05-15")
        
        # Invalid birthday
        result = self.parser._parse_birthday(None)
        self.assertIsNone(result)
        
        # Incomplete birthday
        incomplete_birthday = {"year": 1990, "month": 5}
        result = self.parser._parse_birthday(incomplete_birthday)
        self.assertIsNone(result)
    
    def test_parse_location(self):
        """Test location parsing"""
        # Valid location
        location_data = {"name": "San Francisco, CA"}
        result = self.parser._parse_location(location_data)
        self.assertEqual(result, "San Francisco, CA")
        
        # Invalid location
        result = self.parser._parse_location(None)
        self.assertIsNone(result)
    
    def test_parse_timestamp(self):
        """Test timestamp parsing"""
        # Valid timestamp
        timestamp = 1640995200  # 2022-01-01 00:00:00 UTC
        result = self.parser._parse_timestamp(timestamp)
        self.assertIsNotNone(result)
        # Check that it contains a valid date (timezone may affect exact date)
        self.assertTrue(any(date in result for date in ["2021-12-31", "2022-01-01"]))
        
        # Invalid timestamp
        result = self.parser._parse_timestamp(None)
        self.assertIsNone(result)
    
    def test_extract_dating_profile_data(self):
        """Test extracting dating profile data"""
        facebook_data = {
            'profile_info': {
                'name': 'John Doe',
                'birthday': '1990-05-15',
                'location': 'San Francisco, CA',
                'hometown': 'New York, NY',
                'bio': 'Love hiking and photography'
            },
            'work_education': [
                {
                    'type': 'work',
                    'name': 'Tech Corp',
                    'position': 'Software Engineer',
                    'end_date': None
                },
                {
                    'type': 'education',
                    'name': 'University of California',
                    'position': 'Computer Science',
                    'end_date': '2012-06-01'
                }
            ],
            'interests': [
                {'name': 'Photography'},
                {'name': 'Hiking'},
                {'name': 'Travel'}
            ],
            'photos': [
                {'local_path': '/path/to/photo1.jpg', 'title': 'Photo 1'},
                {'local_path': '/path/to/photo2.jpg', 'title': 'Photo 2'}
            ]
        }
        
        result = self.parser.extract_dating_profile_data(facebook_data)
        
        self.assertEqual(result['name'], 'John Doe')
        self.assertEqual(result['age'], 35)  # Calculated from 1990 birthday (2025 - 1990)
        self.assertEqual(result['occupation'], 'Software Engineer at Tech Corp')
        self.assertEqual(result['education'], 'Computer Science from University of California')
        self.assertEqual(result['location'], 'San Francisco, CA')
        self.assertEqual(result['hometown'], 'New York, NY')
        self.assertEqual(result['bio'], 'Love hiking and photography')
        self.assertIn('Photography', result['interests'])
        self.assertEqual(len(result['photos']), 2)
        self.assertEqual(result['total_photos_found'], 2)
        self.assertEqual(result['available_photos_count'], 2)
    
    def test_find_photo_file(self):
        """Test finding photo files"""
        # Create test photo file
        photo_dir = Path(self.test_dir) / "photos"
        photo_dir.mkdir()
        photo_file = photo_dir / "test.jpg"
        photo_file.write_text("fake image data")
        
        # Test finding by relative path
        result = self.parser._find_photo_file("photos/test.jpg", Path(self.test_dir))
        self.assertEqual(result, str(photo_file))
        
        # Test finding by filename
        result = self.parser._find_photo_file("test.jpg", Path(self.test_dir))
        self.assertEqual(result, str(photo_file))
        
        # Test non-existent file
        result = self.parser._find_photo_file("nonexistent.jpg", Path(self.test_dir))
        self.assertIsNone(result)
    
    def test_parse_facebook_export_file_not_found(self):
        """Test parsing non-existent file"""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_facebook_export("nonexistent.json")
    
    def test_parse_facebook_export_unsupported_format(self):
        """Test parsing unsupported file format"""
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text("test content")
        
        with self.assertRaises(ValueError):
            self.parser.parse_facebook_export(str(test_file))
    
    @patch('zipfile.ZipFile')
    def test_parse_zip_export(self, mock_zipfile):
        """Test parsing ZIP export"""
        # Create test ZIP file
        test_zip = Path(self.test_dir) / "facebook_export.zip"
        test_zip.write_text("fake zip content")
        
        # Mock ZIP extraction
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        
        # Create temporary directory structure
        temp_dir = Path(self.test_dir) / "extracted"
        temp_dir.mkdir()
        
        # Create test JSON files
        profile_file = temp_dir / "profile_information.json"
        with open(profile_file, 'w') as f:
            json.dump(self.sample_profile_data, f)
        
        photos_file = temp_dir / "photos_and_videos.json"
        with open(photos_file, 'w') as f:
            json.dump(self.sample_photos_data, f)
        
        with patch('tempfile.TemporaryDirectory') as mock_temp_dir:
            mock_temp_dir.return_value.__enter__.return_value = str(temp_dir)
            
            with patch.object(Path, 'rglob') as mock_rglob:
                mock_rglob.return_value = [profile_file, photos_file]
                
                result = self.parser._parse_zip_export(test_zip)
                
                self.assertIsInstance(result, dict)
                self.assertIn('profile_info', result)
                self.assertIn('photos', result)


if __name__ == '__main__':
    unittest.main()