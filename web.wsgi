import sys
import os

# Add the Flask app directory to the Python path
# Note: The virtual environment is already activated by Apache's  WSGIDaemonProcess python-home directive,
# so we don't need to manually add site-packages or hardcode the Python version!
sys.path.insert(0, '/var/www/VolcDef_web/')

from volcdef_web import app
application = app
