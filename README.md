# YOLO11 DNF 自动刷图脚本

这是一个基于 YOLO11 检测的 DNF 自动刷图脚本，包含图形化启动器、通用小地图寻路、进门、打怪、拾取、卡住恢复、定时按键和奖励提示处理。

完整中文说明见：

[DNF刷图使用说明.md](./DNF刷图使用说明.md)

## 快速启动

推荐使用图形化启动器：

```powershell
python -m dnf.launcher
```

直接运行主循环：

```powershell
$env:DNF_MAP_NAME="universal"
$env:DNF_YOLO_WEIGHTS="ldd.pt"
python -m dnf.main
```

## 调试小地图

```powershell
$env:DNF_DEBUG_MINIMAP="1"
python -m dnf.launcher
```

单独打开网格预览：

```powershell
python -m dnf.minimap_grid_preview
```

## 打包 EXE

```powershell
.\打包DNF刷图界面.bat
```

打包结果：

```text
dist\DNFBrushLauncher\DNFBrushLauncher.exe
```

## 测试

```powershell
python -m pytest tests/test_dnf_detector.py tests/test_minimap_nav.py tests/test_game_fallback_search.py tests/test_game_attack_cooldown.py tests/test_timed_keys.py tests/test_ui_detector.py
```

## 注意

- 默认地图配置为 `universal`。
- 默认模型可在启动器里选择，常用模型文件位于 `dnf/*.pt`。
- 使用前请先打开 DNF 游戏窗口。
- 如果重新打包时 exe 被占用，请先关闭正在运行的旧 exe。
- 本项目仅用于个人学习和自动化实验，请自行承担使用风险。
