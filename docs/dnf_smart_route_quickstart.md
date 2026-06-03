# DNF 智能寻路快速验证

这份说明只用于验证小地图智能寻路，不会让角色移动。

## 1. 只验证小地图路线

```powershell
Set-Location D:\yolo\yolo11
$env:DNF_ROUTE_ONLY="1"
$env:DNF_MAX_FRAMES="1"
$env:DNF_MAP_NAME="auto"
$env:DNF_DEBUG_ROUTE_DIR="D:\yolo\yolo11\output\dnf_route_debug"
$env:DNF_DEBUG_ROUTE_EVERY="1"
python -m dnf.main
python -m dnf.route_debug D:\yolo\yolo11\output\dnf_route_debug
python -m dnf.route_sequence_debug D:\yolo\yolo11\output\dnf_route_debug
```

更安全的一键检查可以直接用 `route_check`，它只截图、识别路线、保存调试包，不会调用 `Game.run()`，也不会按键移动角色：

```powershell
python -m dnf.route_check --out D:\yolo\yolo11\output\dnf_route_check --map auto --frames 1
python -m dnf.route_check --out D:\yolo\yolo11\output\dnf_route_check --map auto --frames 1 --with-detector --device cpu
```

第一条只验证小地图和路线；第二条会额外跑 YOLO，用来验证角色框、门框和选门结果。两条都不会移动角色。

带 `--with-detector` 时，调试包还会保存：
- `route_*_detector.png`：YOLO 画框后的全屏图。
- JSON 里的 `detection_objects`：原始检测框、类别和置信度。

如果不想自己判断 JSON，可以直接跑验收器：

```powershell
python -m dnf.route_acceptance D:\yolo\yolo11\output\dnf_route_check --stage minimap
python -m dnf.route_acceptance D:\yolo\yolo11\output\dnf_route_check --stage detector
python -m dnf.route_acceptance D:\yolo\yolo11\output\dnf_route_debug --stage dry-run
```

`minimap` 通过后再测 `detector`；`detector` 通过后再进 `DNF_DRY_RUN=1`；`dry-run` 通过后才考虑小范围真实执行。

如果验收没通过，可以让程序给下一步建议：

```powershell
python -m dnf.route_advice D:\yolo\yolo11\output\dnf_route_check
```

它会根据调试包建议调模板阈值、固定地图，或继续跑 `--with-detector`。

调试 JSON 里会保存 `frame_index`。连续多帧诊断会优先按这个序号排序，避免复制文件或修改时间变化后误判先后顺序。

使用 `--map auto` 时，调试摘要会显示 `自动选图分数`。如果实际地图被识别错，先看哪个地图分数最高；必要时临时改成固定地图，例如 `--map generic` 或设置 `$env:DNF_MAP_NAME="generic"`。

`DNF_ROUTE_ONLY=1` 会跳过 YOLO 检测和 `Game.run()`，只截图、识别小地图、计算下一步房间方向，并保存调试包。

主循环保存调试包有两种原因：按 `DNF_DEBUG_ROUTE_EVERY` 周期保存，或路线异常自动保存。JSON 里的 `debug_reason` 会说明原因，例如 `scheduled`、`missing_current`、`missing_target`、`unreachable`、`door_not_detected`、`door_not_selected`、`route_recovery_active`。同一种异常会按 `DNF_DEBUG_ROUTE_EVERY` 节流保存，避免刷出太多文件。

## 2. 看调试包

调试目录里会生成三类文件：

- `route_*.json`：识别结果、房间坐标、目标、下一步方向、模板分数。
- `route_*.png`：裁剪出来的小地图篮筐框。
- `route_*_frame.png`：原截图上的小地图篮筐外框。

JSON 里的 `marker_centers` 是小地图局部坐标，表示 `current/query/boss/elite/down` 等标记中心点落在哪里。房间判断错时，先对照 `route_*.png` 看这些点是否落在正确网格附近。

`python -m dnf.route_debug ...` 会显示 `路线路径` 和 `路线步数`。如果路线步数很长，通常是 `room_grid` 里有不可走房间导致 BFS 正在绕路。

如果 `python -m dnf.route_debug ...` 提示 hero 分数低，优先调小地图篮筐外框。

`路线状态` 的含义：

