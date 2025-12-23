"""
LeRobot Tools Package
Interactive CLI tools for LeRobot hardware setup and configuration
"""

__version__ = "2.0.0"
__author__ = "LeRobot Team"

from .setup_cli import main as setup_cli_main

__all__ = ["setup_cli_main"]