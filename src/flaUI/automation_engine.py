"""
FlaUI Automation Engine for OkBot
Provides basic desktop automation functions and JSON script execution capabilities.
"""

import json
import time
from typing import Dict, Any, Union
from pathlib import Path
import logging
from automation_engine.actions import ActionExecutor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutomationEngine:
    """
    Core automation engine that provides basic desktop automation functions.
    """
    
    def __init__(self):
        self.action_executor = ActionExecutor()
        self.variables = self.action_executor.variables  # Reference to variables
    
    def start_process(self, target: str, **kwargs) -> bool:
        """Start a process or open a URL in an application."""
        return self.action_executor.start_process(target, **kwargs)
    
    def wait_for(self, condition: str, timeout=None, **kwargs) -> bool:
        """Wait for a condition to be met."""
        return self.action_executor.wait_for(condition, timeout, **kwargs)
    
    def type_text(self, text: str, **kwargs) -> bool:
        """Type text into the active application."""
        return self.action_executor.type_text(text, **kwargs)
    
    def click(self, target: str, **kwargs) -> bool:
        """Click on a UI element."""
        return self.action_executor.click(target, **kwargs)
    
    def set_variable(self, name: str, value: Any) -> None:
        """Set a variable for use in scripts."""
        self.action_executor.set_variable(name, value)
    
    def get_variable(self, name: str) -> Any:
        """Get a variable value."""
        return self.action_executor.get_variable(name)
    
    def wait(self, duration: int = 0, **kwargs) -> bool:
        """Wait for a specified duration or wait for human input."""
        return self.action_executor.wait(duration, **kwargs)
    
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
                **{k: v for k, v in action.items() if k not in ['type', 'target']}
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
            return self.wait(duration, **{k: v for k, v in action.items() if k not in ['type', 'duration']})
        
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
    
    # Load and execute the blackboard example script
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