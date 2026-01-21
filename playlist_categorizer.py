"""
Playlist Categorization Module for YouTube Organizer

This module provides functionality to categorize YouTube playlists
into broader categories like Food, Career, Investment, etc.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class PlaylistCategory(Enum):
    """Predefined playlist categories."""
    FOOD = "Food"
    CAREER = "Career"
    INVESTMENT = "Investment"
    EDUCATION = "Education"
    ENTERTAINMENT = "Entertainment"
    HEALTH_FITNESS = "Health & Fitness"
    TECHNOLOGY = "Technology"
    TRAVEL = "Travel"
    LIFESTYLE = "Lifestyle"
    OTHER = "Other"

@dataclass
class CategoryRule:
    """Rule for categorizing playlists."""
    keywords: List[str]
    category: PlaylistCategory
    weight: int = 1  # Higher weight = higher priority

class PlaylistCategorizer:
    """Categorizes YouTube playlists based on content analysis."""
    
    def __init__(self):
        """Initialize the categorizer with predefined rules."""
        self.rules = self._initialize_rules()
        self.custom_rules = []
    
    def _initialize_rules(self) -> List[CategoryRule]:
        """Initialize default categorization rules."""
        return [
            # Food Category - Highest priority for food-related content
            CategoryRule(
                keywords=[
                    'pizza', 'recipe', 'recipes', 'cooking', 'food', 'bake', 'baked', 'brownies',
                    'cookies', 'bread', 'fruit', 'vegetable', 'veg', 'masala', 'falafel', 'hummus',
                    'spreads', 'carrot', 'quinoa', 'cauliflower', 'mushroom', 'tomato', 'pumpkin',
                    'laddu', 'chutney', 'amla', 'drumsticks', 'kofta', 'noodles', 'parwal',
                    'methi', 'soyabean', 'curry', 'kanji', 'poha', 'achar', 'sabji', 'pulao',
                    'chaat', 'snacks', 'millet', 'singhada', 'lotus', 'vermicelli', 'dry fruits',
                    'rice', 'sprouts', 'thecha', 'satvik', 'air fry', 'indian', 'chinese'
                ],
                category=PlaylistCategory.FOOD,
                weight=10
            ),
            
            # Career Category
            CategoryRule(
                keywords=[
                    'career', 'product management', 'professional', 'business', 'work', 'job',
                    'interview', 'resume', 'skills', 'development', 'leadership', 'management'
                ],
                category=PlaylistCategory.CAREER,
                weight=8
            ),
            
            # Investment Category
            CategoryRule(
                keywords=[
                    'investment', 'investing', 'stock', 'trading', 'finance', 'money', 'wealth',
                    'portfolio', 'mutual fund', 'crypto', 'bitcoin', 'market', 'shares'
                ],
                category=PlaylistCategory.INVESTMENT,
                weight=8
            ),
            
            # Health & Fitness Category
            CategoryRule(
                keywords=[
                    'exercise', 'workout', 'fitness', 'health', 'yoga', 'gym', 'training',
                    'weight loss', 'diet', 'nutrition', 'meditation', 'wellness'
                ],
                category=PlaylistCategory.HEALTH_FITNESS,
                weight=7
            ),
            
            # Education Category
            CategoryRule(
                keywords=[
                    'learn', 'tutorial', 'course', 'education', 'study', 'academic', 'lesson',
                    'programming', 'coding', 'math', 'science', 'history', 'language'
                ],
                category=PlaylistCategory.EDUCATION,
                weight=6
            ),
            
            # Technology Category
            CategoryRule(
                keywords=[
                    'tech', 'technology', 'software', 'app', 'programming', 'coding', 'computer',
                    'ai', 'machine learning', 'data science', 'web development', 'mobile'
                ],
                category=PlaylistCategory.TECHNOLOGY,
                weight=6
            ),
            
            # Travel Category
            CategoryRule(
                keywords=[
                    'travel', 'trip', 'vacation', 'tourism', 'destination', 'hotel', 'flight',
                    'adventure', 'explore', 'journey', 'wanderlust'
                ],
                category=PlaylistCategory.TRAVEL,
                weight=5
            ),
            
            # Entertainment Category
            CategoryRule(
                keywords=[
                    'movie', 'music', 'song', 'comedy', 'entertainment', 'gaming', 'show',
                    'series', 'drama', 'funny', 'dance', 'performance'
                ],
                category=PlaylistCategory.ENTERTAINMENT,
                weight=5
            ),
            
            # Lifestyle Category
            CategoryRule(
                keywords=[
                    'lifestyle', 'fashion', 'beauty', 'style', 'hairstyles', 'home', 'decor',
                    'personal', 'daily', 'routine', 'tips', 'life hacks'
                ],
                category=PlaylistCategory.LIFESTYLE,
                weight=4
            )
        ]
    
    def add_custom_rule(self, keywords: List[str], category: PlaylistCategory, weight: int = 5):
        """Add a custom categorization rule."""
        rule = CategoryRule(keywords=keywords, category=category, weight=weight)
        self.custom_rules.append(rule)
    
    def categorize_playlist(self, title: str, description: str = "") -> Tuple[PlaylistCategory, float]:
        """
        Categorize a playlist based on title and description.
        
        Args:
            title: Playlist title
            description: Playlist description
            
        Returns:
            Tuple of (category, confidence_score)
        """
        # Combine title and description for analysis
        text = f"{title} {description}".lower()
        
        category_scores = {}
        
        # Score against all rules (default + custom)
        all_rules = self.rules + self.custom_rules
        
        for rule in all_rules:
            score = 0
            for keyword in rule.keywords:
                # Count keyword occurrences
                keyword_count = len(re.findall(rf'\b{re.escape(keyword.lower())}\b', text))
                score += keyword_count * rule.weight
            
            if score > 0:
                if rule.category not in category_scores:
                    category_scores[rule.category] = 0
                category_scores[rule.category] += score
        
        # Determine the best category
        if not category_scores:
            return PlaylistCategory.OTHER, 0.0
        
        best_category = max(category_scores.items(), key=lambda x: x[1])
        confidence = min(best_category[1] / 20.0, 1.0)  # Normalize to 0-1 range
        
        return best_category[0], confidence
    
    def categorize_playlists(self, playlists: List[Dict]) -> List[Dict]:
        """
        Categorize a list of playlists.
        
        Args:
            playlists: List of playlist dictionaries
            
        Returns:
            List of playlists with category information added
        """
        categorized_playlists = []
        
        for playlist in playlists:
            title = playlist.get('title', '')
            description = playlist.get('description', '')
            
            category, confidence = self.categorize_playlist(title, description)
            
            # Add category info to playlist
            enhanced_playlist = playlist.copy()
            enhanced_playlist['category'] = category.value
            enhanced_playlist['category_confidence'] = confidence
            
            categorized_playlists.append(enhanced_playlist)
        
        return categorized_playlists
    
    def get_category_summary(self, playlists: List[Dict]) -> Dict[str, Dict]:
        """
        Get a summary of playlists by category.
        
        Args:
            playlists: List of categorized playlists
            
        Returns:
            Dictionary with category statistics
        """
        categorized = self.categorize_playlists(playlists)
        
        summary = {}
        for category in PlaylistCategory:
            category_playlists = [p for p in categorized if p['category'] == category.value]
            total_videos = sum(p.get('video_count', 0) for p in category_playlists)
            
            summary[category.value] = {
                'playlist_count': len(category_playlists),
                'total_videos': total_videos,
                'playlists': category_playlists
            }
        
        return summary
    
    def suggest_category_improvements(self, playlists: List[Dict]) -> List[Dict]:
        """
        Suggest playlists that might need manual categorization.
        
        Args:
            playlists: List of categorized playlists
            
        Returns:
            List of playlists with low confidence scores
        """
        categorized = self.categorize_playlists(playlists)
        
        # Find playlists with low confidence or in 'Other' category
        suggestions = [
            p for p in categorized 
            if p['category_confidence'] < 0.3 or p['category'] == PlaylistCategory.OTHER.value
        ]
        
        return suggestions


def main():
    """Example usage of the playlist categorizer."""
    
    # Example playlists (similar to your actual playlists)
    example_playlists = [
        {'title': 'Pizza', 'description': 'Delicious pizza recipes', 'video_count': 1},
        {'title': 'Career focus product management', 'description': 'PM career tips', 'video_count': 1},
        {'title': 'Brownies', 'description': 'Chocolate brownie recipes', 'video_count': 6},
        {'title': 'Hairstyles', 'description': 'Different hairstyle tutorials', 'video_count': 1},
        {'title': 'Exercise', 'description': 'Workout routines', 'video_count': 1},
        {'title': 'Investment basics', 'description': 'Stock market investing', 'video_count': 5},
        {'title': 'Random stuff', 'description': 'Various videos', 'video_count': 2},
    ]
    
    categorizer = PlaylistCategorizer()
    
    print("PLAYLIST CATEGORIZATION EXAMPLE")
    print("=" * 50)
    
    # Categorize individual playlists
    for playlist in example_playlists:
        category, confidence = categorizer.categorize_playlist(
            playlist['title'], playlist['description']
        )
        print(f"{playlist['title']}: {category.value} (confidence: {confidence:.2f})")
    
    print("\nCATEGORY SUMMARY")
    print("=" * 50)
    
    # Get category summary
    summary = categorizer.get_category_summary(example_playlists)
    for category, stats in summary.items():
        if stats['playlist_count'] > 0:
            print(f"{category}: {stats['playlist_count']} playlists, {stats['total_videos']} videos")
    
    print("\nSUGGESTIONS FOR MANUAL REVIEW")
    print("=" * 50)
    
    # Get suggestions
    suggestions = categorizer.suggest_category_improvements(example_playlists)
    for playlist in suggestions:
        print(f"{playlist['title']}: {playlist['category']} (confidence: {playlist['category_confidence']:.2f})")


if __name__ == "__main__":
    main()
