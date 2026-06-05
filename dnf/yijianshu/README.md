# YiJianShu input backend

Put the YiJianShu V6.4 64-bit SDK DLL here as:

```text
dnf/yijianshu/msdk64.dll
```

Then start DNF normally. The input backend is locked to YiJianShu:

```powershell
python -m dnf.main
```

Optional settings:

```powershell
$env:YJS_DLL_PATH = "D:\path\to\msdk64.dll"
$env:YJS_DEVICE_INDEX = "1"
$env:YJS_VID = "888C"
$env:YJS_PID = "88C1"
```

The public test package I found exposes these functions from `msdk.dll`:
`M_Open`, `M_Open_VidPid`, `M_Close`, `M_KeyDown`, `M_KeyUp`, `M_KeyPress`,
`M_MoveR`, `M_LeftClick`, and `M_ReleaseAllKey`.

Use the 64-bit `msdk64.dll` with 64-bit Python. The downloaded `msdk.dll`
from older test tools is 32-bit and cannot be loaded by this Python runtime.
