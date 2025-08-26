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
            **kwargs: Additional options like 'delay' between characters
            
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
            
            try:
                # Set a small delay to prevent issues
                pyautogui.PAUSE = 0.01
                
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
            **kwargs: Additional options like 'button' (left/right/middle)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            button = kwargs.get('button', 'left')
            logger.info(f"Clicking {target} with {button} button")
            
            # For now, just log the action
            # In a real implementation, this would locate and click the element
            time.sleep(0.5)  # Simulate click delay
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to click '{target}': {e}")
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

    script_path = Path(__file__).parent / "example_scripts" / "notepad_example.json"
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