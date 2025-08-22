"""
JSON Schema Generator for UIA Listener Data
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import sys

sys.path.append(str(Path(__file__).parent.parent))
from OpenAI.openai_client import run_request

JSON_SCHEMA_PROMPT = """
You are a senior QA automation engineer. From raw UIA listener events and examples,
produce a STRICT JSON Schema (Draft 2020-12) that validates an ARRAY of UIA events.

## Inputs
<bot_listener_data>
{bot_listener_data}
</bot_listener_data>

<listener_data_examples>
{listener_data_examples}
</listener_data_examples>

<format_templates>
{format_templates}
</format_templates>

## Objectives
- Infer a robust schema for UIA events that compiles under Draft 2020-12.
- Support common fields across all events and event-specific fields via conditional validation.
- Prefer strong typing where safe; keep flexible where inputs vary.

## Requirements
The following requirements MUST be reflected in the generated schema:

<schema_requirements>
{schema_requirements}
</schema_requirements>

## Deliverable
Return ONLY: {{"schema": {{...}}}}

"""

class UIA_Listener_Data:
    def __init__(self):
        script_dir = Path(__file__).parent
        self.model = "gpt-4o-mini"
        self.temperature = 0.1
        self.data = self.load_json(script_dir / "resources/uia_log.json")
        self.examples = self.load_json(script_dir / "resources/listener_data_examples.json")
        self.templates = self.load_text(script_dir / "resources/format_templates.md")
        self.schema_requirements = self.load_text(script_dir / "resources/schema_requirements.md")

    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {file_path} not found")
            return {}
        except json.JSONDecodeError:
            print(f"Warning: {file_path} contains invalid JSON")
            return {}

    @staticmethod
    def load_text(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: {file_path} not found")
            return ""

    @staticmethod
    def _escape_braces(s: str) -> str:
        return s.replace("{", "{{").replace("}", "}}")
    
    def generate_schema_prompt(self) -> Optional[Dict[str, Any]]:
        """
        Build the prompt and call the LLM. Expects run_request to return a dict like:
        {"success": bool, "prompt": str, "schema": dict} OR {"success": bool, "output_json": {...}}
        """
        try:
            prompt = JSON_SCHEMA_PROMPT.format (
            bot_listener_data=json.dumps(self.data, indent=2),
            listener_data_examples=json.dumps(self.examples, indent=2),
            format_templates=self.templates,
            schema_requirements=self._escape_braces(self.schema_requirements),
            )

            # Optional: avoid dumping giant prompt bodies to stdout
            print(f"Prompt built. Length: {len(prompt)} chars")

            result = run_request(
                prompt=prompt,
                model=self.model,
                temperature=self.temperature,
                max_tokens=4000,
            )
            
            # Save the result in a file (only if it's serializable)
            try:
                with open("result.json", "w") as f:
                    json.dump(result, f, indent=2, default=str)
                print("📄 Result saved to result.json")
            except (TypeError, ValueError) as e:
                print(f"⚠️ Could not save result to JSON: {e}")
                # Save as string representation instead
                with open("result.txt", "w") as f:
                    f.write(str(result))
                print("📄 Result saved to result.txt as string")
            
            return result
        except Exception as e:
            print(f"❌ Error calling OpenAI API: {e}")
            return None


def main():
    print("🚀 Starting JSON Schema Generation...")
    engine = UIA_Listener_Data()              # loads resources in __init__
    result = engine.generate_schema_prompt()  # calls the LLM

    if not result or not result.get("success"):
        print("❌ Process failed")
        if result and result.get("error"):
            print(f"Error: {result['error']}")
        return

    print("🎉 Success")
    
    # Extract and save the schema
    schema_obj = None
    
    # Try to extract schema from different possible locations in the result
    if isinstance(result.get("schema"), dict):
        schema_obj = result["schema"]
    elif isinstance(result.get("output_json"), dict):
        output = result["output_json"]
        if isinstance(output.get("schema"), dict):
            schema_obj = output["schema"]
    elif result.get("content"):
        # The schema might be in the content field as a JSON string
        content_str = result["content"]
        
        # Handle markdown code blocks if present
        if content_str.startswith("```") and content_str.endswith("```"):
            # Extract content between code blocks
            lines = content_str.split('\n')
            if len(lines) >= 3:
                # Skip first line (```json) and last line (```)
                json_content = '\n'.join(lines[1:-1])
                try:
                    content = json.loads(json_content)
                    if isinstance(content.get("schema"), dict):
                        schema_obj = content["schema"]
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"⚠️ Could not parse extracted JSON content: {e}")
                    print(f"Extracted content preview: {json_content[:200]}...")
        else:
            # Try to parse the content directly as JSON
            try:
                content = json.loads(content_str)
                if isinstance(content.get("schema"), dict):
                    schema_obj = content["schema"]
            except (json.JSONDecodeError, TypeError) as e:
                print(f"⚠️ Could not parse content as JSON: {e}")
                print(f"Content preview: {content_str[:200]}...")
    
    if schema_obj:
        # Save the schema to a file
        script_dir = Path(__file__).parent
        schema_file = script_dir / "resources/generated_schema.json"
        with open(schema_file, 'w', encoding='utf-8') as f:
            json.dump(schema_obj, f, indent=2)
        print(f"📋 Schema saved to: {schema_file}")
        
        # Show a preview
        preview = json.dumps(schema_obj, indent=2)
        print("\n📋 Schema Preview:")
        print(preview[:1000] + ("..." if len(preview) > 1000 else ""))
    else:
        print("❌ No schema was found in the result")
        print("Available keys in result:", list(result.keys()) if result else "None")
        if result and "output_json" in result:
            print("Available keys in output_json:", list(result["output_json"].keys()) if isinstance(result["output_json"], dict) else "Not a dict")
        if result and "content" in result:
            print("Content field contains:", type(result["content"]), "with length:", len(str(result["content"])))


if __name__ == "__main__":
    main()