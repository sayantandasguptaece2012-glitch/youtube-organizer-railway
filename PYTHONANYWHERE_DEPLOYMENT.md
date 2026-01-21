# PythonAnywhere Deployment Guide for YouTube Organizer

## 🚀 Step-by-Step Deployment

### 1. Create PythonAnywhere Account
1. Go to [pythonanywhere.com](https://pythonanywhere.com)
2. Sign up for a **Free** account (or choose a paid plan for more features)
3. Verify your email address

### 2. Create a New Web App
1. Go to the **Web** tab in your PythonAnywhere dashboard
2. Click **"Add a new web app"**
3. Choose **Flask** as the web framework
4. Select **Python 3.9** (or latest available)
5. Leave the path as `/home/yourusername/youtube-organizer`
6. Click **Next**

### 3. Upload Your Files
1. Go to the **Files** tab
2. Create a new directory called `youtube-organizer`
3. Upload these files to the directory:
   - `app.py`
   - `youtube_auth.py`
   - `playlist_categorizer.py`
   - `requirements.txt`
   - `static/` folder (with index.html inside)

### 4. Install Dependencies
1. Go to the **Consoles** tab
2. Create a **Bash** console
3. Navigate to your project directory:
   ```bash
   cd youtube-organizer
   ```
4. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

### 5. Configure the Web App
1. Go back to the **Web** tab
2. Click on your web app name
3. Edit the **WSGI configuration file**
4. Replace the contents with:

```python
import sys
from app import app as application

# Add your project directory to the Python path
project_home = '/home/yourusername/youtube-organizer'
if project_home not in sys.path:
    sys.path.insert(0, project_home)
```

5. **Important**: Replace `yourusername` with your actual PythonAnywhere username

### 6. Set Environment Variables
1. In the **Web** tab, scroll down to **"Environment variables"**
2. Add these variables:
   - `SECRET_KEY`: `your-secret-key-here` (generate a random string)
   - `FLASK_DEBUG`: `False`

### 7. Configure Domain
1. In the **Web** tab, you'll see your domain
2. It will be something like: `yourusername.pythonanywhere.com`
3. This is your public URL!

### 8. Test Your App
1. Click the **"Restart"** button in the Web tab
2. Wait for the restart to complete
3. Visit your domain URL
4. Your YouTube Organizer should be live!

## 🔧 Important Notes for PythonAnywhere

### Free Account Limitations
- **Traffic**: 100,000 hits/month
- **CPU**: Limited CPU time
- **Storage**: 512MB
- **One web app** at a time

### Google Cloud Setup for Users
Since each user needs their own credentials:
1. Create a **setup guide** page in your app
2. Explain how users can get their own `credentials.json`
3. Provide a template credentials file for reference

### Static Files
PythonAnywhere serves static files differently:
1. In the **Web** tab, configure static file mappings:
   - URL: `/static/`
   - Directory: `/home/yourusername/youtube-organizer/static/`

### Troubleshooting
**Common Issues:**
- **Import errors**: Make sure all dependencies are installed
- **Permission errors**: Check file permissions in the Files tab
- **Port conflicts**: PythonAnywhere handles this automatically
- **Credentials issues**: Users need their own Google Cloud setup

## 📱 User Instructions Template

Add this to your app's homepage:

```
👋 Welcome to YouTube Playlist Organizer!

🔧 Setup Required:
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials
5. Add this redirect URI: https://yourusername.pythonanywhere.com
6. Download credentials.json
7. Upload credentials.json to this app

🚀 Once setup is complete, your playlists will be automatically categorized!
```

## 🎯 Next Steps After Deployment

1. **Test thoroughly** with different YouTube accounts
2. **Monitor usage** in the PythonAnywhere dashboard
3. **Upgrade plan** if you need more resources
4. **Add analytics** to track user engagement
5. **Share your URL** with others!

## 🆘 Support

If you run into issues:
1. Check the **error logs** in the Web tab
2. Make sure all files are uploaded correctly
3. Verify environment variables are set
4. Test locally first to ensure everything works

---

**Your YouTube Organizer will be live at:**
`https://yourusername.pythonanywhere.com`
