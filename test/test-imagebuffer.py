"""
Test ImageBuffer construction APIs from Windows App SDK.
This should NOT require package identity.
"""
import asyncio
import sys
import os

print("=" * 60)
print("ImageBuffer Construction Test")
print("=" * 60)
print(f"Python: {sys.version}")
print()

# Test 1: Check imports and available methods
print("Test 1: Checking imports and available methods...")
try:
    from winappsdk_AI.microsoft.graphics.imaging import ImageBuffer, ImageBufferPixelFormat
    print(f"  ✅ ImageBuffer imported: {ImageBuffer}")
    print(f"  ✅ ImageBufferPixelFormat imported: {ImageBufferPixelFormat}")
    
    # Check ImageBuffer type info
    print(f"\n  ImageBuffer type: {type(ImageBuffer)}")
    print(f"  ImageBuffer metaclass: {type(type(ImageBuffer))}")
    
    # List methods on the metaclass (static methods)
    metaclass = type(ImageBuffer)
    static_methods = [m for m in dir(metaclass) if not m.startswith('_')]
    print(f"  Static methods on metaclass: {static_methods}")
    
    # List instance methods
    instance_methods = [m for m in dir(ImageBuffer) if not m.startswith('_')]
    print(f"  Instance methods: {instance_methods}")
    
    # Check create methods
    print(f"\n  create_for_software_bitmap: {getattr(ImageBuffer, 'create_for_software_bitmap', 'NOT FOUND')}")
    print(f"  create_for_buffer: {getattr(ImageBuffer, 'create_for_buffer', 'NOT FOUND')}")
    
except ImportError as e:
    print(f"  ❌ Import error: {e}")
    sys.exit(1)

# Test 2: Load a SoftwareBitmap
print("\n" + "=" * 60)
print("Test 2: Loading SoftwareBitmap from image file...")

async def test_load_bitmap():
    from winrt.windows.storage import StorageFile, FileAccessMode
    from winrt.windows.graphics.imaging import BitmapDecoder, BitmapPixelFormat, BitmapAlphaMode
    
    image_path = r"C:\Users\leilzh\Pictures\Screenshots\test-ocr.png"
    if not os.path.exists(image_path):
        print(f"  ⚠️ Image not found: {image_path}")
        # Create a simple test image
        image_path = os.path.join(os.environ.get('TEMP', '.'), 'test-image.png')
        print(f"  Creating test image: {image_path}")
        
        # Use PIL if available, otherwise skip
        try:
            from PIL import Image
            img = Image.new('RGB', (100, 100), color='red')
            img.save(image_path)
            print(f"  ✅ Created test image")
        except ImportError:
            print(f"  ❌ PIL not available, cannot create test image")
            return None
    
    print(f"  Loading: {image_path}")
    
    storage_file = await StorageFile.get_file_from_path_async(image_path)
    stream = await storage_file.open_async(FileAccessMode.READ)
    decoder = await BitmapDecoder.create_async(stream)
    
    # Get bitmap in default format first
    bitmap_default = await decoder.get_software_bitmap_async()
    print(f"  ✅ Loaded bitmap (default): {bitmap_default.pixel_width}x{bitmap_default.pixel_height}, format={bitmap_default.bitmap_pixel_format}")
    
    # Convert to Gray8 using SoftwareBitmap.convert()
    try:
        bitmap_gray8 = bitmap_default.convert(BitmapPixelFormat.GRAY8, BitmapAlphaMode.IGNORE)
        print(f"  ✅ Converted to Gray8: {bitmap_gray8.pixel_width}x{bitmap_gray8.pixel_height}, format={bitmap_gray8.bitmap_pixel_format}")
    except Exception as e:
        print(f"  ⚠️ Could not convert to Gray8: {e}")
        bitmap_gray8 = None
    
    # Convert to BGRA8
    try:
        bitmap_bgra8 = bitmap_default.convert(BitmapPixelFormat.BGRA8, BitmapAlphaMode.PREMULTIPLIED)
        print(f"  ✅ Converted to BGRA8: {bitmap_bgra8.pixel_width}x{bitmap_bgra8.pixel_height}, format={bitmap_bgra8.bitmap_pixel_format}")
    except Exception as e:
        print(f"  ⚠️ Could not convert to BGRA8: {e}")
        bitmap_bgra8 = None
    
    return bitmap_default, bitmap_gray8, bitmap_bgra8

