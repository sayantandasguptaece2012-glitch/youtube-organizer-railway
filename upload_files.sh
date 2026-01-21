#!/bin/bash

# Simple file upload commands for PythonAnywhere

echo "🚀 Uploading YouTube Organizer files to PythonAnywhere..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}Uploading app.py...${NC}"
scp "/Users/sayantandasgupta/Desktop/Youtube Organizer/app.py" sayantandasguptaece2012@ssh.pythonanywhere.com:/home/sayantandasguptaece2012/youtube-organizer/app.py

echo -e "${GREEN}Uploading web_auth.py...${NC}"
scp "/Users/sayantandasgupta/Desktop/Youtube Organizer/web_auth.py" sayantandasguptaece2012@ssh.pythonanywhere.com:/home/sayantandasguptaece2012/youtube-organizer/web_auth.py

echo -e "${GREEN}Uploading static files...${NC}"
scp -r "/Users/sayantandasgupta/Desktop/Youtube Organizer/static/"* sayantandasguptaece2012@ssh.pythonanywhere.com:/home/sayantandasguptaece2012/youtube-organizer/static/

echo -e "${GREEN}Uploading other Python files...${NC}"
scp "/Users/sayantandasgupta/Desktop/Youtube Organizer/"*.py sayantandasguptaece2012@ssh.pythonanywhere.com:/home/sayantandasguptaece2012/youtube-organizer/

echo -e "${GREEN}Restarting web app...${NC}"
ssh sayantandasguptaece2012@ssh.pythonanywhere.com "/usr/bin/supervisorctl restart youtube-organizer"

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${BLUE}https://sayantandasguptaece2012.pythonanywhere.com${NC}"
