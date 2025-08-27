#!/usr/bin/env python3
"""
Debug script to identify UIA elements in Chrome windows
"""

import time
from pywinauto import Desktop, Application
from pywinauto.controls.uiawrapper import UIAWrapper

def debug_chrome_elements():
    """Debug Chrome UIA elements to see what's available"""
    print("🔍 Debugging Chrome UIA Elements...")
    print("=" * 50)
    
    try:
        # Get all UIA windows
        desktop = Desktop(backend="uia")
        windows = desktop.windows()
        
        print(f"Found {len(windows)} total UIA windows")
        print()
        
        # Look for Chrome-related windows
        chrome_windows = []
        for window in windows:
            try:
                window_text = window.window_text()
                if window_text and ("chrome" in window_text.lower() or "google" in window_text.lower()):
                    chrome_windows.append(window)
                    print(f"🎯 Chrome Window: '{window_text}'")
                    try:
                        print(f"   Control Type: {window.control_type()}")
                        print(f"   Class Name: {window.class_name()}")
                        print(f"   Process ID: {window.process_id()}")
                    except:
                        print(f"   Could not get full details")
                    print()
            except Exception as e:
                continue
        
        if not chrome_windows:
            print("❌ No Chrome windows found")
            return
        
        # Focus on the first actual Chrome window (not Cursor)
        target_window = None
        for window in chrome_windows:
            if "cursor" not in window.window_text().lower():
                target_window = window
                break
        
        if not target_window:
            print("❌ No actual Chrome browser windows found")
            return
            
        print(f"🔍 Analyzing Chrome window: '{target_window.window_text()}'")
        print("=" * 50)
        
        # Get all children
        try:
            children = target_window.children()
            print(f"Found {len(children)} child elements")
            print()
            
            # Show first 20 children with details
            for i, child in enumerate(children[:20]):
                try:
                    child_text = child.window_text()
                    child_type = child.control_type()
                    child_class = child.class_name()
                    
                    print(f"Child {i+1}:")
                    print(f"  Text: '{child_text}'")
                    print(f"  Type: {child_type}")
                    print(f"  Class: {child_class}")
                    
                    # Look for specific elements we're interested in
                    if "profile" in str(child_text).lower():
                        print(f"  ⭐ PROFILE ELEMENT FOUND!")
                    if "address" in str(child_text).lower() or "search" in str(child_text).lower():
                        print(f"  ⭐ ADDRESS BAR ELEMENT FOUND!")
                    if "button" in str(child_type).lower():
                        print(f"  ⭐ BUTTON ELEMENT FOUND!")
                    
                    print()
                    
                except Exception as e:
                    print(f"Child {i+1}: Error getting details - {e}")
                    print()
            
            if len(children) > 20:
                print(f"... and {len(children) - 20} more children")
            
        except Exception as e:
            print(f"Error getting children: {e}")
        
        # Try to find specific elements using different methods
        print("🔍 Looking for specific elements...")
        print("=" * 50)
        
        # Look for profile button - try different approaches
        try:
            # Method 1: Search by name
            profile_elements = []
            for child in children:
                try:
                    if hasattr(child, 'window_text'):
                        child_text = child.window_text()
                        if child_text and "profile" in child_text.lower():
                            profile_elements.append(child)
                except:
                    continue
            
            if profile_elements:
                print(f"✅ Found {len(profile_elements)} profile-related element(s)")
                for elem in profile_elements:
                    try:
                        print(f"  - {elem.window_text()} ({elem.control_type()})")
                    except:
                        print(f"  - <profile element>")
            else:
                print("❌ Profile button not found")
        except Exception as e:
            print(f"Error searching for profile button: {e}")
        
        # Look for address bar - try different approaches
        try:
            address_elements = []
            for child in children:
                try:
                    if hasattr(child, 'window_text'):
                        child_text = child.window_text()
                        if child_text and ("address" in child_text.lower() or "search" in child_text.lower()):
                            address_elements.append(child)
                except:
                    continue
            
            if address_elements:
                print(f"✅ Found {len(address_elements)} address bar element(s)")
                for elem in address_elements:
                    try:
                        print(f"  - {elem.window_text()} ({elem.control_type()})")
                    except:
                        print(f"  - <address bar element>")
            else:
                print("❌ Address bar not found")
        except Exception as e:
            print(f"Error searching for address bar: {e}")
        
        # Look for any buttons
        try:
            button_elements = []
            for child in children:
                try:
                    if hasattr(child, 'control_type'):
                        child_type = str(child.control_type())
                        if "button" in child_type.lower():
                            button_elements.append(child)
                except:
                    continue
            
            if button_elements:
                print(f"✅ Found {len(button_elements)} button(s)")
                for i, elem in enumerate(button_elements[:10]):  # Show first 10
                    try:
                        elem_text = elem.window_text()
                        print(f"  {i+1}. {elem_text} ({elem.control_type()})")
                    except:
                        print(f"  {i+1}. <no text> ({elem.control_type()})")
                if len(button_elements) > 10:
                    print(f"  ... and {len(button_elements) - 10} more")
            else:
                print("❌ No buttons found")
        except Exception as e:
            print(f"Error searching for buttons: {e}")
        
        # Look for any edit fields
        try:
            edit_elements = []
            for child in children:
                try:
                    if hasattr(child, 'control_type'):
                        child_type = str(child.control_type())
                        if "edit" in child_type.lower():
                            edit_elements.append(child)
                except:
                    continue
            
            if edit_elements:
                print(f"✅ Found {len(edit_elements)} edit field(s)")
                for i, elem in enumerate(edit_elements[:10]):  # Show first 10
                    try:
                        elem_text = elem.window_text()
                        print(f"  {i+1}. {elem_text} ({elem.control_type()})")
                    except:
                        print(f"  {i+1}. <no text> ({elem.control_type()})")
                if len(edit_elements) > 10:
                    print(f"  ... and {len(edit_elements) - 10} more")
            else:
                print("❌ No edit fields found")
        except Exception as e:
            print(f"Error searching for edit fields: {e}")
        
    except Exception as e:
        print(f"❌ Error in debug script: {e}")

if __name__ == "__main__":
    debug_chrome_elements()
