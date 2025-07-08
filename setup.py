"""
Setup script for the public detection agent package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="public-detection-agent",
    version="1.0.0",
    author="Detection Team",
    author_email="team@detection.example.com",
    description="A Python package for detection and monitoring activities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/charlessoft/public_detection_agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
        "monitoring": [
            "psutil>=5.9.0",
            "watchdog>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "detection-agent=detection_agent.agent:main",
        ],
    },
)