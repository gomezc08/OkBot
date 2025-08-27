"""
FlaUI Automation Engine for OkBot
Provides basic desktop automation functions and JSON script execution capabilities.
"""

import json
import time
import subprocess
import webbrowser
from typing import Dict, Any, Optional, Union
from pathlib import Path
import logging
import pyautogui
import pygetwindow as gw

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutomationEngine:
    """
    Core automation engine that provides basic desktop automation functions.
    """
    
    def __init__(self):
        self.variables = {}  # Store variables for script execution
        self.timeout_default = 30  # Default timeout in seconds
        
    def start_process(self, target: str, **kwargs) -> bool:
        """
        Start a process or open a URL in an application.
        
        Args:
            target: Process name/path or URL to open
            **kwargs: Additional options like 'app_path' for specific application path
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            app_path = kwargs.get('app_path')
            
            # Handle URL.
            if target.startswith(('http://', 'https://')):
                # Handle URL opening
                if app_path and Path(app_path).exists():
                    # Use specified app path for URL
                    subprocess.Popen([app_path, target])
                    logger.info(f"Opened URL in specified app: {target}")
                    return True
                else:
                    # Open in default browser
                    webbrowser.open(target)
                    logger.info(f"Opened URL in default browser: {target}")
                    return True
            # Handle desktop application.
            else:
                # Handle process launching
                if app_path:
                    # Use specified app path
                    if Path(app_path).exists():
                        subprocess.Popen([app_path])
                        logger.info(f"Started process with path: {app_path}")
                        return True
                    else:
                        logger.error(f"App path not found: {app_path}")
                        return False
                else:
                    # Try to launch the target directly (let Windows handle it)
                    subprocess.Popen([target])
                    logger.info(f"Started process: {target}")
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to start process '{target}': {e}")
            return False
    
    def wait_for(self, condition: str, timeout: Optional[int] = None, **kwargs) -> bool:
        """
        Wait for a condition to be met (placeholder for element detection).
        
        Args:
            condition: Description of what to wait for
            timeout: Timeout in seconds (uses default if None)
            **kwargs: Additional condition parameters
            
        Returns:
            bool: True if condition met, False if timeout
        """
        timeout = timeout or self.timeout_default
        logger.info(f"Waiting for: {condition} (timeout: {timeout}s)")
        
        # For now, just wait a bit and return True
        # In a real implementation, this would check for UI elements
        time.sleep(2)
        logger.info(f"Condition met: {condition}")
        return True
    
    def type_text(self, text: str, **kwargs) -> bool:
        """
        Type text into the active application.
        
        Args:
            text: Text to type (can be variable reference like ${var_name})
            **kwargs: Additional options like 'delay' between characters, 'focus_app' for app name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Handle variable substitution
            if text.startswith('${') and text.endswith('}'):
                var_name = text[2:-1]
                if var_name in self.variables:
                    text = str(self.variables[var_name])
                    logger.info(f"Substituted variable {var_name} with value: {text}")
                else:
                    logger.warning(f"Variable {var_name} not found")
                    return False
            
            delay = kwargs.get('delay', 0.01)  # Default 10ms delay between characters
            focus_app = kwargs.get('focus_app')  # Optional app name to focus
            
            try:
                # Set a small delay to prevent issues
                pyautogui.PAUSE = 0.01
                
                # Focus the target application if specified
                if focus_app:
                    logger.info(f"Focusing application: {focus_app}")
                    try:
                        # Try to focus the application by its window title
                        windows = gw.getWindowsWithTitle(focus_app)
                        if windows:
                            target_window = windows[0]
                            target_window.activate()
                            target_window.maximize()
                            logger.info(f"Focused window: {target_window.title}")
                            # Wait a bit for the window to be ready
                            time.sleep(1)
                        else:
                            logger.warning(f"Could not find window with title: {focus_app}")
                    except ImportError:
                        logger.warning("pygetwindow not available, cannot focus application")
                    except Exception as e:
                        logger.warning(f"Could not focus application {focus_app}: {e}")
                
                logger.info(f"Typing text: '{text}' (delay: {delay}s)")
                
                # Actually type the text
                pyautogui.write(text, interval=delay)
                
                return True
                
            except ImportError:
                logger.warning("pyautogui not installed, falling back to simulation")
                # Fallback to simulation if pyautogui is not available
                logger.info(f"Simulating typing text: '{text}' (delay: {delay}s)")
                time.sleep(len(text) * delay)
                return True
            
        except Exception as e:
            logger.error(f"Failed to type text '{text}': {e}")
            return False
    
    def click(self, target: str, **kwargs) -> bool:
        """
        Click on a UI element.
        
        Args:
            target: Description of element to click
            **kwargs: Additional options like 'button' (left/right/middle), 'coordinates' for x,y position,
                     'element_selector' for UIA-based element detection, 'keyboard_shortcut' for keyboard actions
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            button = kwargs.get('button', 'left')
            coordinates = kwargs.get('coordinates')  # Optional x,y coordinates
            focus_app = kwargs.get('focus_app')  # Optional app to focus before clicking
            element_selector = kwargs.get('element_selector')  # UIA element selector
            keyboard_shortcut = kwargs.get('keyboard_shortcut')  # Keyboard shortcut (e.g., 'alt+f4')
            
            logger.info(f"Clicking {target} with {button} button")
            
            # Focus the target application if specified
            if focus_app:
                logger.info(f"Focusing application: {focus_app}")
                try:
                    windows = gw.getWindowsWithTitle(focus_app)
                    if windows:
                        target_window = windows[0]
                        target_window.activate()
                        logger.info(f"Focused window: {target_window.title}")
                        time.sleep(0.5)  # Wait for window to be ready
                    else:
                        logger.warning(f"Could not find window with title: {focus_app}")
                except Exception as e:
                    logger.warning(f"Could not focus application {focus_app}: {e}")
            
            # Try keyboard shortcut first (most reliable for window actions)
            if keyboard_shortcut:
                logger.info(f"Using keyboard shortcut: {keyboard_shortcut}")
                try:
                    pyautogui.hotkey(*keyboard_shortcut.split('+'))
                    logger.info(f"Executed keyboard shortcut: {keyboard_shortcut}")
                    return True
                except Exception as e:
                    logger.warning(f"Keyboard shortcut failed: {e}")
            
            # Try UIA-based element detection
            if element_selector:
                success = self._click_by_uia(element_selector, button)
                if success:
                    return True
                else:
                    logger.warning("UIA element detection failed, falling back to coordinates")
            
            # Perform the actual click
            if coordinates:
                x, y = coordinates
                logger.info(f"Clicking at coordinates: ({x}, {y})")
                pyautogui.click(x, y, button=button)
            else:
                # For now, just log the action (future: implement element detection)
                logger.info(f"Clicking {target} (coordinates not specified)")
                time.sleep(0.5)  # Simulate click delay
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to click '{target}': {e}")
            return False
    
    def _click_by_uia(self, element_selector: dict, button: str = 'left') -> bool:
        """
        Click on a UI element using UIA element detection.
        
        Args:
            element_selector: Dictionary with UIA properties to identify the element
            button: Mouse button to use
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            control_type = element_selector.get('control_type', 'Any')
            name = element_selector.get('name', '')
            class_name = element_selector.get('class_name', '')
            process_name = element_selector.get('process_name', '')
            
            logger.info(f"UIA: Looking for element - Type: {control_type}, Name: '{name}', Class: '{class_name}', Process: '{process_name}'")
            
            # Try to use pywinauto for UIA element detection
            try:
                from pywinauto import Desktop, Application
                from pywinauto.findwindows import find_window
                from pywinauto.controls.uiawrapper import UIAWrapper
                
                # Find the target window first
                target_window = None
                if process_name:
                    # Try to find by process name
                    try:
                        # First try to connect by process name
                        app = Application(backend="uia").connect(process=process_name)
                        target_window = app.top_window()
                        logger.info(f"Found window by process: {target_window.window_text()}")
                    except Exception as e:
                        logger.info(f"Could not find window by process name '{process_name}': {e}")
                        
                        # Try to find by executable name
                        try:
                            import psutil
                            for proc in psutil.process_iter(['pid', 'name']):
                                if proc.info['name'].lower() == process_name.lower():
                                    try:
                                        app = Application(backend="uia").connect(pid=proc.info['pid'])
                                        target_window = app.top_window()
                                        logger.info(f"Found window by PID {proc.info['pid']}: {target_window.window_text()}")
                                        break
                                    except Exception as pid_e:
                                        logger.info(f"Could not connect to PID {proc.info['pid']}: {pid_e}")
                                        continue
                        except ImportError:
                            logger.info("psutil not available for process enumeration")
                        except Exception as e:
                            logger.info(f"Process enumeration failed: {e}")
                
                if not target_window and class_name:
                    # Try to find by class name
                    try:
                        target_window = find_window(class_name=class_name)
                        target_window = UIAWrapper(target_window)
                        logger.info(f"Found window by class: {target_window.window_text()}")
                    except Exception as e:
                        logger.info(f"Could not find window by class {class_name}: {e}")
                
                if not target_window:
                    # Try to find any window that might contain our element
                    try:
                        windows = Desktop(backend="uia").windows()
                        for window in windows:
                            try:
                                window_text = window.window_text()
                                if window_text and window_text != "" and "chrome" in window_text.lower():
                                    target_window = window
                                    logger.info(f"Found Chrome window: {window_text}")
                                    break
                            except:
                                continue
                    except Exception as e:
                        logger.info(f"Could not enumerate windows: {e}")
                
                if not target_window:
                    # Last resort: try to find any visible window
                    try:
                        windows = Desktop(backend="uia").windows()
                        for window in windows:
                            try:
                                window_text = window.window_text()
                                if window_text and window_text != "" and len(window_text) > 3:
                                    target_window = window
                                    logger.info(f"Using fallback window: {window_text}")
                                    break
                            except:
                                continue
                    except Exception as e:
                        logger.info(f"Could not enumerate windows: {e}")
                
                if target_window:
                    # Look for the specific element within the window
                    element = None
                    
                    # Try to find by name first (most reliable)
                    if name:
                        try:
                            # Try different methods to find elements by name
                            try:
                                element = target_window.child_window(name=name, control_type=control_type)
                                logger.info(f"Found element by name: {name}")
                            except:
                                # Fallback: search all children for name match
                                all_children = target_window.children()
                                for child in all_children:
                                    try:
                                        if hasattr(child, 'window_text'):
                                            child_text = child.window_text()
                                            if child_text and name.lower() in child_text.lower():
                                                element = child
                                                logger.info(f"Found element by name in children: {child_text}")
                                                break
                                    except:
                                        continue
                        except Exception as e:
                            logger.info(f"Element not found by name '{name}': {e}")
                    
                    # Try to find by control type if name didn't work
                    if not element and control_type != 'Any':
                        try:
                            # Try different approaches to find elements
                            try:
                                elements = target_window.children(control_type=control_type)
                            except:
                                # Fallback: try to get all children and filter by type
                                try:
                                    all_children = target_window.children()
                                    elements = []
                                    for child in all_children:
                                        try:
                                            if hasattr(child, 'control_type'):
                                                child_type = str(child.control_type())
                                                if control_type.lower() in child_type.lower():
                                                    elements.append(child)
                                        except:
                                            continue
                                except:
                                    elements = []
                            
                            if elements:
                                # If we have a name, try to find the best match
                                if name:
                                    for elem in elements:
                                        try:
                                            elem_text = elem.window_text()
                                            if elem_text and name.lower() in elem_text.lower():
                                                element = elem
                                                logger.info(f"Found element by type and partial name match: {elem_text}")
                                                break
                                        except:
                                            continue
                                
                                # If still no match, use the first element of this type
                                if not element:
                                    element = elements[0]
                                    try:
                                        logger.info(f"Using first element of type {control_type}: {element.window_text()}")
                                    except:
                                        logger.info(f"Using first element of type {control_type}")
                        except Exception as e:
                            logger.info(f"Could not find elements by control type {control_type}: {e}")
                    
                    # Last resort: try to find any element with the name
                    if not element and name:
                        try:
                            # Search more broadly for elements with the name
                            all_children = target_window.children()
                            for child in all_children:
                                try:
                                    if hasattr(child, 'window_text'):
                                        child_text = child.window_text()
                                        if child_text and name.lower() in child_text.lower():
                                            element = child
                                            logger.info(f"Found element by name in any type: {child_text}")
                                            break
                                except:
                                    continue
                        except Exception as e:
                            logger.info(f"Could not search all children: {e}")
                    
                    if element:
                        # Get the element's bounding rectangle and click at its center
                        try:
                            rect = element.rectangle()
                            center_x = (rect.left + rect.right) // 2
                            center_y = (rect.top + rect.bottom) // 2
                            
                            logger.info(f"Clicking at element center: ({center_x}, {center_y})")
                            pyautogui.click(center_x, center_y, button=button)
                            return True
                            
                        except Exception as e:
                            logger.warning(f"Could not get element rectangle: {e}")
                            # Fallback: try to click the element directly
                            try:
                                element.click_input(button=button)
                                logger.info("Clicked element using UIA click_input")
                                return True
                            except Exception as click_e:
                                logger.warning(f"Could not click element directly: {click_e}")
                    else:
                        logger.warning("Could not find target element")
                else:
                    logger.warning("Could not find target window")
                
            except ImportError:
                logger.warning("pywinauto not available for UIA element detection")
            except Exception as e:
                logger.warning(f"UIA element detection failed: {e}")
            
            return False
            
        except Exception as e:
            logger.error(f"UIA element detection failed: {e}")
            return False
    
    def set_variable(self, name: str, value: Any) -> None:
        """
        Set a variable for use in scripts.
        
        Args:
            name: Variable name
            value: Variable value
        """
        self.variables[name] = value
        logger.info(f"Set variable {name} = {value}")
    
    def get_variable(self, name: str) -> Any:
        """
        Get a variable value.
        
        Args:
            name: Variable name
            
        Returns:
            Variable value or None if not found
        """
        return self.variables.get(name)
    
    def run_script(self, script: Union[str, Dict[str, Any]]) -> bool:
        """
        Execute a JSON automation script.
        
        Args:
            script: JSON string or dictionary containing the script
            
        Returns:
            bool: True if script executed successfully, False otherwise
        """
        try:
            # Parse script if it's a string
            if isinstance(script, str):
                script_data = json.loads(script)
            else:
                script_data = script
            
            # Validate script structure
            if not isinstance(script_data, dict):
                logger.error("Script must be a dictionary")
                return False
            
            actions = script_data.get('actions', [])
            if not actions:
                logger.error("No actions found in script")
                return False
            
            logger.info(f"Executing script with {len(actions)} actions")
            
            # Execute each action in sequence
            for i, action in enumerate(actions):
                action_type = action.get('type')
                if not action_type:
                    logger.error(f"Action {i+1} missing 'type' field")
                    continue
                
                logger.info(f"Executing action {i+1}: {action_type}")
                
                # Execute the action based on its type
                success = self._execute_action(action)
                
                if not success:
                    logger.error(f"Action {i+1} ({action_type}) failed")
                    if action.get('continue_on_failure', False):
                        logger.warning("Continuing despite failure")
                    else:
                        logger.error("Stopping script execution due to failure")
                        return False
                
                # Add delay between actions if specified
                delay = action.get('delay', 0)
                if delay > 0:
                    logger.info(f"Waiting {delay} seconds before next action")
                    time.sleep(delay)
            
            logger.info("Script execution completed successfully")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON script: {e}")
            return False
        except Exception as e:
            logger.error(f"Script execution failed: {e}")
            return False
    
    def _execute_action(self, action: Dict[str, Any]) -> bool:
        """
        Execute a single action.
        
        Args:
            action: Action dictionary
            
        Returns:
            bool: True if successful, False otherwise
        """
        action_type = action.get('type')
        
        if action_type == 'start_process':
            return self.start_process(
                action['target'],
                app=action.get('app', 'default')
            )
        
        elif action_type == 'wait_for':
            return self.wait_for(
                action['condition'],
                timeout=action.get('timeout'),
                **{k: v for k, v in action.items() if k not in ['type', 'condition', 'timeout']}
            )
        
        elif action_type == 'type_text':
            return self.type_text(
                action['text'],
                **{k: v for k, v in action.items() if k not in ['type', 'text']}
            )
        
        elif action_type == 'click':
            return self.click(
                action['target'],
                **{k: v for k, v in action.items() if k not in ['type', 'target']}
            )
        
        elif action_type == 'set_variable':
            self.set_variable(action['name'], action['value'])
            return True
        
        elif action_type == 'wait':
            duration = action.get('duration', 0)
            if duration > 0:
                # Simple delay
                time.sleep(duration)
                return True
            else:
                # Wait for human input (for sensitive data like passwords)
                prompt = action.get('prompt', 'Press Enter to continue...')
                input(f"⏸️  {prompt}")
                return True
        
        else:
            logger.error(f"Unknown action type: {action_type}")
            return False


