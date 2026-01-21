import sys
from app import app as application

# Add your project directory to the Python path
project_home = '/home/yourusername/youtube-organizer'
if project_home not in sys.path:
    sys.path.insert(0, project_home)
