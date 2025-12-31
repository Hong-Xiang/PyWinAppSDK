using System;
using System.Numerics;
using Microsoft.UI.Composition;
using Microsoft.UI.Content;
using Microsoft.UI.Dispatching;
using Microsoft.UI.Windowing;

class Program
{
    // STA is required for WinRT/COM interop
    [STAThread]
    static int Main(string[] args)
    {
        Console.WriteLine("=== WinAppSDK Composition API Demo ===");
        Console.WriteLine("Using AppWindow + ContentIsland + DesktopChildSiteBridge");
        Console.WriteLine("(Minimal Win32 interop!)");
        Console.WriteLine();

        // 1. Create DispatcherQueue for the current thread
        var controller = DispatcherQueueController.CreateOnCurrentThread();
        var dispatcherQueue = controller.DispatcherQueue;
        Console.WriteLine("✓ DispatcherQueue created");

        // 2. Create Compositor
        using var compositor = new Compositor();
        Console.WriteLine("✓ Compositor created");

        // 3. Create AppWindow (high-level, no HWND management!)
        var appWindow = CreateAppWindow(dispatcherQueue);
        Console.WriteLine("✓ AppWindow created");

        // 4. Create ContentIsland with visual tree
        var contentIsland = CreateContentIsland(compositor);
        Console.WriteLine("✓ ContentIsland created");

        // 5. Create bridge and connect to window
        var bridge = CreateDesktopChildSiteBridge(compositor, appWindow, contentIsland);
        Console.WriteLine("✓ Bridge connected to AppWindow");

        // 6. Show window
        appWindow.Show();

        Console.WriteLine();
        Console.WriteLine("Window displayed! Close the window to exit.");
        Console.WriteLine();

        // 7. Modern message loop - no Win32 PInvoke needed!
        dispatcherQueue.RunEventLoop();

        Console.WriteLine("Event loop exited");

        // 8. Cleanup resources
        bridge?.Dispose();
        contentIsland?.Dispose();
        appWindow.Destroy();

        // 9. Properly shutdown the DispatcherQueue
        // This triggers cleanup and raises shutdown events
        controller?.ShutdownQueue();

        Console.WriteLine("✓ Application closed cleanly");
        return 0;
    }

    static AppWindow CreateAppWindow(DispatcherQueue dispatcherQueue)
    {
        // Create AppWindow and associate it with the DispatcherQueue
        // This enables automatic cleanup when DispatcherQueue shuts down
        var appWindow = AppWindow.Create();
        appWindow.Title = "WinAppSDK Composition API - AppWindow Demo";

        // CRITICAL: Associate AppWindow with DispatcherQueue for proper lifecycle management
        appWindow.AssociateWithDispatcherQueue(dispatcherQueue);

        // Set initial size
        appWindow.Resize(new Windows.Graphics.SizeInt32 { Width = 1000, Height = 800 });

        // Handle window closing
        appWindow.Closing += (sender, args) =>
        {
            Console.WriteLine("\nWindow closing...");
            // Exit the modern event loop
            dispatcherQueue?.EnqueueEventLoopExit();
        };

        appWindow.Destroying += (sender, args) =>
        {
            Console.WriteLine("Window destroying...");
        };

        return appWindow;
    }

    static ContentIsland CreateContentIsland(Compositor compositor)
    {
        // Create visual tree
        var rootVisual = compositor.CreateContainerVisual();
        rootVisual.RelativeSizeAdjustment = Vector2.One; // Fill parent

        // Add colorful animated visuals
        AddDemoVisuals(compositor, rootVisual);

        // Create ContentIsland (the modern replacement for DesktopWindowTarget)
        var contentIsland = ContentIsland.Create(rootVisual);

        return contentIsland;
    }

    static DesktopChildSiteBridge CreateDesktopChildSiteBridge(Compositor compositor, AppWindow appWindow, ContentIsland contentIsland)
    {
        // Connect ContentIsland to AppWindow via DesktopChildSiteBridge
        var bridge = DesktopChildSiteBridge.Create(compositor, appWindow.Id);
        bridge.Connect(contentIsland);
        bridge.Show();
        bridge.ResizePolicy = ContentSizePolicy.ResizeContentToParentWindow;

        return bridge;
    }

