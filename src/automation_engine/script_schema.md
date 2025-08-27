# OkBot Automation Script JSON Schema

This document describes the JSON format for automation scripts that can be executed by the OkBot FlaUI Automation Engine.

## Script Structure

```json
{
  "description": "Human-readable description of what this script does",
  "actions": [
    // Array of actions to execute in sequence
  ]
}
```

## Action Types

### 1. start_process
Launches an application or opens a URL.

```json
{
  "type": "start_process",
  "target": "notepad",
  "app_path": "notepad.exe",
  "description": "Open Notepad application"
}
```

**Parameters:**
- `target` (required): Process name, path, or URL
- `app_path` (optional): Full path to the application executable
- `description` (optional): Human-readable description

**Examples:**
```json
// Open Notepad
{
  "type": "start_process",
  "target": "notepad",
  "app_path": "notepad.exe"
}

// Open URL in Chrome
{
  "type": "start_process",
  "target": "https://www.google.com",
  "app_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
}

// Open specific application
{
  "type": "start_process",
  "target": "calc.exe",
  "description": "Open Calculator"
}
```

### 2. wait_for
Waits for a condition to be met (currently a placeholder for future UI element detection).

```json
{
  "type": "wait_for",
  "condition": "Notepad window appears",
  "timeout": 30,
  "description": "Wait for Notepad to fully load"
}
```

**Parameters:**
- `condition` (required): Description of what to wait for
- `timeout` (optional): Maximum wait time in seconds (default: 30)
- `description` (optional): Human-readable description

### 3. type_text
Types text into the active application.

```json
{
  "type": "type_text",
  "text": "Hello, World!",
  "delay": 0.05,
  "focus_app": "Notepad",
  "description": "Type greeting message"
}
```

**Parameters:**
- `text` (required): Text to type (supports variable substitution with `${var_name}`)
- `delay` (optional): Delay between characters in seconds (default: 0.01)
- `focus_app` (optional): Application window title to focus before typing
- `description` (optional): Human-readable description

**Variable Substitution:**
```json
// Set a variable first
{
  "type": "set_variable",
  "name": "greeting",
  "value": "Hello from OkBot!"
}

// Use the variable in text
{
  "type": "type_text",
  "text": "${greeting}",
  "description": "Type the greeting variable"
}
```

### 4. click
Clicks on a UI element using UIA element detection or coordinates.

```json
{
  "type": "click",
  "target": "Save button",
  "button": "left",
  "focus_app": "Notepad",
  "element_selector": {
    "control_type": "Button",
    "name": "Save",
    "class_name": "Button"
  },
  "description": "Click the save button using UIA detection"
}
```

**Parameters:**
- `target` (required): Description of element to click
- `button` (optional): Mouse button to use - `"left"`, `"right"`, `"middle"` (default: `"left"`)
- `focus_app` (optional): Application window title to focus before clicking
- `keyboard_shortcut` (optional): Keyboard shortcut to execute (e.g., `"alt+f4"`, `"ctrl+s"`)
- `element_selector` (optional): UIA element selector for intelligent element detection
- `coordinates` (optional): [x, y] coordinates to click at (fallback if UIA detection fails)
- `description` (optional): Human-readable description

**Element Selector Properties:**
- `control_type`: UI element type (e.g., "Button", "Edit", "Window", "Pane")
- `name`: Element name or text content
- `class_name`: Element's class name
- `process_name`: Target application process name

**Usage Priority:**
1. **Keyboard Shortcut** (most reliable for window actions): Uses `keyboard_shortcut` for standard actions
2. **UIA Element Detection** (recommended for UI elements): Uses `element_selector` for intelligent element finding
3. **Coordinates Fallback**: Falls back to `coordinates` if UIA detection fails
4. **Simulation**: Logs action if neither method is available

### 5. set_variable
Sets a variable for use in subsequent actions.

```json
{
  "type": "set_variable",
  "name": "filename",
  "value": "my_document.txt",
  "description": "Set filename variable"
}
```

**Parameters:**
- `name` (required): Variable name
- `value` (required): Variable value (any JSON-compatible type)
- `description` (optional): Human-readable description

### 6. wait
Simple delay or wait for human input.

```json
{
  "type": "wait",
  "duration": 2,
  "description": "Wait 2 seconds"
}
```

**Parameters:**
- `duration` (optional): Wait time in seconds (if 0 or not provided, waits for human input)
- `prompt` (optional): Custom prompt message for human input
- `description` (optional): Human-readable description

**Usage:**
- **Simple delay**: Set `duration` to a positive number
- **Human input**: Omit `duration` or set to 0, optionally provide a `prompt`

## Global Script Options

### continue_on_failure
You can add `continue_on_failure: true` to any action to continue script execution even if that specific action fails.

```json
{
  "type": "click",
  "target": "Optional button",
  "continue_on_failure": true,
  "description": "Try to click, but continue if it fails"
}
```

### delay
Add a delay after any action completes:

```json
{
  "type": "type_text",
  "text": "Some text",
  "delay": 1,
  "description": "Type text, then wait 1 second"
}
```

## Complete Example Script

```json
{
  "description": "Open Notepad and create a simple document",
  "actions": [
    {
      "type": "start_process",
      "target": "notepad",
      "app_path": "notepad.exe",
      "description": "Launch Notepad"
    },
    {
      "type": "wait",
      "duration": 2,
      "description": "Wait for Notepad to load"
    },
    {
      "type": "set_variable",
      "name": "message",
      "value": "This document was created by OkBot!",
      "description": "Set the message to type"
    },
    {
      "type": "type_text",
      "text": "${message}",
      "delay": 0.05,
      "focus_app": "Untitled - Notepad",
      "description": "Type the message with variable substitution"
    },
    {
      "type": "wait",
      "duration": 1,
      "description": "Pause to show the result"
    }
  ]
}
```

## Running Scripts

Scripts can be executed in several ways:

1. **From Python code:**
```python
from automation_engine import AutomationEngine

engine = AutomationEngine()
success = engine.run_script(script_data)
```

2. **From JSON file:**
```python
import json

with open('script.json', 'r') as f:
    script = json.load(f)

engine = AutomationEngine()
success = engine.run_script(script)
```

3. **From JSON string:**
```python
script_json = '{"description": "test", "actions": [...]}'
engine = AutomationEngine()
success = engine.run_script(script_json)
```

## Future Enhancements

The current implementation provides basic functionality. Future versions will include:

- **Real UI element detection** using FlaUI
- **Advanced element selection** (by name, ID, coordinates, etc.)
- **Conditional logic** (if/else statements)
- **Loops and repetition**
- **Error handling and recovery**
- **Screenshot capture**
- **File operations**
- **Network operations**
- **Database interactions**
