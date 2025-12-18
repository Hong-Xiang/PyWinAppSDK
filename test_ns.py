import sys
sys.path.insert(0, r"temp_wheel_check")
try:
    import winappsdk
    print(f"winappsdk works: {winappsdk}")
except Exception as e:
    print(f"Cannot import winappsdk: {e}")
