from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dnf.scene_detection import build_probe, match_probe, probe_matches, SceneRoomTracker
from dnf.scene_types import DungeonProfileConfig, GameFrameContext, RoomSceneConfig


def make_frame(width: int = 200, height: int = 120, *, color_bgr: tuple[int, int, int] = (0, 0, 0)) -> np.ndarray:
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:, :] = color_bgr
    return frame


def make_ctx(frame: np.ndarray, *, captured_at: float = 1.0) -> GameFrameContext:
    height, width = frame.shape[:2]
    return GameFrameContext(
        hwnd=1,
        frame_bgr=frame,
        client_width=width,
        client_height=height,
        client_rect=(0, 0, width, height),
        captured_at=captured_at,
    )


def test_region_to_pixels_uses_current_client_size() -> None:
    frame = make_frame(width=400, height=300)
    ctx = make_ctx(frame)
    assert ctx.region_to_pixels((0.25, 0.10, 0.75, 0.90)) == (100, 30, 300, 270)


def test_probe_matching_tolerates_small_brightness_variation() -> None:
    frame = make_frame()
    frame[20:60, 50:120] = (225, 155, 60)  # BGR for RGB ~= (60, 155, 225)
    ctx = make_ctx(frame)
    probe = build_probe(
        "bright-blue",
        (0.20, 0.10, 0.70, 0.60),
        start_hex="#FF3B90D8",
        end_hex="#FF449BE4",
        match_threshold=0.45,
        brightness_tolerance=18,
    )
    assert match_probe(ctx, probe) >= 0.45
    assert probe_matches(ctx, probe)


def test_scene_room_tracker_confirms_and_holds_profile_and_room() -> None:
    profile_probe = build_probe("profile", (0.0, 0.0, 0.25, 0.25), start_hex="#FF112233", end_hex="#FF112233", match_threshold=0.9)
    room_probe = build_probe("room1", (0.25, 0.25, 0.50, 0.50), start_hex="#FF445566", end_hex="#FF445566", match_threshold=0.9)
    profile = DungeonProfileConfig(
        profile_name="test-profile",
        entry_probes=(profile_probe,),
        room_configs=(RoomSceneConfig(room_id=1, scene_probes=(room_probe,), confirm_frames=2, hold_seconds=0.5),),
        confirm_frames=2,
        hold_seconds=0.8,
    )
    tracker = SceneRoomTracker({"test-profile": profile})

    matched = make_frame()
    matched[0:30, 0:50] = (51, 34, 17)  # BGR for RGB(17,34,51)
    matched[30:60, 50:100] = (102, 85, 68)  # BGR for RGB(68,85,102)

    ctx1 = make_ctx(matched, captured_at=1.0)
    ctx2 = make_ctx(matched, captured_at=1.1)
    assert tracker.detect_profile(ctx1) is None
    assert tracker.detect_profile(ctx2) == "test-profile"

    assert tracker.detect_room(ctx1, "test-profile") is None
    assert tracker.detect_room(ctx2, "test-profile") == 1

    blank = make_ctx(make_frame(), captured_at=1.4)
    assert tracker.detect_profile(blank) == "test-profile"
    assert tracker.detect_room(blank, "test-profile") == 1

    expired = make_ctx(make_frame(), captured_at=2.2)
    assert tracker.detect_profile(expired) is None
