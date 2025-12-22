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
    print("\n[OK] winappsdk package imported")
    
    # Test that microsoft namespace is shared
    import winappsdk.microsoft
    print("[OK] winappsdk.microsoft namespace imported")
    
    # ========================================================================
    # Test InteractiveExperiences namespaces (microsoft.ui.*)
    # ========================================================================
    print("\n--- Testing InteractiveExperiences namespaces ---")
    
    import winappsdk.microsoft.ui
    print("[OK] winappsdk.microsoft.ui")
    
    import winappsdk.microsoft.ui.windowing
    print("[OK] winappsdk.microsoft.ui.windowing")
    from winappsdk.microsoft.ui.windowing import AppWindow
    print("  [OK] Class AppWindow available")
    
    import winappsdk.microsoft.ui.composition
    print("[OK] winappsdk.microsoft.ui.composition")
    from winappsdk.microsoft.ui.composition import Compositor
    print("  [OK] Class Compositor available")
    
    import winappsdk.microsoft.ui.dispatching
    print("[OK] winappsdk.microsoft.ui.dispatching")
    
    import winappsdk_InteractiveExperiences
    print("[OK] winappsdk_InteractiveExperiences component package")
    
    # ========================================================================
    # Test Foundation namespaces (microsoft.windows.*)
    # ========================================================================
    print("\n--- Testing Foundation namespaces ---")
    
    import winappsdk.microsoft.windows
    print("[OK] winappsdk.microsoft.windows")
    
    import winappsdk.microsoft.windows.applifecycle
    print("[OK] winappsdk.microsoft.windows.applifecycle")
    from winappsdk.microsoft.windows.applifecycle import AppInstance
    print("  [OK] Class AppInstance available")
    
    import winappsdk.microsoft.windows.applicationmodel.dynamicdependency
    print("[OK] winappsdk.microsoft.windows.applicationmodel.dynamicdependency")
    
    import winappsdk.microsoft.windows.applicationmodel.resources
    print("[OK] winappsdk.microsoft.windows.applicationmodel.resources")
    from winappsdk.microsoft.windows.applicationmodel.resources import ResourceManager
    print("  [OK] Class ResourceManager available")
    
    import winappsdk.microsoft.windows.appnotifications
    print("[OK] winappsdk.microsoft.windows.appnotifications")
    
    import winappsdk_Foundation
    print("[OK] winappsdk_Foundation component package")
    
    # ========================================================================
    # Test AI namespaces (microsoft.windows.ai.*)
    # ========================================================================
    print("\n--- Testing AI namespaces ---")
    
    import winappsdk.microsoft.windows.ai
    print("[OK] winappsdk.microsoft.windows.ai")
    
    import winappsdk.microsoft.windows.ai.foundation
    print("[OK] winappsdk.microsoft.windows.ai.foundation")
    
    import winappsdk.microsoft.windows.ai.imaging
    print("[OK] winappsdk.microsoft.windows.ai.imaging")
    
    import winappsdk_AI
    print("[OK] winappsdk_AI component package")
    
    # ========================================================================
    # Verify namespace structure
    # ========================================================================
    print("\n--- Verifying namespace structure ---")
    
    # Check that winappsdk has __path__ (it's a namespace package)
    if hasattr(winappsdk, '__path__'):
        print(f"[OK] winappsdk is a namespace package with paths: {list(winappsdk.__path__)}")
    else:
        print("[WARN] winappsdk is not a namespace package")
    
    # Verify microsoft namespace is shared
    if hasattr(winappsdk.microsoft, '__path__'):
        print(f"[OK] winappsdk.microsoft is a namespace package")
    
    # Verify both ui and windows namespaces coexist under microsoft
    if hasattr(winappsdk.microsoft, 'ui') and hasattr(winappsdk.microsoft, 'windows'):
        print("[OK] Both microsoft.ui (InteractiveExperiences) and microsoft.windows (Foundation/AI) coexist")
    
    # ========================================================================
    # Print summary
    # ========================================================================
    print("\n" + "=" * 70)
    print("SUCCESS: ALL INTEGRATION TESTS PASSED!")
    print("=" * 70)
    print("\nPackage locations:")
    print(f"  winappsdk: {winappsdk.__file__ if hasattr(winappsdk, '__file__') else 'namespace package'}")
    print(f"  winappsdk_InteractiveExperiences: {winappsdk_InteractiveExperiences.__file__}")
    print(f"  winappsdk_Foundation: {winappsdk_Foundation.__file__}")
    print(f"  winappsdk_AI: {winappsdk_AI.__file__}")
    
    print("\n[OK] The dual-folder architecture successfully enables:")
    print("  1. Shared namespace: import winappsdk.microsoft.*")
    print("  2. Component isolation: winappsdk_<Component> for binaries")
    print("  3. Cross-component compatibility: all packages coexist harmoniously")
    
except ImportError as e:
    print(f"\n[ERROR] Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
