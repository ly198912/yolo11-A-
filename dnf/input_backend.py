from __future__ import annotations

import ctypes
import os
import platform
from pathlib import Path
from typing import Dict, Optional

from loguru import logger


BACKEND_NAME = "yijianshu"
_HANDLE = ctypes.c_void_p


_VK_CODES = {
    "back": 0x08,
    "tab": 0x09,
    "enter": 0x0D,
    "shift": 0x10,
    "ctrl": 0x11,
    "alt": 0x12,
    "esc": 0x1B,
    "space": 0x20,
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
    "delete": 0x2E,
    "0": 0x30,
    "1": 0x31,
    "2": 0x32,
    "3": 0x33,
    "4": 0x34,
    "5": 0x35,
    "6": 0x36,
    "7": 0x37,
    "8": 0x38,
    "9": 0x39,
    "a": 0x41,
    "b": 0x42,
    "c": 0x43,
    "d": 0x44,
    "e": 0x45,
    "f": 0x46,
    "g": 0x47,
    "h": 0x48,
    "i": 0x49,
    "j": 0x4A,
    "k": 0x4B,
    "l": 0x4C,
    "m": 0x4D,
    "n": 0x4E,
    "o": 0x4F,
    "p": 0x50,
    "q": 0x51,
    "r": 0x52,
    "s": 0x53,
    "t": 0x54,
    "u": 0x55,
    "v": 0x56,
    "w": 0x57,
    "x": 0x58,
    "y": 0x59,
    "z": 0x5A,
    "f1": 0x70,
    "f2": 0x71,
    "f3": 0x72,
    "f4": 0x73,
    "f5": 0x74,
    "f6": 0x75,
    "f7": 0x76,
    "f8": 0x77,
    "f9": 0x78,
    "f10": 0x79,
    "f11": 0x7A,
    "f12": 0x7B,
    "num0": 0x60,
    "num1": 0x61,
    "num2": 0x62,
    "num3": 0x63,
    "num4": 0x64,
    "num5": 0x65,
    "num6": 0x66,
    "num7": 0x67,
    "num8": 0x68,
    "num9": 0x69,
}


def _backend_name() -> str:
    return BACKEND_NAME


def _debug_input() -> bool:
    return os.getenv("DNF_DEBUG_INPUT", "0") == "1"


def _key_code(key: str) -> int:
    normalized = str(key).strip().lower()
    if normalized in _VK_CODES:
        return _VK_CODES[normalized]
    raise KeyError(f"unsupported key for yijianshu backend: {key!r}")


