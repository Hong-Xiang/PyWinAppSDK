r"""
Widget Provider Registration Script

This registers the PyWinAppSDK widget provider with Windows.

Usage:
    Register:   python widget-register.py
    Unregister: python widget-register.py --unregister

Note: May require administrator rights for registry access.
"""

import sys
import winreg
import os
import json

# Widget Configuration
WIDGET_PROVIDER_CLSID = "{12345678-1234-1234-1234-123456789ABC}"
WIDGET_ID = "PyWinAppSDK_TestWidget"
WIDGET_DISPLAY_NAME = "PyWinAppSDK Test Widget"
WIDGET_DESCRIPTION = "A test widget created with Python and Windows App SDK"

def create_widget_manifest():
    """Create the widget manifest JSON."""
    return {
        "WidgetProviderVersion": "1.0.0",
        "Widgets": [
            {
                "Id": WIDGET_ID,
                "DisplayName": WIDGET_DISPLAY_NAME,
                "Description": WIDGET_DESCRIPTION,
                "Screenshots": [],
                "Icon": "",
                "AllowMultiple": True,
                "WidgetCapabilities": [
                    {
                        "Size": "Small"
                    },
                    {
                        "Size": "Medium"
                    },
                    {
                        "Size": "Large"
                    }
                ]
            }
        ]
    }


def register_widget_provider():
    """Register the widget provider in Windows registry."""
    print("=" * 60)
    print("📝 Registering PyWinAppSDK Widget Provider")
    print("=" * 60)
    
    try:
        # Get current script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        provider_path = os.path.join(script_dir, "widget-provider-example.py")
        python_exe = sys.executable
        
        # Widget provider registry path
        registry_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsWidgets\Providers"
        
        # Create/open provider key
        with winreg.CreateKeyEx(
            winreg.HKEY_CURRENT_USER,
            registry_path,
            0,
            winreg.KEY_WRITE
        ) as providers_key:
            
            # Create key for our provider
            provider_key_path = f"{registry_path}\\{WIDGET_PROVIDER_CLSID}"
            
            with winreg.CreateKeyEx(
                winreg.HKEY_CURRENT_USER,
                provider_key_path,
                0,
                winreg.KEY_WRITE
            ) as provider_key:
                
                # Set provider properties
                winreg.SetValueEx(
                    provider_key,
                    "DisplayName",
                    0,
                    winreg.REG_SZ,
                    "PyWinAppSDK Widget Provider"
                )
                
                winreg.SetValueEx(
                    provider_key,
                    "Description",
                    0,
                    winreg.REG_SZ,
                    "Python-based widget provider using Windows App SDK"
                )
                
                # Save manifest
                manifest = create_widget_manifest()
                manifest_path = os.path.join(script_dir, "widget-manifest.json")
                with open(manifest_path, 'w') as f:
                    json.dump(manifest, f, indent=2)
                
                winreg.SetValueEx(
                    provider_key,
                    "ManifestPath",
                    0,
                    winreg.REG_SZ,
                    manifest_path
                )
                
                # Set provider executable (Python script)
                winreg.SetValueEx(
                    provider_key,
                    "ProviderPath",
                    0,
                    winreg.REG_SZ,
                    f'"{python_exe}" "{provider_path}"'
                )
        
        print(f"\n✅ Successfully registered widget provider!")
        print(f"\nProvider CLSID: {WIDGET_PROVIDER_CLSID}")
        print(f"Widget ID: {WIDGET_ID}")
        print(f"Manifest: {manifest_path}")
        print(f"\nNext steps:")
        print(f"  1. Run: python widget-provider-example.py")
        print(f"  2. Open Widgets Board (Win+W)")
        print(f"  3. Look for '{WIDGET_DISPLAY_NAME}'")
        
        return True
        
    except PermissionError:
        print("❌ Permission denied. Try running as administrator.")
        return False
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def unregister_widget_provider():
    """Remove the widget provider from registry."""
    print("=" * 60)
    print("🗑️  Unregistering PyWinAppSDK Widget Provider")
    print("=" * 60)
    
    try:
        registry_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsWidgets\Providers"
        provider_key_path = f"{registry_path}\\{WIDGET_PROVIDER_CLSID}"
        
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, provider_key_path)
            print(f"✅ Provider unregistered: {WIDGET_PROVIDER_CLSID}")
        except FileNotFoundError:
            print(f"⚠️  Provider not found in registry")
        
        # Clean up manifest file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        manifest_path = os.path.join(script_dir, "widget-manifest.json")
        if os.path.exists(manifest_path):
            os.remove(manifest_path)
            print(f"✅ Removed manifest: {manifest_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Unregistration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if "--unregister" in sys.argv:
        success = unregister_widget_provider()
    else:
        success = register_widget_provider()
    
    sys.exit(0 if success else 1)
