"""
Comprehensive integration test for all winappsdk packages.
Tests namespace merging across InteractiveExperiences, Foundation, and AI.
"""

print("=" * 70)
print("Testing winappsdk namespace integration across all packages")
print("=" * 70)

import sys

try:
    # Test shared winappsdk namespace
    import winappsdk
    print("\n✓ winappsdk package imported")
    
    # Test that microsoft namespace is shared
    import winappsdk.microsoft
    print("✓ winappsdk.microsoft namespace imported")
    
    # ========================================================================
    # Test InteractiveExperiences namespaces (microsoft.ui.*)
    # ========================================================================
    print("\n--- Testing InteractiveExperiences namespaces ---")
    
    import winappsdk.microsoft.ui
    print("✓ winappsdk.microsoft.ui")
    
    import winappsdk.microsoft.ui.windowing
    print("✓ winappsdk.microsoft.ui.windowing")
    from winappsdk.microsoft.ui.windowing import AppWindow
    print("  ✓ Class AppWindow available")
    
    import winappsdk.microsoft.ui.composition
    print("✓ winappsdk.microsoft.ui.composition")
    from winappsdk.microsoft.ui.composition import Compositor
    print("  ✓ Class Compositor available")
    
    import winappsdk.microsoft.ui.dispatching
    print("✓ winappsdk.microsoft.ui.dispatching")
    
    import winappsdk_InteractiveExperiences
    print("✓ winappsdk_InteractiveExperiences component package")
    
    # ========================================================================
    # Test Foundation namespaces (microsoft.windows.*)
    # ========================================================================
    print("\n--- Testing Foundation namespaces ---")
    
    import winappsdk.microsoft.windows
    print("✓ winappsdk.microsoft.windows")
    
    import winappsdk.microsoft.windows.applifecycle
    print("✓ winappsdk.microsoft.windows.applifecycle")
    from winappsdk.microsoft.windows.applifecycle import AppInstance
    print("  ✓ Class AppInstance available")
    
    import winappsdk.microsoft.windows.applicationmodel.dynamicdependency
    print("✓ winappsdk.microsoft.windows.applicationmodel.dynamicdependency")
    
    import winappsdk.microsoft.windows.applicationmodel.resources
    print("✓ winappsdk.microsoft.windows.applicationmodel.resources")
    from winappsdk.microsoft.windows.applicationmodel.resources import ResourceManager
    print("  ✓ Class ResourceManager available")
    
    import winappsdk.microsoft.windows.appnotifications
    print("✓ winappsdk.microsoft.windows.appnotifications")
    
    import winappsdk_Foundation
    print("✓ winappsdk_Foundation component package")
    
    # ========================================================================
    # Test AI namespaces (microsoft.windows.ai.*)
    # ========================================================================
    print("\n--- Testing AI namespaces ---")
    
    import winappsdk.microsoft.windows.ai
    print("✓ winappsdk.microsoft.windows.ai")
    
    import winappsdk.microsoft.windows.ai.foundation
    print("✓ winappsdk.microsoft.windows.ai.foundation")
    
    import winappsdk.microsoft.windows.ai.imaging
    print("✓ winappsdk.microsoft.windows.ai.imaging")
    
    import winappsdk_AI
    print("✓ winappsdk_AI component package")
    
    # ========================================================================
    # Verify namespace structure
    # ========================================================================
    print("\n--- Verifying namespace structure ---")
    
    # Check that winappsdk has __path__ (it's a namespace package)
    if hasattr(winappsdk, '__path__'):
        print(f"✓ winappsdk is a namespace package with paths: {list(winappsdk.__path__)}")
    else:
        print("⚠ winappsdk is not a namespace package")
    
    # Verify microsoft namespace is shared
    if hasattr(winappsdk.microsoft, '__path__'):
        print(f"✓ winappsdk.microsoft is a namespace package")
    
    # Verify both ui and windows namespaces coexist under microsoft
    if hasattr(winappsdk.microsoft, 'ui') and hasattr(winappsdk.microsoft, 'windows'):
        print("✓ Both microsoft.ui (InteractiveExperiences) and microsoft.windows (Foundation/AI) coexist")
    
    # ========================================================================
    # Print summary
    # ========================================================================
    print("\n" + "=" * 70)
    print("✅ ALL INTEGRATION TESTS PASSED!")
    print("=" * 70)
    print("\nPackage locations:")
    print(f"  winappsdk: {winappsdk.__file__ if hasattr(winappsdk, '__file__') else 'namespace package'}")
    print(f"  winappsdk_InteractiveExperiences: {winappsdk_InteractiveExperiences.__file__}")
    print(f"  winappsdk_Foundation: {winappsdk_Foundation.__file__}")
    print(f"  winappsdk_AI: {winappsdk_AI.__file__}")
    
    print("\n✅ The dual-folder architecture successfully enables:")
    print("  1. Shared namespace: import winappsdk.microsoft.*")
    print("  2. Component isolation: winappsdk_<Component> for binaries")
    print("  3. Cross-component compatibility: all packages coexist harmoniously")
    
except ImportError as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
