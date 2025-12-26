r"""
Windows 11 Widget Provider - Full Example

This creates a COM server that provides a visible widget to Windows 11 Widgets Board.

Requirements:
    - Windows 11
    - Administrator rights for registration
    - PyWinAppSDK wheels installed

Setup:
    1. Run: python widget-register.py (creates registry entries)
    2. Run: python widget-provider-example.py (starts the provider server)
    3. Open Widgets Board (Win+W)
    4. Click "+" to add widgets, find "PyWinAppSDK Test Widget"
    5. Pin it to see the widget

To unregister:
    python widget-register.py --unregister
"""

import sys
import json
import time
import threading
from winappsdk.bootstrap import initialize_windows_app_sdk, BootstrapInitializeOptions
from winappsdk.microsoft.windows.widgets.providers import (
    IWidgetProvider,
    IWidgetProvider2,
    WidgetManager,
    WidgetContext,
    WidgetUpdateRequestOptions,
)

# Widget Provider Implementation
class PyTestWidgetProvider:
    """Implementation of IWidgetProvider for a simple test widget."""
    
    def __init__(self):
        self.active_widgets = {}
        print("✓ PyTestWidgetProvider initialized")
    
    def create_widget(self, context):
        """Called when a widget instance is created (user pins it)."""
        widget_id = context.id
        print(f"📌 Widget created: {widget_id}")
        self.active_widgets[widget_id] = context
        
        # Send initial content
        self.update_widget(widget_id)
    
    def delete_widget(self, widget_id):
        """Called when a widget is removed."""
        print(f"🗑️  Widget deleted: {widget_id}")
        if widget_id in self.active_widgets:
            del self.active_widgets[widget_id]
    
    def on_action_invoked(self, args):
        """Called when user interacts with the widget."""
        print(f"🖱️  Action invoked: {args.verb}")
        widget_id = args.widget_context.id
        self.update_widget(widget_id, click_count=True)
    
    def on_widget_context_changed(self, args):
        """Called when widget context changes (size, etc)."""
        print(f"🔄 Context changed for widget: {args.widget_context.id}")
    
    def update_widget(self, widget_id, click_count=False):
        """Update widget content with current data."""
        template = self.create_adaptive_card(click_count)
        data = json.dumps({})
        
        try:
            update_options = WidgetUpdateRequestOptions(widget_id)
            update_options.template = template
            update_options.data = data
            
            # Send update to widget
            manager = WidgetManager.get_default()
            manager.update_widget(update_options)
            print(f"✓ Widget {widget_id} updated")
        except Exception as e:
            print(f"❌ Failed to update widget: {e}")
    
    def create_adaptive_card(self, clicked=False):
        """Create the visual content (Adaptive Card JSON)."""
        current_time = time.strftime("%I:%M:%S %p")
        
        card = {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.5",
            "body": [
                {
                    "type": "Container",
                    "style": "emphasis",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "🐍 PyWinAppSDK Widget",
                            "size": "Large",
                            "weight": "Bolder",
                            "color": "Accent"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Live from Python! {current_time}",
                            "size": "Medium",
                            "wrap": True,
                            "color": "Good" if clicked else "Default"
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {"title": "Status:", "value": "🟢 Running"},
                                {"title": "Language:", "value": "Python 3.12"},
                                {"title": "SDK:", "value": "Windows App SDK"},
                                {"title": "Updated:", "value": current_time}
                            ]
                        }
                    ]
                },
                {
                    "type": "ActionSet",
                    "actions": [
                        {
                            "type": "Action.Execute",
                            "title": "🔄 Refresh",
                            "verb": "refresh"
                        }
                    ]
                }
            ]
        }
        
        return json.dumps(card)


def run_widget_provider():
    """Run the widget provider server."""
    print("=" * 60)
    print("🚀 Starting PyWinAppSDK Widget Provider")
    print("=" * 60)
    
    with initialize_windows_app_sdk(
        options=BootstrapInitializeOptions.ON_ERROR_SHOW_UI,
        verbose=True
    ):
        print("\n✅ Windows App SDK initialized")
        
        # Create provider instance
        provider = PyTestWidgetProvider()
        
        print("\n📋 Provider Instructions:")
        print("  1. This provider is now running")
        print("  2. Open Widgets Board: Press Win+W")
        print("  3. Click '+' to add widgets")
        print("  4. Look for 'PyWinAppSDK Test Widget'")
        print("  5. Pin it to see the widget!")
        print("\n⚠️  Keep this window open - closing will stop the provider")
        print("\nPress Ctrl+C to stop the provider...\n")
        
        # Keep provider running
        try:
            while True:
                # Update all active widgets every 10 seconds
                for widget_id in list(provider.active_widgets.keys()):
                    provider.update_widget(widget_id)
                time.sleep(10)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping widget provider...")
            print("✓ Provider stopped")


if __name__ == "__main__":
    try:
        run_widget_provider()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
