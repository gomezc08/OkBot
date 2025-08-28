"""
Example usage of the four core automation actions.
Demonstrates how to use click, type_text, load, and wait_user_input actions.
"""

import logging
from actions import ActionExecutor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Demonstrate the four core automation actions."""
    executor = ActionExecutor()
    
    # Example 1: Click action with UIA fallback to coordinates
    click_action = {
        "type": "click",
        "target": "Login Button",
        "button": "left",
        "element_selector": {
            "name": "Sign In",
            "control_type": "Button",
            "class_name": "Chrome_WidgetWin_1",
            "process_name": "chrome"
        },
        "coordinate_selector": {
            "coords": {"x": 500, "y": 300}
        },
        "description": "Click the login button"
    }
    
    print("=== Testing Click Action ===")
    result = executor.click(click_action)
    print(f"Click action result: {result}\n")
    
    # Example 2: Type text action
    type_action = {
        "type": "type_text",
        "text": "user@example.com",
        "description": "Enter email address"
    }
    
    print("=== Testing Type Text Action ===")
    result = executor.type_text(type_action)
    print(f"Type text action result: {result}\n")
    
    # Example 3: Load action (browser context)
    load_browser_action = {
        "type": "load",
        "description": "Wait for login page to load",
        "condition": {
            "type": "url.contains",
            "value": "accounts.google.com/signin"
        },
        "timeout": 10
    }
    
    print("=== Testing Load Action (Browser) ===")
    result = executor.load(load_browser_action)
    print(f"Load browser action result: {result}\n")
    
    # Example 4: Load action (desktop context)
    load_desktop_action = {
        "type": "load",
        "description": "Wait for Word document to open",
        "condition": {
            "type": "uia.exists",
            "selector": {
                "name": "Document1 - Microsoft Word",
                "control_type": "Window"
            }
        },
        "timeout": 15
    }
    
    print("=== Testing Load Action (Desktop) ===")
    result = executor.load(load_desktop_action)
    print(f"Load desktop action result: {result}\n")
    
    # Example 5: Wait for user input action
    wait_action = {
        "type": "wait_user",
        "description": "Wait for user to complete login",
        "condition": {
            "type": "url.contains",
            "value": "mail.google.com/mail/u/0/#inbox"
        },
        "timeout": 60
    }
    
    print("=== Testing Wait User Input Action ===")
    result = executor.wait_user_input(wait_action)
    print(f"Wait user input action result: {result}\n")

if __name__ == "__main__":
    main()
