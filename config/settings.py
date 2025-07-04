
# config/settings.py
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Get the API key
GOOGLE_API_KEY=""
# Pick an absolute path to your project
BASE_PROJECT_PATH = "/home/dev/Desktop/sandbox/my-app"

# --- For testing purposes, we'll keep these for now ---
# We will replace this with a dynamic path later
# BASE_PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IGNORED_PATH = {'node_modules', '.venv', '.idea', '__pycache__', '.git', 'code-chat-assistant.egg-info'}




























