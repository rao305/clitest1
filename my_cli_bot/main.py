#!/usr/bin/env python3
"""
Main entry point for Purdue CS AI Assistant
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the deployment system
from complete_replit_deployment import main

if __name__ == "__main__":
    main()