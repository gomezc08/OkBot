"""
Simple test script to verify the FlaUI module can be imported and used.
"""

try:
    from automation_engine import AutomationEngine
    print("✅ Successfully imported AutomationEngine")
    
    # Test basic functionality
    engine = AutomationEngine()
    print("✅ Successfully created AutomationEngine instance")
    
    # Test variable system
    engine.set_variable("test_var", "Hello World")
    value = engine.get_variable("test_var")
    print(f"✅ Variable system working: {value}")
    
    print("\n🎉 All basic functionality tests passed!")
    print("The FlaUI automation module is ready to use.")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
