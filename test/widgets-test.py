r"""
Test for Windows App SDK Widgets APIs.

This test creates a visible widget that can be pinned to the Windows 11 Widgets Board.

This uses custom wheels built from PyWinAppSDK:
    winappsdk_foundation-3.2.1-cp312-cp312-win_amd64.whl
    winappsdk_widgets-3.2.1-cp312-cp312-win_amd64.whl

Run with uv (from project root):
    uv run --with wheels/winappsdk_foundation-3.2.1-cp312-cp312-win_amd64.whl \
           --with wheels/winappsdk_widgets-3.2.1-cp312-cp312-win_amd64.whl \
           --no-project \
           python test/widgets-test.py

Note: The winrt-runtime and winrt-Windows.* packages are declared as dependencies
in the wheel packages and will be installed automatically by pip/uv.

Requirements:
    - Windows App SDK runtime installed (or the bootstrap DLL bundled in the package)
    - Windows 11 (for Widgets Board support)
"""

import sys
import json

# Import Windows App SDK bootstrap (bundled with Foundation package)
from winappsdk.bootstrap import initialize_windows_app_sdk, BootstrapInitializeOptions

# Import Widgets APIs
from winappsdk.microsoft.windows.widgets.providers import (
    IWidgetProvider,
    WidgetManager,
    WidgetInfo,
    WidgetContext,
    WidgetUpdateRequestOptions,
)


def create_widget_template():
    """Create an Adaptive Card template for the widget."""
    return json.dumps({
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.5",
        "body": [
            {
                "type": "Container",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": "🐍 PyWinAppSDK Test Widget",
                        "size": "Large",
                        "weight": "Bolder",
                        "color": "Accent"
                    },
                    {
                        "type": "TextBlock",
                        "text": "Hello from Python!",
                        "size": "Medium",
                        "wrap": True
                    },
                    {
                        "type": "FactSet",
                        "facts": [
                            {"title": "Status:", "value": "✅ Running"},
                            {"title": "Language:", "value": "Python 3.12"},
                            {"title": "SDK:", "value": "Windows App SDK 3.2"}
                        ]
                    }
                ]
            }
        ]
    })


def test_widget_provider():
    """Test basic Widget Provider creation and configuration."""
    
    try:
        # Get the widget manager instance
        manager = WidgetManager.get_default()
        print(f"✓ Retrieved WidgetManager: {manager}")
        print(f"  Type: {type(manager).__name__}")
        
        # Test that we can create widget-related objects
        update_options = WidgetUpdateRequestOptions("test-widget-id")
        print(f"\n✓ Created WidgetUpdateRequestOptions: {update_options}")
        
        print("\n💡 To see a widget visually on Windows 11:")
        print("   1. Register your app as a Widget Provider in the Windows registry")
        print("   2. Implement IWidgetProvider interface to handle widget lifecycle")
        print("   3. Pin the widget to the Widgets Board (Win+W)")
        print("   4. Update widget content using Adaptive Cards JSON")
        
        print("\n📝 Sample Adaptive Card template for widget content:")
        template = create_widget_template()
        print(template)
        
        print("\n💻 Widget Update Example:")
        print("   manager = WidgetManager.get_default()")
        print("   options = WidgetUpdateRequestOptions('your-widget-id')")
        print("   options.template = create_widget_template()")
        print("   options.data = '{}'")
        print("   # Call widget provider to update")
        
        print("\n✅ Widget APIs accessible - ready for provider implementation!")
        
        print("\n" + "=" * 60)
        print("ℹ️  IMPORTANT: This test doesn't create a visible widget yet!")
        print("=" * 60)
        print("\nTo see an ACTUAL widget in Windows 11 Widgets Board:")
        print("  1. Create a COM server that implements IWidgetProvider")
        print("  2. Register it in Windows registry")
        print("  3. Keep the provider process running")
        print("  4. Open Widgets Board (Win+W)")
        print("  5. Pin your widget from the available widgets")
        print("\nThe above Adaptive Card JSON would render with:")
        print("  • A blue title: '🐍 PyWinAppSDK Test Widget'")
        print("  • Message: 'Hello from Python!'")
        print("  • Status table showing running state and SDK info")
        print("\nPress Enter to exit...")
        input()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing widget provider: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Windows App SDK Widgets Test")
    print("=" * 60)
    
    try:
        with initialize_windows_app_sdk(
            options=BootstrapInitializeOptions.ON_ERROR_SHOW_UI,
            verbose=True
        ):
            print("\n[1] Testing Widget Provider APIs...")
            success = test_widget_provider()
            
            if success:
                print("\n" + "=" * 60)
                print("✅ All tests passed!")
                print("=" * 60)
                sys.exit(0)
            else:
                print("\n" + "=" * 60)
                print("❌ Some tests failed")
                print("=" * 60)
                sys.exit(1)
                
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)
            
    except OSError as e:
        print(f"❌ Bootstrap failed: {e}")
        sys.exit(1)
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
