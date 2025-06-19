import sys
import os

# Add the project root to the Python path to resolve module imports.
# The project root is two levels above this file's directory (agents -> backend -> root).
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# This file makes the 'agents' directory a Python package. 
from . import agent