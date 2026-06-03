# DNF 智能导航运行说明

## 已实现

当前运行入口是：

```powershell
python -m dnf.run_with_diagnostics
```

程序会自动绑定标题包含“地下城与勇士”的游戏窗口，只截取游戏客户区。截图已经使用 `mss`，不再依赖全屏截图。

不熟悉命令时，直接双击项目根目录中的：

```text
run_dnf_with_diagnostics.bat
```

运行时优先级：

1. 翻牌和再来一次
2. 玩家脚底坐标与平滑坐标
3. 换房确认与卡住检测
4. boss、小怪
5. 物品、金币
6. 智能门评分
7. YOLO 暂时看不到门时的稳定找门

## 首次安装

缺少依赖时执行：

```powershell
pip install mss pywin32 pydirectinput
```

YOLO 原有依赖仍然需要保留。

程序默认使用 `dnf/ldd.pt` 作为刷图 YOLO 权重。如果需要临时切换到其他训练权重，请指定实际路径：

```powershell
$env:DNF_WEIGHTS="D:\path\to\weights.pt"
```

程序会检查模型标签，并自动把 `boss_xxx / monster_xxx / door_xxx / goods_xxx` 变体归一化。如果日志提示缺少 `player / monster / goods / door`，说明当前权重不是 DNF 检测模型。

## 可调参数

所有参数都可以在 PowerShell 中临时设置，不需要改代码：

```powershell
$env:DNF_STUCK_TIME="0.6"
$env:DNF_STUCK_PIXEL_THRESHOLD="5"
$env:DNF_NUDGE_PRESS_TIME="0.03"
$env:DNF_Y_DEAD_ZONE="35"
$env:DNF_X_DEAD_ZONE="25"
$env:DNF_DOOR_MATCH_SCORE_THRESHOLD="-900"
$env:DNF_TEMPLATE_MATCH_THRESHOLD="0.8"
$env:DNF_FANPAI_COOLDOWN="5"
$env:DNF_ZAILAIYICI_COOLDOWN="5"
$env:DNF_SEARCH_DIRECTION_TICKS="25"
$env:DNF_POSITION_SMOOTH_ALPHA="0.35"
$env:DNF_YOLO_CONF="0.3"
$env:DNF_YOLO_IOU="0.5"
$env:DNF_DOOR_ATTEMPT_TIMEOUT="2.5"
$env:DNF_DOOR_RETRY_COOLDOWN="3"
$env:DNF_PLAYER_MISSING_GRACE="1.2"
$env:DNF_LOCAL_ASTAR="1"
$env:DNF_LOCAL_ASTAR_CELL_SIZE="32"
$env:DNF_WINDOW_LEFT="3"
$env:DNF_WINDOW_TOP="3"
```

## 重点观察日志

正常运行时重点看：

- `窗口绑定成功`
- `玩家脚底坐标: raw=..., smooth=...`
- `当前检测到 N 个门`
- `门候选: position=..., direction=..., score=..., reasons=...`
- `最终选择门`
- `DoorSearcher 找门`
- `卡住检测`
- `执行脱困`
- `换房成功`
- `状态=翻牌`
- `状态=再来一次`

任何异常都会使用 `logger.exception` 打印调用堆栈，不再静默忽略。

## BUG 自动定位

程序启动失败、运行异常或后台线程异常时，会自动生成：

```text
output\bug_reports\LATEST_BUG_REPORT.txt
output\bug_reports\REPORT_FOR_AI.txt
```

`LATEST_BUG_REPORT.txt` 会写出最可能出错的文件、精确行号、附近代码、调用路径、环境变量和最近运行日志。把它交给 AI，并说“按报告修复并验证”即可。

也可以直接双击：

```text
open_latest_dnf_bug_report.bat
```

它会用记事本打开最新报告。

源码、依赖和权重路径也可以一键检查。直接双击：

```text
check_dnf_bug.bat
```

检查结果保存在：

```text
output\bug_reports\LATEST_STATIC_CHECK.txt
```
