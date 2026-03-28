"""Pytest configuration for MagicGPT8Ball tests."""
import sys
import os

# Add parent directory to path so imports work when running from test/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
