"""
Main detection agent implementation.
"""

import time
import threading
import logging
from typing import List, Dict, Any, Optional, Callable
from .config import Config
from .detector import Detector, FileDetector, ProcessDetector


class DetectionAgent:
    """Main detection agent that coordinates detection activities."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the detection agent.
        
        Args:
            config: Configuration object. If None, uses default config.
        """
        self.config = config or Config()
        self.detector = Detector()
        self._running = False
        self._thread = None
        self._callbacks = []
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, self.config.get("log_level", "INFO")),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize detectors based on config
        self._initialize_detectors()
    
    def _initialize_detectors(self) -> None:
        """Initialize detectors based on configuration."""
        enabled_detectors = self.config.get("enabled_detectors", [])
        
        if "file" in enabled_detectors:
            file_detector = FileDetector()
            self.detector.add_detector(file_detector)
            self.logger.info("File detector initialized")
        
        if "process" in enabled_detectors:
            process_detector = ProcessDetector()
            self.detector.add_detector(process_detector)
            self.logger.info("Process detector initialized")
    
    def add_callback(self, callback: Callable[[List[Dict[str, Any]]], None]) -> None:
        """
        Add a callback function to be called when detections occur.
        
        Args:
            callback: Function that takes a list of detection results.
        """
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[List[Dict[str, Any]]], None]) -> bool:
        """
        Remove a callback function.
        
        Args:
            callback: Callback function to remove.
            
        Returns:
            True if callback was removed, False if not found.
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)
            return True
        return False
    
    def _notify_callbacks(self, results: List[Dict[str, Any]]) -> None:
        """
        Notify all registered callbacks with detection results.
        
        Args:
            results: Detection results to pass to callbacks.
        """
        for callback in self._callbacks:
            try:
                callback(results)
            except Exception as e:
                self.logger.error(f"Error in callback: {e}")
    
    def run_single_detection(self) -> List[Dict[str, Any]]:
        """
        Run a single detection cycle.
        
        Returns:
            List of detection results.
        """
        self.logger.debug("Running single detection cycle")
        results = self.detector.run_all_detections()
        
        if results:
            self.logger.info(f"Detected {len(results)} events")
            self._notify_callbacks(results)
        
        return results
    
    def start(self) -> None:
        """Start the detection agent in continuous mode."""
        if self._running:
            self.logger.warning("Agent is already running")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self.logger.info("Detection agent started")
    
    def stop(self) -> None:
        """Stop the detection agent."""
        if not self._running:
            self.logger.warning("Agent is not running")
            return
        
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        
        self.logger.info("Detection agent stopped")
    
    def _run_loop(self) -> None:
        """Main detection loop running in a separate thread."""
        interval = self.config.get("detection_interval", 30)
        self.logger.info(f"Starting detection loop with {interval}s interval")
        
        while self._running:
            try:
                self.run_single_detection()
                time.sleep(interval)
            except Exception as e:
                self.logger.error(f"Error in detection loop: {e}")
                time.sleep(1)  # Brief pause before retrying
    
    def is_running(self) -> bool:
        """
        Check if the agent is currently running.
        
        Returns:
            True if running, False otherwise.
        """
        return self._running
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent.
        
        Returns:
            Dictionary containing status information.
        """
        detector_status = {}
        for name, detector in self.detector.detectors.items():
            detector_status[name] = {
                "enabled": detector.is_enabled(),
                "last_detection": detector.last_detection_time
            }
        
        return {
            "running": self._running,
            "config": self.config.get_all(),
            "detectors": detector_status,
            "detection_count": len(self.detector.get_detection_history()),
            "callbacks_registered": len(self._callbacks)
        }
    
    def get_detection_history(self) -> List[Dict[str, Any]]:
        """
        Get all detection history.
        
        Returns:
            List of all detection results.
        """
        return self.detector.get_detection_history()
    
    def clear_history(self) -> None:
        """Clear detection history."""
        self.detector.clear_history()
        self.logger.info("Detection history cleared")