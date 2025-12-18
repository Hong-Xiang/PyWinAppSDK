"""Debug script to check what's installed"""
import sys
import os

print("Python executable:", sys.executable)
print("\nsite-packages locations:")
for p in sys.path:
    if 'site-packages' in p:
        print(f"  {p}")
        
print("\nChecking for winappsdk installations:")
for p in sys.path:
    if 'site-packages' in p and os.path.exists(p):
        winappsdk_path = os.path.join(p, 'winappsdk')
        if os.path.exists(winappsdk_path):
            print(f"\n✓ Found winappsdk at: {winappsdk_path}")
            # List contents
            for root, dirs, files in os.walk(winappsdk_path):
                level = root.replace(winappsdk_path, '').count(os.sep)
                if level > 2:  # limit depth
                    continue
                indent = ' ' * 2 * level
                print(f'{indent}{os.path.basename(root)}/')
                sub_indent = ' ' * 2 * (level + 1)
                for file in files[:3]:
                    print(f'{sub_indent}{file}')
                if len(files) > 3:
                    print(f'{sub_indent}... and {len(files)-3} more')

print("\nChecking for component packages:")
for comp in ['winappsdk_InteractiveExperiences', 'winappsdk_Foundation', 'winappsdk_AI']:
    for p in sys.path:
        if 'site-packages' in p and os.path.exists(p):
            comp_path = os.path.join(p, comp)
            if os.path.exists(comp_path):
                print(f"✓ Found {comp}")
                break
    else:
        print(f"✗ Missing {comp}")

print("\nTrying to import winappsdk:")
try:
    import winappsdk
    print(f"✓ Import successful")
    if hasattr(winappsdk, '__path__'):
        print(f"  __path__: {winappsdk.__path__}")
    if hasattr(winappsdk, '__file__'):
        print(f"  __file__: {winappsdk.__file__}")
    
    # Try to see what's in microsoft
    print("\nChecking winappsdk.microsoft:")
    import winappsdk.microsoft
    if hasattr(winappsdk.microsoft, '__path__'):
        print(f"  __path__: {winappsdk.microsoft.__path__}")
        
    # List what's visible under microsoft
    microsoft_dir = list(winappsdk.microsoft.__path__)[0]
    if os.path.exists(microsoft_dir):
        subdirs = [d for d in os.listdir(microsoft_dir) if os.path.isdir(os.path.join(microsoft_dir, d))]
        print(f"  Subdirectories: {subdirs}")
        
except ImportError as e:
    print(f"✗ Import failed: {e}")
