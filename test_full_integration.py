"""
Full integration test for PyWinAppSDK.
Verifies that all components can be imported and used together in a single environment.
"""
import sys
import os

print(f"Python: {sys.version}")
print(f"Platform: {sys.platform}")

try:
    print("\n--- Testing Shared Namespace ---")
    import winappsdk
    print(f"✓ winappsdk package: {winappsdk.__file__}")
    
    import winappsdk.microsoft
    print("✓ winappsdk.microsoft namespace")
    
    import winappsdk.microsoft.windows
    print("✓ winappsdk.microsoft.windows namespace")
    
    import winappsdk.microsoft.ui
    print("✓ winappsdk.microsoft.ui namespace")

    print("\n--- Testing InteractiveExperiences Component ---")
    import winappsdk_InteractiveExperiences
    print(f"✓ winappsdk_InteractiveExperiences package: {winappsdk_InteractiveExperiences.__file__}")
    
    from winappsdk.microsoft.ui.windowing import AppWindow
    print("✓ Imported AppWindow from winappsdk.microsoft.ui.windowing")
    
    from winappsdk.microsoft.ui.composition import Compositor
    print("✓ Imported Compositor from winappsdk.microsoft.ui.composition")

    print("\n--- Testing Foundation Component ---")
    import winappsdk_Foundation
    print(f"✓ winappsdk_Foundation package: {winappsdk_Foundation.__file__}")
    
    from winappsdk.microsoft.windows.applifecycle import AppInstance
    print("✓ Imported AppInstance from winappsdk.microsoft.windows.applifecycle")
    
    from winappsdk.microsoft.windows.applicationmodel.resources import ResourceManager
    print("✓ Imported ResourceManager from winappsdk.microsoft.windows.applicationmodel.resources")

    print("\n--- Testing AI Component ---")
    import winappsdk_AI
    print(f"✓ winappsdk_AI package: {winappsdk_AI.__file__}")
    
    # Note: AI might not have easily instantiable classes without Windows App Runtime, 
    # but we can check for module existence
    import winappsdk.microsoft.windows.ai
    print("✓ Imported winappsdk.microsoft.windows.ai")

    print("\n✅ Full Integration Test Passed!")

except ImportError as e:
    print(f"\n❌ Import Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Unexpected Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
