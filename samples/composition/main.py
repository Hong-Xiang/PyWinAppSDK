"""
Windows App SDK Composition API Demo with AppWindow
Translated from C# demo: wincomp.cs

This demonstrates the modern WinAppSDK Composition API using:
- AppWindow (high-level window management, no Win32 HWND!)
- ContentIsland (modern content hosting)
- DesktopChildSiteBridge (connects ContentIsland to AppWindow)
- Compositor (visual tree and animations)

This approach avoids Win32 PInvoke and provides a clean, modern API.

⚠️ REQUIREMENTS:
   - Python from Microsoft Store (has package identity built-in)
   - OR use register_sparse_package.py to add package identity

Setup:
   1. Install Python from Microsoft Store
   2. Create venv: python -m venv venv-store
   3. Activate: .\\venv-store\\Scripts\\Activate.ps1
   4. Install: pip install --find-links wheels winappsdk-foundation winappsdk-interactiveexperiences
   5. Run: python test/composition-appwindow-test.py

Run:
    python composition-appwindow-test.py
"""

import sys
from datetime import timedelta

# Import Windows App SDK bootstrap
from winappsdk.bootstrap import initialize_windows_app_sdk, BootstrapInitializeOptions

# Import Composition APIs
from winappsdk.microsoft.ui.composition import (
    Compositor,
    ContainerVisual,
    SpriteVisual,
    AnimationIterationBehavior,
    ShapeVisual,
    CompositionColorBrush,
    CompositionLinearGradientBrush,
    CompositionColorGradientStop,
    CompositionRoundedRectangleGeometry,
    CompositionSpriteShape,
)

# Import Content APIs
from winappsdk.microsoft.ui.content import (
    ContentIsland,
    DesktopChildSiteBridge,
    ContentSizePolicy,
)

# Import Dispatching APIs  
from winappsdk.microsoft.ui.dispatching import (
    DispatcherQueueController,
)

# Import Windowing APIs
from winappsdk.microsoft.ui.windowing import (
    AppWindow,
)

# Import Windows Runtime support
from winrt.windows.ui import Color
from winrt.windows.graphics import SizeInt32
import winrt.windows.foundation.numerics as numerics


def create_app_window(dispatcher_queue):
    """Create AppWindow and associate it with DispatcherQueue."""
    print("Creating AppWindow...")
    
    # Create AppWindow
    app_window = AppWindow.create()
    app_window.title = "WinAppSDK Composition API - AppWindow Demo (Python)"
    
    # CRITICAL: Associate AppWindow with DispatcherQueue for proper lifecycle management
    app_window.associate_with_dispatcher_queue(dispatcher_queue)
    
    # Set initial size
    app_window.resize(SizeInt32(width=1000, height=800))
    
    # Handle window closing
    def on_closing(sender, args):
        print("\nWindow closing...")
        # Exit the modern event loop
        dispatcher_queue.enqueue_event_loop_exit()
    
    def on_destroying(sender, args):
        print("Window destroying...")
    
    app_window.add_closing(on_closing)
    app_window.add_destroying(on_destroying)
    
    print("✓ AppWindow created")
    return app_window


def create_content_island(compositor):
    """Create ContentIsland with visual tree."""
    print("Creating ContentIsland...")
    
    # Create visual tree
    root_visual = compositor.create_container_visual()
    root_visual.relative_size_adjustment = numerics.Vector2(1.0, 1.0)  # Fill parent
    
    # Add colorful animated visuals
    add_demo_visuals(compositor, root_visual)
    
    # Create ContentIsland (the modern replacement for DesktopWindowTarget)
    content_island = ContentIsland.create(root_visual)
    
    print("✓ ContentIsland created")
    return content_island


def create_desktop_child_site_bridge(compositor, app_window, content_island):
    """Connect ContentIsland to AppWindow via DesktopChildSiteBridge."""
    print("Creating DesktopChildSiteBridge...")
    
    # Connect ContentIsland to AppWindow via DesktopChildSiteBridge
    bridge = DesktopChildSiteBridge.create(compositor, app_window.id)
    bridge.connect(content_island)
    bridge.show()
    bridge.resize_policy = ContentSizePolicy.RESIZE_CONTENT_TO_PARENT_WINDOW
    
    print("✓ Bridge connected to AppWindow")
    return bridge


