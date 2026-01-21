#!/usr/bin/env python3

from youtube_auth import YouTubeManager

def comprehensive_playlist_test():
    youtube = YouTubeManager()
    
    if youtube.login():
        print("✓ Authentication successful")
        
        service = youtube.authenticator.service
        
        # Get channel info first
        channel_response = service.channels().list(
            part='snippet,contentDetails',
            mine=True
        ).execute()
        
        if not channel_response.get('items'):
            print("No channel found!")
            return
            
        channel = channel_response['items'][0]
        channel_id = channel['id']
        print(f"Channel ID: {channel_id}")
        print(f"Channel Title: {channel['snippet']['title']}")
        
        # Get all possible playlist IDs from contentDetails
        content_details = channel['contentDetails']
        related_playlists = content_details.get('relatedPlaylists', {})
        
        print(f"\nRelated Playlists:")
        for playlist_type, playlist_id in related_playlists.items():
            print(f"- {playlist_type}: {playlist_id}")
            
            if playlist_id:  # Only try if ID exists
                try:
                    playlist_response = service.playlists().list(
                        part='snippet,contentDetails',
                        id=playlist_id
                    ).execute()
                    
                    if playlist_response.get('items'):
                        playlist = playlist_response['items'][0]
                        print(f"  Title: {playlist['snippet']['title']}")
                        print(f"  Video Count: {playlist['contentDetails']['itemCount']}")
                        
                        # Get first few videos
                        items_response = service.playlistItems().list(
                            part='snippet',
                            playlistId=playlist_id,
                            maxResults=3
                        ).execute()
                        
                        print(f"  Recent videos:")
                        for item in items_response.get('items', []):
                            print(f"    - {item['snippet']['title']}")
                    else:
                        print(f"  No details found for playlist {playlist_id}")
                        
                except Exception as e:
                    print(f"  Error accessing playlist {playlist_id}: {e}")
                print()
        
        # Now try to get all user-created playlists
        print("Getting all user-created playlists...")
        try:
            playlists_response = service.playlists().list(
                part='snippet,contentDetails,status',
                mine=True,
                maxResults=50
            ).execute()
            
            user_playlists = playlists_response.get('items', [])
            print(f"Found {len(user_playlists)} user-created playlists:")
            
            for i, playlist in enumerate(user_playlists, 1):
                status = playlist.get('status', {})
                privacy_status = status.get('privacyStatus', 'unknown')
                
                print(f"{i}. {playlist['snippet']['title']}")
                print(f"   ID: {playlist['id']}")
                print(f"   Videos: {playlist['contentDetails']['itemCount']}")
                print(f"   Privacy: {privacy_status}")
                print(f"   Description: {playlist['snippet'].get('description', 'No description')[:100]}...")
                print()
                
        except Exception as e:
            print(f"Error getting user playlists: {e}")
    
    else:
        print("✗ Authentication failed")

if __name__ == "__main__":
    comprehensive_playlist_test()
