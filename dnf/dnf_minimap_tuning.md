# DNF 小地图识别调试与新增地图接入指南

这份文档说明当前程序的小地图识别是怎么工作的，以及当小地图裁切不准、房间网格不准、地图形状变多时，应该改哪里、怎么调、怎么接到主程序里。

## 相关文件

- `dnf/main.py`
  - 主循环入口。
  - 创建 `MiniMapNavigator`。
  - 打印 `route: map=..., current=..., boss=..., query=..., direction=..., scores=...` 日志。
- `dnf/minimap_nav.py`
  - 小地图裁切、模板匹配、房间坐标计算、路线方向计算。
- `dnf/map_specs.py`
  - 地图规格配置。
  - 新增地图类型主要改这里。
- `dnf/res/`
  - 小地图模板图片，例如角色、问号、boss、精英、下楼标记等。
- `dnf/game.py`
  - 根据小地图给出的方向、YOLO 检测到的门/怪/物品执行移动。

## 主程序怎么选择地图

`dnf/main.py` 里有这一行：

```python
navigator = MiniMapNavigator(os.getenv("DNF_MAP_NAME", "auto"))
```

也就是说，默认是自动识别地图类型：

```powershell
$env:DNF_MAP_NAME="auto"
python -m dnf.main
```

如果你已经知道当前是哪张地图，可以强制指定：

```powershell
$env:DNF_MAP_NAME="generic"
python -m dnf.main
```

或者：

```powershell
$env:DNF_MAP_NAME="haibolun"
python -m dnf.main
```

新增地图后，比如叫 `forest_01`，就可以这样接入主程序：

```powershell
$env:DNF_MAP_NAME="forest_01"
python -m dnf.main
```

## 当前日志怎么看

主循环会打印类似这样的日志：

```text
route: map=generic, current=(0, 1), boss=None, query=(2, 1), elite=None, down=None, target=query@(2, 1), direction=DOWN, door=None, scores={'hero': 0.5924, 'boss': 0.4793, 'query': 0.3948}
```

重点看这些字段：

- `map=generic`
  - 当前使用的地图规格。
  - 如果这里的地图类型不对，后面网格大概率也会错。
- `current=(0, 1)`
  - 当前角色所在房间。
  - 如果角色明明在右边，但这里显示在上方或左边，通常是 `room_rect` 或 `rows/cols` 配错。
- `query=(2, 1)`
  - 问号目标房间。
  - 如果问号房识别错，可能是模板分数低、颜色兜底误判、网格划分不对。
- `direction=DOWN`
  - 路线系统算出来的下一步方向。
  - 如果视觉上应该往右，但这里是 `DOWN`，说明房间坐标映射错了。
- `door=None`
  - YOLO 没找到能配合路线使用的门。
  - 这不一定是小地图问题，也可能是目标检测没识别到门。
- `scores`
  - 模板匹配分数。
  - `hero` 低，通常是角色小地图标记没匹配上。
  - `query` 低，通常是问号模板没匹配上。
  - 分数低还识别出房间，要警惕误判。

## 打开小地图调试窗口

启动前设置：

```powershell
$env:DNF_DEBUG_MINIMAP="1"
python -m dnf.main
```

程序会显示 `dnf-minimap-debug` 窗口。

这个窗口会画出：

- 当前裁出来的小地图区域。
- 房间网格线。
- 当前角色标记。
- boss / query / elite / down 等目标标记。

调裁切和网格时，优先看这个窗口。

如果 debug 窗口里：

- 小地图显示不完整：改 `crop_rect_*`。
- 小地图完整，但网格罩错位置：改 `room_rect_*`。
- 网格行列数量不对：改 `rows`、`cols`。
- 标记识别位置对，但房间编号错：优先改 `room_rect_*`。
- 标记本身识别错：改模板、阈值，或者关闭兜底。

## 地图规格在哪里改

地图配置在 `dnf/map_specs.py`：

```python
MAP_SPECS = {
    "generic": MapSpec(
        name="generic",
        crop_rect_1067=(893, 52, 1055, 142),
        crop_rect_800=(680, 57, 780, 155),
        minimap_width=162,
        minimap_height=90,
        rows=5,
        cols=9,
        room_grid=_all_walkable(5, 9),
        room_rect_800=(686, 82, 776, 151),
    ),
}
```

字段含义：

- `name`
  - 地图类型名称。
  - 必须和 `MAP_SPECS` 字典的 key 对上。
- `crop_rect_1067`
  - 在 1067x600 客户端截图里的小地图裁切区域。
  - 格式是 `(x1, y1, x2, y2)`。
- `crop_rect_800`
  - 在 800x600 客户端截图里的小地图裁切区域。
  - 如果这个地图没有 800 分辨率配置，可以写 `None`。
- `minimap_width` / `minimap_height`
  - 小地图预期宽高。
  - 当前主要作为规格记录，核心裁切还是看 `crop_rect_*`。
- `rows` / `cols`
  - 房间网格的行数和列数。
  - 比如 4 行 5 列就是 `rows=4, cols=5`。
