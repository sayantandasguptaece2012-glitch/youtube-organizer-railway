"""
YouTube Authentication and Playlist Access Module

This module provides functionality to authenticate with YouTube accounts
and retrieve saved playlists using the YouTube Data API.
"""

import os
import json
import pickle
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class YouTubeAuthenticator:
    """Handles YouTube authentication using OAuth2."""
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.pickle"):
        """
        Initialize the YouTube authenticator.
        
        Args:
            credentials_file: Path to OAuth2 credentials file
            token_file: Path to store authentication token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.credentials = None
        self.service = None
        
        # YouTube Data API scope for full access to playlists (including private)
        self.scopes = ['https://www.googleapis.com/auth/youtube']
    
    def authenticate(self) -> bool:
        """
        Authenticate with YouTube using OAuth2.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Check if we have existing credentials
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # If credentials are invalid or missing, get new ones
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        raise FileNotFoundError(
                            f"Credentials file '{self.credentials_file}' not found. "
                            "Please download it from Google Cloud Console."
                        )
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.scopes
                    )
                    self.credentials = flow.run_local_server(port=0)
                
                # Save the credentials for next run
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            # Build YouTube service
            self.service = build('youtube', 'v3', credentials=self.credentials)
            return True
            
        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.service is not None


class YouTubePlaylistManager:
    """Manages YouTube playlist operations."""
    
    def __init__(self, authenticator: YouTubeAuthenticator):
        """
        Initialize playlist manager.
        
        Args:
            authenticator: Authenticated YouTubeAuthenticator instance
        """
        self.authenticator = authenticator
        self.service = authenticator.service
    
    def get_playlists(self, max_results: int = 50) -> List[Dict]:
        """
        Get all playlists from the authenticated user's account.
        
        Args:
            max_results: Maximum number of playlists to retrieve
            
        Returns:
            List of dictionaries containing playlist information
        """
        if not self.authenticator.is_authenticated():
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        try:
            playlists = []
            next_page_token = None
            
            while len(playlists) < max_results:
                request = self.service.playlists().list(
                    part='snippet,contentDetails',
                    mine=True,
                    maxResults=min(50, max_results - len(playlists)),
                    pageToken=next_page_token
                )
                
                response = request.execute()
                
                for item in response.get('items', []):
                    playlist_info = {
                        'id': item['id'],
                        'title': item['snippet']['title'],
                        'description': item['snippet'].get('description', ''),
                        'published_at': item['snippet']['publishedAt'],
                        'video_count': item['contentDetails']['itemCount'],
                        'thumbnail_url': item['snippet']['thumbnails'].get('high', {}).get('url', '')
                    }
                    playlists.append(playlist_info)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            
            return playlists
            
        except HttpError as e:
            print(f"HTTP Error retrieving playlists: {e}")
            return []
        except Exception as e:
            print(f"Error retrieving playlists: {e}")
            return []
    
    def get_playlist_items(self, playlist_id: str, max_results: int = 50) -> List[Dict]:
        """
        Get all videos in a specific playlist.
        
        Args:
            playlist_id: ID of the playlist
            max_results: Maximum number of videos to retrieve
            
        Returns:
            List of dictionaries containing video information
        """
        if not self.authenticator.is_authenticated():
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        try:
            videos = []
            next_page_token = None
            
            while len(videos) < max_results:
                request = self.service.playlistItems().list(
                    part='snippet,contentDetails',
                    playlistId=playlist_id,
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token
                )
                
                response = request.execute()
                
                for item in response.get('items', []):
                    video_info = {
                        'video_id': item['snippet']['resourceId']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet'].get('description', ''),
                        'published_at': item['snippet']['publishedAt'],
                        'position': item['snippet']['position'],
                        'thumbnail_url': item['snippet']['thumbnails'].get('high', {}).get('url', '')
                    }
                    videos.append(video_info)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            
            return videos
            
        except HttpError as e:
            print(f"HTTP Error retrieving playlist items: {e}")
            return []
        except Exception as e:
            print(f"Error retrieving playlist items: {e}")
            return []
    
    def get_channel_info(self) -> Dict:
        """
        Get information about the authenticated user's channel.
        
        Returns:
            Dictionary containing channel information
        """
        if not self.authenticator.is_authenticated():
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        try:
            request = self.service.channels().list(
                part='snippet,statistics',
                mine=True
            )
            
            response = request.execute()
            
            if response.get('items'):
                channel = response['items'][0]
                return {
                    'id': channel['id'],
                    'title': channel['snippet']['title'],
                    'description': channel['snippet'].get('description', ''),
                    'subscriber_count': channel['statistics'].get('subscriberCount', 0),
                    'video_count': channel['statistics'].get('videoCount', 0),
                    'view_count': channel['statistics'].get('viewCount', 0),
                    'thumbnail_url': channel['snippet']['thumbnails'].get('high', {}).get('url', '')
                }
            
            return {}
            
        except HttpError as e:
            print(f"HTTP Error retrieving channel info: {e}")
            return {}
        except Exception as e:
            print(f"Error retrieving channel info: {e}")
            return {}


