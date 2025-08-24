"""
Detection modules for the detection agent.
"""

import time
import os
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod


class BaseDetector(ABC):
    """Base class for all detectors."""
    
    def __init__(self, name: str):
        """
        Initialize detector.
        
        Args:
            name: Name of the detector.
        """
        self.name = name
        self.enabled = True
        self.last_detection_time = None
    
    @abstractmethod
    def detect(self) -> List[Dict[str, Any]]:
        """
        Perform detection and return results.
        
        Returns:
            List of detection results.
        """
        pass
    
    def is_enabled(self) -> bool:
        """Check if detector is enabled."""
        return self.enabled
    
    def enable(self) -> None:
        """Enable the detector."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable the detector."""
        self.enabled = False


class FileDetector(BaseDetector):
    """Detector for file system changes."""
    
    def __init__(self, watch_paths: Optional[List[str]] = None):
        """
        Initialize file detector.
        
        Args:
            watch_paths: List of paths to monitor. Defaults to current directory.
        """
        super().__init__("file_detector")
        self.watch_paths = watch_paths or ["."]
        self._file_cache = {}
        self._initialize_cache()
    
    def _initialize_cache(self) -> None:
        """Initialize file cache with current state."""
        for path in self.watch_paths:
            if os.path.exists(path):
                if os.path.isfile(path):
                    self._file_cache[path] = os.path.getmtime(path)
                elif os.path.isdir(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            self._file_cache[file_path] = os.path.getmtime(file_path)
    
    def detect(self) -> List[Dict[str, Any]]:
        """
        Detect file system changes.
        
        Returns:
            List of detected changes.
        """
        if not self.enabled:
            return []
        
        detections = []
        current_time = time.time()
        
        for path in self.watch_paths:
            if not os.path.exists(path):
                continue
            
            if os.path.isfile(path):
                current_mtime = os.path.getmtime(path)
                if path not in self._file_cache or self._file_cache[path] != current_mtime:
                    detections.append({
                        "type": "file_change",
                        "path": path,
                        "timestamp": current_time,
                        "action": "modified" if path in self._file_cache else "created"
                    })
                    self._file_cache[path] = current_mtime
            
            elif os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.exists(file_path):  # Check if file still exists
                            current_mtime = os.path.getmtime(file_path)
                            
                            if file_path not in self._file_cache or self._file_cache[file_path] != current_mtime:
                                detections.append({
                                    "type": "file_change",
                                    "path": file_path,
                                    "timestamp": current_time,
                                    "action": "modified" if file_path in self._file_cache else "created"
                                })
                                self._file_cache[file_path] = current_mtime
        
        self.last_detection_time = current_time
        return detections


class ProcessDetector(BaseDetector):
    """Detector for process monitoring."""
    
    def __init__(self):
        """Initialize process detector."""
        super().__init__("process_detector")
        self._process_cache = set()
    
    def detect(self) -> List[Dict[str, Any]]:
        """
        Detect process changes.
        
        Returns:
            List of detected process changes.
        """
        if not self.enabled:
            return []
        
        detections = []
        current_time = time.time()
        
        # For simplicity, we'll just return a mock detection
        # In a real implementation, this would use psutil or similar
        detections.append({
            "type": "process_check",
            "timestamp": current_time,
            "message": "Process monitoring active"
        })
        
        self.last_detection_time = current_time
        return detections


class Detector:
    """Main detector coordinator."""
    
    def __init__(self):
        """Initialize the detector coordinator."""
        self.detectors = {}
        self.results = []
    
    def add_detector(self, detector: BaseDetector) -> None:
        """
        Add a detector to the coordinator.
        
        Args:
            detector: Detector instance to add.
        """
        self.detectors[detector.name] = detector
    
    def remove_detector(self, name: str) -> bool:
        """
        Remove a detector by name.
        
        Args:
            name: Name of the detector to remove.
            
        Returns:
            True if detector was removed, False if not found.
        """
        if name in self.detectors:
            del self.detectors[name]
            return True
        return False
    
    def get_detector(self, name: str) -> Optional[BaseDetector]:
        """
        Get a detector by name.
        
        Args:
            name: Name of the detector.
            
        Returns:
            Detector instance or None if not found.
        """
        return self.detectors.get(name)
    
    def run_all_detections(self) -> List[Dict[str, Any]]:
        """
        Run all enabled detectors and collect results.
        
        Returns:
            List of all detection results.
        """
        all_results = []
        
        for detector in self.detectors.values():
            if detector.is_enabled():
                try:
                    results = detector.detect()
                    all_results.extend(results)
                except Exception as e:
                    # Log error but continue with other detectors
                    all_results.append({
                        "type": "detection_error",
                        "detector": detector.name,
                        "error": str(e),
                        "timestamp": time.time()
                    })
        
        self.results.extend(all_results)
        return all_results
    
    def get_detection_history(self) -> List[Dict[str, Any]]:
        """
        Get all detection results history.
        
        Returns:
            List of all historical detection results.
        """
        return self.results.copy()
    
    def clear_history(self) -> None:
        """Clear detection history."""
        self.results.clear()