- `room_grid`
  - 寻路网格。
  - `0` 表示可走，`1` 表示不可走。
  - 全部可走可以用 `_all_walkable(rows, cols)`。
- `room_rect_1067`
  - 在 1067x600 客户端截图里的房间网格区域。
  - 不是整个小地图，而是房间格子所在区域。
- `room_rect_800`
  - 在 800x600 客户端截图里的房间网格区域。

## crop_rect 和 room_rect 的区别

`crop_rect_*` 是先把小地图从整张游戏截图里裁出来。

例如：

```python
crop_rect_800=(680, 57, 780, 155)
```

意思是从 800x600 的游戏截图里裁：

- 左上角：`x=680, y=57`
- 右下角：`x=780, y=155`

`room_rect_*` 是在整张游戏截图坐标系下，标出小地图里真正用于计算房间格子的区域。

例如：

```python
room_rect_800=(686, 82, 776, 151)
```

意思是小地图里只有这块区域参与房间坐标换算。

如果 `crop_rect` 对，但 `room_rect` 错，就会出现这种问题：

```text
current=(0, 1), query=(2, 1), direction=DOWN
```

明明视觉上目标在右边，但程序算成下方。

## 怎么手动调裁切

优先用环境变量临时试数值，不要一上来就改代码。

通用地图的 800 分辨率裁切：

```powershell
$env:DNF_MAP_NAME="generic"
$env:DNF_MINIMAP_GENERIC_CROP_800="680,57,780,155"
$env:DNF_DEBUG_MINIMAP="1"
python -m dnf.main
```

通用地图的 1067 分辨率裁切：

```powershell
$env:DNF_MAP_NAME="generic"
$env:DNF_MINIMAP_GENERIC_CROP_1067="893,52,1055,142"
$env:DNF_DEBUG_MINIMAP="1"
python -m dnf.main
```

如果不带地图名前缀，也可以设全局值：

```powershell
$env:DNF_MINIMAP_CROP_800="680,57,780,155"
```

优先级是：

1. `DNF_MINIMAP_<地图名>_CROP_800`
2. `DNF_MINIMAP_CROP_800`
3. `dnf/map_specs.py` 里的默认值

`1067` 版本同理。

## 怎么手动调房间网格区域

如果小地图已经裁完整，但格子线套不准，就调 `room_rect_*`。

例如：

```powershell
$env:DNF_MAP_NAME="generic"
$env:DNF_MINIMAP_GENERIC_ROOM_800="686,82,776,151"
$env:DNF_DEBUG_MINIMAP="1"
python -m dnf.main
```

调的时候看 `dnf-minimap-debug`：

- 白色矩形应该包住实际房间格子区域。
- 竖线应该刚好分开各列房间。
- 横线应该刚好分开各行房间。
- 角色标记所在格子应该和游戏小地图上的实际房间一致。

如果方向错，比如视觉上在右边却算成 `DOWN`，优先检查：

1. `rows` / `cols` 是否符合这张小地图。
2. `room_rect_*` 是否框住了真实房间格子，而不是框住了整个小地图 UI。
3. 当前 `map=...` 是否用错了地图规格。

## 新增一个地图类型

假设新增地图叫 `forest_01`，步骤如下。

第一步，在 `dnf/map_specs.py` 的 `MAP_SPECS` 里加：

```python
"forest_01": MapSpec(
    name="forest_01",
    crop_rect_1067=(966, 52, 1056, 124),
    crop_rect_800=None,
    minimap_width=90,
    minimap_height=72,
    rows=4,
    cols=5,
    room_grid=_all_walkable(4, 5),
),
```

第二步，如果这张图不是全连通，把 `room_grid` 改成真实可走关系。

例如 4 行 5 列，中间有一个不可走：

```python
room_grid=[
    [0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
],
```

第三步，启动时指定地图：

```powershell
$env:DNF_MAP_NAME="forest_01"
$env:DNF_DEBUG_MINIMAP="1"
python -m dnf.main
```

第四步，根据 debug 窗口微调：

- `crop_rect_1067`
- `crop_rect_800`
- `room_rect_1067`
- `room_rect_800`
- `rows`
- `cols`
- `room_grid`

第五步，确认日志：

```text
route: map=forest_01, current=(...), query=(...), target=...@..., direction=...
```

只有当 `current`、`target` 和 `direction` 都符合肉眼判断时，这张地图才算接好了。

## 小地图有很多种形状怎么办

不要把所有地图都塞进 `generic`。

正确做法是：

1. 每一种明显不同的小地图形状都单独建一个 `MapSpec`。
2. 用不同的 key 区分，比如：

```python
MAP_SPECS = {
    "generic": MapSpec(...),
    "haibolun": MapSpec(...),
    "forest_01": MapSpec(...),
    "forest_02": MapSpec(...),
    "tower_cross": MapSpec(...),
}
```

3. 每个地图单独配置自己的：

- `crop_rect_*`
- `room_rect_*`
- `rows`
- `cols`
- `room_grid`

4. 稳定后再考虑用 `DNF_MAP_NAME=auto` 自动切换。

