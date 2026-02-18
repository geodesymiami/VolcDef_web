import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Flask app configurations
class Config:
    DEBUG = True
    SECRET_KEY = 'your_secret_key_here'
    # Add more configurations as needed