- `moving`：已经算出下一步方向，可以向目标房移动。
- `at_target`：目标就在当前房间，应该清怪/拾取，不主动找门。
- `missing_current`：没识别到当前标记，优先检查 hero 模板和小地图篮筐外框。
- `missing_target`：没识别到目标，也没有可探索房间。
- `unreachable`：当前房间和目标房间不连通，优先检查 `room_grid`。

`python -m dnf.route_sequence_debug ...` 用来分析连续多帧。如果提示连续停在同一房间，通常要检查门检测、门选择或移动执行；如果连续 `missing_current`，优先调小地图裁剪和 hero 模板。

在 `DNF_ROUTE_ONLY=1` 下，程序会故意跳过 YOLO，所以 `选中门中心` 为空不是错误。只有关闭 route-only、使用 `DNF_DRY_RUN=1` 或真实执行时仍然没有门候选，才优先检查 YOLO 的 door 检测。

如果调试摘要里模板分数只比阈值低一点，可以先临时调低对应阈值，不用改代码：

```powershell
$env:DNF_MINIMAP_HERO_THRESHOLD="0.52"
$env:DNF_MINIMAP_QUERY_THRESHOLD="0.45"
$env:DNF_MINIMAP_GENERIC_HERO_THRESHOLD="0.52"
```

通用变量会影响所有地图；带地图名的变量只影响指定地图。阈值必须在 `0` 到 `1` 之间。

真实执行时，如果连续多帧都是同一个当前房间、同一个目标房间和同一个移动方向，主循环会认为可能卡在门口或门框检测抖动，日志会出现 `route recovery active`，并临时绕过门框追踪，直接按智能路线方向移动。默认连续 6 帧触发；需要调节或关闭时：

```powershell
$env:DNF_ROUTE_STUCK_FRAMES="6"
$env:DNF_ROUTE_STUCK_FRAMES="0"
```

## 3. 调小地图裁剪框

按当前分辨率设置。800 宽窗口用 `_800`，1067/1600 等宽屏截图用 `_1067`。

```powershell
$env:DNF_MAP_NAME="generic"
$env:DNF_MINIMAP_GENERIC_CROP_1067="747,0,1067,210"
$env:DNF_MINIMAP_GENERIC_ROOM_1067="747,0,1067,210"
```

也可以用通用变量覆盖所有地图：

```powershell
$env:DNF_MINIMAP_CROP_1067="747,0,1067,210"
$env:DNF_MINIMAP_ROOM_1067="747,0,1067,210"
```

## 4. 离线分析一张截图

如果已经有截图，可以不启动游戏循环：

```powershell
python -m dnf.route_probe D:\yolo\yolo11\output\example_screenshot.png --out D:\yolo\yolo11\output\dnf_route_probe --map generic
python -m dnf.route_debug D:\yolo\yolo11\output\dnf_route_probe
```

不传 `--objects-json` 时，离线分析会把 `detector_enabled` 记为 `false`，所以没有选中门不是错误；传入 YOLO 对象 JSON 后，才会检查门候选和选门结果。

## 5. 外部地图配置

如果某张图不是所有房间都连通，可以写一个 JSON，不用改 Python 代码：

```json
{
  "maps": {
    "detour": {
      "base": "generic",
      "rows": 3,
      "cols": 3,
      "room_grid": [
        [0, 1, 0],
        [0, 1, 0],
        [0, 0, 0]
      ]
    }
  }
}
```

`room_grid` 里 `0` 表示可走房间，`1` 表示不存在或不可走。使用时：

```powershell
$env:DNF_MAP_SPEC_FILE="D:\yolo\yolo11\config\dnf_maps.json"
$env:DNF_MAP_NAME="detour"
```

## 6. 确认稳定后再开执行

当调试结果能稳定识别：

- 当前房间不是 `None`
- 目标房间不是 `None`
- 下一步方向是 `up/down/left/right`
- 小地图篮筐外框落在正确位置

如果目标房间等于当前房间，`下一步方向` 可以是 `None`，这表示已经在目标房间，程序会停留清怪/拾取，不会主动找门离开。

再去掉 `DNF_ROUTE_ONLY`，用 `DNF_DRY_RUN=1` 观察 YOLO 门框和路线门选择。最后确认无误后，才关闭 dry-run。

默认情况下，如果智能寻路没有算出下一步方向，程序会跳过本帧执行，不会自动回退旧固定路线。确实需要旧路线兜底时再显式开启：

```powershell
$env:DNF_ALLOW_FIXED_FALLBACK="1"
```
