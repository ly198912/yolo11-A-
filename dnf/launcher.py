#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
from pathlib import Path
from typing import Optional

import tkinter as tk
from tkinter import messagebox, ttk

from dnf.map_specs import MAP_SPECS
from dnf.timed_keys import DEFAULT_TIMED_KEY_SPEC, parse_timed_key_spec


ROOT = Path(__file__).resolve().parents[1]
DNF_DIR = Path(__file__).resolve().parent


def _model_search_dirs() -> list[Path]:
    dirs = [
        DNF_DIR,
        ROOT / "dnf",
        Path.cwd() / "dnf",
    ]
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        dirs.extend(
            [
                exe_dir / "_internal" / "dnf",
                exe_dir / "dnf",
                Path(getattr(sys, "_MEIPASS", exe_dir)) / "dnf",
            ]
        )

    unique_dirs: list[Path] = []
    seen = set()
    for directory in dirs:
        key = str(directory.resolve()) if directory.exists() else str(directory)
        if key not in seen:
            seen.add(key)
            unique_dirs.append(directory)
    return unique_dirs


def _available_model_names(current_value: str) -> list[str]:
    names: list[str] = []
    seen = set()
    for directory in _model_search_dirs():
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.pt")):
            if path.name not in seen:
                seen.add(path.name)
                names.append(path.name)
    if current_value and current_value not in seen:
        names.append(current_value)
    return names


def _resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent)) / "dnf" / relative_path
    return DNF_DIR / relative_path


