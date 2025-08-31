"""
Core Action Execution Functions for OkBot FlaUI Automation Engine
Provides the main automation actions like clicking, typing, loading, and waiting for user input.
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
import requests
from urllib.parse import urlparse
from conditions import Conditions   

logger = logging.getLogger(__name__)

class ActionExecutor:
    """
    Core action executor that provides basic desktop automation functions.
    """
    
    def __init__(self):
        self.variables = {}  # Store variables for script execution
        self.timeout_default = 30  # Default timeout in seconds
    
    def click(self, data: Dict[str, Any]) -> bool:
        """
        Click action with fallback to coordinates.
        
        Schema:
        {
            "type": "click",
            "target": "GWU Profile Button",
            "button": "left",
            "element_selector": {
                "name": "Open GWU profile",
                "control_type": "Button",
                "class_name": "Chrome_WidgetWin_1",
                "process_name": "chrome",
                "ancestor_path": ["RootView", "ProfilePickerView"]
            },
            "coordinate_selector": {
                "coords": {
                    "x": 727,
                    "y": 673
                },
                "bbox": {
                    "left": 680,
                    "top": 640,
                    "right": 780,
                    "bottom": 705
                }
            },
            "description": "Click the GWU profile button"
        }
        """            
        target = data.get("target")
        button = data.get("button", "left")
        description = data.get("description", f"Click {target}")
        
        logger.info(f"Executing click action: {description}")
        
        # Try element-based clicking first (UIA)
        element_selector = data.get("element_selector")
        if element_selector:
            logger.info(f"Attempting UIA-based click on element: {element_selector.get('name', 'Unknown')}")
            # Here you would integrate with your UIA listener for element-based clicking
            # For now, we'll simulate success and fall back to coordinates
            success = False  # Placeholder - implement actual UIA clicking
            
            if success:
                logger.info("UIA-based click successful")
                return True
            else:
                logger.info("UIA-based click failed, falling back to coordinates")
        
        # Fall back to coordinate-based clicking
        coordinate_selector = data.get("coordinate_selector")
        if coordinate_selector:
            coords = coordinate_selector.get("coords")
            if coords and "x" in coords and "y" in coords:
                x, y = coords["x"], coords["y"]
                logger.info(f"Clicking at coordinates: ({x}, {y})")
                
                try:
                    pyautogui.click(x, y, button=button)
                    logger.info("Coordinate-based click successful")
                    return True
                except Exception as e:
                    logger.error(f"Coordinate-based click failed: {e}")
                    return False
        
        logger.error("No valid click target found (neither element selector nor coordinates)")
        return False
    
    def type_text(self, data: Dict[str, Any]) -> bool:
        """
        Type text action.
        
        Schema:
        {
            "type": "type_text",
            "text": "my.email@gwu.edu",
            "description": "Enter email in focused field"
        }
        """            
        text = data.get("text")
        description = data.get("description", f"Type text: {text[:20]}...")
        
        logger.info(f"Executing type_text action: {description}")
        
        try:
            pyautogui.typewrite(text)
            logger.info("Text typing successful")
            return True
        except Exception as e:
            logger.error(f"Text typing failed: {e}")
            return False
    
    def load(self, data: Dict[str, Any]) -> bool:
        """
        Load action - wait for conditions to be met.
        """
        description = data.get("description")
        condition = data.get("condition")
        timeout = data.get("timeout", self.timeout_default)
        condition_type = condition["type"]
        condition_value = condition["value"]

        logger.info(f"Executing load action: {description}")
        logger.info(f"Waiting for condition: {condition_type} = {condition_value}")

        if condition_type == "url.contains" or condition_type == "url.is":
            logger.info(f"Waiting until URL contains: {condition_value}")
            start_time = time.time()
            while time.time() - start_time < timeout:
                if Conditions.url_contains_or_is(condition_value):
                    logger.info("URL condition met successfully")
                    return True
                time.sleep(0.5)
            logger.warning(f"URL condition not met within {timeout}s")
            return False

        if condition_type == "uia.exists" or condition_type == "uia.not_exists":
            logger.info(f"Waiting until UIA element exists: {condition_value}")
            start_time = time.time()
            while time.time() - start_time < timeout:
                if Conditions.uia_exists_or_not_exists(condition_value):
                    logger.info("UIA condition met successfully")
                    return True
                time.sleep(0.5)
            logger.warning(f"UIA condition not met within {timeout}s")
            return False

        logger.error(f"Unknown condition type: {condition_type}")
        return False

    
    def wait_user_input(self, data: Dict[str, Any]) -> bool:
        """
        Wait for user input action.
        
        Schema:
        {
            "type": "wait_user",
            "description": "Wait for user to complete login and reach inbox",
            "condition": {
                "type": "url.contains",
                "value": "mail.google.com/mail/u/0/#inbox"
            },
            "timeout": 120
        }
        """
            
        description = data.get("description")
        condition = data.get("condition")
        timeout = data.get("timeout", self.timeout_default)