class _YiJianShuBackend:
    def __init__(self) -> None:
        self._dll: Optional[ctypes.WinDLL] = None
        self._handle: Optional[int] = None
        self._dll_path: Optional[Path] = None
        self._logged_config = False
        self._logged_device_info = False

    def _default_dll_path(self) -> Path:
        dll_name = "msdk64.dll" if platform.architecture()[0] == "64bit" else "msdk.dll"
        return Path(__file__).resolve().parent / "yijianshu" / dll_name

    def _configured_dll_path(self) -> Path:
        return Path(os.getenv("YJS_DLL_PATH", str(self._default_dll_path()))).expanduser()

    def _open_method(self) -> str:
        vid = os.getenv("YJS_VID")
        pid = os.getenv("YJS_PID")
        if vid and pid:
            return f"M_Open_VidPid(vid=0x{int(vid, 16):04X}, pid=0x{int(pid, 16):04X})"
        return f"M_Open(device_index={int(os.getenv('YJS_DEVICE_INDEX', '1'))})"

    def config_info(self) -> Dict[str, object]:
        dll_path = self._configured_dll_path()
        return {
            "backend": "yijianshu",
            "dll_path": str(dll_path),
            "dll_exists": dll_path.exists(),
            "python_arch": platform.architecture()[0],
            "open_method": self._open_method(),
        }

    def log_config(self) -> None:
        if self._logged_config:
            return
        info = self.config_info()
        logger.info(
            "input backend: {backend}, dll={dll_path}, exists={dll_exists}, python_arch={python_arch}, open={open_method}",
            **info,
        )
        self._logged_config = True

    def _load(self) -> ctypes.WinDLL:
        if self._dll is not None:
            return self._dll

        self.log_config()
        dll_path = self._configured_dll_path()
        if not dll_path.exists():
            raise FileNotFoundError(
                f"YiJianShu DLL not found: {dll_path}. "
                "Set YJS_DLL_PATH or put msdk64.dll under dnf/yijianshu/."
            )

        self._dll_path = dll_path
        self._dll = ctypes.WinDLL(str(dll_path))
        self._dll.M_Close.argtypes = [_HANDLE]
        self._dll.M_Close.restype = ctypes.c_int
        for name in ("M_KeyDown2", "M_KeyUp2"):
            func = getattr(self._dll, name)
            func.argtypes = [_HANDLE, ctypes.c_int]
            func.restype = ctypes.c_int
        self._dll.M_KeyPress2.argtypes = [_HANDLE, ctypes.c_int, ctypes.c_int]
        self._dll.M_KeyPress2.restype = ctypes.c_int
        if hasattr(self._dll, "M_ReleaseAllKey"):
            self._dll.M_ReleaseAllKey.argtypes = [_HANDLE]
            self._dll.M_ReleaseAllKey.restype = ctypes.c_int
        return self._dll

    def log_device_info(self) -> None:
        if self._logged_device_info or not self._handle:
            return

        logger.info(
            "YiJianShu device info: handle={} (0x{:X})",
            self._handle,
            self._handle,
        )
        self._logged_device_info = True

    def _call_key_proc(self, name: str, key: str) -> int:
        code = _key_code(key)
        result = int(getattr(self._load(), name)(self._open(), code))
        if _debug_input():
            logger.info("YiJianShu {} key={} code={} result={}", name, key, code, result)
        return result

    def _open(self) -> int:
        if self._handle:
            return self._handle

        dll = self._load()
        vid = os.getenv("YJS_VID")
        pid = os.getenv("YJS_PID")
        if vid and pid and hasattr(dll, "M_Open_VidPid"):
            dll.M_Open_VidPid.argtypes = [ctypes.c_int, ctypes.c_int]
            dll.M_Open_VidPid.restype = _HANDLE
            self._handle = int(dll.M_Open_VidPid(int(vid, 16), int(pid, 16)) or 0)
        else:
            dll.M_Open.argtypes = [ctypes.c_int]
            dll.M_Open.restype = _HANDLE
            device_index = int(os.getenv("YJS_DEVICE_INDEX", "1"))
            self._handle = int(dll.M_Open(device_index) or 0)

        if not self._handle:
            raise RuntimeError("failed to open YiJianShu keyboard/mouse box")
        logger.info("YiJianShu keyboard/mouse box opened: handle={}", self._handle)
        self.log_device_info()
        return self._handle

    def close(self) -> None:
        if self._dll is not None and self._handle:
            self._dll.M_Close(self._handle)
        self._handle = None

    def key_down(self, key: str) -> None:
        self._call_key_proc("M_KeyDown2", key)

    def key_up(self, key: str) -> None:
        self._call_key_proc("M_KeyUp2", key)

    def key_press(self, key: str) -> None:
        code = _key_code(key)
        result = int(self._load().M_KeyPress2(self._open(), code, 1))
        if _debug_input():
            logger.info("YiJianShu M_KeyPress2 key={} code={} count=1 result={}", key, code, result)

    def release_all_keys(self) -> None:
        dll = self._load()
        if hasattr(dll, "M_ReleaseAllKey"):
            result = int(dll.M_ReleaseAllKey(self._open()))
            if _debug_input():
                logger.info("YiJianShu M_ReleaseAllKey result={}", result)
            return
        for key in ("up", "down", "left", "right"):
            self.key_up(key)


_yijianshu = _YiJianShuBackend()


def log_backend_info() -> None:
    _yijianshu.log_config()


def keyDown(key: str, _pause: Optional[bool] = None) -> None:
    _yijianshu.key_down(key)


def keyUp(key: str, _pause: Optional[bool] = None) -> None:
    _yijianshu.key_up(key)


def press(key: str, duration: float = 0.08) -> None:
    _yijianshu.key_press(key)


def release_all_keys() -> None:
    _yijianshu.release_all_keys()


def close() -> None:
    _yijianshu.close()