def main():
    """
    Main function to demonstrate the automation engine.
    """
    print("🤖 OkBot FlaUI Automation Engine")
    print("=" * 40)
    
    # Create automation engine
    engine = AutomationEngine()
    
    # Example script: Open Notepad and type some text
    example_script = {
        "description": "Simple Notepad automation example",
        "actions": [
            {
                "type": "start_process",
                "target": "notepad",
                "app_path": "notepad.exe",
                "description": "Open Notepad"
            },
            {
                "type": "wait",
                "duration": 2,
                "description": "Wait for Notepad to load"
            },
            {
                "type": "type_text",
                "text": "Hello, this is OkBot typing!",
                "delay": 0.05,
                "description": "Type greeting message"
            },
            {
                "type": "wait",
                "duration": 1,
                "description": "Pause to show result"
            }
        ]
    }

    script_path = Path(__file__).parent / "example_scripts" / "blackboard_simple_example.json"
    with open(script_path, "r") as f:
        example_script = json.load(f)
    
    # Execute the script
    print("\n📝 Running example script...")
    success = engine.run_script(example_script)
    
    if success:
        print("✅ Script executed successfully!")
    else:
        print("❌ Script execution failed!")
    
    print("\n🎯 Ready for automation tasks!")


if __name__ == "__main__":
    main()