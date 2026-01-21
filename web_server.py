#!/usr/bin/env python3

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from youtube_auth import YouTubeManager
from playlist_categorizer import PlaylistCategorizer

app = Flask(__name__, static_folder='static')
CORS(app)

# Global YouTube manager instance
youtube_manager = None
categorizer = PlaylistCategorizer()

@app.route('/')
def index():
    """Serve the main HTML page."""
    return app.send_static_file('index.html')

@app.route('/api/playlists', methods=['GET'])
def get_playlists():
    """Get all playlists from the authenticated YouTube account."""
    global youtube_manager
    
    try:
        if not youtube_manager:
            youtube_manager = YouTubeManager()
            if not youtube_manager.login():
                return jsonify({'error': 'Failed to authenticate with YouTube'}), 500
        
        # Get channel info
        channel_info = youtube_manager.get_channel_info()
        
        # Get user playlists
        user_playlists = youtube_manager.get_saved_playlists(max_results=50)
        
        # Categorize user playlists
        categorized_user_playlists = categorizer.categorize_playlists(user_playlists)
        
        # Get category summary
        category_summary = categorizer.get_category_summary(user_playlists)
        
        # Get system playlists (likes, uploads)
        system_playlists = {}
        try:
            service = youtube_manager.authenticator.service
            channel_response = service.channels().list(
                part='contentDetails',
                mine=True
            ).execute()
            
            if channel_response.get('items'):
                related_playlists = channel_response['items'][0]['contentDetails']['relatedPlaylists']
                
                # Get likes playlist
                if related_playlists.get('likes'):
                    likes_response = service.playlists().list(
                        part='snippet,contentDetails',
                        id=related_playlists['likes']
                    ).execute()
                    
                    if likes_response.get('items'):
                        likes = likes_response['items'][0]
                        system_playlists['likes'] = {
                            'id': likes['id'],
                            'title': likes['snippet']['title'],
                            'description': likes['snippet'].get('description', ''),
                            'published_at': likes['snippet']['publishedAt'],
                            'video_count': likes['contentDetails']['itemCount'],
                            'thumbnail_url': likes['snippet']['thumbnails'].get('high', {}).get('url', '')
                        }
                
                # Get uploads playlist
                if related_playlists.get('uploads'):
                    uploads_response = service.playlists().list(
                        part='snippet,contentDetails',
                        id=related_playlists['uploads']
                    ).execute()
                    
                    if uploads_response.get('items'):
                        uploads = uploads_response['items'][0]
                        system_playlists['uploads'] = {
                            'id': uploads['id'],
                            'title': uploads['snippet']['title'],
                            'description': uploads['snippet'].get('description', ''),
                            'published_at': uploads['snippet']['publishedAt'],
                            'video_count': uploads['contentDetails']['itemCount'],
                            'thumbnail_url': uploads['snippet']['thumbnails'].get('high', {}).get('url', '')
                        }
                        
        except Exception as e:
            print(f"Error getting system playlists: {e}")
        
        return jsonify({
            'channel': channel_info,
            'user_playlists': categorized_user_playlists,
            'system_playlists': system_playlists,
            'category_summary': category_summary
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/playlist/<playlist_id>', methods=['GET'])
def get_playlist_videos(playlist_id):
    """Get videos from a specific playlist."""
    global youtube_manager
    
    try:
        if not youtube_manager:
            return jsonify({'error': 'Not authenticated'}), 401
        
        playlist_type = request.args.get('type', 'user')
        max_results = int(request.args.get('max_results', 25))
        
        # Get videos from playlist
        videos = youtube_manager.get_playlist_videos(playlist_id, max_results)
        
        return jsonify(videos)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh', methods=['POST'])
def refresh_authentication():
    """Force re-authentication with YouTube."""
    global youtube_manager
    
    try:
        # Delete cached token
        if os.path.exists('token.pickle'):
            os.remove('token.pickle')
        
        # Reset manager
        youtube_manager = None
        
        # Re-authenticate
        youtube_manager = YouTubeManager()
        if youtube_manager.login():
            return jsonify({'success': True, 'message': 'Successfully re-authenticated'})
        else:
            return jsonify({'error': 'Failed to authenticate'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/playlist/<playlist_id>/category', methods=['POST'])
def update_playlist_category(playlist_id):
    """Update the category of a playlist."""
    global youtube_manager
    
    try:
        if not youtube_manager:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        new_category = data.get('category')
        
        if not new_category:
            return jsonify({'error': 'Category is required'}), 400
        
        # Find the playlist in the cached data
        # Note: In a real implementation, you'd want to persist this to a database
        # For now, we'll just update the in-memory categorizer
        
        # Re-categorize the playlist with manual override
        from playlist_categorizer import PlaylistCategory
        
        # Convert string to enum
        try:
            category_enum = PlaylistCategory(new_category)
        except ValueError:
            return jsonify({'error': f'Invalid category: {new_category}'}), 400
        
        # Update categorizer with custom rule for this playlist
        categorizer.add_custom_rule(
            keywords=[playlist_id],  # Use playlist ID as unique identifier
            category=category_enum,
            weight=10  # High priority for manual categorization
        )
        
        return jsonify({
            'success': True,
            'message': f'Playlist category updated to {new_category}',
            'playlist_id': playlist_id,
            'new_category': new_category
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'authenticated': youtube_manager is not None})

if __name__ == '__main__':
    print("Starting YouTube Playlist Web Server...")
    print("Open your browser and go to: http://localhost:8082")
    print("Make sure you have authenticated with YouTube first!")
    
    app.run(debug=True, host='0.0.0.0', port=8082)
