import os
import sys

# Add project root directory to sys.path so modules (main, application, initial_data) can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
