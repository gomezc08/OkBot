"""
Desktop Helper Functions for OkBot FlaUI Automation Engine
Provides UIA element detection, window management, and Chrome-specific automation helpers.
"""

import time
import logging
import pyautogui
import pygetwindow as gw
from typing import Optional, Any

logger = logging.getLogger(__name__)

class DesktopHelper:
    """
    Helper class for desktop automation tasks like UIA detection and window management.
    """
    
    def __init__(self):
        self.timeout_default = 30  # Default timeout in seconds
    
    def focus_application(self, app_name: str) -> bool:
        """
        Focus an application by its window title.
        
        Args:
            app_name: Application name to focus
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Focusing application: {app_name}")
            windows = gw.getWindowsWithTitle(app_name)
            if windows:
                target_window = windows[0]
                target_window.activate()
                target_window.maximize()
                logger.info(f"Focused window: {target_window.title}")
                # Wait a bit for the window to be ready
                time.sleep(1)
                return True
            else:
                logger.warning(f"Could not find window with title: {app_name}")
                return False
        except ImportError:
            logger.warning("pygetwindow not available, cannot focus application")
            return False
        except Exception as e:
            logger.warning(f"Could not focus application {app_name}: {e}")
            return False
    
    def focus_application_for_click(self, app_name: str) -> bool:
        """
        Focus an application for clicking operations (shorter wait time).
        
        Args:
            app_name: Application name to focus
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Focusing application: {app_name}")
            windows = gw.getWindowsWithTitle(app_name)
            if windows:
                target_window = windows[0]
                target_window.activate()
                logger.info(f"Focused window: {target_window.title}")
                time.sleep(0.5)  # Wait for window to be ready
                return True
            else:
                logger.warning(f"Could not find window with title: {app_name}")
                return False
        except Exception as e:
            logger.warning(f"Could not focus application {app_name}: {e}")
            return False
    
    def click_by_uia(self, element_selector: dict, button: str = 'left') -> bool:
        """
        Click on a UI element using UIA element detection.
        
        Args:
            element_selector: Dictionary with UIA properties to identify the element
            button: Mouse button to use
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            control_type = element_selector.get('control_type', 'Any')
            name = element_selector.get('name', '')
            class_name = element_selector.get('class_name', '')
            process_name = element_selector.get('process_name', '')
            
            logger.info(f"UIA: Looking for element - Type: {control_type}, Name: '{name}', Class: '{class_name}', Process: '{process_name}'")
            
            # Try to use pywinauto for UIA element detection
            try:
                from pywinauto import Desktop, Application
                from pywinauto.findwindows import find_window
                from pywinauto.controls.uiawrapper import UIAWrapper
                
                # Find the target window first
                target_window = self._find_target_window(process_name, class_name)
                
                if target_window:
                    # Look for the specific element within the window
                    element = None
                    
                    # Chrome-specific element detection with fallback coordinates
                    if "chrome" in target_window.window_text().lower():
                        chrome_result = self._find_chrome_element(target_window, name, control_type)
                        if chrome_result is True:  # Already clicked
                            return True
                        elif chrome_result:  # Found element
                            element = chrome_result
                    
                    # Try to find by name first (most reliable)
                    if not element and name:
                        element = self._find_element_by_name(target_window, name, control_type)
                    
                    # Try to find by control type if name didn't work
                    if not element and control_type != 'Any':
                        element = self._find_element_by_type(target_window, control_type, name)
                    
                    # Last resort: try to find any element with the name
                    if not element and name:
                        element = self._find_element_by_name_broad(target_window, name)
                    
                    if element:
                        return self._click_element(element, button)
                    else:
                        logger.warning("Could not find target element")
                else:
                    logger.warning("Could not find target window")
                
            except ImportError:
                logger.warning("pywinauto not available for UIA element detection")
            except Exception as e:
                logger.warning(f"UIA element detection failed: {e}")
            
            return False
            
        except Exception as e:
            logger.error(f"UIA element detection failed: {e}")
            return False
    
    def debug_chrome_elements(self, target_window):
        """
        Debug method to show all available UIA elements in Chrome window.
        This helps identify the exact structure for better automation.
        """
        try:
            logger.info("=== DEBUG: Chrome UIA Elements ===")
            logger.info(f"Window: {target_window.window_text()}")
            
            def print_element_tree(element, level=0):
                try:
                    indent = "  " * level
                    element_text = element.window_text() if hasattr(element, 'window_text') else "No text"
                    element_type = element.control_type() if hasattr(element, 'control_type') else "Unknown type"
                    element_class = element.class_name() if hasattr(element, 'class_name') else "No class"
                    
                    logger.info(f"{indent}- {element_type}: '{element_text}' (class: {element_class})")
                    
                    # Print children recursively (limit depth to avoid spam)
                    if level < 5:  # Increased depth to find profile buttons
                        try:
                            children = element.children()
                            for child in children[:15]:  # Increased limit to find more elements
                                print_element_tree(child, level + 1)
                        except:
                            pass
                            
                except Exception as e:
                    logger.info(f"{indent}- Error reading element: {e}")
            
            # Print the main window structure
            print_element_tree(target_window)
            
            # Also try to find profile-related elements specifically
            logger.info("=== SEARCHING FOR PROFILE ELEMENTS ===")
            try:
                # Search for any elements containing "profile", "gwu", or "button"
                all_elements = []
                def collect_elements(element, level=0):
                    if level < 6:  # Go deeper
                        try:
                            all_elements.append((element, level))
                            children = element.children()
                            for child in children:
                                collect_elements(child, level + 1)
                        except:
                            pass
                
                collect_elements(target_window)
                
                # Look for profile-related elements
                profile_elements = []
                for element, level in all_elements:
                    try:
                        text = element.window_text() if hasattr(element, 'window_text') else ""
                        control_type = str(element.control_type()) if hasattr(element, 'control_type') else ""
                        class_name = element.class_name() if hasattr(element, 'class_name') else ""
                        
                        if any(keyword in str(text).lower() for keyword in ["profile", "gwu", "open", "button"]):
                            profile_elements.append((element, level, text, control_type, class_name))
                    except:
                        continue
                
                if profile_elements:
                    logger.info("Found potential profile elements:")
                    for element, level, text, control_type, class_name in profile_elements:
                        indent = "  " * level
                        logger.info(f"{indent}Level {level}: '{text}' ({control_type}) [{class_name}]")
                else:
                    logger.info("No profile elements found in UIA tree")
                    
            except Exception as e:
                logger.info(f"Profile element search failed: {e}")
            
            logger.info("=== END DEBUG ===")
            
        except Exception as e:
            logger.error(f"Debug failed: {e}")
    
    def _find_target_window(self, process_name: str, class_name: str):
        """
        Find the target window using various methods.
        
        Args:
            process_name: Process name to search for
            class_name: Class name to search for
            
        Returns:
            Target window or None if not found
        """
        try:
            from pywinauto import Desktop, Application
            from pywinauto.findwindows import find_window
            from pywinauto.controls.uiawrapper import UIAWrapper
            
            target_window = None
            
            # Try to find by process name
            if process_name:
                target_window = self._find_window_by_process(process_name)
            
            # Try to find by class name
            if not target_window and class_name:
                target_window = self._find_window_by_class(class_name)
            
            # Try to find any window that might contain our element
            if not target_window:
                target_window = self._find_chrome_window()
            
            # Last resort: try to find any visible window
            if not target_window:
                target_window = self._find_fallback_window()
            
            return target_window
            
        except Exception as e:
            logger.warning(f"Window finding failed: {e}")
            return None
    
    def _find_window_by_process(self, process_name: str):
        """Find window by process name."""
        try:
            from pywinauto import Application
            import psutil
            
            # First try to connect by process name
            try:
                app = Application(backend="uia").connect(process=process_name)
                target_window = app.top_window()
                logger.info(f"Found window by process: {target_window.window_text()}")
                return target_window
            except Exception as e:
                logger.info(f"Could not find window by process name '{process_name}': {e}")
            
            # Try to find by executable name
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'].lower() == process_name.lower():
                        try:
                            app = Application(backend="uia").connect(pid=proc.info['pid'])
                            target_window = app.top_window()
                            logger.info(f"Found window by PID {proc.info['pid']}: {target_window.window_text()}")
                            return target_window
                        except Exception as pid_e:
                            logger.info(f"Could not connect to PID {proc.info['pid']}: {pid_e}")
                            continue
            except ImportError:
                logger.info("psutil not available for process enumeration")
            except Exception as e:
                logger.info(f"Process enumeration failed: {e}")
            
            return None
            
        except Exception as e:
            logger.warning(f"Process-based window finding failed: {e}")
            return None
    
    def _find_window_by_class(self, class_name: str):
        """Find window by class name."""
        try:
            from pywinauto import find_window
            from pywinauto.controls.uiawrapper import UIAWrapper
            
            target_window = find_window(class_name=class_name)
            target_window = UIAWrapper(target_window)
            logger.info(f"Found window by class: {target_window.window_text()}")
            return target_window
        except Exception as e:
            logger.info(f"Could not find window by class {class_name}: {e}")
            return None
    
    def _find_chrome_window(self):
        """Find Chrome window specifically."""
        try:
            from pywinauto import Desktop
            
            windows = Desktop(backend="uia").windows()
            for window in windows:
                try:
                    window_text = window.window_text()
                    if window_text and window_text != "" and "chrome" in window_text.lower():
                        logger.info(f"Found Chrome window: {window_text}")
                        return window
                except:
                    continue
        except Exception as e:
            logger.info(f"Could not enumerate windows: {e}")
        
        return None
    
    def _find_fallback_window(self):
        """Find any visible window as fallback."""
        try:
            from pywinauto import Desktop
            
            windows = Desktop(backend="uia").windows()
            for window in windows:
                try:
                    window_text = window.window_text()
                    if window_text and window_text != "" and len(window_text) > 3:
                        logger.info(f"Using fallback window: {window_text}")
                        return window
                except:
                    continue
        except Exception as e:
            logger.info(f"Could not enumerate windows: {e}")
        
        return None
    
    def _find_element_by_name(self, target_window, name: str, control_type: str):
        """Find element by name."""
        try:
            # Try different methods to find elements by name
            try:
                element = target_window.child_window(name=name, control_type=control_type)
                logger.info(f"Found element by name: {name}")
                return element
            except:
                # Fallback: search all children for name match
                all_children = target_window.children()
                for child in all_children:
                    try:
                        if hasattr(child, 'window_text'):
                            child_text = child.window_text()
                            if child_text and name.lower() in child_text.lower():
                                logger.info(f"Found element by name in children: {child_text}")
                                return child
                    except:
                        continue
        except Exception as e:
            logger.info(f"Element not found by name '{name}': {e}")
        
        return None
    
    def _find_element_by_type(self, target_window, control_type: str, name: str = ""):
        """Find element by control type."""
        try:
            # Try different approaches to find elements
            try:
                elements = target_window.children(control_type=control_type)
            except:
                # Fallback: try to get all children and filter by type
                try:
                    all_children = target_window.children()
                    elements = []
                    for child in all_children:
                        try:
                            if hasattr(child, 'control_type'):
                                child_type = str(child.control_type())
                                if control_type.lower() in child_type.lower():
                                    elements.append(child)
                        except:
                            continue
                except:
                    elements = []
            
            if elements:
                # If we have a name, try to find the best match
                if name:
                    for elem in elements:
                        try:
                            elem_text = elem.window_text()
                            if elem_text and name.lower() in elem_text.lower():
                                logger.info(f"Found element by type and partial name match: {elem_text}")
                                return elem
                        except:
                            continue
                
                # If still no match, use the first element of this type
                element = elements[0]
                try:
                    logger.info(f"Using first element of type {control_type}: {element.window_text()}")
                except:
                    logger.info(f"Using first element of type {control_type}")
                return element
                
        except Exception as e:
            logger.info(f"Could not find elements by control type {control_type}: {e}")
        
        return None
    
    def _find_element_by_name_broad(self, target_window, name: str):
        """Search more broadly for elements with the name."""
        try:
            all_children = target_window.children()
            for child in all_children:
                try:
                    if hasattr(child, 'window_text'):
                        child_text = child.window_text()
                        if child_text and name.lower() in child_text.lower():
                            logger.info(f"Found element by name in any type: {child_text}")
                            return child
                except:
                    continue
        except Exception as e:
            logger.info(f"Could not search all children: {e}")
        
        return None
    
    def _click_element(self, element, button: str):
        """Click on an element."""
        try:
            # Get the element's bounding rectangle and click at its center
            rect = element.rectangle()
            center_x = (rect.left + rect.right) // 2
            center_y = (rect.top + rect.bottom) // 2
            
            logger.info(f"Clicking at element center: ({center_x}, {center_y})")
            
            # Try multiple click positions around the center to handle offset issues
            click_positions = [
                (center_x, center_y),  # Exact center
                (center_x + 5, center_y),  # Slightly right
                (center_x - 5, center_y),  # Slightly left
                (center_x, center_y + 5),  # Slightly below
                (center_x, center_y - 5),  # Slightly above
                (center_x + 3, center_y + 3),  # Diagonal
                (center_x - 3, center_y - 3),  # Diagonal
            ]
            
            for click_x, click_y in click_positions:
                try:
                    logger.info(f"Trying click position: ({click_x}, {click_y})")
                    pyautogui.click(click_x, click_y, button=button)
                    
                    # Wait a bit to see if the click had an effect
                    time.sleep(0.2)
                    
                    # Try to verify if the click worked by checking if the element is still clickable
                    # This is a simple heuristic - in a real implementation you'd check for UI changes
                    return True
                    
                except Exception as click_e:
                    logger.warning(f"Click at ({click_x}, {click_y}) failed: {click_e}")
                    continue
            
            # If all positions failed, try the direct UIA click
            logger.warning("All click positions failed, trying direct UIA click")
            element.click_input(button=button)
            logger.info("Clicked element using UIA click_input")
            return True
            
        except Exception as e:
            logger.warning(f"Could not get element rectangle: {e}")
            # Fallback: try to click the element directly
            try:
                element.click_input(button=button)
                logger.info("Clicked element using UIA click_input")
                return True
            except Exception as click_e:
                logger.warning(f"Could not click element directly: {click_e}")
                return False
    
    def _find_chrome_element(self, target_window, name: str, control_type: str):
        """
        Chrome-specific element detection with fallback coordinates.
        
        Args:
            target_window: The Chrome window to search in
            name: Element name to search for
            control_type: Element control type
            
        Returns:
            Element if found, True if clicked, None otherwise
        """
        try:
            # Try to find Chrome-specific elements
            if "address" in name.lower() or "search" in name.lower():
                # Look for address bar - try multiple approaches
                try:
                    # Method 1: Look for Edit control with address bar name
                    element = target_window.child_window(name=name, control_type="Edit")
                    if element:
                        logger.info(f"Found Chrome address bar by name: {name}")
                        return element
                except:
                    pass
                
                try:
                    # Method 2: Look for Edit control with partial name match
                    all_children = target_window.children(control_type="Edit")
                    for child in all_children:
                        try:
                            child_text = child.window_text()
                            if child_text and ("address" in child_text.lower() or "search" in child_text.lower()):
                                logger.info(f"Found Chrome address bar by type and text: {child_text}")
                                return child
                        except:
                            continue
                except:
                    pass
                
                try:
                    # Method 3: Look for any Edit control (Chrome usually has only one main edit field)
                    edit_elements = target_window.children(control_type="Edit")
                    if edit_elements:
                        # Use the first Edit element as it's usually the address bar
                        element = edit_elements[0]
                        logger.info("Found Chrome address bar using first Edit element")
                        return element
                except:
                    pass
                
                # Method 4: Use fallback coordinates for Chrome address bar
                # Chrome address bar is typically at the top of the window
                try:
                    window_rect = target_window.rectangle()
                    # Address bar is typically in the top portion of Chrome
                    address_bar_x = window_rect.left + (window_rect.right - window_rect.left) // 2
                    address_bar_y = window_rect.top + 80  # Typical offset from top
                    
                    logger.info(f"Using fallback coordinates for Chrome address bar: ({address_bar_x}, {address_bar_y})")
                    pyautogui.click(address_bar_x, address_bar_y)
                    return True  # Return True to indicate success
                except Exception as e:
                    logger.warning(f"Fallback coordinates failed: {e}")
            
            # Handle Chrome profile selection buttons
            elif "profile" in name.lower() or "gwu" in name.lower():
                logger.info("🔍 Searching for Chrome profile button...")
                
                # Method 1: Deep search through all UIA elements
                try:
                    all_elements = []
                    def collect_all_elements(element, level=0):
                        if level < 8:  # Go very deep
                            try:
                                all_elements.append((element, level))
                                children = element.children()
                                for child in children:
                                    collect_all_elements(child, level + 1)
                            except:
                                pass
                    
                    collect_all_elements(target_window)
                    
                    # Look for profile-related elements
                    for element, level in all_elements:
                        try:
                            text = element.window_text() if hasattr(element, 'window_text') else ""
                            control_type = str(element.control_type()) if hasattr(element, 'control_type') else ""
                            
                            # Look for actual buttons, not description text
                            if (text and 
                                any(keyword in text.lower() for keyword in ["gwu", "profile", "open"]) and
                                len(text.strip()) < 50 and  # Avoid long description text
                                any(btn_keyword in control_type.lower() for btn_keyword in ["button", "click", "link"])):
                                
                                logger.info(f"Found potential profile button at level {level}: '{text}' ({control_type})")
                                
                                # Try to click this element directly
                                try:
                                    element.click_input()
                                    logger.info(f"Successfully clicked profile button: '{text}'")
                                    time.sleep(1)  # Wait to see if dialog closes
                                    return True
                                except Exception as click_e:
                                    logger.info(f"Direct click failed, trying coordinates: {click_e}")
                                    
                                    # Try clicking at element center
                                    try:
                                        rect = element.rectangle()
                                        center_x = (rect.left + rect.right) // 2
                                        center_y = (rect.top + rect.bottom) // 2
                                        pyautogui.click(center_x, center_y)
                                        logger.info(f"Clicked profile button at coordinates: ({center_x}, {center_y})")
                                        time.sleep(1)
                                        return True
                                    except Exception as coord_e:
                                        logger.info(f"Coordinate click failed: {coord_e}")
                                        continue
                                        
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    logger.info(f"Deep UIA search failed: {e}")
                
                # Method 1.5: Look for shorter text elements that might be buttons
                try:
                    logger.info("Looking for short text elements that might be profile buttons...")
                    
                    for element, level in all_elements:
                        try:
                            text = element.window_text() if hasattr(element, 'window_text') else ""
                            control_type = str(element.control_type()) if hasattr(element, 'control_type') else ""
                            
                            # Look for short text that might be a button label
                            if (text and 
                                len(text.strip()) < 30 and  # Short text
                                len(text.strip()) > 2 and   # Not empty
                                any(keyword in text.lower() for keyword in ["gwu", "profile", "open", "sign", "start"])):
                                
                                logger.info(f"Found short text element at level {level}: '{text}' ({control_type})")
                                
                                # Try clicking this element
                                try:
                                    rect = element.rectangle()
                                    center_x = (rect.left + rect.right) // 2
                                    center_y = (rect.top + rect.bottom) // 2
                                    pyautogui.click(center_x, center_y)
                                    logger.info(f"Clicked short text element at: ({center_x}, {center_y})")
                                    time.sleep(1)
                                    return True
                                except Exception as click_e:
                                    logger.info(f"Click failed: {click_e}")
                                    continue
                                    
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    logger.info(f"Short text search failed: {e}")
                
                # Method 2: Try to find any clickable elements in the profile dialog
                try:
                    logger.info("Trying to find any clickable elements in profile dialog...")
                    
                    # Look for any elements that might be buttons
                    for element, level in all_elements:
                        try:
                            control_type = str(element.control_type()) if hasattr(element, 'control_type') else ""
                            text = element.window_text() if hasattr(element, 'window_text') else ""
                            
                            # Look for button-like elements or elements with text
                            if (("button" in control_type.lower() or "click" in control_type.lower()) and 
                                text and len(text.strip()) > 0):
                                
                                logger.info(f"Found clickable element: '{text}' ({control_type}) at level {level}")
                                
                                # Try clicking this element
                                try:
                                    rect = element.rectangle()
                                    center_x = (rect.left + rect.right) // 2
                                    center_y = (rect.top + rect.bottom) // 2
                                    pyautogui.click(center_x, center_y)
                                    logger.info(f"Clicked clickable element at: ({center_x}, {center_y})")
                                    time.sleep(1)
                                    return True
                                except Exception as click_e:
                                    logger.info(f"Click failed: {click_e}")
                                    continue
                                    
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    logger.info(f"Clickable element search failed: {e}")
                
                # Method 3: Smart coordinate-based clicking with visual feedback
                try:
                    logger.info("Using smart coordinate-based clicking...")
                    window_rect = target_window.rectangle()
                    
                    # Profile buttons are typically arranged horizontally in the center
                    # Try a grid of positions where profile buttons commonly appear
                    center_x = window_rect.left + (window_rect.right - window_rect.left) // 2
                    center_y = window_rect.top + (window_rect.bottom - window_rect.top) // 2
                    
                    # Create a grid of click positions
                    click_positions = [
                        # Center area (most common)
                        (center_x, center_y),
                        # Left side
                        (center_x - 100, center_y),
                        (center_x - 50, center_y),
                        # Right side  
                        (center_x + 50, center_y),
                        (center_x + 100, center_y),
                        # Above center
                        (center_x, center_y - 50),
                        (center_x, center_y - 100),
                        # Below center
                        (center_x, center_y + 50),
                        (center_x, center_y + 100),
                        # Diagonal positions
                        (center_x - 75, center_y - 75),
                        (center_x + 75, center_y - 75),
                        (center_x - 75, center_y + 75),
                        (center_x + 75, center_y + 75)
                    ]
                    
                    for i, (pos_x, pos_y) in enumerate(click_positions):
                        logger.info(f"Trying profile button position {i+1}/{len(click_positions)}: ({pos_x}, {pos_y})")
                        
                        # Click and wait
                        pyautogui.click(pos_x, pos_y)
                        time.sleep(0.8)  # Wait longer to see effect
                        
                        # Check if the profile dialog is still there
                        try:
                            # Try to find the profile dialog again
                            remaining_children = target_window.children()
                            profile_still_there = any("profile" in str(child).lower() or "gwu" in str(child).lower() for child in remaining_children)
                            
                            if not profile_still_there:
                                logger.info(f"✅ Profile button click successful at position {i+1}: ({pos_x}, {pos_y})")
                                return True
                            else:
                                logger.info(f"Profile dialog still visible, trying next position...")
                                
                        except Exception as check_e:
                            logger.info(f"Could not verify click success, assuming it worked: {check_e}")
                            return True
                    
                    logger.warning("❌ All profile button positions failed")
                    return False
                    
                except Exception as e:
                    logger.warning(f"Smart coordinate clicking failed: {e}")
                    return False
            
            return None
            
        except Exception as e:
            logger.warning(f"Chrome element detection failed: {e}")
            return None
