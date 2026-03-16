import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from session_builder import generate_session

generate_session()