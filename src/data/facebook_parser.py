"""
Facebook Data Export Parser
Processes Facebook data export JSON files to extract profile information and photos
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re
import zipfile
import shutil
import tempfile

class FacebookDataParser:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_formats = ['.json', '.zip']
        
    def parse_facebook_export(self, file_path: str) -> Dict[str, Any]:
        """
        Parse Facebook data export file
        
        Args:
            file_path: Path to Facebook export file (.json or .zip)
            
        Returns:
            Dictionary containing parsed Facebook data
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if file_path.suffix.lower() == '.zip':
                return self._parse_zip_export(file_path)
            elif file_path.suffix.lower() == '.json':
                return self._parse_json_export(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
                
        except Exception as e:
            self.logger.error(f"Error parsing Facebook export: {str(e)}")
            raise
    
    def _parse_zip_export(self, zip_path: Path) -> Dict[str, Any]:
        """Parse Facebook ZIP export"""
        self.logger.info(f"Parsing Facebook ZIP export: {zip_path}")
        
        # Create a permanent extraction directory
        extract_dir = Path("temp_facebook_data")
        extract_dir.mkdir(exist_ok=True)
        
        # Clean up any existing extraction
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extract_dir.mkdir()
        
        try:
            # Extract ZIP file to permanent location
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find and parse relevant JSON files
            parsed_data = {
                'profile_info': {},
                'photos': [],
                'posts': [],
                'about_info': {},
                'friends': [],
                'interests': [],
                'work_education': [],
                'extraction_path': str(extract_dir)  # Store extraction path
            }
            
            # Look for Facebook export files in the new structure
            json_files = list(extract_dir.rglob('*.json'))
            
            for json_file in json_files:
                file_name = json_file.name.lower()
                relative_path = str(json_file.relative_to(extract_dir)).lower()
                
                # Parse posts for profile information (do this first to extract name)
                if 'your_posts__check_ins__photos' in file_name:
                    parsed_data['posts'].extend(self._parse_new_posts(json_file))
                
                # Parse photos from various sources
                if ('your_uncategorized_photos' in file_name or 
                    'album' in relative_path):
                    parsed_data['photos'].extend(self._parse_new_photos(json_file, extract_dir))
                
                # Parse interests from liked pages
                elif 'pages_you\'ve_liked' in file_name or 'pages_you_have_liked' in file_name:
                    parsed_data['interests'].extend(self._parse_new_interests(json_file))
                
                # Parse other data sources
                elif 'comments' in file_name:
                    parsed_data['posts'].extend(self._parse_comments_for_profile(json_file))
            
            return parsed_data
            
        except Exception as e:
            # Clean up on error
            if extract_dir.exists():
                shutil.rmtree(extract_dir, ignore_errors=True)
            raise
    
    def _parse_json_export(self, json_path: Path) -> Dict[str, Any]:
        """Parse single Facebook JSON export file"""
        self.logger.info(f"Parsing Facebook JSON export: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Process the JSON data based on its structure
        return self._process_json_data(data, json_path.parent)
    
    def _parse_profile_info(self, json_file: Path) -> Dict[str, Any]:
        """Parse profile information from JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            profile_info = {}
            
            # Extract basic profile information
            if 'profile_v2' in data:
                profile_data = data['profile_v2']
                profile_info.update({
                    'name': profile_data.get('name', {}).get('full_name', ''),
                    'birthday': self._parse_birthday(profile_data.get('birthday')),
                    'gender': profile_data.get('gender', {}).get('pronoun', ''),
                    'location': self._parse_location(profile_data.get('current_city')),
                    'hometown': self._parse_location(profile_data.get('hometown')),
                    'relationship_status': profile_data.get('relationship', {}).get('status', ''),
                    'bio': profile_data.get('bio', {}).get('text', ''),
                    'website': profile_data.get('website', ''),
                    'email': profile_data.get('email', ''),
                    'phone': profile_data.get('phone', '')
                })
            
            return profile_info
            
        except Exception as e:
            self.logger.error(f"Error parsing profile info from {json_file}: {str(e)}")
            return {}
    
    def _parse_photos(self, json_file: Path, base_path: Path) -> List[Dict[str, Any]]:
        """Parse photos from JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            photos = []
            
            if 'photos_v2' in data:
                for photo_data in data['photos_v2']:
                    photo_info = {
                        'title': photo_data.get('title', ''),
                        'description': photo_data.get('description', ''),
                        'creation_timestamp': self._parse_timestamp(photo_data.get('creation_timestamp')),
                        'uri': photo_data.get('uri', ''),
                        'media_metadata': photo_data.get('media_metadata', {}),
                        'comments': self._parse_comments(photo_data.get('comments', [])),
                        'reactions': self._parse_reactions(photo_data.get('reactions', [])),
                        'local_path': self._find_photo_file(photo_data.get('uri', ''), base_path)
                    }
                    photos.append(photo_info)
            
            return photos
            
        except Exception as e:
            self.logger.error(f"Error parsing photos from {json_file}: {str(e)}")
            return []
    
    def _parse_posts(self, json_file: Path) -> List[Dict[str, Any]]:
        """Parse posts/timeline data from JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            posts = []
            
            if 'status_updates' in data:
                for post_data in data['status_updates']:
                    post_info = {
                        'timestamp': self._parse_timestamp(post_data.get('timestamp')),
                        'data': post_data.get('data', []),
                        'title': post_data.get('title', ''),
                        'attachments': post_data.get('attachments', [])
                    }
                    posts.append(post_info)
            
            return posts
            
        except Exception as e:
            self.logger.error(f"Error parsing posts from {json_file}: {str(e)}")
            return []
    
    def _parse_friends(self, json_file: Path) -> List[Dict[str, Any]]:
        """Parse friends list from JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            friends = []
            
            if 'friends_v2' in data:
                for friend_data in data['friends_v2']:
                    friend_info = {
                        'name': friend_data.get('name', ''),
                        'timestamp': self._parse_timestamp(friend_data.get('timestamp'))
                    }
                    friends.append(friend_info)
            
            return friends
            
        except Exception as e:
            self.logger.error(f"Error parsing friends from {json_file}: {str(e)}")
            return []
    
    def _parse_interests(self, json_file: Path) -> List[Dict[str, Any]]:
        """Parse interests/likes from JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            interests = []
            
            # Parse liked pages
            if 'page_likes_v2' in data:
                for like_data in data['page_likes_v2']:
                    interest_info = {
                        'name': like_data.get('name', ''),
                        'category': like_data.get('category', ''),
                        'timestamp': self._parse_timestamp(like_data.get('timestamp'))
                    }
                    interests.append(interest_info)
            
            return interests
            
        except Exception as e:
            self.logger.error(f"Error parsing interests from {json_file}: {str(e)}")
            return []
    
    def _parse_work_education(self, json_file: Path) -> List[Dict[str, Any]]:
        """Parse work and education information"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            work_education = []
            
            # Parse work experience
            if 'work_v2' in data:
                for work_data in data['work_v2']:
                    work_info = {
                        'type': 'work',
                        'employer': work_data.get('employer', ''),
                        'position': work_data.get('position', ''),
                        'location': work_data.get('location', ''),
                        'start_timestamp': self._parse_timestamp(work_data.get('start_timestamp')),
                        'end_timestamp': self._parse_timestamp(work_data.get('end_timestamp'))
                    }
                    work_education.append(work_info)
            
            # Parse education
            if 'education_v2' in data:
                for edu_data in data['education_v2']:
                    edu_info = {
                        'type': 'education',
                        'school': edu_data.get('school', ''),
                        'degree': edu_data.get('degree', ''),
                        'field_of_study': edu_data.get('field_of_study', ''),
                        'start_timestamp': self._parse_timestamp(edu_data.get('start_timestamp')),
                        'end_timestamp': self._parse_timestamp(edu_data.get('end_timestamp'))
                    }
                    work_education.append(edu_info)
            
            return work_education
            
        except Exception as e:
            self.logger.error(f"Error parsing work/education from {json_file}: {str(e)}")
            return []
    
    def _parse_birthday(self, birthday_data: Optional[Dict]) -> Optional[str]:
        """Parse birthday information"""
        if not birthday_data:
            return None
        
        try:
            if 'year' in birthday_data and 'month' in birthday_data and 'day' in birthday_data:
                return f"{birthday_data['year']}-{birthday_data['month']:02d}-{birthday_data['day']:02d}"
        except:
            pass
        
        return None
    
    def _parse_location(self, location_data: Optional[Dict]) -> Optional[str]:
        """Parse location information"""
        if not location_data:
            return None
        
        return location_data.get('name', '')
    
    def _parse_timestamp(self, timestamp: Optional[int]) -> Optional[str]:
        """Parse Unix timestamp to readable format"""
        if not timestamp:
            return None
        
        try:
            return datetime.fromtimestamp(timestamp).isoformat()
        except:
            return None
    
    def _parse_comments(self, comments_data: List[Dict]) -> List[Dict[str, Any]]:
        """Parse comments data"""
        comments = []
        for comment in comments_data:
            comments.append({
                'author': comment.get('author', ''),
                'comment': comment.get('comment', ''),
                'timestamp': self._parse_timestamp(comment.get('timestamp'))
            })
        return comments
    
    def _parse_reactions(self, reactions_data: List[Dict]) -> List[Dict[str, Any]]:
        """Parse reactions data"""
        reactions = []
        for reaction in reactions_data:
            reactions.append({
                'reaction': reaction.get('reaction', ''),
                'actor': reaction.get('actor', '')
            })
        return reactions
    
    def _find_photo_file(self, uri: str, base_path: Path) -> Optional[str]:
        """Find the actual photo file in the extracted directory"""
        if not uri:
            return None
        
        # Facebook URIs are usually relative paths
        photo_path = base_path / uri
        if photo_path.exists():
            return str(photo_path)
        
        # Try alternative path structures
        # Remove leading path components that might not match
        if '/' in uri:
            # Try with just the filename
            filename = Path(uri).name
            for photo_file in base_path.rglob(filename):
                return str(photo_file)
            
            # Try with the last few path components
            path_parts = Path(uri).parts
            if len(path_parts) > 1:
                # Try last 2 components
                relative_path = Path(*path_parts[-2:])
                photo_path = base_path / relative_path
                if photo_path.exists():
                    return str(photo_path)
                
                # Try last 3 components
                if len(path_parts) > 2:
                    relative_path = Path(*path_parts[-3:])
                    photo_path = base_path / relative_path
                    if photo_path.exists():
                        return str(photo_path)
        
        return None
    
    def _process_json_data(self, data: Dict[str, Any], base_path: Path) -> Dict[str, Any]:
        """Process raw JSON data and extract relevant information"""
        # This method handles single JSON files that might contain mixed data
        processed_data = {
            'profile_info': {},
            'photos': [],
            'posts': [],
            'about_info': {},
            'friends': [],
            'interests': [],
            'work_education': []
        }
        
        # Try to identify and parse different data types
        for key, value in data.items():
            if 'profile' in key.lower():
                processed_data['profile_info'].update(self._extract_profile_from_data(value))
            elif 'photo' in key.lower():
                processed_data['photos'].extend(self._extract_photos_from_data(value, base_path))
            elif 'post' in key.lower() or 'status' in key.lower():
                processed_data['posts'].extend(self._extract_posts_from_data(value))
            elif 'friend' in key.lower():
                processed_data['friends'].extend(self._extract_friends_from_data(value))
            elif 'like' in key.lower() or 'page' in key.lower():
                processed_data['interests'].extend(self._extract_interests_from_data(value))
            elif 'work' in key.lower() or 'education' in key.lower():
                processed_data['work_education'].extend(self._extract_work_education_from_data(value))
        
        return processed_data
    
    def _extract_profile_from_data(self, data: Any) -> Dict[str, Any]:
        """Extract profile information from various data structures"""
        if isinstance(data, dict):
            return {
                'name': data.get('name', ''),
                'email': data.get('email', ''),
                'birthday': data.get('birthday', ''),
                'location': data.get('location', ''),
                'bio': data.get('bio', ''),
                'website': data.get('website', '')
            }
        return {}
    
    def _extract_photos_from_data(self, data: Any, base_path: Path) -> List[Dict[str, Any]]:
        """Extract photos from various data structures"""
        photos = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    photos.append({
                        'title': item.get('title', ''),
                        'uri': item.get('uri', ''),
                        'timestamp': item.get('timestamp', ''),
                        'local_path': self._find_photo_file(item.get('uri', ''), base_path)
                    })
        return photos
    
    def _extract_posts_from_data(self, data: Any) -> List[Dict[str, Any]]:
        """Extract posts from various data structures"""
        posts = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    posts.append({
                        'content': item.get('data', []),
                        'timestamp': item.get('timestamp', ''),
                        'attachments': item.get('attachments', [])
                    })
        return posts
    
    def _extract_friends_from_data(self, data: Any) -> List[Dict[str, Any]]:
        """Extract friends from various data structures"""
        friends = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    friends.append({
                        'name': item.get('name', ''),
                        'timestamp': item.get('timestamp', '')
                    })
        return friends
    
    def _extract_interests_from_data(self, data: Any) -> List[Dict[str, Any]]:
        """Extract interests from various data structures"""
        interests = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    interests.append({
                        'name': item.get('name', ''),
                        'category': item.get('category', ''),
                        'timestamp': item.get('timestamp', '')
                    })
        return interests
    
    def _extract_work_education_from_data(self, data: Any) -> List[Dict[str, Any]]:
        """Extract work/education from various data structures"""
        work_education = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    work_education.append({
                        'type': 'work' if 'employer' in item else 'education',
                        'name': item.get('employer', item.get('school', '')),
                        'position': item.get('position', item.get('degree', '')),
                        'location': item.get('location', ''),
                        'start_date': item.get('start_timestamp', ''),
                        'end_date': item.get('end_timestamp', '')
                    })
        return work_education
    
    def _parse_new_photos(self, json_file: Path, base_path: Path) -> List[Dict[str, Any]]:
        """Parse photos from the new Facebook export format"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            photos = []
            
            # Handle uncategorized photos
            if 'other_photos_v2' in data:
                for photo_data in data['other_photos_v2']:
                    photo_info = {
                        'title': 'Uncategorized Photo',
                        'description': '',
                        'creation_timestamp': self._parse_timestamp(photo_data.get('creation_timestamp')),
                        'uri': photo_data.get('uri', ''),
                        'media_metadata': photo_data.get('media_metadata', {}),
                        'comments': [],
                        'reactions': [],
                        'local_path': self._find_photo_file(photo_data.get('uri', ''), base_path)
                    }
                    photos.append(photo_info)
            
            # Handle album photos
            if 'photos' in data:
                album_name = data.get('name', 'Unknown Album')
                for photo_data in data['photos']:
                    photo_info = {
                        'title': photo_data.get('title', album_name),
                        'description': photo_data.get('description', ''),
                        'creation_timestamp': self._parse_timestamp(photo_data.get('creation_timestamp')),
                        'uri': photo_data.get('uri', ''),
                        'media_metadata': photo_data.get('media_metadata', {}),
                        'comments': [],
                        'reactions': [],
                        'local_path': self._find_photo_file(photo_data.get('uri', ''), base_path)
                    }
                    photos.append(photo_info)
            
            return photos
            
        except Exception as e:
            self.logger.error(f"Error parsing new photos from {json_file}: {str(e)}")
            return []
    
    def _parse_new_posts(self, json_file: Path) -> List[Dict[str, Any]]:
        """Parse posts from the new Facebook export format"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            posts = []
            
            if isinstance(data, list):
                for post_data in data:
                    if isinstance(post_data, dict):
                        post_info = {
                            'timestamp': self._parse_timestamp(post_data.get('timestamp')),
                            'title': post_data.get('title', ''),
                            'data': post_data.get('data', []),
                            'attachments': post_data.get('attachments', [])
                        }
                        posts.append(post_info)
            
            return posts
            
        except Exception as e:
            self.logger.error(f"Error parsing new posts from {json_file}: {str(e)}")
            return []
    
    def _parse_new_interests(self, json_file: Path) -> List[Dict[str, Any]]:
        """Parse interests from the new Facebook export format"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            interests = []
            
            # Parse liked pages
            if 'page_likes_v2' in data:
                for like_data in data['page_likes_v2']:
                    name = like_data.get('name', '')
                    # Fix common encoding issues
                    name = name.replace('Ã½', 'ý').replace('Ã¡', 'á').replace('Ã©', 'é').replace('Ã­', 'í').replace('Ã³', 'ó').replace('Ãº', 'ú')
                    
                    interest_info = {
                        'name': name,
                        'category': 'Page',  # Default category for new format
                        'timestamp': self._parse_timestamp(like_data.get('timestamp')),
                        'url': like_data.get('url', '')
                    }
                    interests.append(interest_info)
            
            return interests
            
        except Exception as e:
            self.logger.error(f"Error parsing new interests from {json_file}: {str(e)}")
            return []
    
    def _parse_comments_for_profile(self, json_file: Path) -> List[Dict[str, Any]]:
        """Parse comments to extract personality insights"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # This could be used for personality analysis in the future
            # For now, just return empty list
            return []
            
        except Exception as e:
            self.logger.error(f"Error parsing comments from {json_file}: {str(e)}")
            return []
    
    def extract_dating_profile_data(self, facebook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and format data suitable for dating profile generation
        
        Args:
            facebook_data: Parsed Facebook data
            
        Returns:
            Dictionary formatted for dating profile use
        """
        profile_info = facebook_data.get('profile_info', {})
        work_education = facebook_data.get('work_education', [])
        interests = facebook_data.get('interests', [])
        photos = facebook_data.get('photos', [])
        posts = facebook_data.get('posts', [])
        
        # Try to extract name from posts if not in profile
        name = profile_info.get('name', '')
        if not name and posts:
            # Look for name in post titles
            for post in posts:
                title = post.get('title', '')
                if 'shared' in title or 'posted' in title:
                    # Extract name from "Name shared a link" or similar
                    parts = title.split(' ')
                    if len(parts) >= 2:
                        potential_name = ' '.join(parts[:2])  # Take first two words as name
                        if potential_name and not any(word in potential_name.lower() for word in ['shared', 'posted', 'updated']):
                            name = potential_name
                            break
        
        # Calculate age from birthday if available
        age = None
        if profile_info.get('birthday'):
            try:
                birth_date = datetime.fromisoformat(profile_info['birthday'].replace('Z', '+00:00'))
                age = (datetime.now() - birth_date).days // 365
            except:
                pass
        
        # Extract current job
        current_job = None
        for work in work_education:
            if work.get('type') == 'work' and not work.get('end_date'):
                current_job = f"{work.get('position', '')} at {work.get('name', '')}".strip()
                break
        
        # Extract education
        education = None
        for edu in work_education:
            if edu.get('type') == 'education':
                education = f"{edu.get('position', '')} from {edu.get('name', '')}".strip()
                break
        
        # Extract top interests
        top_interests = [interest.get('name', '') for interest in interests[:15] if interest.get('name')]
        
        # Filter photos with local paths (available for analysis)
        available_photos = [photo for photo in photos if photo.get('local_path') and Path(photo['local_path']).exists()]
        
        # Sort photos by creation timestamp (newest first)
        available_photos.sort(key=lambda x: x.get('creation_timestamp', ''), reverse=True)
        
        # Generate a basic bio from available data
        bio_parts = []
        if top_interests:
            bio_parts.append(f"Interested in {', '.join(top_interests[:5])}")
        
        # Extract location from photo metadata if available
        location = profile_info.get('location', '')
        if not location and available_photos:
            # Could potentially extract location from photo EXIF data in the future
            pass
        
        dating_profile_data = {
            'age': age,
            'name': name,
            'occupation': current_job or 'Not specified',
            'education': education or 'Not specified',
            'location': location or 'Not specified',
            'hometown': profile_info.get('hometown', ''),
            'bio': profile_info.get('bio', '') or '. '.join(bio_parts),
            'interests': ', '.join(top_interests),
            'relationship_status': profile_info.get('relationship_status', ''),
            'photos': available_photos,
            'total_photos_found': len(photos),
            'available_photos_count': len(available_photos),
            'posts_analyzed': len(posts),
            'interests_found': len(interests)
        }
        
        return dating_profile_data