"""
Test script for AI package namespaces
"""

print("Testing winappsdk-AI namespace imports...")

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
    
    # Test AI namespace
    import winappsdk.microsoft.windows.ai
    print("✓ winappsdk.microsoft.windows.ai imported")
    
    # Test that Foundation namespaces also work (dependency)
    import winappsdk.microsoft.windows.applifecycle
    print("✓ winappsdk.microsoft.windows.applifecycle imported (from Foundation)")
    
    # Test that InteractiveExperiences namespaces also work (dependency)
    import winappsdk.microsoft.ui.windowing
    print("✓ winappsdk.microsoft.ui.windowing imported (from InteractiveExperiences)")
    
    # Verify component-specific packages exist
    import winappsdk_AI
    print("✓ winappsdk_AI package imported")
    
    import winappsdk_Foundation
    print("✓ winappsdk_Foundation package imported")
    
    import winappsdk_InteractiveExperiences
    print("✓ winappsdk_InteractiveExperiences package imported")
    
    print("\n✅ All imports successful!")
    print(f"winappsdk location: {winappsdk.__file__}")
    print(f"winappsdk_AI location: {winappsdk_AI.__file__}")
    
except ImportError as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
