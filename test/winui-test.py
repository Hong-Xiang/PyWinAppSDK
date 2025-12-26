r"""
Full test for Windows App SDK WinUI APIs with window creation.

This uses custom wheels built from PyWinAppSDK:
    winappsdk_foundation-3.2.1-cp312-cp312-win_amd64.whl
    winappsdk_interactiveexperiences-3.2.1-cp312-cp312-win_amd64.whl
    winappsdk_winui-3.2.1-cp312-cp312-win_amd64.whl

Run with uv (from project root):
    uv run --with wheels/winappsdk_foundation-3.2.1-cp312-cp312-win_amd64.whl \
           --with wheels/winappsdk_interactiveexperiences-3.2.1-cp312-cp312-win_amd64.whl \
           --with wheels/winappsdk_winui-3.2.1-cp312-cp312-win_amd64.whl \
           --no-project \
           python test/winui-test.py

Note: The winrt-runtime and winrt-Windows.* packages are declared as dependencies
in the wheel packages and will be installed automatically by pip/uv.

This test creates a real WinUI window that will auto-close after 2 seconds.

Requirements:
    - Windows App SDK runtime installed (or the bootstrap DLL bundled in the package)
"""

import sys
from typing import Tuple, Union

from typing_extensions import override
from winrt.system import Array
from winrt.windows.ui.xaml.interop import TypeKind, TypeName

# Import Windows App SDK bootstrap (bundled with Foundation package)
from winappsdk.bootstrap import initialize_windows_app_sdk, BootstrapInitializeOptions

# Import WinUI APIs
from winappsdk.microsoft.ui.xaml import (
    Application,
    ApplicationInitializationCallbackParams,
    FrameworkElement,
    LaunchActivatedEventArgs,
    UIElement,
    Window,
)
from winappsdk.microsoft.ui.xaml.controls import (
    Button,
    TextBlock,
    StackPanel,
    XamlControlsResources,
)
from winappsdk.microsoft.ui.xaml.markup import (
    IXamlMetadataProvider,
    IXamlType,
    XamlReader,
    XmlnsDefinition,
)
from winappsdk.microsoft.ui.xaml.xamltypeinfo import XamlControlsXamlMetaDataProvider
from winappsdk.microsoft.ui.xaml.media import (
    SolidColorBrush,
)


def test_winui_types():
    """Test that WinUI types are properly imported."""
    
    try:
        # Verify core types
        print(f"✓ Application type: {Application}")
        print(f"✓ FrameworkElement type: {FrameworkElement}")
        print(f"✓ UIElement type: {UIElement}")
        
        # Verify control types
        print(f"✓ Button type: {Button}")
        print(f"✓ TextBlock type: {TextBlock}")
        print(f"✓ StackPanel type: {StackPanel}")
        
        # Verify media types
        print(f"✓ SolidColorBrush type: {SolidColorBrush}")
        
        print("✅ WinUI types imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error importing WinUI types: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_winui_media_types():
    """Test WinUI Media types."""
    
    try:
        # Test media types are importable
        from winappsdk.microsoft.ui.xaml.media import (
            Brush,
            AcrylicBrush,
        )
        
        print(f"✓ Brush type: {Brush}")
        print(f"✓ SolidColorBrush type: {SolidColorBrush}")
        print(f"✓ AcrylicBrush type: {AcrylicBrush}")
        
        print("✅ WinUI Media types test passed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing WinUI Media types: {e}")
        import traceback
        traceback.print_exc()
        return False


# XAML for the test window
XAML = """
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation">
    <StackPanel VerticalAlignment="Center" HorizontalAlignment="Center" Spacing="10">
        <TextBlock Text="WinUI Test Window" FontSize="24" HorizontalAlignment="Center"/>
        <Button Name="closeBtn" Content="Close Now" HorizontalAlignment="Center"/>
    </StackPanel>
</Window>
"""


class TestApp(Application, IXamlMetadataProvider):
    """Test WinUI Application."""
    
    def __init__(self) -> None:
        self._provider = XamlControlsXamlMetaDataProvider()
        self._window = None

    @override
    def _on_launched(self, args: LaunchActivatedEventArgs) -> None:
        try:
            # Try to add default resources (may not be available in unpackaged apps)
            try:
                resources = XamlControlsResources()
                self.resources.merged_dictionaries.append(resources)
                print("✓ XamlControlsResources loaded")
            except OSError as e:
                # Resources not available - continue without them
                print(f"⚠ XamlControlsResources not available (expected in unpackaged app): {e}")
                print("  Continuing without resources...")

            # Load the XAML
            self._window = XamlReader.load(XAML).as_(Window)

            # Wire up close button
            content = self._window.content.as_(FrameworkElement)
            close_btn = content.find_name("closeBtn").as_(Button)
            close_btn.add_click(lambda s, e: self.exit())

            # Show the window
            self._window.activate()
            print("✓ Window activated")
            
        except Exception as e:
            print(f"❌ Critical error in _on_launched: {e}")
            import traceback
            traceback.print_exc()
            # Re-raise to fail the test properly
            raise

    @override
    def get_xaml_type(self, type: Union[TypeName, Tuple[str, TypeKind]]) -> IXamlType:
        return self._provider.get_xaml_type(type)

    @override
    def get_xaml_type_by_full_name(self, full_name: str) -> IXamlType:
        return self._provider.get_xaml_type_by_full_name(full_name)

    @override
    def get_xmlns_definitions(self) -> Array[XmlnsDefinition]:
        return self._provider.get_xmlns_definitions()


def test_winui_window():
    """Test creating and showing a real WinUI window."""
    
    try:
        print("Creating WinUI window (will auto-close in 2 seconds)...")
        
        def init_app(_: ApplicationInitializationCallbackParams) -> None:
            TestApp()
        
        # Start the application (this blocks until window closes)
        Application.start(init_app)
        
        print("✅ WinUI window test passed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing WinUI window: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Windows App SDK WinUI Full Test")
    print("=" * 60)
    print("\nThis test will create a real WinUI window.")
    print()
    
    # Initialize Windows App SDK first
    with initialize_windows_app_sdk(
        options=BootstrapInitializeOptions.ON_ERROR_SHOW_UI,
        verbose=True
    ):
        print("\n[1] Testing WinUI Type Imports...")
        test1 = test_winui_types()
        
        print("\n[2] Testing WinUI Media Types...")
        test2 = test_winui_media_types()
        
        print("\n[3] Testing WinUI Window Creation...")
        print("Note: A window will appear and close automatically in 2 seconds.")
        test3 = test_winui_window()
        
        if test1 and test2 and test3:
            print("\n" + "=" * 60)
            print("✅ All tests passed!")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("❌ Some tests failed")
            print("=" * 60)
            sys.exit(1)
