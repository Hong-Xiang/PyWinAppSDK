r"""
Windows App SDK Toast Notifications Demo

This shows VISIBLE toast notifications that pop up on your screen!

⚠️ REQUIREMENTS:
   - Python from Microsoft Store (has package identity built-in)
   - OR use register_sparse_package.py to add package identity

Setup with Store Python:
   1. Install Python from Microsoft Store
   2. Create venv: python -m venv venv-store
   3. Activate: .\venv-store\Scripts\Activate.ps1
   4. Install: pip install --find-links wheels winappsdk-foundation winappsdk-interactiveexperiences
   5. Run: python test/notifications-demo.py

Or with uv using Store Python:
   1. Find Store Python: where.exe python (look for WindowsApps path)
   2. Run: uv run --python "C:\...\WindowsApps\...\python.exe" notifications-demo.py

Run:
    python notifications-demo.py
"""

import sys
import time

# Import Windows App SDK bootstrap
from winappsdk.bootstrap import initialize_windows_app_sdk, BootstrapInitializeOptions

# Import Notification APIs
from winappsdk.microsoft.windows.appnotifications import (
    AppNotification,
    AppNotificationManager,
    AppNotificationPriority,
)


def show_simple_toast():
    """Show a simple text toast notification."""
    print("\n[1] Showing simple text notification...")
    
    # Create simple XML content
    toast_xml = """
    <toast>
        <visual>
            <binding template="ToastGeneric">
                <text>🐍 Hello from Python!</text>
                <text>PyWinAppSDK Notification Test</text>
            </binding>
        </visual>
    </toast>
    """
    
    notification = AppNotification(toast_xml)
    AppNotificationManager.default.show(notification)
    
    print("✅ Simple toast notification sent!")
    print("   Look for it in the bottom-right corner of your screen!")


def show_image_toast():
    """Show a toast with an image and buttons."""
    print("\n[2] Showing notification with image and buttons...")
    
    toast_xml = """
    <toast>
        <visual>
            <binding template="ToastGeneric">
                <text>🎉 PyWinAppSDK Test</text>
                <text>This is a rich notification with an image!</text>
                <image placement="hero" src="https://picsum.photos/364/180?image=883" />
            </binding>
        </visual>
        <actions>
            <action content="View" arguments="action=view" />
            <action content="Dismiss" arguments="action=dismiss" />
        </actions>
    </toast>
    """
    
    notification = AppNotification(toast_xml)
    notification.priority = AppNotificationPriority.HIGH
    AppNotificationManager.default.show(notification)
    
    print("✅ Rich toast notification sent!")
    print("   This one has an image and buttons!")


def show_progress_toast():
    """Show a toast with a progress bar."""
    print("\n[3] Showing notification with progress bar...")
    
    toast_xml = """
    <toast>
        <visual>
            <binding template="ToastGeneric">
                <text>⚙️ Processing Data</text>
                <text>Python task in progress...</text>
                <progress value="0.6" status="60% Complete" />
            </binding>
        </visual>
    </toast>
    """
    
    notification = AppNotification(toast_xml)
    AppNotificationManager.default.show(notification)
    
    print("✅ Progress toast notification sent!")
    print("   Shows a progress bar at 60%")


def show_reminder_toast():
    """Show a reminder-style toast with scenario."""
    print("\n[4] Showing reminder notification...")
    
    toast_xml = """
    <toast scenario="reminder">
        <visual>
            <binding template="ToastGeneric">
                <text>⏰ Python Reminder</text>
                <text>Don't forget to check your PyWinAppSDK tests!</text>
            </binding>
        </visual>
        <actions>
            <input id="snoozeTime" type="selection" defaultInput="15">
                <selection id="5" content="5 minutes" />
                <selection id="15" content="15 minutes" />
                <selection id="60" content="1 hour" />
            </input>
            <action activationType="system" arguments="snooze" content="Snooze" />
            <action activationType="system" arguments="dismiss" content="Dismiss" />
        </actions>
    </toast>
    """
    
    notification = AppNotification(toast_xml)
    AppNotificationManager.default.show(notification)
    
    print("✅ Reminder toast notification sent!")
    print("   This one stays on screen and has snooze options!")


def test_notifications():
    """Run all notification tests."""
    try:
        # Register for notifications first
        AppNotificationManager.default.register()
        print(f"✓ Registered AppNotificationManager")
        
        # Show different types of notifications with delays
        show_simple_toast()
        time.sleep(2)
        
        show_image_toast()
        time.sleep(2)
        
        show_progress_toast()
        time.sleep(2)
        
        show_reminder_toast()
        
        print("\n" + "=" * 60)
        print("✅ All notifications sent successfully!")
        print("=" * 60)
        print("\n💡 Check the bottom-right corner of your screen!")
        print("   You should see 4 different toast notifications:")
        print("\n   • Simple text notification")
        print("   • Rich notification with image and buttons")
        print("   • Progress bar notification (60% complete)")
        print("   • Reminder with snooze options")
        
        print("\n⏱️  Waiting 5 seconds before cleanup...")
        time.sleep(5)
        
        AppNotificationManager.default.unregister()
        print("✓ Unregistered notification manager")
        
        return True
        
    except OSError as e:
        if "package identity" in str(e).lower():
            print("\n❌ ERROR: No package identity detected!")
            print("\n📦 To fix this, you need Python with package identity:")
            print("\nOption 1 - Microsoft Store Python (Recommended):")
            print("  1. Install Python from Microsoft Store")
            print("  2. Create venv: python -m venv venv-store")
            print("  3. Activate: .\\venv-store\\Scripts\\Activate.ps1")
            print("  4. Install wheels from ../wheels/ directory")
            print("  5. Run this script")
            print("\nOption 2 - Sparse Package:")
            print("  1. Run: python register_sparse_package.py register")
            print("  2. Use: python register_sparse_package.py run notifications-demo.py")
        else:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🔔 Windows App SDK Toast Notifications Demo")
    print("=" * 60)
    print("\nThis will show VISIBLE toast notifications on your screen!")
    print("Requires: Python with package identity (Store Python)\n")
    
    try:
        # Use bootstrap to load Windows App SDK runtime
        # Store Python has package identity but doesn't have WinAppSDK framework dependency
        # So we use bootstrap to dynamically load it
        with initialize_windows_app_sdk(
            options=BootstrapInitializeOptions.ON_ERROR_SHOW_UI,
            verbose=True
        ):
            success = test_notifications()
            
            if success:
                print("\nPress Enter to exit...")
                input()
            
            sys.exit(0 if success else 1)
            
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)