try:
    bitmaps = asyncio.run(test_load_bitmap())
    if bitmaps is None:
        print("  ⚠️ Skipping bitmap tests")
        bitmaps = (None, None, None)
except Exception as e:
    print(f"  ❌ Error loading bitmap: {e}")
    import traceback
    traceback.print_exc()
    bitmaps = (None, None, None)

# Test 3: Try to create ImageBuffer from SoftwareBitmap
print("\n" + "=" * 60)
print("Test 3: Creating ImageBuffer from SoftwareBitmap...")

if bitmaps[0] is not None:
    bitmap_default, bitmap_gray8, bitmap_bgra8 = bitmaps
    
    for name, bitmap in [("default", bitmap_default), ("Gray8", bitmap_gray8), ("BGRA8", bitmap_bgra8)]:
        print(f"\n  Trying with {name} bitmap...")
        try:
            image_buffer = ImageBuffer.create_for_software_bitmap(bitmap)
            print(f"    ✅ SUCCESS! ImageBuffer created: {image_buffer}")
            print(f"    Properties: {image_buffer.pixel_width}x{image_buffer.pixel_height}, format={image_buffer.pixel_format}")
            image_buffer.close()
        except AttributeError as e:
            print(f"    ❌ AttributeError: {e}")
            if "not available in this version" in str(e):
                print(f"    ⚠️ This is the PyWinRT ApiInformation check failing!")
        except OSError as e:
            error_code = getattr(e, 'winerror', None)
            print(f"    ❌ OSError: {e}")
            print(f"    Error code: {error_code} (0x{error_code & 0xFFFFFFFF:08X})" if error_code else "")
            if error_code == -2147009196:
                print(f"    ⚠️ This means 'no package identity' - this API requires package identity!")
        except Exception as e:
            print(f"    ❌ {type(e).__name__}: {e}")

# Test 4: Try to create ImageBuffer from IBuffer
print("\n" + "=" * 60)
print("Test 4: Creating ImageBuffer from IBuffer...")

if bitmaps[1] is not None:  # Use Gray8 bitmap
    bitmap = bitmaps[1]
    
    try:
        import winrt.windows.graphics.imaging as imaging
        import winrt.windows.storage.streams as streams
        
        # Lock buffer and get reference
        pixel_data = bitmap.lock_buffer(imaging.BitmapBufferAccessMode.READ)
        reference = pixel_data.create_reference()
        
        print(f"  Got pixel data reference: {reference}")
        print(f"  Reference type: {type(reference)}")
        
        # Try to get as IBuffer
        try:
            buffer = reference.as_(streams.IBuffer)
            print(f"  ✅ Got IBuffer: {buffer}")
            print(f"  Buffer length: {buffer.length}")
            
            # Try create_for_buffer
            width = bitmap.pixel_width
            height = bitmap.pixel_height
            row_stride = width  # Gray8 = 1 byte per pixel
            
            print(f"  Calling create_for_buffer({buffer}, Gray8, {width}, {height}, {row_stride})...")
            image_buffer = ImageBuffer.create_for_buffer(
                buffer,
                ImageBufferPixelFormat.GRAY8,
                width,
                height,
                row_stride
            )
            print(f"  ✅ SUCCESS! ImageBuffer created via create_for_buffer")
            image_buffer.close()
            
        except OSError as e:
            print(f"  ❌ OSError when getting IBuffer: {e}")
        except AttributeError as e:
            print(f"  ❌ AttributeError: {e}")
            
    except Exception as e:
        print(f"  ❌ {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)
