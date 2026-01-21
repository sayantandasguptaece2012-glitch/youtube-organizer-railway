"""
Simple YouTube authentication for web deployment
"""

import os
import json
import pickle
try:
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
except ImportError:
    # Fallback for older versions
    from google_auth_oauthlib.flow import InstalledAppFlow as Flow
    from googleapiclient.discovery import build

def get_authenticated_service(credentials_path='credentials.json', token_path='token.pickle'):
    """
    Get authenticated YouTube service using existing tokens or new authentication.
    """
    scopes = ['https://www.googleapis.com/auth/youtube']
    
    creds = None
    # Check if we have existing credentials
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # If credentials are invalid or missing, return None (web app can't authenticate)
    if not creds or not creds.valid:
        return None
    
    # Build service
    try:
        service = build('youtube', 'v3', credentials=creds)
        return service
    except Exception:
        return None

def is_authenticated(token_path='token.pickle'):
    """Check if user is authenticated."""
    if not os.path.exists(token_path):
        return False
    
    try:
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
            return creds.valid
    except:
        return False
