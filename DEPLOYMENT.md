# YouTube Playlist Organizer - Production Deployment

## Overview
A web application that automatically categorizes YouTube playlists into meaningful categories like Food, Career, Investment, Education, and more.

## Features
- **Smart Categorization**: Automatically categorizes playlists based on titles and descriptions
- **Manual Category Editing**: Users can override automatic categorization
- **Category Filtering**: View playlists by specific categories
- **Video Browsing**: Browse videos within each playlist
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Data**: Fetches live data from YouTube API

## Categories
- Food (recipes, cooking, ingredients)
- Career (professional development, skills)
- Investment (finance, stocks, trading)
- Education (learning, tutorials, courses)
- Entertainment (movies, music, comedy)
- Health & Fitness (exercise, wellness, nutrition)
- Technology (programming, software, tech)
- Travel (destinations, tourism)
- Lifestyle (fashion, beauty, daily routines)
- Other (miscellaneous content)

## Deployment Options

### 1. Heroku (Recommended for beginners)
```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set FLASK_DEBUG=False

# Deploy
git add .
git commit -m "Deploy YouTube Organizer"
git push heroku main
```

### 2. PythonAnywhere
1. Create a free account at pythonanywhere.com
2. Create a new Web app
3. Upload your files
4. Configure the WSGI file
5. Set environment variables

### 3. Vercel (Serverless)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### 4. Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

### 5. Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

## Environment Variables Required
- `SECRET_KEY`: Flask secret key for sessions
- `FLASK_DEBUG`: Set to False in production
- `PORT`: Port number (usually 5000)

## Google Cloud Setup for Users
Each user needs to:
1. Create a Google Cloud project
2. Enable YouTube Data API v3
3. Create OAuth 2.0 credentials
4. Add their redirect URI to the credentials
5. Download credentials.json

## Security Considerations
- Store credentials.json securely
- Use HTTPS in production
- Set appropriate CORS policies
- Validate all user inputs
- Rate limit API calls

## Scaling Considerations
- Add database for persistent category storage
- Implement caching for API responses
- Add user authentication system
- Use CDN for static assets
- Monitor YouTube API quotas

## Support
- Documentation: README.md
- Issues: GitHub Issues
- Email: support@example.com
