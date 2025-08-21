"""
OpenAI API Client for JSON Schema Generation
"""

import os
import json
from typing import Dict, Any, Optional
import openai
from openai import OpenAI

def run_request(
    prompt: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.1,
    max_tokens: int = 4000,
    system_message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Make a request to OpenAI API to generate a JSON schema.
    
    Args:
        prompt (str): The main prompt containing the UIA listener data
        model (str): OpenAI model to use (default: gpt-4o-mini)
        temperature (float): Creativity level (0.0 = focused, 1.0 = creative)
        max_tokens (int): Maximum tokens for the response
        system_message (str, optional): Additional system instructions
    
    Returns:
        Dict[str, Any]: OpenAI API response
        
    Raises:
        ValueError: If OPENAI_API_KEY environment variable is not set
        Exception: For other API errors
    """
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Prepare messages
    messages = []
    
    # Add system message if provided
    if system_message:
        messages.append({
            "role": "system",
            "content": system_message
        })
    
    # Add user message with the prompt
    messages.append({
        "role": "user",
        "content": prompt
    })
    
    try:
        # Make the API call
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Extract the response content
        content = response.choices[0].message.content
        
        return {
            "success": True,
            "content": content,
            "model": model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            "raw_response": response
        }
        
    except openai.APIError as e:
        return {
            "success": False,
            "error": f"OpenAI API error: {str(e)}",
            "error_type": "api_error"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_type": "general_error"
        }

def extract_json_schema(response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract JSON schema from OpenAI response.
    
    Args:
        response (Dict[str, Any]): Response from run_request function
        
    Returns:
        Optional[Dict[str, Any]]: Parsed JSON schema or None if extraction fails
    """
    if not response.get("success"):
        print(f"Error in response: {response.get('error')}")
        return None
    
    content = response.get("content", "")
    
    # Try to find JSON schema in the response
    # Look for content between <schema> tags
    if "<schema>" in content and "</schema>" in content:
        start = content.find("<schema>") + len("<schema>")
        end = content.find("</schema>")
        schema_text = content[start:end].strip()
        
        try:
            return json.loads(schema_text)
        except json.JSONDecodeError:
            print("Failed to parse JSON from schema tags")
    
    # If no schema tags, try to find JSON in the content
    try:
        # Look for JSON-like content
        lines = content.split('\n')
        json_start = None
        json_end = None
        
        for i, line in enumerate(lines):
            if line.strip().startswith('{'):
                json_start = i
                break
        
        if json_start is not None:
            for i in range(json_start, len(lines)):
                if lines[i].strip().endswith('}'):
                    json_end = i + 1
                    break
        
        if json_start is not None and json_end is not None:
            json_content = '\n'.join(lines[json_start:json_end])
            return json.loads(json_content)
            
    except (json.JSONDecodeError, IndexError):
        pass
    
    print("Could not extract JSON schema from response")
    return None

# Example usage
if __name__ == "__main__":
    # Test the function
    test_prompt = "Generate a simple JSON schema for a user object with name and email fields."
    
    try:
        response = run_request(test_prompt)
        if response.get("success"):
            print("Response received successfully!")
            print(f"Content: {response['content'][:200]}...")
            
            # Try to extract JSON schema
            schema = extract_json_schema(response)
            if schema:
                print(f"Extracted schema: {json.dumps(schema, indent=2)}")
        else:
            print(f"Error: {response.get('error')}")
    except Exception as e:
        print(f"Test failed: {e}")