"""
Minimal test script to verify winappsdk namespace imports work correctly.
Tests the new structure: winappsdk.microsoft.ui.*
"""

print("Testing winappsdk namespace imports...")

try:
    # Test importing the shared winappsdk namespace
    import winappsdk
    print("✓ winappsdk package imported")
    
    # Test importing microsoft namespace
    import winappsdk.microsoft
    print("✓ winappsdk.microsoft namespace imported")
    
    # Test importing UI namespaces
    import winappsdk.microsoft.ui
    print("✓ winappsdk.microsoft.ui imported")
    
    import winappsdk.microsoft.ui.windowing
    print("✓ winappsdk.microsoft.ui.windowing imported")
    
    import winappsdk.microsoft.ui.composition
    print("✓ winappsdk.microsoft.ui.composition imported")
    
    # Test importing graphics namespaces
    import winappsdk.microsoft.graphics.directx
    print("✓ winappsdk.microsoft.graphics.directx imported")
    
    # Verify that the component-specific package exists
    import winappsdk_InteractiveExperiences
    print("✓ winappsdk_InteractiveExperiences package imported")
    
    print("\n✅ All imports successful!")
    print(f"winappsdk location: {winappsdk.__file__}")
    print(f"winappsdk_InteractiveExperiences location: {winappsdk_InteractiveExperiences.__file__}")
    
except ImportError as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
