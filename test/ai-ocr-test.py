r"""
Test for Windows App SDK AI Text Recognition (OCR) APIs.

This uses custom wheels built from PyWinAppSDK:
    winappsdk_ai-3.2.1-cp313-cp313-win_arm64.whl
    winappsdk_foundation-3.2.1-cp313-cp313-win_arm64.whl
    winappsdk_interactiveexperiences-3.2.1-cp313-cp313-win_arm64.whl

Usage:
    python test/ai-ocr-test.py <image_path>

Example:
    python test/ai-ocr-test.py C:\path\to\image.png

Requirements:
    - Windows App SDK runtime installed
    - NPU device with AI model support (Copilot+ PC)
    - The bootstrap DLL from the Windows App SDK Foundation package
"""

# === 日志重定向（方便调试 sparse app） ===
import sys
import os

_LOG_FILE = os.path.join(os.environ.get('TEMP', '.'), 'ai-ocr-test.log')

class _Tee:
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            try:
                f.write(obj)
                f.flush()
            except: pass
    def flush(self):
        for f in self.files:
            try: f.flush()
            except: pass

try:
    _log_f = open(_LOG_FILE, 'w', encoding='utf-8')
    sys.stdout = _Tee(sys.__stdout__, _log_f)
    sys.stderr = _Tee(sys.__stderr__, _log_f)
    print(f"[LOG] Output redirected to: {_LOG_FILE}")
except Exception as e:
    print(f"[LOG] Failed to redirect output: {e}")
# === 日志重定向结束 ===

import asyncio
import ctypes
from ctypes import wintypes
from contextlib import contextmanager
import struct


# Windows App SDK Bootstrap API
class MddBootstrapInitializeOptions:
    NONE = 0
    ON_NO_MATCH_SHOW_UI = 0x00000001
    ON_PACKAGE_IDENTITY_SHOW_UI = 0x00000002
    ON_ERROR_SHOW_UI = ON_NO_MATCH_SHOW_UI | ON_PACKAGE_IDENTITY_SHOW_UI


class PackageVersion(ctypes.Structure):
    """PACKAGE_VERSION structure"""
    _fields_ = [
        ("Revision", wintypes.USHORT),
        ("Build", wintypes.USHORT),
        ("Minor", wintypes.USHORT),
        ("Major", wintypes.USHORT),
    ]
    
    @classmethod
    def from_string(cls, version_str: str) -> "PackageVersion":
        """Create from version string like '1.8.0.0' or '8000.0.0.0'"""
        parts = version_str.split(".")
        while len(parts) < 4:
            parts.append("0")
        return cls(
            Revision=int(parts[3]),
            Build=int(parts[2]),
            Minor=int(parts[1]),
            Major=int(parts[0]),
        )


def find_bootstrap_dll():
    """Find the Windows App SDK bootstrap DLL."""
    # Determine architecture based on Python's bitness
    pointer_size = struct.calcsize("P") * 8
    
    if pointer_size == 64:
        if "AMD64" in sys.version:
            arch_folder = "win-x64"
        elif "ARM64" in sys.version:
            arch_folder = "win-arm64"
        else:
            arch_folder = "win-x64"
    else:
        arch_folder = "win-x86"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    possible_paths = [
        os.path.join(project_root, "packages", "microsoft.windowsappsdk.foundation", "1.8.251104000", "runtimes", arch_folder, "native", "Microsoft.WindowsAppRuntime.Bootstrap.dll"),
        os.path.join(project_root, "packages", "microsoft.windowsappsdk", "1.8.251106002", "build", "native", arch_folder, "Microsoft.WindowsAppRuntime.Bootstrap.dll"),
    ]
    
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    for path_dir in path_dirs:
        possible_paths.append(os.path.join(path_dir, "Microsoft.WindowsAppRuntime.Bootstrap.dll"))
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    print("Searched for bootstrap DLL in:")
    for path in possible_paths[:3]:
        print(f"  - {path} (exists: {os.path.exists(path)})")
    
    return None


