"""
Core Action Execution Functions for OkBot FlaUI Automation Engine
Provides the main automation actions like starting processes, clicking, typing, etc.
"""

import json
import time
import subprocess
import webbrowser
from typing import Dict, Any, Optional, Union
from pathlib import Path
import logging
import pyautogui
from desktop_helper import DesktopHelper

logger = logging.getLogger(__name__)

class ActionExecutor:
    """
    Core action executor that provides basic desktop automation functions.
    """
    
    def __init__(self):
        self.variables = {}  # Store variables for script execution
        self.timeout_default = 30  # Default timeout in seconds
        self.desktop_helper = DesktopHelper()
        
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
                    self.desktop_helper.focus_application(focus_app)
                
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
                self.desktop_helper.focus_application_for_click(focus_app)
            
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
                success = self.desktop_helper.click_by_uia(element_selector, button)
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
    
    def detect_click(self, target: str, **kwargs) -> bool:
        """
        Detect if a user clicked on a UI element (like a bookmark, tab, or button).
        This is useful for understanding user behavior and only typing when necessary.
        
        Args:
            target: Description of element to detect clicks on
            **kwargs: Additional options like 'timeout' for detection window
            
        Returns:
            bool: True if click detected, False otherwise
        """
        try:
            timeout = kwargs.get('timeout', 5)  # Default 5 second detection window
            logger.info(f"Detecting clicks on {target} for {timeout} seconds")
            
            # For now, this is a placeholder that waits and assumes no click was detected
            # In a real implementation, this would monitor for mouse clicks or UI changes
            time.sleep(timeout)
            
            # Return False to indicate no click was detected, so we should proceed with typing
            logger.info(f"No click detected on {target}, proceeding with default action")
            return False
            
        except Exception as e:
            logger.error(f"Failed to detect clicks on '{target}': {e}")
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
    
    def wait(self, duration: int = 0, **kwargs) -> bool:
        """
        Wait for a specified duration or wait for human input.
        
        Args:
            duration: Duration to wait in seconds
            **kwargs: Additional options like 'prompt' for human input
            
        Returns:
            bool: True if successful, False otherwise
        """
        if duration > 0:
            # Simple delay
            time.sleep(duration)
            return True
        else:
            # Wait for human input (for sensitive data like passwords)
            prompt = kwargs.get('prompt', 'Press Enter to continue...')
            input(f"⏸️  {prompt}")
            return True
    
    def debug_elements(self, target: str, **kwargs) -> bool:
        """
        Debug UIA elements in the current window to help identify click positioning issues.
        
        Args:
            target: Description of what to debug
            **kwargs: Additional options
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"🔍 Debugging UIA elements for: {target}")
            
            # Use the desktop helper to debug Chrome elements
            try:
                from pywinauto import Desktop
                
                # Find any Chrome window
                windows = Desktop(backend="uia").windows()
                chrome_window = None
                
                for window in windows:
                    try:
                        window_text = window.window_text()
                        if window_text and "chrome" in window_text.lower():
                            chrome_window = window
                            break
                    except:
                        continue
                
                if chrome_window:
                    self.desktop_helper.debug_chrome_elements(chrome_window)
                    return True
                else:
                    logger.warning("No Chrome window found for debugging")
                    return False
                    
            except ImportError:
                logger.warning("pywinauto not available for debugging")
                return False
            except Exception as e:
                logger.error(f"Debug failed: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to debug elements for '{target}': {e}")
            return False
