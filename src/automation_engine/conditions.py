import pygetwindow as gw
import pyautogui
import time
import pyperclip
import logging
from typing import Union, Dict, Any
import pywinauto as auto
import uiautomation as uia

logger = logging.getLogger(__name__)

class Conditions:
    @staticmethod
    def url_contains_or_is(expected_url: str) -> bool:
        # grab active window.
        browser_window = gw.getActiveWindow()
        
        # grab the url.
        try:
            # Ctrl+L focuses the address bar in most browsers
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.2)
            
            # Select all and copy
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.2)
            
            # Get URL from clipboard
            url = pyperclip.paste()
            
            # Press Escape to deselect
            pyautogui.press('escape')

            # check if the url contains the expected url.
            if expected_url in url:
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"Error getting URL: {e}")
            return False

    @staticmethod
    def uia_exists_or_not_exists(uia_element: Union[str, Dict[str, Any]], 
                            control_type: str = None, 
                            timeout: float = 1.0,
                            search_depth: int = 10) -> bool:
        """
        Check if specific text exists on the current screen.
        """
        try:
            # Get the desktop root element
            desktop = uia.GetRootControl()
            
            if not desktop:
                logger.debug("Could not get desktop root control")
                return False
            
            logger.info(f"Starting UIA search for: {uia_element}")
            
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    if isinstance(uia_element, str):
                        # Simple manual search through the tree
                        def search_tree(control, depth=0):
                            if depth > search_depth:
                                return None
                            try:
                                if control.Name == uia_element:
                                    return control
                                for child in control.GetChildren():
                                    result = search_tree(child, depth + 1)
                                    if result:
                                        return result
                            except Exception:
                                pass
                            return None
                        
                        element = search_tree(desktop)
                        
                        if element:
                            logger.info(f"Found UIA element: {uia_element}")
                            return True
                        
                    elif isinstance(uia_element, dict):
                        # Handle dict format...
                        pass
                            
                except Exception as e:
                    logger.debug(f"UIA search error: {e}")
                    pass
                
                time.sleep(0.1)
            
            logger.info(f"UIA element not found within {timeout}s: {uia_element}")
            return False
            
        except Exception as e:
            logger.error(f"UIA search failed: {e}")
            return False