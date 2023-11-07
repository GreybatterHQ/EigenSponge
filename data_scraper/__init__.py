import sys
import os

# Get the current directory path
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory path
parent_dir = os.path.dirname(current_dir)

# Append the parent directory to the system path
sys.path.append(parent_dir)