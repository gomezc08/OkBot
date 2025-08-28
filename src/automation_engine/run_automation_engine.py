"""
FlaUI Automation Engine for OkBot
Provides basic desktop automation functions and JSON script execution capabilities.
"""

import json
import time
from typing import Dict, Any, Union, List
from pathlib import Path
import logging
from actions import ActionExecutor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RunAutomationEngine:
    """
    Core automation engine that provides basic desktop automation functions.
    """
    
    def __init__(self):
        self.action_executor = ActionExecutor()
        self.variables = self.action_executor.variables  # Reference to variables
    
    def run_script(self, script: Union[List[Dict[str, Any]], Dict[str, Any]]) -> bool:
        """
        Run a complete automation script.
        
        Args:
            script: Script data (list of actions or dict with 'actions' key)
            
        Returns:
            bool: True if all actions succeeded, False otherwise
        """
        # Handle different script formats
        if isinstance(script, dict):
            if "actions" in script:
                actions = script["actions"]
            else:
                logger.error("Script dictionary must contain 'actions' key")
                return False
        else:
            actions = script
        
        if not actions:
            logger.error("No actions found in script")
            return False
        
        logger.info(f"Executing script with {len(actions)} actions")
        
        success_count = 0
        for i, action in enumerate(actions, 1):
            logger.info(f"Executing action {i}: {action.get('type', 'unknown')}")
            
            success = self._execute_action(action)
            if success:
                success_count += 1
                logger.info(f"Action {i} completed successfully")
            else:
                logger.error(f"Action {i} failed")
                return False
            
            # Add grace period between actions (1 second)
            if i < len(actions):  # Don't wait after the last action
                logger.debug("Waiting 1 second before next action...")
                time.sleep(1)
        
        logger.info(f"Script completed: {success_count}/{len(actions)} actions succeeded")
        return True
    
    def _execute_action(self, action: Dict[str, Any]) -> bool:
        """
        Execute a single action using our new ActionExecutor.
        
        Args:
            action: Action dictionary
            
        Returns:
            bool: True if successful, False otherwise
        """
        action_type = action.get('type')
        
        try:
            if action_type == 'click':
                return self.action_executor.click(action)
            
            elif action_type == 'type_text':
                return self.action_executor.type_text(action)
            
            elif action_type == 'load':
                return self.action_executor.load(action)
            
            elif action_type == 'wait_user':
                return self.action_executor.wait_user_input(action)
            
            else:
                logger.error(f"Unknown action type: {action_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing action {action_type}: {e}")
            return False


def main():
    """
    Main function to demonstrate the automation engine.
    """
    print("🤖 OkBot FlaUI Automation Engine")
    print("=" * 40)
    
    # Create automation engine
    engine = RunAutomationEngine()
    
    # Load and execute the recorded Chrome activity script
    script_path = Path(__file__).parent / "example_scripts" / "recorded_chrome_activity_example.json"
    
    try:
        with open(script_path, "r") as f:
            example_script = json.load(f)
        
        # Execute the script
        print("\n📝 Running recorded Chrome activity script...")
        print(f"Script path: {script_path}")
        print(f"Number of actions: {len(example_script)}")
        
        success = engine.run_script(example_script)
        
        if success:
            print("✅ Script executed successfully!")
        else:
            print("❌ Script execution failed!")
            
    except FileNotFoundError:
        print(f"❌ Script file not found: {script_path}")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in script file: {e}")
    except Exception as e:
        print(f"❌ Error loading script: {e}")
    
    print("\n🎯 Ready for automation tasks!")


if __name__ == "__main__":
    main()