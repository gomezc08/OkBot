"""
Script Runner for OkBot Automation Engine
Loads and executes JSON automation scripts from files.
"""

import json
import sys
from pathlib import Path
from automation_engine import AutomationEngine

def load_script(script_path: str) -> dict:
    """
    Load a JSON script from a file.
    
    Args:
        script_path: Path to the JSON script file
        
    Returns:
        dict: The loaded script data
        
    Raises:
        FileNotFoundError: If the script file doesn't exist
        json.JSONDecodeError: If the JSON is invalid
    """
    script_file = Path(script_path)
    
    if not script_file.exists():
        raise FileNotFoundError(f"Script file not found: {script_path}")
    
    with open(script_file, 'r', encoding='utf-8') as f:
        script_data = json.load(f)
    
    return script_data

def run_script_file(script_path: str) -> bool:
    """
    Load and execute a script from a file.
    
    Args:
        script_path: Path to the JSON script file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load the script
        print(f"📁 Loading script: {script_path}")
        script_data = load_script(script_path)
        
        # Create automation engine
        engine = AutomationEngine()
        
        # Execute the script
        print(f"🚀 Executing script: {script_data.get('description', 'No description')}")
        success = engine.run_script(script_data)
        
        if success:
            print("✅ Script executed successfully!")
        else:
            print("❌ Script execution failed!")
        
        return success
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in script file: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def list_example_scripts():
    """List available example scripts."""
    script_dir = Path(__file__).parent / "example_scripts"
    
    if not script_dir.exists():
        print("❌ Example scripts directory not found")
        return
    
    print("📚 Available example scripts:")
    for script_file in script_dir.glob("*.json"):
        print(f"  - {script_file.name}")
    
    print(f"\n💡 Run a script with: python run_script.py <script_name.json>")

def main():
    """
    Main function to run scripts from command line.
    """
    print("🤖 OkBot Script Runner")
    print("=" * 30)
    
    if len(sys.argv) < 2:
        print("Usage: python run_script.py <script_file.json>")
        print("\nOr use one of the example scripts:")
        list_example_scripts()
        return
    
    script_path = sys.argv[1]
    
    # If just a filename is provided, try to find it in example_scripts
    if not Path(script_path).is_absolute() and not Path(script_path).exists():
        example_path = Path(__file__).parent / "example_scripts" / script_path
        if example_path.exists():
            script_path = str(example_path)
            print(f"📁 Found script in examples: {script_path}")
    
    # Run the script
    success = run_script_file(script_path)
    
    if success:
        print("\n🎉 Script completed successfully!")
    else:
        print("\n💥 Script execution failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
