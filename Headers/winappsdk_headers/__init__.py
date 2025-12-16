"""Helpers for locating Windows App SDK header projections."""

from pathlib import Path

_PACKAGE_DIR = Path(__file__).parent

def get_include_dir() -> Path:
    """Return the root include directory that contains all header files."""

    return _PACKAGE_DIR / "include"


def get_cppwinrt_include_dir() -> Path:
    """Return the location of the generated CppWinRT headers."""

    return get_include_dir() / "cppwinrt"


def get_pywinrt_include_dir() -> Path:
    """Return the location of the generated PyWinRT headers."""

    return get_include_dir() / "pywinrt"


def get_include_dirs() -> list[str]:
    """Return both include directories as strings for setuptools Extension use."""

    base = get_include_dir()
    return [str(base / "cppwinrt"), str(base / "pywinrt")]


__all__ = [
    "get_include_dirs",
]
