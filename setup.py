"""
Setup script for LeRobot Tools
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

# Read CLI requirements
cli_requirements = []
cli_req_file = Path(__file__).parent / "requirements-cli.txt"
if cli_req_file.exists():
    with open(cli_req_file, 'r') as f:
        cli_requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith('#')
        ]

setup(
    name="lerobot-setup-tools",
    version="2.0.0",
    author="LeRobot Team",
    description="Interactive CLI tools for LeRobot hardware setup",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=cli_requirements,  # Only CLI dependencies
    entry_points={
        "console_scripts": [
            "lerobot-setup=tools.setup_cli:main",
            "lr-setup=tools.setup_cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)