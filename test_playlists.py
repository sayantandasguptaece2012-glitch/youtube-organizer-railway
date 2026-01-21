#!/usr/bin/env python3

from youtube_auth import YouTubeManager

def test_playlists():
    youtube = YouTubeManager()
    
    if youtube.login():
        print("✓ Authentication successful")
        
        # Get channel info
        channel = youtube.get_channel_info()
        print(f"Channel: {channel.get('title', 'Unknown')}")
        print(f"Channel ID: {channel.get('id', 'Unknown')}")
        print(f"Video count: {channel.get('video_count', 0)}")
        
        # Try to get playlists with different parameters
        print("\nTrying to fetch playlists...")
        playlists = youtube.get_saved_playlists(max_results=25)
        print(f"Found {len(playlists)} playlists")
        
        if playlists:
            for i, playlist in enumerate(playlists, 1):
                print(f"{i}. {playlist['title']}")
                print(f"   ID: {playlist['id']}")
                print(f"   Videos: {playlist['video_count']}")
                print(f"   Privacy: {playlist.get('status', 'Unknown')}")
                print()
        else:
            print("No playlists found. This could mean:")
            print("- You have no playlists")
            print("- Playlists are private and require different scopes")
            print("- API quota exceeded")
            
            # Try a different approach - get liked videos
            print("\nTrying to get liked videos...")
            try:
                service = youtube.authenticator.service
                liked_response = service.channels().list(
                    part='contentDetails',
                    mine=True
                ).execute()
                
                if liked_response.get('items'):
                    channel_id = liked_response['items'][0]['id']
                    likes_playlist_id = liked_response['items'][0]['contentDetails']['relatedPlaylists']['likes']
                    
                    print(f"Found likes playlist ID: {likes_playlist_id}")
                    
                    # Get some liked videos
                    likes_response = service.playlistItems().list(
                        part='snippet',
                        playlistId=likes_playlist_id,
                        maxResults=5
                    ).execute()
                    
                    print(f"Found {len(likes_response.get('items', []))} liked videos:")
                    for item in likes_response.get('items', []):
                        print(f"- {item['snippet']['title']}")
                        
            except Exception as e:
                print(f"Error getting liked videos: {e}")
    
    else:
        print("✗ Authentication failed")

if __name__ == "__main__":
    test_playlists()
