# Public Detection Agent

A Python package for detection and monitoring activities.

## Features

- File system monitoring and detection
- Process monitoring and detection
- Configurable detection intervals and settings
- Extensible detector framework
- Comprehensive unit test coverage

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from detection_agent import DetectionAgent, Config

# Create agent with default configuration
agent = DetectionAgent()

# Run a single detection cycle
results = agent.run_single_detection()
print(f"Detected {len(results)} events")

# Start continuous monitoring
agent.start()

# Stop monitoring
agent.stop()
```

### Custom Configuration

```python
from detection_agent import DetectionAgent, Config

# Create custom configuration
config = Config()
config.set("detection_interval", 60)  # Check every 60 seconds
config.set("enabled_detectors", ["file", "process"])

# Create agent with custom config
agent = DetectionAgent(config)
```

### Adding Callbacks

```python
def my_callback(results):
    for result in results:
        print(f"Detection: {result}")

agent.add_callback(my_callback)
```

## Testing

Run the unit tests:

```bash
cd tests
python run_tests.py
```

Or run individual test modules:

```bash
python -m unittest tests.test_config
python -m unittest tests.test_detector
python -m unittest tests.test_agent
```

## Project Structure

```
detection_agent/
├── __init__.py
├── agent.py          # Main detection agent
├── config.py         # Configuration management
└── detector.py       # Detection modules

tests/
├── __init__.py
├── test_agent.py     # Agent tests
├── test_config.py    # Configuration tests
├── test_detector.py  # Detector tests
└── run_tests.py      # Test runner
```

## Configuration Options

- `detection_interval`: Time between detection cycles (seconds)
- `max_threads`: Maximum number of worker threads
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `output_format`: Output format for results
- `enabled_detectors`: List of enabled detector types

## License

This project is licensed under the MIT License.