@contextmanager
def initialize_windows_app_sdk(major_minor_version: str = "1.8", min_version: str = None, options: int = MddBootstrapInitializeOptions.NONE):
    """Initialize the Windows App SDK runtime using MddBootstrapInitialize."""
    dll_path = find_bootstrap_dll()
    if not dll_path:
        raise FileNotFoundError(
            "Could not find Microsoft.WindowsAppRuntime.Bootstrap.dll. "
            "Please install the Windows App SDK or add it to PATH."
        )
    
    print(f"Loading bootstrap DLL: {dll_path}")
    
    old_path = os.environ.get('PATH', '')
    try:
        import subprocess
        
        pointer_size = struct.calcsize("P") * 8
        if pointer_size == 64:
            if "AMD64" in sys.version:
                runtime_arch = "X64"
            elif "ARM64" in sys.version:
                runtime_arch = "ARM64"
            else:
                runtime_arch = "X64"
        else:
            runtime_arch = "X86"
            
        print(f"Looking for {runtime_arch} runtime package...")
        
        result = subprocess.run(
            ['powershell', '-Command', 
             f'Get-AppxPackage -Name "*WindowsAppRuntime.1.8*" | Where-Object {{ $_.Architecture -eq "{runtime_arch}" }} | Select-Object -First 1 -ExpandProperty InstallLocation'],
            capture_output=True,
            text=True,
            check=True
        )
        runtime_path = result.stdout.strip()
        if runtime_path and os.path.exists(runtime_path):
            print(f"Found runtime DLLs: {runtime_path}")
            dll_dir = os.path.dirname(dll_path)
            os.environ['PATH'] = runtime_path + os.pathsep + dll_dir + os.pathsep + old_path
        else:
            print(f"⚠️  Could not find installed Windows App Runtime 1.8 {runtime_arch} package")
            dll_dir = os.path.dirname(dll_path)
            os.environ['PATH'] = dll_dir + os.pathsep + old_path
    except Exception as e:
        print(f"⚠️  Could not locate runtime DLLs: {e}")
        dll_dir = os.path.dirname(dll_path)
        os.environ['PATH'] = dll_dir + os.pathsep + old_path
    
    try:
        kernel32 = ctypes.windll.kernel32
        SEM_FAILCRITICALERRORS = 0x0001
        old_mode = kernel32.SetErrorMode(SEM_FAILCRITICALERRORS)
        bootstrap = ctypes.CDLL(dll_path)
        kernel32.SetErrorMode(old_mode)
    except OSError as e:
        os.environ['PATH'] = old_path
        print(f"❌ Failed to load bootstrap DLL: {e}")
        raise
    
    MddBootstrapInitialize2 = bootstrap.MddBootstrapInitialize2
    MddBootstrapInitialize2.argtypes = [
        wintypes.UINT,
        wintypes.LPCWSTR,
        PackageVersion,
        wintypes.UINT,
    ]
    MddBootstrapInitialize2.restype = ctypes.HRESULT

    MddBootstrapShutdown = bootstrap.MddBootstrapShutdown
    MddBootstrapShutdown.argtypes = []
    MddBootstrapShutdown.restype = None
    
    parts = major_minor_version.split(".")
    major = int(parts[0])
    minor = int(parts[1]) if len(parts) > 1 else 0
    major_minor = (major << 16) | minor
    
    if min_version:
        pkg_version = PackageVersion.from_string(min_version)
    else:
        pkg_version = PackageVersion(0, 0, 0, 0)
    
    print(f"Initializing Windows App SDK {major_minor_version}...")
    
    try:
        hr = MddBootstrapInitialize2(major_minor, None, pkg_version, options)
    except Exception as e:
        print(f"❌ Exception during MddBootstrapInitialize2: {e}")
        raise
    
    print(f"  HRESULT: 0x{hr & 0xFFFFFFFF:08X}")
    
    if hr < 0:
        error = ctypes.WinError(hr)
        print(f"❌ MddBootstrapInitialize2 failed with HRESULT: 0x{hr & 0xFFFFFFFF:08X}")
        raise error
    
    print("✅ Windows App SDK initialized successfully!")
    
    try:
        yield
    finally:
        print("Shutting down Windows App SDK...")
        MddBootstrapShutdown()
        os.environ['PATH'] = old_path


