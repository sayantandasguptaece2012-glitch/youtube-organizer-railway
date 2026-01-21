#!/usr/bin/env python3
"""
Simple authentication script for YouTube Playlist Organizer
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

def authenticate():
    """Authenticate with YouTube and save credentials."""
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        print("Please upload credentials.json first.")
        return False
    
    try:
        # Create OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', 
            ['https://www.googleapis.com/auth/youtube']
        )
        
        # Run authentication flow (port=0 finds available port)
        print("🔐 Starting authentication...")
        print("A browser window will open for Google authentication...")
        
        creds = flow.run_local_server(port=0)
        
        # Save credentials
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        
        print("✅ Authentication successful!")
        print("🎉 You can now use the web app!")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

if __name__ == '__main__':
    authenticate()
