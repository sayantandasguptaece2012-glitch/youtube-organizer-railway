#!/bin/bash

# YouTube Organizer Deployment Script for PythonAnywhere

echo "🚀 Deploying YouTube Organizer to PythonAnywhere..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Step 1: Uploading files...${NC}"

# Upload main app file
echo -e "${GREEN}✓ Uploading app.py${NC}"
scp /Users/sayantandasgupta/Desktop/Youtube\ Organizer/app.py sayantandasguptaece2012@ssh.pythonanywhere.com:/home/sayantandasguptaece2012/youtube-organizer/app.py

# Upload authentication files
echo -e "${GREEN}✓ Uploading web_auth.py${NC}"
scp /Users/sayantandasgupta/Desktop/Youtube\ Organizer/web_auth.py sayantandasguptaece2012@ssh.pythonanywhere.com:/home/sayantandasguptaece2012/youtube-organizer/web_auth.py

# Upload static files
echo -e "${GREEN}✓ Uploading static files...${NC}"
scp -r /Users/sayantandasgupta/Desktop/Youtube\ Organizer/static/* sayantandasguptaece2012@ssh.pythonanywhere.com:/home/sayantandasguptaece2012/youtube-organizer/static/

# Upload other Python files
echo -e "${GREEN}✓ Uploading Python files...${NC}"
scp /Users/sayantandasgupta/Desktop/Youtube\ Organizer/*.py sayantandasguptaece2012@ssh.pythonanywhere.com:/home/sayantandasguptaece2012/youtube-organizer/

# Upload config files
echo -e "${GREEN}✓ Uploading config files...${NC}"
scp /Users/sayantandasgupta/Desktop/Youtube\ Organizer/*.txt sayantandasguptaece2012@ssh.pythonanywhere.com:/home/sayantandasguptaece2012/youtube-organizer/

echo -e "${GREEN}✓ All files uploaded!${NC}"
echo ""
echo -e "${BLUE}Step 2: Restarting web app...${NC}"

# Reload the web app
ssh sayantandasguptaece2012@ssh.pythonanywhere.com "touch /var/www/sayantandasguptaece2012_pythonanywhere_com_wsgi.py && /usr/bin/supervisorctl restart youtube-organizer"

echo -e "${GREEN}✓ Web app restarted!${NC}"
echo ""
echo -e "${YELLOW}📱 Your YouTube Organizer is now live at:${NC}"
echo -e "${BLUE}https://sayantandasguptaece2012.pythonanywhere.com${NC}"
echo ""
echo -e "${GREEN}🎉 Deployment complete!${NC}"
