# OkBot Automation Engine - Core Actions

This document describes the four core automation actions available in the OkBot FlaUI Automation Engine.

## Overview

The automation engine provides four fundamental actions that can handle both browser and desktop application automation:

1. **click** - Click elements with UIA fallback to coordinates
2. **type_text** - Type text into focused fields
3. **load** - Wait for conditions to be met (browser or desktop)
4. **wait_user_input** - Wait for user to complete actions

## Action Details

### 1. Click Action

**Purpose**: Click on UI elements with intelligent fallback from UIA-based selection to coordinate-based clicking.

**Schema**:
```json
{
    "type": "click",
    "target": "Login Button",
    "button": "left",
    "element_selector": {
        "name": "Sign In",
        "control_type": "Button",
        "class_name": "Chrome_WidgetWin_1",
        "process_name": "chrome",
        "ancestor_path": ["RootView", "ProfilePickerView"]
    },
    "coordinate_selector": {
        "coords": {
            "x": 500,
            "y": 300
        },
        "bbox": {
            "left": 450,
            "top": 250,
            "right": 550,
            "bottom": 350
        }
    },
    "description": "Click the login button"
}
```

**Behavior**:
- First attempts UIA-based clicking using the `element_selector`
- If UIA fails, falls back to coordinate-based clicking using `coordinate_selector`
- Supports left, right, and middle mouse buttons
- Returns `true` on success, `false` on failure

### 2. Type Text Action

**Purpose**: Type text into the currently focused input field.

**Schema**:
```json
{
    "type": "type_text",
    "text": "user@example.com",
    "description": "Enter email address"
}
```

**Behavior**:
- Types the specified text using pyautogui
- Assumes the target field is already focused
- Returns `true` on success, `false` on failure

### 3. Load Action

**Purpose**: Wait for specific conditions to be met, automatically detecting browser vs desktop context.

**Schema**:
```json
{
    "type": "load",
    "description": "Wait for page to load",
    "condition": {
        "type": "url.contains",
        "value": "accounts.google.com/signin"
    },
    "timeout": 30
}
```

**Browser Conditions**:
- `url.is`: Exact URL match
- `url.contains`: Partial URL match

**Desktop Conditions**:
- `uia.exists`: Wait for element to appear
- `uia.not_exists`: Wait for element to disappear

**Behavior**:
- Automatically detects browser vs desktop context
- Polls conditions every 500ms
- Returns `true` when condition is met, `false` on timeout

### 4. Wait User Input Action

**Purpose**: Wait for user to complete manual actions (e.g., login, CAPTCHA).

**Schema**:
```json
{
    "type": "wait_user",
    "description": "Wait for user to complete login",
    "condition": {
        "type": "url.contains",
        "value": "mail.google.com/mail/u/0/#inbox"
    },
    "timeout": 120
}
```

**Behavior**:
- Similar to load action but designed for user interaction scenarios
- Polls conditions every 1 second (slower than load)
- Useful for login flows, manual verification steps
- Returns `true` when condition is met, `false` on timeout

## Context Detection

The engine automatically detects whether you're working in a browser or desktop application:

- **Browser Context**: Detected by window titles containing browser names (Chrome, Firefox, Edge, Safari)
- **Desktop Context**: All other applications (Word, Excel, Notepad, etc.)

## Condition Types

### Browser Conditions
```json
{
    "type": "url.contains",
    "value": "gmail.com"
}
```

### Desktop Conditions
```json
{
    "type": "uia.exists",
    "selector": {
        "name": "Document1 - Microsoft Word",
        "control_type": "Window"
    }
}
```

## Usage Examples

### Complete Login Flow
```json
[
    {
        "type": "click",
        "target": "Email Field",
        "element_selector": {
            "name": "Email",
            "control_type": "Edit"
        },
        "description": "Click email input field"
    },
    {
        "type": "type_text",
        "text": "user@example.com",
        "description": "Enter email address"
    },
    {
        "type": "load",
        "description": "Wait for password field to appear",
        "condition": {
            "type": "uia.exists",
            "selector": {
                "name": "Password",
                "control_type": "Edit"
            }
        },
        "timeout": 10
    },
    {
        "type": "wait_user_input",
        "description": "Wait for user to complete login",
        "condition": {
            "type": "url.contains",
            "value": "mail.google.com/mail/u/0/#inbox"
        },
        "timeout": 120
    }
]
```

## Error Handling

- All actions return boolean values indicating success/failure
- Comprehensive logging for debugging
- Schema validation ensures proper data structure
- Graceful fallbacks (UIA → coordinates for clicking)

## Dependencies

- `pyautogui`: For coordinate-based clicking and text typing
- `pygetwindow`: For window context detection
- `logging`: For comprehensive action logging

## Integration Notes

- UIA element detection is currently placeholder - integrate with your UIA listener
- Browser URL detection is simplified - enhance with proper browser automation tools
- All timeouts are configurable per action
- Actions can be chained together in automation scripts
