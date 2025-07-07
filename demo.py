#!/usr/bin/env python3
"""
Demo script to showcase the detection agent functionality.
"""

import time
import tempfile
import os
from detection_agent import DetectionAgent, Config


def demo_callback(results):
    """Callback function to handle detection results."""
    print(f"🚨 Detection Alert: {len(results)} events detected!")
    for result in results:
        print(f"  - {result}")
    print()


def main():
    """Run the detection agent demo."""
    print("🔍 Public Detection Agent Demo")
    print("=" * 40)
    
    # Create custom configuration
    config = Config()
    config.set("detection_interval", 2)  # Check every 2 seconds
    config.set("log_level", "WARNING")   # Reduce log verbosity for demo
    
    # Create and configure agent
    agent = DetectionAgent(config)
    agent.add_callback(demo_callback)
    
    print("✅ Agent initialized with configuration:")
    status = agent.get_status()
    print(f"  - Detectors: {list(status['detectors'].keys())}")
    print(f"  - Detection interval: {config.get('detection_interval')}s")
    print(f"  - Callbacks registered: {status['callbacks_registered']}")
    print()
    
    # Test single detection
    print("🔄 Running single detection...")
    results = agent.run_single_detection()
    print(f"Initial detection found {len(results)} events")
    print()
    
    # Create a temporary file to trigger file detection
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "demo_file.txt")
    
    print(f"📁 Creating test file: {test_file}")
    with open(test_file, 'w') as f:
        f.write("Initial content")
    
    # Add file detector for our temp directory
    from detection_agent.detector import FileDetector
    file_detector = FileDetector([temp_dir])
    agent.detector.add_detector(file_detector)
    
    print("🚀 Starting continuous monitoring for 10 seconds...")
    agent.start()
    
    # Simulate file changes
    time.sleep(3)
    print("✏️  Modifying test file...")
    with open(test_file, 'a') as f:
        f.write("\nAdded content")
    
    time.sleep(3)
    print("✏️  Creating another file...")
    another_file = os.path.join(temp_dir, "another_file.txt")
    with open(another_file, 'w') as f:
        f.write("Another file content")
    
    time.sleep(4)
    
    # Stop monitoring
    print("⏹️  Stopping agent...")
    agent.stop()
    
    # Show final statistics
    print("\n📊 Final Statistics:")
    history = agent.get_detection_history()
    print(f"  - Total detections: {len(history)}")
    
    detection_types = {}
    for detection in history:
        det_type = detection.get('type', 'unknown')
        detection_types[det_type] = detection_types.get(det_type, 0) + 1
    
    for det_type, count in detection_types.items():
        print(f"  - {det_type}: {count}")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    if os.path.exists(test_file):
        os.unlink(test_file)
    if os.path.exists(another_file):
        os.unlink(another_file)
    os.rmdir(temp_dir)
    
    print("✨ Demo completed successfully!")


if __name__ == "__main__":
    main()