    static void AddDemoVisuals(Compositor compositor, ContainerVisual root)
    {
        // Background gradient
        var backgroundVisual = compositor.CreateSpriteVisual();
        backgroundVisual.RelativeSizeAdjustment = Vector2.One;

        var gradientBrush = compositor.CreateLinearGradientBrush();
        gradientBrush.StartPoint = Vector2.Zero;
        gradientBrush.EndPoint = new Vector2(1, 1);

        var stop1 = compositor.CreateColorGradientStop(0f, Windows.UI.Color.FromArgb(255, 20, 30, 50));
        var stop2 = compositor.CreateColorGradientStop(1f, Windows.UI.Color.FromArgb(255, 60, 20, 80));
        gradientBrush.ColorStops.Add(stop1);
        gradientBrush.ColorStops.Add(stop2);

        backgroundVisual.Brush = gradientBrush;
        root.Children.InsertAtBottom(backgroundVisual);

        // Animated square 1
        var square1 = compositor.CreateSpriteVisual();
        square1.Size = new Vector2(200, 200);
        square1.Offset = new Vector3(100, 100, 0);
        square1.Brush = compositor.CreateColorBrush(Windows.UI.Color.FromArgb(255, 0, 120, 215));

        var rotationAnimation = compositor.CreateScalarKeyFrameAnimation();
        rotationAnimation.Duration = TimeSpan.FromSeconds(5);
        rotationAnimation.InsertKeyFrame(0f, 0f);
        rotationAnimation.InsertKeyFrame(1f, 360f);
        rotationAnimation.IterationBehavior = AnimationIterationBehavior.Forever;
        square1.StartAnimation("RotationAngleInDegrees", rotationAnimation);
        square1.CenterPoint = new Vector3(100, 100, 0);

        root.Children.InsertAtTop(square1);

        // Animated square 2
        var square2 = compositor.CreateSpriteVisual();
        square2.Size = new Vector2(150, 150);
        square2.Offset = new Vector3(400, 250, 0);
        square2.Brush = compositor.CreateColorBrush(Windows.UI.Color.FromArgb(255, 0, 204, 153));

        var scaleAnimation = compositor.CreateVector3KeyFrameAnimation();
        scaleAnimation.Duration = TimeSpan.FromSeconds(3);
        scaleAnimation.InsertKeyFrame(0f, new Vector3(1f, 1f, 1f));
        scaleAnimation.InsertKeyFrame(0.5f, new Vector3(1.3f, 1.3f, 1f));
        scaleAnimation.InsertKeyFrame(1f, new Vector3(1f, 1f, 1f));
        scaleAnimation.IterationBehavior = AnimationIterationBehavior.Forever;
        square2.StartAnimation("Scale", scaleAnimation);
        square2.CenterPoint = new Vector3(75, 75, 0);

        root.Children.InsertAtTop(square2);

        // Circle with opacity animation
        var circle = compositor.CreateSpriteVisual();
        circle.Size = new Vector2(180, 180);
        circle.Offset = new Vector3(650, 150, 0);

        var circleBrush = compositor.CreateColorBrush(Windows.UI.Color.FromArgb(255, 255, 185, 0));
        circle.Brush = circleBrush;

        var roundedShape = compositor.CreateRoundedRectangleGeometry();
        roundedShape.Size = new Vector2(180, 180);
        roundedShape.CornerRadius = new Vector2(90, 90);

        var shapeVisual = compositor.CreateShapeVisual();
        shapeVisual.Size = new Vector2(180, 180);
        var spriteShape = compositor.CreateSpriteShape(roundedShape);
        spriteShape.FillBrush = circleBrush;
        shapeVisual.Shapes.Add(spriteShape);
        shapeVisual.Offset = new Vector3(650, 150, 0);

        var opacityAnimation = compositor.CreateScalarKeyFrameAnimation();
        opacityAnimation.Duration = TimeSpan.FromSeconds(2);
        opacityAnimation.InsertKeyFrame(0f, 1f);
        opacityAnimation.InsertKeyFrame(0.5f, 0.3f);
        opacityAnimation.InsertKeyFrame(1f, 1f);
        opacityAnimation.IterationBehavior = AnimationIterationBehavior.Forever;
        shapeVisual.StartAnimation("Opacity", opacityAnimation);

        root.Children.InsertAtTop(shapeVisual);

        Console.WriteLine("✓ Created animated visuals:");
        Console.WriteLine("  - Gradient background");
        Console.WriteLine("  - Rotating blue square");
        Console.WriteLine("  - Scaling teal square");
        Console.WriteLine("  - Pulsing yellow circle");
    }
}
