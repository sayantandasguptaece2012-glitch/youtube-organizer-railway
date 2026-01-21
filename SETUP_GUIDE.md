# YouTube Playlist Organizer - PythonAnywhere Setup

## 🚀 Quick Start Guide

### Step 1: Create Account
1. Go to [pythonanywhere.com](https://pythonanywhere.com)
2. Sign up for FREE account
3. Verify email

### Step 2: Create Web App
1. **Web** tab → **Add a new web app**
2. Choose **Flask** framework
3. Select **Python 3.9**
4. Path: `/home/yourusername/youtube-organizer`

### Step 3: Upload Files
Upload these files to your directory:
- ✅ `app.py`
- ✅ `youtube_auth.py` 
- ✅ `playlist_categorizer.py`
- ✅ `requirements.txt`
- ✅ `wsgi.py`
- ✅ `static/` folder (with `index.html`)

### Step 4: Install Dependencies
In Bash console:
```bash
cd youtube-organizer
pip install -r requirements.txt
```

### Step 5: Configure WSGI
Replace WSGI file contents with `wsgi.py` contents
**Important**: Change `yourusername` to your actual username!

### Step 6: Set Environment Variables
In Web tab → Environment variables:
- `SECRET_KEY`: `your-secret-key-here`
- `FLASK_DEBUG`: `False`

### Step 7: Configure Static Files
In Web tab → Static files:
- URL: `/static/`
- Directory: `/home/yourusername/youtube-organizer/static/`

### Step 8: Restart & Test
1. Click **Restart** button
2. Visit: `https://yourusername.pythonanywhere.com`
3. 🎉 Your app is live!

## 🔧 User Setup Instructions

Each user needs their own Google Cloud credentials:

1. **Google Cloud Console**: https://console.cloud.google.com/
2. **Create Project** → Enable YouTube Data API v3
3. **Create OAuth 2.0 Client ID**
4. **Add Redirect URI**: `https://yourusername.pythonanywhere.com`
5. **Download credentials.json**
6. **Upload to the app**

## 📱 Your Live URL
`https://yourusername.pythonanywhere.com`

## 🆘 Troubleshooting
- Check error logs in Web tab
- Verify all files uploaded
- Test locally first
- Check environment variables

---

**Ready to share your YouTube Organizer with the world! 🌍**
