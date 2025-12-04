import sys
import os

_LOG_FILE = os.path.join(os.environ.get('TEMP', '.'), 'imagebuffer-test.log')

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
    print(f"[LOG] Output to: {_LOG_FILE}")
except: pass

import asyncio
print("=" * 60)
print("ImageBuffer Test (with package identity)")
print("=" * 60)
print(f"Python: {sys.version}")

from winappsdk_AI.microsoft.graphics.imaging import ImageBuffer

print(f"ImageBuffer type: {type(ImageBuffer)}")
print(f"create_for_software_bitmap: {ImageBuffer.create_for_software_bitmap}")

async def test():
    from winrt.windows.storage import StorageFile, FileAccessMode
    from winrt.windows.graphics.imaging import BitmapDecoder
    
    image_path = r"C:\Users\leilzh\Pictures\Screenshots\test-ocr.png"
    print(f"Loading: {image_path}")
    
    storage_file = await StorageFile.get_file_from_path_async(image_path)
    stream = await storage_file.open_async(FileAccessMode.READ)
    decoder = await BitmapDecoder.create_async(stream)
    bitmap = await decoder.get_software_bitmap_async()
    
    print(f"Bitmap: {bitmap.pixel_width}x{bitmap.pixel_height}")
    
    print("Calling ImageBuffer.create_for_software_bitmap(bitmap)...")
    try:
        result = ImageBuffer.create_for_software_bitmap(bitmap)
        print(f"SUCCESS! Result: {result}")
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
print("Done!")
input("Press Enter...")
