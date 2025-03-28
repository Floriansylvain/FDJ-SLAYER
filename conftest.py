"""
Add the parent directory to the sys.path so the tests can import the modules from the parent dir.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
