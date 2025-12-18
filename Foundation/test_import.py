"""
Test script for Foundation package namespaces
"""

print("Testing winappsdk-Foundation namespace imports...")

try:
    # Test importing the shared winappsdk namespace
    import winappsdk
    print("✓ winappsdk package imported")
    
    # Test importing microsoft namespace
    import winappsdk.microsoft
    print("✓ winappsdk.microsoft namespace imported")
    
    # Test importing Windows namespaces
    import winappsdk.microsoft.windows
    print("✓ winappsdk.microsoft.windows imported")
    
    import winappsdk.microsoft.windows.applifecycle
    print("✓ winappsdk.microsoft.windows.applifecycle imported")
    
    import winappsdk.microsoft.windows.applicationmodel.dynamicdependency
    print("✓ winappsdk.microsoft.windows.applicationmodel.dynamicdependency imported")
    
    import winappsdk.microsoft.windows.applicationmodel.resources
    print("✓ winappsdk.microsoft.windows.applicationmodel.resources imported")
    
    # Verify that the component-specific package exists
    import winappsdk_Foundation
    print("✓ winappsdk_Foundation package imported")
    
    print("\n✅ All imports successful!")
    print(f"winappsdk location: {winappsdk.__file__}")
    print(f"winappsdk_Foundation location: {winappsdk_Foundation.__file__}")
    
except ImportError as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
