"""
Public Detection Agent - A Python package for detection and monitoring.
"""

__version__ = "1.0.0"
__author__ = "Detection Team"

from .agent import DetectionAgent
from .detector import Detector
from .config import Config

__all__ = ["DetectionAgent", "Detector", "Config"]