def add_demo_visuals(compositor, root):
    """Add animated demo visuals to the root container."""
    
    # === Background gradient ===
    background_visual = compositor.create_sprite_visual()
    background_visual.relative_size_adjustment = numerics.Vector2(1.0, 1.0)
    
    gradient_brush = compositor.create_linear_gradient_brush()
    gradient_brush.start_point = numerics.Vector2(0.0, 0.0)
    gradient_brush.end_point = numerics.Vector2(1.0, 1.0)
    
    stop1 = compositor.create_color_gradient_stop_with_offset_and_color(
        0.0, Color(a=255, r=20, g=30, b=50)
    )
    stop2 = compositor.create_color_gradient_stop_with_offset_and_color(
        1.0, Color(a=255, r=60, g=20, b=80)
    )
    gradient_brush.color_stops.append(stop1)
    gradient_brush.color_stops.append(stop2)
    
    background_visual.brush = gradient_brush
    root.children.insert_at_bottom(background_visual)
    
    # === Animated square 1: Rotation ===
    square1 = compositor.create_sprite_visual()
    square1.size = numerics.Vector2(200.0, 200.0)
    square1.offset = numerics.Vector3(100.0, 100.0, 0.0)
    square1.brush = compositor.create_color_brush_with_color(
        Color(a=255, r=0, g=120, b=215)  # Windows blue
    )
    
    # Rotation animation
    rotation_animation = compositor.create_scalar_key_frame_animation()
    rotation_animation.duration = timedelta(seconds=5)
    rotation_animation.insert_key_frame(0.0, 0.0)
    rotation_animation.insert_key_frame(1.0, 360.0)
    rotation_animation.iteration_behavior = AnimationIterationBehavior.FOREVER
    square1.center_point = numerics.Vector3(100.0, 100.0, 0.0)
    square1.start_animation("RotationAngleInDegrees", rotation_animation)
    
    root.children.insert_at_top(square1)
    
    # === Animated square 2: Scale ===
    square2 = compositor.create_sprite_visual()
    square2.size = numerics.Vector2(150.0, 150.0)
    square2.offset = numerics.Vector3(400.0, 250.0, 0.0)
    square2.brush = compositor.create_color_brush_with_color(
        Color(a=255, r=0, g=204, b=153)  # Teal
    )
    
    # Scale animation
    scale_animation = compositor.create_vector3_key_frame_animation()
    scale_animation.duration = timedelta(seconds=3)
    scale_animation.insert_key_frame(0.0, numerics.Vector3(1.0, 1.0, 1.0))
    scale_animation.insert_key_frame(0.5, numerics.Vector3(1.3, 1.3, 1.0))
    scale_animation.insert_key_frame(1.0, numerics.Vector3(1.0, 1.0, 1.0))
    scale_animation.iteration_behavior = AnimationIterationBehavior.FOREVER
    square2.center_point = numerics.Vector3(75.0, 75.0, 0.0)
    square2.start_animation("Scale", scale_animation)
    
    root.children.insert_at_top(square2)
    
    # === Circle with opacity animation ===
    circle_brush = compositor.create_color_brush_with_color(
        Color(a=255, r=255, g=185, b=0)  # Gold/yellow
    )
    
    rounded_shape = compositor.create_rounded_rectangle_geometry()
    rounded_shape.size = numerics.Vector2(180.0, 180.0)
    rounded_shape.corner_radius = numerics.Vector2(90.0, 90.0)  # Makes it a circle
    
    shape_visual = compositor.create_shape_visual()
    shape_visual.size = numerics.Vector2(180.0, 180.0)
    
    sprite_shape = compositor.create_sprite_shape_with_geometry(rounded_shape)
    sprite_shape.fill_brush = circle_brush
    shape_visual.shapes.append(sprite_shape)
    shape_visual.offset = numerics.Vector3(650.0, 150.0, 0.0)
    
    # Opacity animation
    opacity_animation = compositor.create_scalar_key_frame_animation()
    opacity_animation.duration = timedelta(seconds=2)
    opacity_animation.insert_key_frame(0.0, 1.0)
    opacity_animation.insert_key_frame(0.5, 0.3)
    opacity_animation.insert_key_frame(1.0, 1.0)
    opacity_animation.iteration_behavior = AnimationIterationBehavior.FOREVER
    shape_visual.start_animation("Opacity", opacity_animation)
    
    root.children.insert_at_top(shape_visual)
    
    print("✓ Created animated visuals:")
    print("  - Gradient background")
    print("  - Rotating blue square")
    print("  - Scaling teal square")
    print("  - Pulsing yellow circle")


def main():
    """Main entry point."""
    print("=== WinAppSDK Composition API Demo (Python) ===")
    print("Using AppWindow + ContentIsland + DesktopChildSiteBridge")
    print("(Minimal Win32 interop!)")
    print()

    try:
        # Initialize Windows App SDK
        print("Initializing Windows App SDK...")
        options = BootstrapInitializeOptions.ON_ERROR_SHOW_UI
        
        with initialize_windows_app_sdk(options=options, verbose=True):
            print("✓ Windows App SDK initialized")
            
            # 1. Create DispatcherQueue for the current thread
            print("\nCreating DispatcherQueue...")
            controller = DispatcherQueueController.create_on_current_thread()
            dispatcher_queue = controller.dispatcher_queue
            print("✓ DispatcherQueue created")
            
            # 2. Create Compositor
            print("\nCreating Compositor...")
            compositor = Compositor()
            print("✓ Compositor created")
            
            # 3. Create AppWindow (high-level, no HWND management!)
            app_window = create_app_window(dispatcher_queue)
            
            # 4. Create ContentIsland with visual tree
            content_island = create_content_island(compositor)
            
            # 5. Create bridge and connect to window
            bridge = create_desktop_child_site_bridge(compositor, app_window, content_island)
            
            # 6. Show window
            app_window.show()
            
            print()
            print("Window displayed! Close the window to exit.")
            print()
            
            # 7. Modern message loop - no Win32 PInvoke needed!
            dispatcher_queue.run_event_loop()
            
            print("Event loop exited")
            
            # 8. Cleanup resources
            if bridge:
                bridge.close()
            if content_island:
                content_island.close()
            if app_window:
                app_window.destroy()
            
            # 9. Properly shutdown the DispatcherQueue
            # This triggers cleanup and raises shutdown events
            if controller:
                controller.shutdown_queue()
            
            print("✓ Application closed cleanly")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0
        
  
if __name__ == "__main__":
    sys.exit(main())