class DnfBrushLauncher(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("DNF 自动刷图控制台")
        self._set_window_icon()
        self.geometry("1040x760")
        self.minsize(920, 680)

        self.process: Optional[subprocess.Popen[str]] = None
        self.log_queue: "queue.Queue[str]" = queue.Queue()

        self.map_var = tk.StringVar(value=os.getenv("DNF_MAP_NAME", "universal"))
        self.model_var = tk.StringVar(value=os.getenv("DNF_YOLO_WEIGHTS", "ldd.pt"))
        self.imgsz_var = tk.StringVar(value=os.getenv("DNF_YOLO_IMGSZ", "512"))
        self.conf_var = tk.StringVar(value=os.getenv("DNF_YOLO_CONF", "0.35"))
        self.iou_var = tk.StringVar(value=os.getenv("DNF_YOLO_IOU", "0.45"))
        self.boss_conf_var = tk.StringVar(value=os.getenv("DNF_YOLO_CONF_BOSS", "0.65"))
        self.monster_conf_var = tk.StringVar(value=os.getenv("DNF_YOLO_CONF_MONSTER", "0.60"))
        self.door_conf_var = tk.StringVar(value=os.getenv("DNF_YOLO_CONF_DOOR", "0.60"))
        self.goods_conf_var = tk.StringVar(value=os.getenv("DNF_YOLO_CONF_GOODS", "0.60"))
        self.money_conf_var = tk.StringVar(value=os.getenv("DNF_YOLO_CONF_MONEY", "0.60"))
        self.player_conf_var = tk.StringVar(value=os.getenv("DNF_YOLO_CONF_PLAYER", "0.45"))

        self.attack_key_var = tk.StringVar(value=os.getenv("DNF_ATTACK_KEY", "x"))
        self.attack_cooldown_var = tk.StringVar(value=os.getenv("DNF_ATTACK_COOLDOWN", "0.45"))
        self.special_key_var = tk.StringVar(value=os.getenv("DNF_SPECIAL_ATTACK_KEY", "q"))
        special_min, special_max = self._split_range(os.getenv("DNF_SPECIAL_ATTACK_COOLDOWN", "8.0-9.0"))
        self.special_min_var = tk.StringVar(value=special_min)
        self.special_max_var = tk.StringVar(value=special_max)
        self.extra_key_var = tk.StringVar(value=os.getenv("DNF_EXTRA_ATTACK_KEY", "a"))
        extra_min, extra_max = self._split_range(os.getenv("DNF_EXTRA_ATTACK_COOLDOWN", "17.0-18.0"))
        self.extra_min_var = tk.StringVar(value=extra_min)
        self.extra_max_var = tk.StringVar(value=extra_max)
        self.attack_range_x_var = tk.StringVar(value=os.getenv("DNF_MONSTER_ATTACK_RANGE_X", "70"))
        self.attack_range_y_var = tk.StringVar(value=os.getenv("DNF_MONSTER_ATTACK_RANGE_Y", "55"))

        self.timed_keys_enabled_var = tk.BooleanVar(value=os.getenv("DNF_TIMED_KEYS_ENABLED", "1") == "1")
        self.timed_key_rows: list[tuple[tk.StringVar, tk.StringVar, tk.StringVar, tk.StringVar, tk.StringVar]] = []

        self.vertical_stuck_seconds_var = tk.StringVar(value=os.getenv("DNF_VERTICAL_STUCK_SECONDS", "0.6"))
        self.vertical_move_tolerance_var = tk.StringVar(value=os.getenv("DNF_VERTICAL_STUCK_MOVE_TOLERANCE", "16"))
        self.vertical_y_tolerance_var = tk.StringVar(value=os.getenv("DNF_VERTICAL_STUCK_Y_TOLERANCE", "6"))
        self.vertical_nudge_pixels_var = tk.StringVar(value=os.getenv("DNF_VERTICAL_EDGE_NUDGE_PIXELS", "3"))
        self.vertical_right_seconds_var = tk.StringVar(value=os.getenv("DNF_VERTICAL_RIGHT_SEARCH_SECONDS", "1.2"))
        self.right_search_pixels_var = tk.StringVar(value=os.getenv("DNF_RIGHT_SEARCH_PIXELS", "40"))
        self.route_search_y_amplitude_var = tk.StringVar(value=os.getenv("DNF_ROUTE_SEARCH_Y_AMPLITUDE", "6"))
        self.horizontal_y_deadzone_var = tk.StringVar(value=os.getenv("DNF_HORIZONTAL_MOVE_Y_DEADZONE", "48"))
        self.horizontal_door_align_distance_var = tk.StringVar(value=os.getenv("DNF_HORIZONTAL_DOOR_ALIGN_DISTANCE", "120"))
        self.diagonal_y_ratio_var = tk.StringVar(value=os.getenv("DNF_DIAGONAL_Y_RATIO", "0.35"))
        self.move_press_time_var = tk.StringVar(value=os.getenv("DNF_MOVE_PRESS_TIME", "0.16"))
        self.missing_player_threshold_var = tk.StringVar(value=os.getenv("DNF_MISSING_PLAYER_RECOVER_THRESHOLD", "10"))
        self.entry_protect_seconds_var = tk.StringVar(value=os.getenv("DNF_ENTRY_DOOR_PROTECT_SECONDS", "30"))
        self.entry_protect_radius_var = tk.StringVar(value=os.getenv("DNF_ENTRY_DOOR_PROTECT_RADIUS", "280"))

        self.show_detection_window_var = tk.BooleanVar(value=os.getenv("DNF_SHOW_DETECTION_WINDOW", "0") == "1")
        self.debug_minimap_var = tk.BooleanVar(value=os.getenv("DNF_DEBUG_MINIMAP", "0") == "1")
        self.boss_route_var = tk.BooleanVar(value=os.getenv("DNF_BOSS_ROUTE", "0") == "1")
        self.query_color_fallback_var = tk.BooleanVar(value=os.getenv("DNF_QUERY_COLOR_FALLBACK", "0") == "1")
        self.layout_threshold_var = tk.StringVar(value=os.getenv("DNF_LAYOUT_TEMPLATE_THRESHOLD", "0.72"))
        self.reward_threshold_var = tk.StringVar(value=os.getenv("DNF_REWARD_TEMPLATE_THRESHOLD", "0.88"))
        self.reward_mean_diff_var = tk.StringVar(value=os.getenv("DNF_REWARD_TEMPLATE_MEAN_DIFF_MAX", "35"))
        self.reward_interval_var = tk.StringVar(value=os.getenv("DNF_REWARD_CHECK_INTERVAL", "0.5"))

        self.status_var = tk.StringVar(value="未启动")
        self._configure_style()
        self._build_ui()
        self.after(100, self._drain_log_queue)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _set_window_icon(self) -> None:
        icon_path = _resource_path("res/app.ico")
        if not icon_path.exists():
            return
        try:
            self.iconbitmap(str(icon_path))
        except tk.TclError:
            pass

    @staticmethod
    def _split_range(value: str) -> tuple[str, str]:
        parts = value.replace(",", "-").split("-", 1)
        if len(parts) != 2:
            return "0", "0"
        return parts[0].strip(), parts[1].strip()

    def _configure_style(self) -> None:
        self.configure(bg="#f3f7fb")
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", font=("Microsoft YaHei UI", 10))
        style.configure("Root.TFrame", background="#f3f7fb")
        style.configure("Panel.TFrame", background="#ffffff")
        style.configure("Header.TFrame", background="#14213d")
        style.configure("TNotebook", background="#f3f7fb", borderwidth=0)
        style.configure("TNotebook.Tab", padding=(16, 9), background="#e8edf5", foreground="#334155")
        style.map("TNotebook.Tab", background=[("selected", "#18a999")], foreground=[("selected", "#ffffff")])
        style.configure("TLabel", background="#ffffff", foreground="#1f2937")
        style.configure("Muted.TLabel", background="#ffffff", foreground="#64748b")
        style.configure("Title.TLabel", background="#14213d", foreground="#ffffff", font=("Microsoft YaHei UI", 18, "bold"))
        style.configure("Status.TLabel", background="#14213d", foreground="#fca311", font=("Microsoft YaHei UI", 10, "bold"))
        style.configure("TLabelframe", background="#ffffff", bordercolor="#d7dee9", relief="solid")
        style.configure("TLabelframe.Label", background="#ffffff", foreground="#0f766e", font=("Microsoft YaHei UI", 10, "bold"))
        style.configure("TEntry", fieldbackground="#fbfdff", foreground="#111827", insertcolor="#111827", bordercolor="#cbd5e1")
        style.configure("TCombobox", fieldbackground="#fbfdff", foreground="#111827", bordercolor="#cbd5e1")
        style.configure("TCheckbutton", background="#ffffff", foreground="#1f2937")
        style.map("TCheckbutton", background=[("active", "#ffffff")], foreground=[("active", "#0f766e")])
        style.configure("Accent.TButton", background="#18a999", foreground="#ffffff", padding=(18, 9), font=("Microsoft YaHei UI", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#12877b"), ("disabled", "#94a3b8")])
        style.configure("Danger.TButton", background="#ef476f", foreground="#ffffff", padding=(18, 9), font=("Microsoft YaHei UI", 10, "bold"))
        style.map("Danger.TButton", background=[("active", "#d63f64"), ("disabled", "#94a3b8")])

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, style="Header.TFrame", padding=(18, 14))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)
        ttk.Label(header, text="DNF 自动刷图控制台", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, textvariable=self.status_var, style="Status.TLabel").grid(row=0, column=2, sticky="e")

        body = ttk.Frame(self, style="Root.TFrame", padding=14)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)

        notebook = ttk.Notebook(body)
        self.notebook = notebook
        notebook.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        base_page = self._page(notebook)
        skill_page = self._page(notebook)
        recovery_page = self._page(notebook)
        minimap_page = self._page(notebook)

        notebook.add(base_page, text="模型与阈值")
        notebook.add(skill_page, text="技能按键")
        notebook.add(recovery_page, text="卡住恢复")
        notebook.add(minimap_page, text="小地图与提示")

        self._build_base_page(base_page)
        self._build_skill_page(skill_page)
        self._build_recovery_page(recovery_page)
        self._build_minimap_page(minimap_page)
        self._build_log_page(body)
        notebook.bind("<<NotebookTabChanged>>", self._resize_notebook_to_selected_page)
        self.after_idle(self._resize_notebook_to_selected_page)

        bottom = ttk.Frame(self, style="Header.TFrame", padding=(18, 12))
        bottom.grid(row=2, column=0, sticky="ew")
        bottom.columnconfigure(2, weight=1)
        self.start_button = ttk.Button(bottom, text="开始刷图", command=self.start_brush, style="Accent.TButton")
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        self.stop_button = ttk.Button(bottom, text="停止", command=self.stop_brush, state="disabled", style="Danger.TButton")
        self.stop_button.grid(row=0, column=1)
        ttk.Label(bottom, text="配置会在启动子进程时生效", style="Status.TLabel").grid(row=0, column=3, sticky="e")

    def _page(self, notebook: ttk.Notebook) -> ttk.Frame:
        page = ttk.Frame(notebook, style="Panel.TFrame", padding=16)
        page.columnconfigure(0, weight=1)
        return page

    def _resize_notebook_to_selected_page(self, _event: object | None = None) -> None:
        selected_tab = self.notebook.select()
        if not selected_tab:
            return

        selected_page = self.nametowidget(selected_tab)
        selected_page.update_idletasks()
        content_bottom = 0
        for child in selected_page.winfo_children():
            content_bottom = max(content_bottom, child.winfo_y() + child.winfo_reqheight())
        target_height = max(220, min(360, content_bottom + 54))
        self.notebook.configure(height=target_height)

    def _build_base_page(self, page: ttk.Frame) -> None:
        top = ttk.LabelFrame(page, text="地图与模型", padding=14)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        for column in range(4):
            top.columnconfigure(column, weight=1)

        model_values = _available_model_names(self.model_var.get())
        self._combo(top, "地图", self.map_var, ["auto", *MAP_SPECS.keys()], 0, 0)
        self._combo(top, "模型", self.model_var, model_values, 0, 2)

        detect = ttk.LabelFrame(page, text="YOLO 检测阈值", padding=14)
        detect.grid(row=1, column=0, sticky="ew")
        for column in range(6):
            detect.columnconfigure(column, weight=1)

        self._entry(detect, "输入尺寸", self.imgsz_var, 0, 0)
        self._entry(detect, "总阈值", self.conf_var, 0, 2)
        self._entry(detect, "IoU", self.iou_var, 0, 4)
        self._entry(detect, "角色", self.player_conf_var, 1, 0)
        self._entry(detect, "怪物", self.monster_conf_var, 1, 2)
        self._entry(detect, "Boss", self.boss_conf_var, 1, 4)
        self._entry(detect, "房门", self.door_conf_var, 2, 0)
        self._entry(detect, "物品", self.goods_conf_var, 2, 2)
        self._entry(detect, "金币", self.money_conf_var, 2, 4)

    def _build_skill_page(self, page: ttk.Frame) -> None:
        attacks = ttk.LabelFrame(page, text="自动攻击按键", padding=14)
        attacks.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        for column in range(6):
            attacks.columnconfigure(column, weight=1)

        self._entry(attacks, "普攻键", self.attack_key_var, 0, 0)
        self._entry(attacks, "普攻冷却", self.attack_cooldown_var, 0, 2)
        self._entry(attacks, "攻击 X 范围", self.attack_range_x_var, 0, 4)
        self._entry(attacks, "技能键", self.special_key_var, 1, 0)
        self._range_entries(attacks, "技能冷却", self.special_min_var, self.special_max_var, 1, 2)
        self._entry(attacks, "攻击 Y 范围", self.attack_range_y_var, 1, 4)
        self._entry(attacks, "额外技能键", self.extra_key_var, 2, 0)
        self._range_entries(attacks, "额外冷却", self.extra_min_var, self.extra_max_var, 2, 2)

        timed = ttk.LabelFrame(page, text="自定义定时按键", padding=14)
        timed.grid(row=1, column=0, sticky="ew")
        for column in range(5):
            timed.columnconfigure(column, weight=1)
        ttk.Checkbutton(timed, text="启用定时按键", variable=self.timed_keys_enabled_var).grid(row=0, column=0, sticky="w", pady=(0, 10))
        ttk.Label(timed, text="按键").grid(row=1, column=0, sticky="w")
        ttk.Label(timed, text="间隔最小/最大秒").grid(row=1, column=1, columnspan=2, sticky="w")
        ttk.Label(timed, text="按住最小/最大秒").grid(row=1, column=3, columnspan=2, sticky="w")

        rules = parse_timed_key_spec(os.getenv("DNF_TIMED_KEYS", DEFAULT_TIMED_KEY_SPEC))
        defaults = [(rule.key, str(rule.interval_min), str(rule.interval_max), str(rule.hold_min), str(rule.hold_max)) for rule in rules]
        while len(defaults) < 5:
            defaults.append(("", "", "", "", ""))
        for index, values in enumerate(defaults[:5], start=2):
            self._timed_key_row(timed, index, values)

    def _build_recovery_page(self, page: ttk.Frame) -> None:
        recovery = ttk.LabelFrame(page, text="卡住恢复与路线保护", padding=14)
        recovery.grid(row=0, column=0, sticky="ew")
        for column in range(6):
            recovery.columnconfigure(column, weight=1)

        self._entry(recovery, "上下卡住秒数", self.vertical_stuck_seconds_var, 0, 0)
        self._entry(recovery, "移动容差", self.vertical_move_tolerance_var, 0, 2)
        self._entry(recovery, "Y 轴容差", self.vertical_y_tolerance_var, 0, 4)
        self._entry(recovery, "反向微移像素", self.vertical_nudge_pixels_var, 1, 0)
        self._entry(recovery, "右搜持续秒", self.vertical_right_seconds_var, 1, 2)
        self._entry(recovery, "右搜像素", self.right_search_pixels_var, 1, 4)
        self._entry(recovery, "找门Y幅度", self.route_search_y_amplitude_var, 2, 0)
        self._entry(recovery, "横向Y死区", self.horizontal_y_deadzone_var, 2, 2)
        self._entry(recovery, "斜向Y比例", self.diagonal_y_ratio_var, 2, 4)
        self._entry(recovery, "贴门校准距离", self.horizontal_door_align_distance_var, 3, 0)
        self._entry(recovery, "移动按住秒", self.move_press_time_var, 3, 2)
        self._entry(recovery, "丢失角色帧数", self.missing_player_threshold_var, 3, 4)
        self._entry(recovery, "入口保护秒", self.entry_protect_seconds_var, 4, 0)
        self._entry(recovery, "入口保护半径", self.entry_protect_radius_var, 4, 2)
        ttk.Label(
            recovery,
            text="横向跑图会优先直走；上/下卡住 0.6 秒后微移 3 像素，再向右持续找门。",
            style="Muted.TLabel",
        ).grid(row=5, column=0, columnspan=6, sticky="w", pady=(12, 0))

    def _build_minimap_page(self, page: ttk.Frame) -> None:
        route = ttk.LabelFrame(page, text="小地图路线", padding=14)
        route.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        for column in range(4):
            route.columnconfigure(column, weight=1)

        ttk.Checkbutton(route, text="显示检测画面窗口", variable=self.show_detection_window_var).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(route, text="显示小地图调试窗口", variable=self.debug_minimap_var).grid(row=0, column=1, sticky="w")
        ttk.Checkbutton(route, text="启用 Boss 路线", variable=self.boss_route_var).grid(row=0, column=2, sticky="w")
        ttk.Checkbutton(route, text="任务点颜色兜底", variable=self.query_color_fallback_var).grid(row=0, column=3, sticky="w")
        self._entry(route, "地图模板阈值", self.layout_threshold_var, 1, 0)

        prompt = ttk.LabelFrame(page, text="奖励/重试提示识别", padding=14)
        prompt.grid(row=1, column=0, sticky="ew")
        for column in range(6):
            prompt.columnconfigure(column, weight=1)
        self._entry(prompt, "奖励模板阈值", self.reward_threshold_var, 0, 0)
        self._entry(prompt, "均值差上限", self.reward_mean_diff_var, 0, 2)
        self._entry(prompt, "检测间隔秒", self.reward_interval_var, 0, 4)

    def _build_log_page(self, page: ttk.Frame) -> None:
        page.rowconfigure(1, weight=1)
        log_outer = ttk.LabelFrame(page, text="运行日志", padding=10)
        log_outer.grid(row=1, column=0, sticky="nsew")
        log_outer.columnconfigure(0, weight=1)
        log_outer.rowconfigure(0, weight=1)

        self.log_text = tk.Text(
            log_outer,
            height=24,
            wrap="word",
            state="disabled",
            bg="#020617",
            fg="#dbeafe",
            insertbackground="#dbeafe",
            relief="flat",
            font=("Consolas", 10),
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(log_outer, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def _entry(self, parent: ttk.Frame, label: str, variable: tk.StringVar, row: int, column: int) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=column, sticky="w", pady=8)
        ttk.Entry(parent, textvariable=variable, width=11).grid(
            row=row,
            column=column + 1,
            sticky="ew",
            padx=(8, 18),
            pady=8,
        )

    def _combo(self, parent: ttk.Frame, label: str, variable: tk.StringVar, values: list[str], row: int, column: int) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=column, sticky="w", pady=8)
        ttk.Combobox(parent, textvariable=variable, values=values, state="readonly").grid(
            row=row,
            column=column + 1,
            sticky="ew",
            padx=(8, 18),
            pady=8,
        )

    def _range_entries(
        self,
        parent: ttk.Frame,
        label: str,
        min_var: tk.StringVar,
        max_var: tk.StringVar,
        row: int,
        column: int,
    ) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=column, sticky="w", pady=8)
        frame = ttk.Frame(parent, style="Panel.TFrame")
        frame.grid(row=row, column=column + 1, sticky="ew", padx=(8, 18), pady=8)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(2, weight=1)
        ttk.Entry(frame, textvariable=min_var, width=6).grid(row=0, column=0, sticky="ew")
        ttk.Label(frame, text="-").grid(row=0, column=1, padx=5)
        ttk.Entry(frame, textvariable=max_var, width=6).grid(row=0, column=2, sticky="ew")

    def _timed_key_row(
        self,
        parent: ttk.Frame,
        row: int,
        values: tuple[str, str, str, str, str],
    ) -> None:
        variables = tuple(tk.StringVar(value=value) for value in values)
        self.timed_key_rows.append(variables)
        for column, variable in enumerate(variables):
            ttk.Entry(parent, textvariable=variable, width=10).grid(row=row, column=column, sticky="ew", padx=(0, 10), pady=5)

    def _validate_settings(self) -> bool:
        numeric_values: dict[str, tuple[str, type]] = {
            "输入尺寸": (self.imgsz_var.get(), int),
            "总阈值": (self.conf_var.get(), float),
            "IoU": (self.iou_var.get(), float),
            "角色阈值": (self.player_conf_var.get(), float),
            "怪物阈值": (self.monster_conf_var.get(), float),
            "Boss 阈值": (self.boss_conf_var.get(), float),
            "房门阈值": (self.door_conf_var.get(), float),
            "物品阈值": (self.goods_conf_var.get(), float),
            "金币阈值": (self.money_conf_var.get(), float),
            "普攻冷却": (self.attack_cooldown_var.get(), float),
            "技能冷却最小": (self.special_min_var.get(), float),
            "技能冷却最大": (self.special_max_var.get(), float),
            "额外冷却最小": (self.extra_min_var.get(), float),
            "额外冷却最大": (self.extra_max_var.get(), float),
            "攻击 X 范围": (self.attack_range_x_var.get(), float),
            "攻击 Y 范围": (self.attack_range_y_var.get(), float),
            "上下卡住秒数": (self.vertical_stuck_seconds_var.get(), float),
            "移动容差": (self.vertical_move_tolerance_var.get(), float),
            "Y 轴容差": (self.vertical_y_tolerance_var.get(), float),
            "反向微移像素": (self.vertical_nudge_pixels_var.get(), float),
            "右搜持续秒": (self.vertical_right_seconds_var.get(), float),
            "右搜像素": (self.right_search_pixels_var.get(), float),
            "找门Y幅度": (self.route_search_y_amplitude_var.get(), float),
            "横向Y死区": (self.horizontal_y_deadzone_var.get(), float),
            "贴门校准距离": (self.horizontal_door_align_distance_var.get(), float),
            "斜向Y比例": (self.diagonal_y_ratio_var.get(), float),
            "移动按住秒": (self.move_press_time_var.get(), float),
            "丢失角色帧数": (self.missing_player_threshold_var.get(), int),
            "入口保护秒": (self.entry_protect_seconds_var.get(), float),
            "入口保护半径": (self.entry_protect_radius_var.get(), float),
            "地图模板阈值": (self.layout_threshold_var.get(), float),
            "奖励模板阈值": (self.reward_threshold_var.get(), float),
            "均值差上限": (self.reward_mean_diff_var.get(), float),
            "检测间隔秒": (self.reward_interval_var.get(), float),
        }
        try:
            for _, (value, parser) in numeric_values.items():
                parser(value)
            if float(self.special_min_var.get()) > float(self.special_max_var.get()):
                raise ValueError("技能冷却最小值不能大于最大值")
            if float(self.extra_min_var.get()) > float(self.extra_max_var.get()):
                raise ValueError("额外冷却最小值不能大于最大值")
            parse_timed_key_spec(self._build_timed_key_spec())
        except ValueError as exc:
            messagebox.showerror("参数错误", f"参数格式不正确：{exc}")
            return False
        return True

    def _build_timed_key_spec(self) -> str:
        parts = []
        for key_var, interval_min_var, interval_max_var, hold_min_var, hold_max_var in self.timed_key_rows:
            key = key_var.get().strip()
            interval_min = interval_min_var.get().strip()
            interval_max = interval_max_var.get().strip()
            hold_min = hold_min_var.get().strip()
            hold_max = hold_max_var.get().strip()
            if not any((key, interval_min, interval_max, hold_min, hold_max)):
                continue
            if not all((key, interval_min, interval_max, hold_min, hold_max)):
                raise ValueError("定时按键每一行都需要填完整")
            parts.append(f"{key}:{interval_min}-{interval_max}:{hold_min}-{hold_max}")
        return ";".join(parts)

    def _build_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env.update(
            {
                "DNF_MAP_NAME": self.map_var.get(),
                "DNF_YOLO_WEIGHTS": self.model_var.get(),
                "DNF_YOLO_IMGSZ": self.imgsz_var.get(),
                "DNF_YOLO_CONF": self.conf_var.get(),
                "DNF_YOLO_IOU": self.iou_var.get(),
                "DNF_YOLO_CONF_BOSS": self.boss_conf_var.get(),
                "DNF_YOLO_CONF_MONSTER": self.monster_conf_var.get(),
                "DNF_YOLO_CONF_DOOR": self.door_conf_var.get(),
                "DNF_YOLO_CONF_GOODS": self.goods_conf_var.get(),
                "DNF_YOLO_CONF_MONEY": self.money_conf_var.get(),
                "DNF_YOLO_CONF_PLAYER": self.player_conf_var.get(),
                "DNF_ATTACK_KEY": self.attack_key_var.get().strip(),
                "DNF_ATTACK_COOLDOWN": self.attack_cooldown_var.get(),
                "DNF_SPECIAL_ATTACK_KEY": self.special_key_var.get().strip(),
                "DNF_SPECIAL_ATTACK_COOLDOWN": f"{self.special_min_var.get()}-{self.special_max_var.get()}",
                "DNF_EXTRA_ATTACK_KEY": self.extra_key_var.get().strip(),
                "DNF_EXTRA_ATTACK_COOLDOWN": f"{self.extra_min_var.get()}-{self.extra_max_var.get()}",
                "DNF_MONSTER_ATTACK_RANGE_X": self.attack_range_x_var.get(),
                "DNF_MONSTER_ATTACK_RANGE_Y": self.attack_range_y_var.get(),
                "DNF_TIMED_KEYS_ENABLED": "1" if self.timed_keys_enabled_var.get() else "0",
                "DNF_TIMED_KEYS": self._build_timed_key_spec(),
                "DNF_VERTICAL_STUCK_SECONDS": self.vertical_stuck_seconds_var.get(),
                "DNF_VERTICAL_STUCK_MOVE_TOLERANCE": self.vertical_move_tolerance_var.get(),
                "DNF_VERTICAL_STUCK_Y_TOLERANCE": self.vertical_y_tolerance_var.get(),
                "DNF_VERTICAL_EDGE_NUDGE_PIXELS": self.vertical_nudge_pixels_var.get(),
                "DNF_VERTICAL_RIGHT_SEARCH_SECONDS": self.vertical_right_seconds_var.get(),
                "DNF_RIGHT_SEARCH_PIXELS": self.right_search_pixels_var.get(),
                "DNF_ROUTE_SEARCH_Y_AMPLITUDE": self.route_search_y_amplitude_var.get(),
                "DNF_HORIZONTAL_MOVE_Y_DEADZONE": self.horizontal_y_deadzone_var.get(),
                "DNF_HORIZONTAL_DOOR_ALIGN_DISTANCE": self.horizontal_door_align_distance_var.get(),
                "DNF_DIAGONAL_Y_RATIO": self.diagonal_y_ratio_var.get(),
                "DNF_MOVE_PRESS_TIME": self.move_press_time_var.get(),
                "DNF_MISSING_PLAYER_RECOVER_THRESHOLD": self.missing_player_threshold_var.get(),
                "DNF_ENTRY_DOOR_PROTECT_SECONDS": self.entry_protect_seconds_var.get(),
                "DNF_ENTRY_DOOR_PROTECT_RADIUS": self.entry_protect_radius_var.get(),
                "DNF_SHOW_DETECTION_WINDOW": "1" if self.show_detection_window_var.get() else "0",
                "DNF_DEBUG_MINIMAP": "1" if self.debug_minimap_var.get() else "0",
                "DNF_BOSS_ROUTE": "1" if self.boss_route_var.get() else "0",
                "DNF_QUERY_COLOR_FALLBACK": "1" if self.query_color_fallback_var.get() else "0",
                "DNF_LAYOUT_TEMPLATE_THRESHOLD": self.layout_threshold_var.get(),
                "DNF_REWARD_TEMPLATE_THRESHOLD": self.reward_threshold_var.get(),
                "DNF_REWARD_TEMPLATE_MEAN_DIFF_MAX": self.reward_mean_diff_var.get(),
                "DNF_REWARD_CHECK_INTERVAL": self.reward_interval_var.get(),
                "PYTHONUNBUFFERED": "1",
                "PYTHONIOENCODING": "utf-8",
                "PYTHONUTF8": "1",
            }
        )
        return env

    def start_brush(self) -> None:
        if self.process and self.process.poll() is None:
            return
        if not self._validate_settings():
            return

        command = _brush_child_command()
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        self._append_log("启动刷图程序...\n")
        try:
            self.process = subprocess.Popen(
                command,
                cwd=str(ROOT),
                env=self._build_env(),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                creationflags=creationflags,
            )
        except Exception as exc:
            messagebox.showerror("启动失败", str(exc))
            self.process = None
            return

        self.status_var.set("运行中")
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        threading.Thread(target=self._read_process_output, daemon=True).start()

    def stop_brush(self) -> None:
        if not self.process or self.process.poll() is not None:
            self._set_stopped()
            return

        self._release_movement_keys()
        self._append_log("正在停止刷图程序...\n")
        self.process.terminate()
        try:
            self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=3)
        self._set_stopped()

    def _read_process_output(self) -> None:
        if not self.process or not self.process.stdout:
            return
        for line in self.process.stdout:
            self.log_queue.put(line)
        self.log_queue.put("__DNF_PROCESS_EXIT__")

    def _drain_log_queue(self) -> None:
        while True:
            try:
                line = self.log_queue.get_nowait()
            except queue.Empty:
                break
            if line == "__DNF_PROCESS_EXIT__":
                if self.process and self.process.poll() is not None:
                    self._set_stopped()
                continue
            self._append_log(line)
        self.after(100, self._drain_log_queue)

    def _append_log(self, text: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _set_stopped(self) -> None:
        self.status_var.set("已停止")
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def _release_movement_keys(self) -> None:
        try:
            import pydirectinput

            keys = {"up", "down", "left", "right", "d", "s", "e"}
            for variable in (self.attack_key_var, self.special_key_var, self.extra_key_var):
                key = variable.get().strip()
                if key:
                    keys.add(key)
            for row in self.timed_key_rows:
                key = row[0].get().strip()
                if key:
                    keys.add(key)
            for key in keys:
                pydirectinput.keyUp(key)
        except Exception:
            pass

    def _on_close(self) -> None:
        if self.process and self.process.poll() is None:
            if not messagebox.askyesno("退出", "刷图程序仍在运行，是否停止并退出？"):
                return
            self.stop_brush()
        self.destroy()


def main() -> None:
    if "--brush-child" in sys.argv:
        from dnf.main import main as brush_main

        brush_main()
        return

    app = DnfBrushLauncher()
    app.mainloop()


def _brush_child_command() -> list[str]:
    if getattr(sys, "frozen", False):
        return [sys.executable, "--brush-child"]
    return [sys.executable, "-m", "dnf.launcher", "--brush-child"]


if __name__ == "__main__":
    main()
