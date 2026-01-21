# YouTube Organizer

A Python module for authenticating with YouTube accounts and accessing saved playlists using the YouTube Data API.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get Google Cloud Credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the YouTube Data API v3
   - Create OAuth 2.0 Client ID credentials
   - Download the JSON file and rename it to `credentials.json`

3. **Place credentials file:**
   - Put the `credentials.json` file in the same directory as the module

## Usage

### Basic Usage

```python
from youtube_auth import YouTubeManager

# Initialize YouTube Manager
youtube = YouTubeManager()

# Login to YouTube (opens browser for authentication)
if youtube.login():
    print("Successfully logged in!")
    
    # Get all saved playlists
    playlists = youtube.get_saved_playlists()
    print(f"Found {len(playlists)} playlists")
    
    for playlist in playlists:
        print(f"- {playlist['title']} ({playlist['video_count']} videos)")
        
        # Get videos from this playlist
        videos = youtube.get_playlist_videos(playlist['id'])
        print(f"  Videos: {len(videos)}")
```

### Advanced Usage

```python
from youtube_auth import YouTubeAuthenticator, YouTubePlaylistManager

# Using individual components
auth = YouTubeAuthenticator()
if auth.authenticate():
    playlist_manager = YouTubePlaylistManager(auth)
    
    # Get channel info
    channel = playlist_manager.get_channel_info()
    print(f"Channel: {channel['title']}")
    
    # Get playlists with pagination
    playlists = playlist_manager.get_playlists(max_results=100)
    
    # Get videos from specific playlist
    if playlists:
        videos = playlist_manager.get_playlist_items(
            playlists[0]['id'], 
            max_results=25
        )
```

## API Reference

### YouTubeManager

Main class that combines authentication and playlist management.

- `login()` - Authenticate with YouTube
- `get_saved_playlists(max_results=50)` - Get user's playlists
- `get_playlist_videos(playlist_id, max_results=50)` - Get videos from playlist
- `get_channel_info()` - Get channel information

### Data Structures

**Playlist info:**
```python
{
    'id': 'playlist_id',
    'title': 'Playlist Title',
    'description': 'Description',
    'published_at': '2023-01-01T00:00:00Z',
    'video_count': 10,
    'thumbnail_url': 'https://...'
}
```

**Video info:**
```python
{
    'video_id': 'video_id',
    'title': 'Video Title',
    'description': 'Description',
    'published_at': '2023-01-01T00:00:00Z',
    'position': 0,
    'thumbnail_url': 'https://...'
}
```

## Notes

- The module uses OAuth2 for secure authentication
- Tokens are cached locally in `token.pickle`
- First-time login will open a browser window
- Only read-only access is requested (no modification permissions)
- API quotas apply: 10,000 units per day
