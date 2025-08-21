"""
JSON Schema Generator for UIA Listener Data
"""

import json
from pathlib import Path
from typing import Dict, Any
import sys

sys.path.append(str(Path(__file__).parent.parent))
from OpenAI.openai_client import run_request

JSON_SCHEMA_PROMPT = """
You are a helpful assistant that generates a JSON schema from raw UIA listener data using a standard JSON schema format.

## Input Data

### Bot Listener Data (Raw Events)
This is the raw UIA log data that was recorded during UI automation:

<bot_listener_data>
{bot_listener_data}
</bot_listener_data>

### Listener Data Examples
Here are some examples of the Json schema structure to help you understand the format:

<listener_data_examples>
{listener_data_examples}
</listener_data_examples>

### Format Templates & Keywords
Important formats, patterns, and keywords to track in the schema:

<format_templates>
{format_templates}
</format_templates>

## Task
Please generate a comprehensive JSON schema that can be used to validate the UIA listener events.

## Requirements
- The schema should be in standard JSON Schema format (draft 2020-12)
- Include all major event types and their properties
- Define required vs optional fields
- Add descriptions for complex fields
- Consider validation rules for data types and formats
- Handle nested structures appropriately
"""

class UIA_Listener_Data:
    def __init__(self):
        self.model = "gpt-5o-mini"
        self.temperature = 0.1
        self.data = UIA_Listener_Data.load_data("resources/uia_log.json")
        self.examples = UIA_Listener_Data.load_data("resources/listener_data_examples.json")
        self.templates = UIA_Listener_Data.load_data("resources/format_templates.md")
    
    @staticmethod
    def load_data(file_path: str) -> Dict[str, Any]:
        """Load the raw UIA log data from the main log file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {file_path} not found")
            return {}
        except json.JSONDecodeError:
            print(f"Warning: {file_path} contains invalid JSON")
            return {}

def generate_schema_prompt(self) -> Dict[str, Any]:
    """
    Generate a JSON schema prompt and optionally call OpenAI LLM to generate the schema.
    
    Returns:
        Dict[str, Any]: Contains prompt, data, and optionally the generated schema
    """        
    try: 
        prompt = JSON_SCHEMA_PROMPT.format(
            bot_listener_data=json.dumps(self.data, indent=2),
            listener_data_examples=json.dumps(self.examples, indent=2),
            format_templates=self.templates,
        )

        return run_request(
            prompt=prompt,
            model=self.model,
            temperature=self.temperature,
            max_tokens=4000
        )

    except Exception as e:
        print(f"❌ Error calling OpenAI API: {e}")
        return None

def main():
    """Main function to demonstrate the schema generation."""
    print("🚀 Starting JSON Schema Generation...")
    
    # Generate schema using the combined function
    result = generate_schema_prompt()
    
    if result["success"]:
        print("\n🎉 Process completed successfully!")
        
        # Save the prompt to a file
        prompt_file = "resources/generated_prompt.txt"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(result["prompt"])
        print(f"📄 Prompt saved to: {prompt_file}")
        
        # If schema was generated, save it too
        if "schema" in result and result["schema"]:
            schema_file = "resources/generated_schema.json"
            with open(schema_file, 'w', encoding='utf-8') as f:
                json.dump(result["schema"], f, indent=2)
            print(f"📋 Schema saved to: {schema_file}")
            
            # Display a preview of the schema
            print("\n📋 Schema Preview:")
            schema_preview = json.dumps(result["schema"], indent=2)
            if len(schema_preview) > 1000:
                print(schema_preview[:1000] + "...")
            else:
                print(schema_preview)
        else:
            print("\n❌ No schema was generated")
            
    else:
        print("\n❌ Process failed")
        if "error" in result:
            print(f"Error: {result['error']}")

if __name__ == "__main__":
    main()