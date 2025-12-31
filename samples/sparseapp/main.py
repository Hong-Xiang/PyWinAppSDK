import ctypes
import ctypes.wintypes


def has_msix_identity():
    kernel32 = ctypes.windll.kernel32
    length = ctypes.wintypes.UINT(0)
    # Call with 0 length to get the required size or a specific error
    res = kernel32.GetCurrentPackageFullName(ctypes.byref(length), None)

    # 15700 is the decimal code for APPMODEL_ERROR_NO_PACKAGE
    if res == 15700:
        return False
    return True


def main():
    print("Hello from sparseapp!")
    if has_msix_identity():
        print("Running with MSIX identity.")
    else:
        print("Running without MSIX identity.")


if __name__ == "__main__":
    main()