class YouTubeManager:
    """Main class that combines authentication and playlist management."""
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.pickle"):
        """
        Initialize YouTube Manager.
        
        Args:
            credentials_file: Path to OAuth2 credentials file
            token_file: Path to store authentication token
        """
        self.authenticator = YouTubeAuthenticator(credentials_file, token_file)
        self.playlist_manager = None
    
    def login(self) -> bool:
        """
        Login to YouTube account.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        if self.authenticator.authenticate():
            self.playlist_manager = YouTubePlaylistManager(self.authenticator)
            return True
        return False
    
    def get_saved_playlists(self, max_results: int = 50) -> List[Dict]:
        """
        Get saved playlists from the account.
        
        Args:
            max_results: Maximum number of playlists to retrieve
            
        Returns:
            List of dictionaries containing playlist information
        """
        if not self.playlist_manager:
            raise ValueError("Not logged in. Call login() first.")
        
        return self.playlist_manager.get_playlists(max_results)
    
    def get_playlist_videos(self, playlist_id: str, max_results: int = 50) -> List[Dict]:
        """
        Get videos from a specific playlist.
        
        Args:
            playlist_id: ID of the playlist
            max_results: Maximum number of videos to retrieve
            
        Returns:
            List of dictionaries containing video information
        """
        if not self.playlist_manager:
            raise ValueError("Not logged in. Call login() first.")
        
        return self.playlist_manager.get_playlist_items(playlist_id, max_results)
    
    def get_channel_info(self) -> Dict:
        """
        Get channel information.
        
        Returns:
            Dictionary containing channel information
        """
        if not self.playlist_manager:
            raise ValueError("Not logged in. Call login() first.")
        
        return self.playlist_manager.get_channel_info()


def main():
    """Example usage of the YouTube Manager."""
    # Initialize YouTube Manager
    youtube = YouTubeManager()
    
    # Login to YouTube
    if youtube.login():
        print("Successfully logged in to YouTube!")
        
        # Get channel information
        channel_info = youtube.get_channel_info()
        print(f"\nChannel: {channel_info.get('title', 'Unknown')}")
        print(f"Subscribers: {channel_info.get('subscriber_count', 0)}")
        
        # Get saved playlists
        playlists = youtube.get_saved_playlists()
        print(f"\nFound {len(playlists)} user-created playlists:")
        
        for playlist in playlists:
            print(f"- {playlist['title']} ({playlist['video_count']} videos)")
        
        # Also show system playlists (likes, uploads)
        print("\nSystem Playlists:")
        try:
            service = youtube.authenticator.service
            
            # Get channel details for system playlists
            channel_response = service.channels().list(
                part='contentDetails',
                mine=True
            ).execute()
            
            if channel_response.get('items'):
                related_playlists = channel_response['items'][0]['contentDetails']['relatedPlaylists']
                
                # Show likes playlist
                if related_playlists.get('likes'):
                    likes_response = service.playlists().list(
                        part='snippet,contentDetails',
                        id=related_playlists['likes']
                    ).execute()
                    
                    if likes_response.get('items'):
                        likes = likes_response['items'][0]
                        print(f"- Liked Videos ({likes['contentDetails']['itemCount']} videos)")
                        
                        # Show first 5 liked videos
                        liked_videos = youtube.get_playlist_videos(related_playlists['likes'], max_results=5)
                        print("  Recent liked videos:")
                        for video in liked_videos:
                            print(f"  • {video['title']}")
                
                # Show uploads playlist
                if related_playlists.get('uploads'):
                    uploads_response = service.playlists().list(
                        part='snippet,contentDetails',
                        id=related_playlists['uploads']
                    ).execute()
                    
                    if uploads_response.get('items'):
                        uploads = uploads_response['items'][0]
                        print(f"- Your Uploads ({uploads['contentDetails']['itemCount']} videos)")
                        
                        # Show first 5 uploaded videos
                        uploaded_videos = youtube.get_playlist_videos(related_playlists['uploads'], max_results=5)
                        print("  Recent uploads:")
                        for video in uploaded_videos:
                            print(f"  • {video['title']}")
                            
        except Exception as e:
            print(f"Error getting system playlists: {e}")
            
    else:
        print("Failed to login to YouTube.")


if __name__ == "__main__":
    main()
