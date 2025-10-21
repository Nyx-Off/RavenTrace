#!/usr/bin/env python3
"""
Setup.py - Installation du projet Raven Trace
"""

from setuptools import setup, find_packages
from pathlib import Path

# Lire le README
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    with open(readme_file, encoding="utf-8") as f:
        long_description = f.read()

# Lire les dépendances
requirements_file = Path(__file__).parent / "requirements.txt"
install_requires = []
if requirements_file.exists():
    with open(requirements_file, encoding="utf-8") as f:
        install_requires = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="raven-trace",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Advanced OSINT Intelligence Tool - Email, Phone, Username Reconnaissance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/raven-trace",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Intended Audience :: Information Technology",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "raven-trace=raven_trace.main:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)