# DNF YOLO11 自动刷图脚本使用说明

这个项目是在 YOLO11 检测基础上做的 DNF 自动刷图脚本，当前版本使用通用小地图逻辑：

- 小地图只保留 `universal` 通用地图配置。
- 寻路优先使用蓝色玩家标志和问号、Boss、精英、下层标志之间的相对位置。
- 网格只作为兜底和调试显示，不再强依赖每张地图单独调试。
- 动作层加入了按键保活，避免角色移动时一走一停。
- 支持拾取物品、进门、卡住恢复、奖励选择提示处理、定时技能按键。

## 目录说明

- `dnf/main.py`：刷图主循环，负责截图、YOLO 检测、小地图寻路和执行动作。
- `dnf/launcher.py`：图形化启动器，可以配置模型、阈值、按键、卡住恢复参数。
- `dnf/game.py`：角色动作逻辑，包括移动、打怪、拾取、进门、卡住恢复。
- `dnf/detector.py`：YOLO11 检测封装。
- `dnf/minimap_nav.py`：小地图标志识别和通用寻路。
- `dnf/map_specs.py`：通用小地图配置。
- `dnf/minimap_grid_preview.py`：小地图裁剪和网格调试预览工具。
- `dnf/timed_keys.py`：定时按键调度。
- `dnf/res/`：小地图模板、UI 模板和启动器图标。
- `dnf/res/jn.png`：技能已过限制时间、图标亮起、可以释放的模板。
- `dnf/res/jn1.png`：技能未过限制时间、图标冷却/不可释放的模板。
- `dnf/*.pt`：刷图检测模型。

## 环境准备

建议使用 Python 3.10。

安装依赖：

```powershell
pip install -e .
pip install pywin32 mss pyautogui pydirectinput loguru pyinstaller
```

如果没有安装 PyTorch/Ultralytics，需要先按你的 CUDA 或 CPU 环境安装对应版本。

## 启动刷图

推荐使用图形界面：

```powershell
python -m dnf.launcher
```

也可以直接运行主循环：

```powershell
$env:DNF_MAP_NAME="universal"
$env:DNF_YOLO_WEIGHTS="ldd.pt"
python -m dnf.main
```

启动前请确认：

- DNF 游戏窗口已经打开。
- 游戏窗口分辨率建议保持 800x600 或当前脚本调试过的窗口比例。
- 角色已经在副本内或可开始刷图的位置。
- 管理员权限运行终端或 exe 会更稳定。

## 常用调试

显示小地图调试窗口：

```powershell
$env:DNF_DEBUG_MINIMAP="1"
python -m dnf.launcher
```

显示 YOLO 检测窗口：

```powershell
$env:DNF_SHOW_DETECTION_WINDOW="1"
python -m dnf.launcher
```

单独预览小地图网格：

```powershell
python -m dnf.minimap_grid_preview
```

打开更详细的路线日志：

```powershell
$env:DNF_ROUTE_DEBUG="1"
python -m dnf.launcher
```

## 常用参数

这些参数可以通过启动器配置，也可以用环境变量覆盖：

- `DNF_YOLO_WEIGHTS`：模型文件，默认启动器使用 `ldd.pt`。
- `DNF_YOLO_IMGSZ`：YOLO 输入尺寸，默认 `512`。
- `DNF_YOLO_CONF`：总检测阈值，默认 `0.35`。
- `DNF_YOLO_CONF_PLAYER`：角色阈值，默认 `0.45`。
- `DNF_YOLO_CONF_DOOR`：门阈值，默认 `0.60`。
- `DNF_YOLO_CONF_GOODS`：物品阈值，默认 `0.60`。
- `DNF_YOLO_CONF_MONEY`：金币阈值，默认 `0.60`。
- `DNF_ATTACK_KEY`：普通攻击键，默认 `x`。
- `DNF_SPECIAL_ATTACK_KEY`：技能键，默认 `q`。
- `DNF_EXTRA_ATTACK_KEY`：额外技能键，默认 `a`。
- `DNF_MOVE_REASSERT_SECONDS`：移动按键保活间隔，默认 `0.12`。
- `DNF_SKILL_ICON_ENABLED`：技能图标识别，默认 `1` 开启。
- `DNF_SKILL_ICON_THRESHOLD`：`jn.png` 匹配阈值，默认 `0.86`。
- `DNF_SKILL_ICON_MARGIN`：`jn.png` 必须比 `jn1.png` 高出的分数，默认 `0.03`。
- `DNF_DEBUG_MINIMAP`：小地图调试窗口，`1` 开启。
- `DNF_SHOW_DETECTION_WINDOW`：检测调试窗口，`1` 开启。

## 打包 exe

仓库里有打包脚本：

```powershell
.\打包DNF刷图界面.bat
```

也可以手动打包：

```powershell
python -m PyInstaller --noconfirm --windowed --name "DNFBrushLauncher" `
  --icon "dnf\res\app.ico" `
  --add-data "dnf\res;dnf\res" `
  --add-data "dnf\best.pt;dnf" `
  --add-data "dnf\ds.pt;dnf" `
  --add-data "dnf\ldd.pt;dnf" `
  --add-data "dnf\pre.pt;dnf" `
  --add-data "dnf\shzn.pt;dnf" `
  --hidden-import win32timezone `
  dnf\launcher.py
```

打包结果在：

```text
dist\DNFBrushLauncher\DNFBrushLauncher.exe
```

如果 exe 正在运行，Windows 会锁定文件，重新打包时请先关闭旧 exe。

## 测试

当前刷图相关测试：

```powershell
python -m pytest tests/test_dnf_detector.py tests/test_minimap_nav.py tests/test_game_fallback_search.py tests/test_game_attack_cooldown.py tests/test_timed_keys.py tests/test_ui_detector.py
```

语法检查：

```powershell
python -m py_compile dnf\detector.py dnf\main.py dnf\game.py dnf\minimap_nav.py dnf\launcher.py dnf\timed_keys.py dnf\ui_detector.py
```

## 注意

- 这个脚本依赖当前训练模型的识别效果；如果角色、门、物品、金币、怪物识别不稳定，需要继续补数据训练。
- 通用小地图逻辑主要靠标志点相对方向寻路，网格只做兜底。
- 如果某个房间卡住，建议保留日志和截图，重点看 `route`、`door`、`player center`。
- 本项目仅用于个人学习和自动化实验，请自行承担使用风险。
