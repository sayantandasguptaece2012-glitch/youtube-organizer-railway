#!/usr/bin/env python3
"""
Web-based authentication for YouTube Playlist Organizer
"""

import os
import json
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import pickle

def create_web_auth_flow(credentials_file='credentials.json'):
    """Create web OAuth flow without localhost redirect."""
    
    # Read credentials
    with open(credentials_file, 'r') as f:
        client_config = json.load(f)
    
    # Create flow for web application
    flow = Flow.from_client_config(
        client_config,
        scopes=['https://www.googleapis.com/auth/youtube'],
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # This uses out-of-band flow
    )
    
    # Generate auth URL
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    return auth_url, flow, state

def authenticate_with_code(auth_code, credentials_file='credentials.json'):
    """Exchange authorization code for credentials."""
    
    # Read credentials
    with open(credentials_file, 'r') as f:
        client_config = json.load(f)
    
    # Create flow
    flow = Flow.from_client_config(
        client_config,
        scopes=['https://www.googleapis.com/auth/youtube'],
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )
    
    # Exchange code for credentials
    flow.fetch_token(code=auth_code)
    
    return flow.credentials

def main():
    """Main authentication process."""
    
    print("🔐 YouTube Playlist Organizer Authentication")
    print("=" * 50)
    
    # Check credentials file
    if not os.path.exists('credentials_native.json'):
        print("❌ credentials_native.json not found!")
        print("Please create a Desktop app OAuth client and download credentials_native.json")
        return False
    
    try:
        # Create auth flow
        auth_url, flow, state = create_web_auth_flow('credentials_native.json')
        
        print("📋 Step 1: Visit this URL to authorize:")
        print(f"\n{auth_url}\n")
        
        print("📋 Step 2: Copy the authorization code from the browser")
        print("   (It will be shown after you click 'Allow')")
        
        # Get authorization code from user
        auth_code = input("\n📋 Step 3: Paste the authorization code here: ").strip()
        
        if not auth_code:
            print("❌ No authorization code provided!")
            return False
        
        # Exchange code for credentials
        print("🔄 Exchanging code for credentials...")
        creds = authenticate_with_code(auth_code, 'credentials_native.json')
        
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
    main()
