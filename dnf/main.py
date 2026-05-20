#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : main.py
@Desc    : Win32-based DNF capture loop
"""
from __future__ import annotations

import os
import pathlib
import time
from typing import Optional, Tuple

import cv2
import mss
import numpy as np
import pyautogui
import win32con
import win32gui
from loguru import logger

from dnf.game import Game
from dnf.minimap_nav import MiniMapNavigator
from dnf.skill_detector import SkillReadinessDetector
from dnf.timed_keys import build_timed_key_scheduler_from_env
from dnf.ui_detector import (
    handle_retry_challenge_prompt,
    handle_reward_selection_prompt,
    is_retry_challenge_prompt,
    is_reward_selection_prompt,
)

temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

from dnf.detector import Detector


WINDOW_OFFSET_X = 10
WINDOW_OFFSET_Y = 10
DEBUG_MINIMAP = os.getenv("DNF_DEBUG_MINIMAP", "0") == "1"
SHOW_DETECTION_WINDOW = os.getenv("DNF_SHOW_DETECTION_WINDOW", "0") == "1"
ROUTE_DEBUG = os.getenv("DNF_ROUTE_DEBUG", "0") == "1"
WINDOW_TITLE_KEYWORD = "地下城与勇士"
WINDOW_CLASS_NAMES = {"地下城与勇士", "地下城与勇士创新世纪"}


def _find_dnf_window() -> int:
    candidates = []

    def _enum_windows(hwnd: int, _: object) -> None:
        if not win32gui.IsWindowVisible(hwnd):
            return

        title = win32gui.GetWindowText(hwnd).strip()
        class_name = win32gui.GetClassName(hwnd).strip()
        if not title and not class_name:
            return

        title_match = WINDOW_TITLE_KEYWORD in title
        class_match = class_name in WINDOW_CLASS_NAMES or WINDOW_TITLE_KEYWORD in class_name
        if not title_match and not class_match:
            return

        try:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            area = max(0, right - left) * max(0, bottom - top)
        except win32gui.error:
            area = 0

        candidates.append((area, hwnd, title, class_name))

    win32gui.EnumWindows(_enum_windows, None)
    if not candidates:
        raise RuntimeError("没有找到 DNF 窗口")

    candidates.sort(key=lambda item: item[0], reverse=True)
    hwnd = candidates[0][1]
    logger.info(
        "绑定窗口: hwnd={}, title={}, class={}",
        hwnd,
        candidates[0][2],
        candidates[0][3],
    )
    return hwnd


def _place_window(hwnd: int) -> None:
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = max(1, right - left)
    height = max(1, bottom - top)
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOPMOST,
        WINDOW_OFFSET_X,
        WINDOW_OFFSET_Y,
        width,
        height,
        win32con.SWP_SHOWWINDOW,
    )


def _get_client_region(hwnd: int) -> Tuple[int, int, int, int]:
    left_top = win32gui.ClientToScreen(hwnd, (0, 0))
    client_rect = win32gui.GetClientRect(hwnd)
    left = int(left_top[0])
    top = int(left_top[1])
    width = int(client_rect[2] - client_rect[0])
    height = int(client_rect[3] - client_rect[1])
    if width <= 0 or height <= 0:
        raise RuntimeError("获取游戏客户区失败")
    return left, top, width, height


def _capture_client(
    hwnd: int,
    screen_grabber: Optional[mss.mss] = None,
) -> Tuple[np.ndarray, Tuple[int, int], Tuple[int, int]]:
    left, top, width, height = _get_client_region(hwnd)
    if screen_grabber is not None:
        frame_bgra = np.asarray(
            screen_grabber.grab({"left": left, "top": top, "width": width, "height": height})
        )
        img_np = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2RGB)
        return img_np, (width, height), (left, top)

    img = pyautogui.screenshot(region=(left, top, width, height))
    img_np = np.array(img)
    return img_np, (width, height), (left, top)


def _timed_key_names(timed_key_scheduler: object) -> Tuple[str, ...]:
    rules = getattr(timed_key_scheduler, "rules", ())
    return tuple(str(getattr(rule, "key", "")).strip() for rule in rules if getattr(rule, "key", ""))


def _pause_actions_for_ui_prompt(timed_key_scheduler: object | None) -> None:
    timed_keys: Tuple[str, ...] = ()
    if timed_key_scheduler is not None:
        timed_keys = _timed_key_names(timed_key_scheduler)
        pause = getattr(timed_key_scheduler, "pause", None)
        if callable(pause):
            pause()
    Game.release_action_keys(timed_keys)
    Game.reset_motion_cache()


def _resume_actions_after_ui_prompt(timed_key_scheduler: object | None) -> None:
    if timed_key_scheduler is None:
        return
    resume = getattr(timed_key_scheduler, "resume", None)
    if callable(resume):
        resume()


def _debug_windows_requested() -> bool:
    return SHOW_DETECTION_WINDOW or DEBUG_MINIMAP


def _debug_window_quit_requested() -> bool:
    if not _debug_windows_requested():
        return False
    return bool(cv2.waitKey(1) & 0xFF == ord("q"))


def main() -> None:
    device_type = ""
    detector = Detector(device_type, draw_detections=SHOW_DETECTION_WINDOW)
    navigator = MiniMapNavigator(os.getenv("DNF_MAP_NAME", "universal"))
    skill_detector = SkillReadinessDetector()

    hwnd = _find_dnf_window()
    _place_window(hwnd)
    screen_grabber = mss.mss()
    timed_key_scheduler = build_timed_key_scheduler_from_env()
    if timed_key_scheduler is not None:
        timed_key_scheduler.start()
    ui_prompt_active = False

    try:
        while True:
            start_time = time.time()
            try:
                img_np, (width, height), screen_origin = _capture_client(hwnd, screen_grabber)
            except Exception as exc:
                logger.exception("截图失败: {}", exc)
                time.sleep(0.2)
                continue

            reward_prompt = is_reward_selection_prompt(img_np)
            retry_prompt = False if reward_prompt else is_retry_challenge_prompt(img_np)
            if reward_prompt or retry_prompt:
                if not ui_prompt_active:
                    logger.info("ui prompt detected, pause all movement and timed keys")
                ui_prompt_active = True
                _pause_actions_for_ui_prompt(timed_key_scheduler)
                if reward_prompt:
                    handle_reward_selection_prompt(img_np, screen_origin)
                else:
                    handle_retry_challenge_prompt(img_np, screen_origin)
                logger.debug("处理时间: {}", time.time() - start_time)
                if _debug_window_quit_requested():
                    break
                continue

            if ui_prompt_active:
                logger.info("ui prompt cleared, resume timed keys")
                _resume_actions_after_ui_prompt(timed_key_scheduler)
                ui_prompt_active = False

            img, obj = detector.detect(img_np)
            logger.debug("obj: {}", obj)

            frame_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            special_skill_ready, skill_scores = skill_detector.detect(frame_bgr)
            route_snapshot = navigator.build_route_snapshot(
                frame_bgr,
                obj or [],
                include_debug_scores=ROUTE_DEBUG or DEBUG_MINIMAP,
            )
            route_direction = (
                route_snapshot.next_room_direction.upper()
                if route_snapshot.next_room_direction
                else None
            )
            logger.debug(
                "route: map={}, current={}, boss={}, query={}, elite={}, down={}, target={}@{}, direction={}, door={}, scores={}",
                navigator.map_name,
                route_snapshot.current_room,
                route_snapshot.boss_room,
                route_snapshot.query_room,
                route_snapshot.elite_room,
                route_snapshot.down_room,
                route_snapshot.target_kind,
                route_snapshot.target_room,
                route_direction,
                route_snapshot.selected_door_center,
                route_snapshot.debug_scores,
            )
            logger.debug("skill: ready={}, scores={}", special_skill_ready, skill_scores)

            game = Game(
                obj,
                width,
                height,
                route_direction,
                route_snapshot.selected_door_center,
                route_snapshot.target_kind,
                special_skill_ready,
            )
            game.run()

            if SHOW_DETECTION_WINDOW:
                display = cv2.resize(img, (640, 360))
                cv2.imshow("dnf-detection-debug", display)
            if DEBUG_MINIMAP:
                minimap_debug = navigator.draw_debug_minimap(frame_bgr)
                cv2.imshow(
                    "dnf-minimap-debug",
                    cv2.resize(minimap_debug, (432, 252), interpolation=cv2.INTER_NEAREST),
                )
            logger.debug("处理时间: {}", time.time() - start_time)
            if _debug_window_quit_requested():
                break
    finally:
        if timed_key_scheduler is not None:
            timed_key_scheduler.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
