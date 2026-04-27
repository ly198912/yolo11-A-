from __future__ import annotations

import json
import os
import time

import cv2
import numpy as np
import pyautogui

from dnf.detector import Detector
from dnf.minimap_nav import MiniMapNavigator


def main() -> None:
    width = 1067
    height = 600
    detector = Detector("")
    navigator = MiniMapNavigator(map_name=os.getenv("DNF_MAP_NAME", "auto"))

    while True:
        started = time.time()
        img = pyautogui.screenshot(region=(0, 0, width, height))
        frame_rgb = np.array(img)
        annotated, objects = detector.detect(frame_rgb)
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        snapshot = navigator.build_route_snapshot(frame_bgr, objects or [])
        print(
            json.dumps(
                {
                    "current_room": snapshot.current_room,
                    "boss_room": snapshot.boss_room,
                    "query_room": snapshot.query_room,
                    "elite_room": snapshot.elite_room,
                    "next_room_direction": snapshot.next_room_direction,
                    "selected_door_center": snapshot.selected_door_center,
                    "cost_ms": round((time.time() - started) * 1000, 1),
                },
                ensure_ascii=False,
            )
        )

        if annotated is not None:
            minimap = navigator.draw_debug_minimap(frame_bgr)
            cv2.imshow("dnf-route-frame", cv2.resize(annotated, (800, 450)))
            cv2.imshow("dnf-route-minimap", cv2.resize(minimap, (432, 252), interpolation=cv2.INTER_NEAREST))

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
