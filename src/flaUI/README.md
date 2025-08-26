# OkBot FlaUI Automation Module

This module provides a flexible automation engine for desktop automation tasks using Python. It's designed to be the foundation for the OkBot project, allowing users to create and execute automation scripts in JSON format.

## Features

- **Process Management**: Launch applications (Notepad, Word, Excel, Chrome, etc.)
- **URL Handling**: Open websites in specific browsers
- **Text Input**: Type text with configurable delays and variable substitution
- **UI Interaction**: Click on UI elements (placeholder for future FlaUI integration)
- **Variable System**: Set and use variables in scripts
- **JSON Scripting**: Execute automation tasks defined in JSON format
- **Error Handling**: Robust error handling with configurable failure behavior
- **Logging**: Comprehensive logging for debugging and monitoring

## Quick Start

### 1. Basic Usage

```python
from automation_engine import AutomationEngine

# Create automation engine
engine = AutomationEngine()

# Simple script to open Notepad and type text
script = {
    "description": "Open Notepad and type hello",
    "actions": [
        {
            "type": "start_process",
            "target": "notepad",
            "app": "notepad"
        },
        {
            "type": "wait",
            "duration": 2
        },
        {
            "type": "type_text",
            "text": "Hello, World!"
        }
    ]
}

# Execute the script
success = engine.run_script(script)
```

### 2. Running Example Scripts

The module includes several example scripts that you can run immediately:

```bash
# Navigate to the flaUI directory
cd src/flaUI

# Run the Notepad example
python run_script.py notepad_example.json

# Run the Chrome example
python run_script.py chrome_example.json

# List all available examples
python run_script.py
```

### 3. Creating Your Own Scripts

Create JSON files with your automation tasks:

```json
{
  "description": "My custom automation",
  "actions": [
    {
      "type": "start_process",
      "target": "calc.exe",
      "description": "Open Calculator"
    },
    {
      "type": "wait",
      "duration": 1
    },
    {
      "type": "type_text",
      "text": "123+456=",
      "delay": 0.1
    }
  ]
}
```

## Supported Actions

### start_process
Launches applications or opens URLs.

```json
{
  "type": "start_process",
  "target": "notepad",
  "app_path": "notepad.exe"
}
```

**Parameters:**
- `target` - Process name, path, or URL
- `app_path` - Full path to the application executable (optional)

### type_text
Types text with optional delays and variable substitution.

```json
{
  "type": "type_text",
  "text": "Hello ${name}!",
  "delay": 0.05
}
```

### wait
Simple delay or wait for human input.

```json
{
  "type": "wait",
  "duration": 2
}
```

**For human input (like passwords):**
```json
{
  "type": "wait",
  "prompt": "Enter your password and press Enter..."
}
```

### set_variable
Sets variables for use in scripts.

```json
{
  "type": "set_variable",
  "name": "username",
  "value": "John Doe"
}
```

### click
Clicks on UI elements (placeholder for future implementation).

```json
{
  "type": "click",
  "target": "Save button",
  "button": "left"
}
```

## Variable System

Use variables in your scripts for dynamic content:

```json
{
  "actions": [
    {
      "type": "set_variable",
      "name": "greeting",
      "value": "Hello from OkBot!"
    },
    {
      "type": "type_text",
      "text": "${greeting}"
    }
  ]
}
```

## Error Handling

Configure how actions handle failures:

```json
{
  "type": "click",
  "target": "Optional button",
  "continue_on_failure": true
}
```

## File Structure

```
src/flaUI/
├── automation_engine.py      # Core automation engine
├── run_script.py            # Script runner utility
├── script_schema.md         # JSON schema documentation
├── README.md                # This file
└── example_scripts/         # Example automation scripts
    ├── notepad_example.json
    └── chrome_example.json
```

## Dependencies

**Required:**
- `pyautogui>=0.9.54` - For actual text typing functionality

**Standard library modules:**
- `json` - JSON parsing
- `subprocess` - Process management
- `webbrowser` - URL handling
- `pathlib` - File path operations
- `logging` - Logging system
- `time` - Delays and timeouts

## Future Enhancements

This is the foundation module. Future versions will include:

1. **Real FlaUI Integration**: Actual UI element detection and interaction
2. **Advanced Element Selection**: Find elements by name, ID, coordinates, etc.
3. **Conditional Logic**: If/else statements and loops
4. **Screenshot Capture**: Visual verification capabilities
5. **File Operations**: Read/write files, create directories
6. **Network Operations**: HTTP requests, API interactions
7. **Database Integration**: Connect to databases for data-driven automation

## Contributing

When adding new automation capabilities:

1. Add the new action type to the `_execute_action` method
2. Update the `script_schema.md` documentation
3. Create example scripts demonstrating the new functionality
4. Add appropriate error handling and logging

## Troubleshooting

### Common Issues

1. **Applications not found**: Ensure the target application is installed and accessible
2. **Script execution fails**: Check the JSON syntax and action parameters
3. **Timing issues**: Adjust wait durations and delays as needed

### Debug Mode

Enable detailed logging by modifying the logging level in `automation_engine.py`:

```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

## License

This module is part of the OkBot project and follows the same licensing terms.