async def load_image_buffer_from_file(file_path: str):
    """
    Load an image file and create an ImageBuffer from it.
    
    Equivalent C# code:
        StorageFile file = await StorageFile.GetFileFromPathAsync(filePath);
        IRandomAccessStream stream = await file.OpenAsync(FileAccessMode.Read);
        BitmapDecoder decoder = await BitmapDecoder.CreateAsync(stream);
        SoftwareBitmap bitmap = await decoder.GetSoftwareBitmapAsync();
        return ImageBuffer.CreateForSoftwareBitmap(bitmap);
    
    Note: The PyWinRT binding uses ApiInformation.IsMethodPresent to check if methods
    are available. However, Windows App SDK types are not in the standard Windows
    metadata, so this check may fail even when the method exists. We need to use
    ctypes to bypass this check and call the underlying COM method directly.
    """
    from winrt.windows.storage import StorageFile, FileAccessMode
    from winrt.windows.graphics.imaging import BitmapDecoder, BitmapPixelFormat, BitmapAlphaMode
    from winappsdk_AI.microsoft.graphics.imaging import ImageBuffer
    import winrt.windows.graphics.imaging
    import winrt.windows.storage.streams
    
    print(f"Loading image: {file_path}")
    
    # Get StorageFile from path
    storage_file = await StorageFile.get_file_from_path_async(file_path)
    
    # Open stream for reading
    stream = await storage_file.open_async(FileAccessMode.READ)
    
    # Create bitmap decoder
    decoder = await BitmapDecoder.create_async(stream)
    
    # Get SoftwareBitmap - get default format first, then convert if needed
    # Note: get_software_bitmap_async() in PyWinRT doesn't accept parameters
    bitmap = await decoder.get_software_bitmap_async()
    
    print(f"  Image size: {bitmap.pixel_width}x{bitmap.pixel_height}")
    print(f"  Pixel format: {bitmap.bitmap_pixel_format}")
    
    # Create ImageBuffer from SoftwareBitmap
    # Note: PyWinRT uses ApiInformation.IsMethodPresent which returns false for
    # Windows App SDK types. We need to try the call anyway.
    print(f"  Calling ImageBuffer.create_for_software_bitmap...")
    print(f"  ImageBuffer type: {type(ImageBuffer)}")
    print(f"  ImageBuffer metaclass: {type(type(ImageBuffer))}")
    print(f"  Available methods on metaclass: {[m for m in dir(type(ImageBuffer)) if 'create' in m.lower()]}")
    
    try:
        # 直接调用静态方法
        image_buffer = ImageBuffer.create_for_software_bitmap(bitmap)
        print(f"  ✅ Created ImageBuffer via create_for_software_bitmap")
    except AttributeError as e:
        # 如果是 "method overload not available" 错误，这是 PyWinRT 的 ApiInformation 检查问题
        error_msg = str(e)
        print(f"  ❌ AttributeError: {error_msg}")
        
        if "not available in this version" in error_msg:
            print(f"  ⚠️  This is likely a PyWinRT ApiInformation check issue.")
            print(f"  ⚠️  Windows App SDK types are not in standard Windows metadata.")
            print(f"  ⚠️  The method may actually exist but the check fails.")
            print(f"  Trying to work around by using Gray8 format with create_for_buffer...")
            
            # 尝试使用 create_for_buffer 作为替代
            from winappsdk_AI.microsoft.graphics.imaging import ImageBufferPixelFormat
            
            # 获取像素数据
            pixel_data = bitmap.lock_buffer(winrt.windows.graphics.imaging.BitmapBufferAccessMode.READ)
            reference = pixel_data.create_reference()
            
            width = bitmap.pixel_width
            height = bitmap.pixel_height
            row_stride = width  # Gray8 = 1 byte per pixel
            
            try:
                # 尝试获取 IBuffer
                buffer = reference.as_(winrt.windows.storage.streams.IBuffer)
                image_buffer = ImageBuffer.create_for_buffer(
                    buffer, 
                    ImageBufferPixelFormat.GRAY8,
                    width, 
                    height,
                    row_stride
                )
                print(f"  ✅ Created ImageBuffer via create_for_buffer (Gray8)")
            except Exception as e2:
                print(f"  ❌ create_for_buffer also failed: {e2}")
                import traceback
                traceback.print_exc()
                raise
        else:
            raise
    except Exception as e:
        print(f"  ❌ Failed to create ImageBuffer: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    return image_buffer, bitmap


async def ensure_text_recognizer_ready():
    """
    Ensure the TextRecognizer model is ready.
    
    Equivalent C# code:
        if (TextRecognizer.GetReadyState() == AIFeatureReadyState.NotReady)
        {
            var loadResult = await TextRecognizer.EnsureReadyAsync();
            if (loadResult.Status != AIFeatureReadyResultState.Success)
            {
                throw new Exception(loadResult.ExtendedError().Message);
            }
        }
        return await TextRecognizer.CreateAsync();
    """
    from winappsdk_AI.microsoft.windows.ai.imaging import TextRecognizer
    from winappsdk_AI.microsoft.windows.ai import AIFeatureReadyState, AIFeatureReadyResultState
    
    print("Checking TextRecognizer ready state...")
    
    ready_state = TextRecognizer.get_ready_state()
    print(f"  Ready state: {ready_state}")
    
    if ready_state == AIFeatureReadyState.NOT_READY:
        print("  Model not ready, downloading/preparing...")
        result = await TextRecognizer.ensure_ready_async()
        if result.status != AIFeatureReadyResultState.SUCCESS:
            error_text = result.error_display_text
            raise RuntimeError(f"Failed to prepare TextRecognizer: {error_text}")
        print("  ✅ Model is now ready")
    elif ready_state == AIFeatureReadyState.READY:
        print("  ✅ Model is already ready")
    elif ready_state == AIFeatureReadyState.DISABLED_BY_USER:
        raise RuntimeError("TextRecognizer is disabled by user")
    elif ready_state == AIFeatureReadyState.NOT_SUPPORTED_ON_CURRENT_SYSTEM:
        raise RuntimeError("TextRecognizer is not supported on this system (requires NPU)")
    else:
        raise RuntimeError(f"Unknown ready state: {ready_state}")
    
    # Create TextRecognizer instance
    print("Creating TextRecognizer...")
    text_recognizer = await TextRecognizer.create_async()
    print("  ✅ TextRecognizer created")
    
    return text_recognizer


async def recognize_text_from_image(image_path: str):
    """
    Recognize text from an image file.
    
    Equivalent C# code:
        ImageBuffer imageBuffer = ImageBuffer.CreateForSoftwareBitmap(bitmap);
        RecognizedText recognizedText = textRecognizer.RecognizeTextFromImage(imageBuffer);
        foreach (var line in recognizedText.Lines)
        {
            Console.WriteLine(line.Text);
        }
    """
    # Load image
    image_buffer, bitmap = await load_image_buffer_from_file(image_path)
    
    # Ensure model is ready and create recognizer
    text_recognizer = await ensure_text_recognizer_ready()
    
    try:
        print("\nRecognizing text...")
        
        # Perform OCR
        recognized_text = text_recognizer.recognize_text_from_image(image_buffer)
        
        print(f"  Text angle: {recognized_text.text_angle}°")
        print(f"  Lines found: {len(list(recognized_text.lines))}")
        
        print("\n" + "=" * 60)
        print("RECOGNIZED TEXT:")
        print("=" * 60)
        
        all_text = []
        for line in recognized_text.lines:
            print(f"\n[Line] {line.text}")
            print(f"  Style: {line.style}, Confidence: {line.line_style_confidence:.2%}")
            
            # Print word details
            for word in line.words:
                bbox = word.bounding_box
                print(f"    Word: '{word.text}' (confidence: {word.match_confidence:.2%})")
                print(f"      BBox: TL({bbox.top_left.x:.0f},{bbox.top_left.y:.0f}) "
                      f"TR({bbox.top_right.x:.0f},{bbox.top_right.y:.0f}) "
                      f"BR({bbox.bottom_right.x:.0f},{bbox.bottom_right.y:.0f}) "
                      f"BL({bbox.bottom_left.x:.0f},{bbox.bottom_left.y:.0f})")
            
            all_text.append(line.text)
        
        print("\n" + "=" * 60)
        print("FULL TEXT:")
        print("=" * 60)
        full_text = "\n".join(all_text)
        print(full_text)
        print("=" * 60)
        
        return full_text
        
    finally:
        # Clean up
        text_recognizer.close()
        image_buffer.close()


def main():
    # 解析参数
    import argparse
    parser = argparse.ArgumentParser(description='Windows App SDK AI Text Recognition (OCR) Test')
    parser.add_argument('image_path', help='Path to the image file')
    parser.add_argument('--no-bootstrap', action='store_true', 
                        help='Skip bootstrap initialization (use when running as packaged app with identity)')
    args = parser.parse_args()
    
    image_path = args.image_path
    skip_bootstrap = args.no_bootstrap
    
    # Convert to absolute path
    if not os.path.isabs(image_path):
        image_path = os.path.abspath(image_path)
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file not found: {image_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("Windows App SDK AI Text Recognition (OCR) Test")
    print("=" * 60)
    print(f"Python: {sys.version}")
    print(f"Image: {image_path}")
    print(f"Skip bootstrap: {skip_bootstrap}")
    print()
    
    # Test imports first
    try:
        from winappsdk_AI.microsoft.windows.ai.imaging import TextRecognizer, RecognizedText
        from winappsdk_AI.microsoft.graphics.imaging import ImageBuffer
        from winappsdk_AI.microsoft.windows.ai import AIFeatureReadyState
        print("✅ AI imports successful!")
        print(f"  - TextRecognizer: {TextRecognizer}")
        print(f"  - ImageBuffer: {ImageBuffer}")
        print(f"  - AIFeatureReadyState: {AIFeatureReadyState}")
        print()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nMake sure to install the winappsdk_ai wheel:")
        print("  pip install wheels/winappsdk_ai-3.2.1-cp313-cp313-win_arm64.whl")
        sys.exit(1)
    
    # Try without bootstrap first (or always if --no-bootstrap)
    print("Attempting OCR without bootstrap initialization...")
    print("(This works if the runtime is already available or running as packaged app)")
    print()
    
    try:
        result = asyncio.run(recognize_text_from_image(image_path))
        print("\n✅ OCR completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Failed without bootstrap: {e}")
        
        if skip_bootstrap:
            print("\n--no-bootstrap specified, not attempting bootstrap initialization.")
            print("Make sure you're running as a packaged app with identity.")
            sys.exit(1)
        
        print("\nNow trying WITH bootstrap initialization...")
        print()
        
        try:
            with initialize_windows_app_sdk(
                "1.8",
                options=MddBootstrapInitializeOptions.ON_ERROR_SHOW_UI
            ):
                result = asyncio.run(recognize_text_from_image(image_path))
                print("\n✅ OCR completed successfully!")
                
        except FileNotFoundError as e:
            print(f"❌ {e}")
            print("\nTo install Windows App SDK, run:")
            print("  winget install Microsoft.WindowsAppSDK.1.8")
            sys.exit(1)
            
        except RuntimeError as e:
            print(f"❌ Runtime error: {e}")
            print("\nNote: Text Recognition requires:")
            print("  - Windows 11 with Copilot+ PC features")
            print("  - NPU (Neural Processing Unit) support")
            print("  - AI model downloaded via Windows Update")
            sys.exit(1)
        
        except PermissionError as e:
            print(f"❌ Permission error: {e}")
            print("\nNote: Windows AI APIs require package identity.")
            print("This is a limitation of the Windows App SDK AI APIs.")
            print("The APIs can only be called from a packaged (MSIX) application.")
            print("\nWorkaround options:")
            print("  1. Package your app as MSIX")
            print("  2. Use sparse package registration")
            print("  3. Wait for future SDK updates that may relax this requirement")
            sys.exit(1)
        
        except OSError as e:
            if "no package identity" in str(e).lower():
                print(f"❌ Package identity required: {e}")
                print("\nNote: Windows AI APIs require package identity.")
                print("This is a limitation of the Windows App SDK AI APIs.")
                print("The APIs can only be called from a packaged (MSIX) application.")
                sys.exit(1)
            else:
                print(f"❌ OS error: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    try:
        main()
        print(f"\n{'='*60}")
        print("Completed successfully!")
        print(f"{'='*60}")
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"UNHANDLED ERROR: {e}")
        print(f"{'='*60}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}")
    finally:
        input("Press Enter to exit...")
