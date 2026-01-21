# YouTube Playlist Organizer

A web application that automatically categorizes YouTube playlists into meaningful categories like Food, Career, Investment, Education, and more.

## 🚀 Live Demo
[https://youtube-organizer-demo.herokuapp.com](https://youtube-organizer-demo.herokuapp.com)

## ✨ Features
- **Smart Categorization**: Automatically categorizes playlists based on titles and descriptions
- **Manual Category Editing**: Users can override automatic categorization
- **Category Filtering**: View playlists by specific categories
- **Video Browsing**: Browse videos within each playlist
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Data**: Fetches live data from YouTube API

## 📋 Categories
- 🍕 **Food** (recipes, cooking, ingredients)
- 💼 **Career** (professional development, skills)
- 💰 **Investment** (finance, stocks, trading)
- 📚 **Education** (learning, tutorials, courses)
- 🎬 **Entertainment** (movies, music, comedy)
- 💪 **Health & Fitness** (exercise, wellness, nutrition)
- 💻 **Technology** (programming, software, tech)
- ✈️ **Travel** (destinations, tourism)
- 🌟 **Lifestyle** (fashion, beauty, daily routines)
- 📦 **Other** (miscellaneous content)

## 🛠️ Setup Instructions

### For Users (Quick Start)
1. Visit the live demo: [https://youtube-organizer-demo.herokuapp.com](https://youtube-organizer-demo.herokuapp.com)
2. Click "Get Started" and follow the authentication steps
3. Your playlists will be automatically categorized!

### For Developers (Local Setup)
```bash
# Clone the repository
git clone https://github.com/yourusername/youtube-organizer.git
cd youtube-organizer

# Install dependencies
pip install -r requirements.txt

# Set up Google Cloud credentials
# 1. Go to https://console.cloud.google.com/
# 2. Create a new project
# 3. Enable YouTube Data API v3
# 4. Create OAuth 2.0 credentials
# 5. Download credentials.json to this directory

# Run the app
python app.py
```

## 🔧 Google Cloud Setup
Each user needs their own Google Cloud credentials:

1. **Create Project**: Go to [Google Cloud Console](https://console.cloud.google.com/)
2. **Enable API**: Enable YouTube Data API v3
3. **Create Credentials**: Create OAuth 2.0 Client ID
4. **Configure Redirect URI**: Add `http://localhost:5000` (or your deployed URL)
5. **Download**: Save as `credentials.json`

## 🚀 Deployment Options

### Heroku (Recommended)
```bash
# Install Heroku CLI
heroku login

# Create and deploy
heroku create your-app-name
git add .
git commit -m "Deploy YouTube Organizer"
git push heroku main
```

### PythonAnywhere
1. Sign up at [pythonanywhere.com](https://pythonanywhere.com)
2. Create a new Web app
3. Upload your files
4. Configure WSGI file

### Docker
```bash
docker build -t youtube-organizer .
docker run -p 5000:5000 youtube-organizer
```

## 📊 API Endpoints
- `GET /api/playlists` - Get all playlists with categories
- `GET /api/playlist/{id}` - Get videos from a playlist
- `POST /api/playlist/{id}/category` - Update playlist category
- `GET /api/health` - Health check

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License
MIT License - see [LICENSE](LICENSE) file for details

## 🆘 Support
- 📧 Email: support@youtube-organizer.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/youtube-organizer/issues)
- 📖 Documentation: [Wiki](https://github.com/yourusername/youtube-organizer/wiki)

## 🔒 Privacy & Security
- Your credentials are stored locally and never sent to our servers
- We only access your YouTube data with your explicit permission
- Read-only access - we cannot modify your playlists
- OAuth 2.0 secure authentication

---

**Made with ❤️ for YouTube enthusiasts**