如果还没调准，不建议用 `auto`。因为自动识别可能会选错地图类型，让问题更难判断。

## 自动地图识别是怎么工作的

`MiniMapNavigator` 初始化时，如果传入 `auto`：

```python
MiniMapNavigator("auto")
```

它会先用 `generic`，然后每帧对所有 `MAP_SPECS` 打分：

```python
scores = {name: self._score_map_spec(frame, spec) for name, spec in MAP_SPECS.items()}
```

如果另一个地图分数明显更高，就切过去。

自动识别依赖模板分数，所以地图配置还没调好时，可能选错。

调试阶段建议：

```powershell
$env:DNF_MAP_NAME="你正在调的地图名"
```

等单张地图稳定后，再改回：

```powershell
$env:DNF_MAP_NAME="auto"
```

## 问号房识别和颜色兜底

问号房优先用模板匹配：

```python
query_matches = self._match_marker(minimap, query_names, "query")
```

模板来自：

```python
QUERY_TEMPLATE_FILES = {
    "query": "map_query.png",
    "query1": "map_query1.png",
    "query3": "map_query3.png",
    "query4": "map_query4.png",
    "query5": "map_query5.png",
}
```

模板文件在：

```text
dnf/res/
```

现在颜色兜底默认关闭：

```python
QUERY_COLOR_FALLBACK_ENABLED = os.getenv("DNF_QUERY_COLOR_FALLBACK", "0") == "1"
```

如果你要临时开启：

```powershell
$env:DNF_QUERY_COLOR_FALLBACK="1"
python -m dnf.main
```

不建议默认开启颜色兜底。因为它可能把小地图上的黄色 UI、房间块、图标边缘误判成问号房，造成方向乱算。

## 常见问题判断

### 小地图裁切错

表现：

- debug 窗口里小地图不完整。
- `scores` 普遍很低。
- `current=None`。

处理：

- 调 `crop_rect_800` 或 `crop_rect_1067`。

### 房间网格错

表现：

- 小地图裁出来是完整的。
- 标记位置也大概对。
- 但 `current=(row, col)` 或 `query=(row, col)` 不符合实际。
- 方向明显错，比如肉眼看应该往右，日志却是 `DOWN`。

处理：

- 调 `room_rect_800` 或 `room_rect_1067`。
- 检查 `rows` / `cols`。
- 检查当前 `map=...` 是否是正确地图类型。

### 模板识别错

表现：

- `scores` 里某个模板分数很低。
- 目标房间经常跳。
- 问号、boss、精英识别不稳定。

处理：

- 更新 `dnf/res/` 里的模板图片。
- 调 `MARKER_THRESHOLDS`。
- 关闭不可靠兜底，例如颜色兜底。

### 门检测不到

表现：

```text
obj: []
door=None
```

或者：

```text
direction=RIGHT, door=None
```

处理：

- 这是 YOLO 检测问题，不一定是小地图问题。
- 小地图方向可以是对的，但没有检测到门，`game.py` 就只能 fallback。

## 调参建议流程

1. 固定地图类型，不用 `auto`。

```powershell
$env:DNF_MAP_NAME="你的地图名"
```

2. 打开 debug 小地图。

```powershell
$env:DNF_DEBUG_MINIMAP="1"
```

3. 先调 `crop_rect_*`，保证小地图完整。

4. 再调 `room_rect_*`，保证网格线套准房间区域。

5. 再调 `rows` / `cols`，保证房间行列数对。

6. 再调 `room_grid`，保证寻路只走真实存在的房间。

7. 最后看日志里的：

```text
current=...
target=...
direction=...
scores=...
```

8. 肉眼确认方向正确后，再启用 `auto`。

## 环境变量速查

```powershell
# 指定地图类型
$env:DNF_MAP_NAME="generic"

# 启用小地图 debug 窗口
$env:DNF_DEBUG_MINIMAP="1"

# 临时覆盖某张地图的 800 分辨率小地图裁切
$env:DNF_MINIMAP_GENERIC_CROP_800="680,57,780,155"

# 临时覆盖某张地图的 1067 分辨率小地图裁切
$env:DNF_MINIMAP_GENERIC_CROP_1067="893,52,1055,142"

# 临时覆盖某张地图的 800 分辨率房间网格区域
$env:DNF_MINIMAP_GENERIC_ROOM_800="686,82,776,151"

# 临时覆盖某张地图的 1067 分辨率房间网格区域
$env:DNF_MINIMAP_GENERIC_ROOM_1067="893,52,1055,142"

# 开启问号颜色兜底，默认不建议
$env:DNF_QUERY_COLOR_FALLBACK="1"
```

## 最重要的一条

当日志方向明显不符合肉眼判断时，不要先改 `game.py` 的移动逻辑。

先看：

1. `map=...` 是否正确。
2. `current=...` 是否正确。
3. `target=...` 是否正确。
4. `scores=...` 是否可靠。
5. debug 小地图里的网格是否套准。

只有小地图路线判断正确之后，再去处理门检测、移动、fallback。
