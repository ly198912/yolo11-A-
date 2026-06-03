from types import SimpleNamespace

import numpy as np

from dnf.detector import Detector
from dnf.game import Game


def _reset_game_state():
    Game._motion_active = False
    Game._player = None
    Game._pre_player = None
    Game._player_missing_started_at = None
    Game._last_player_center = None
    Game._room_entry_position = None
    Game._cached_money_target = None
    Game._cached_money_seen_at = 0.0


def test_detector_accepts_lower_confidence_money_without_relaxing_goods(monkeypatch):
    predict_args = {}

    class FakeTensor:
        def __init__(self, values):
            self._values = np.array(values)

        def cpu(self):
            return self

        def numpy(self):
            return self._values

    class FakeBoxes:
        xyxy = FakeTensor([[0, 0, 10, 10], [10, 10, 20, 20]])
        conf = FakeTensor([0.40, 0.40])
        cls = FakeTensor([0, 1])

        def __len__(self):
            return 2

    class FakeModel:
        names = {0: "goods", 1: "money"}

        def predict(self, **kwargs):
            predict_args.update(kwargs)
            return [SimpleNamespace(boxes=FakeBoxes())]

    class FakeAnnotator:
        def __init__(self, image, **_kwargs):
            self.image = image

        def box_label(self, *_args, **_kwargs):
            return None

        def result(self):
            return self.image

    monkeypatch.setattr("dnf.detector.YOLO", lambda _weights: FakeModel())
    monkeypatch.setattr("dnf.detector.Annotator", FakeAnnotator)
    monkeypatch.setattr("dnf.detector.torch.cuda.is_available", lambda: False)

    detector = Detector()
    _, objects = detector.detect(np.zeros((20, 20, 3), dtype=np.uint8))

    assert predict_args["conf"] == 0.35
    assert objects == [{"money": {"xywh": [10.0, 10.0, 10.0, 10.0], "conf": 0.4}}]


def test_game_prioritizes_money_before_regular_goods():
    _reset_game_state()
    pickups = []

    class DryGame(Game):
        def _pick_up(self, obj_box, clear_money_target=False):
            pickups.append((tuple(obj_box), clear_money_target))

    game = DryGame(
        [
            {"player": {"xywh": [280.0, 260.0, 40.0, 80.0], "conf": 0.99}},
            {"goods": {"xywh": [310.0, 300.0, 20.0, 20.0], "conf": 0.90}},
            {"money": {"xywh": [330.0, 300.0, 20.0, 20.0], "conf": 0.60}},
        ],
        800,
        600,
        None,
    )

    game.run()

    assert pickups == [((340.0, 310.0, 20.0, 20.0), True)]


def test_game_reuses_recent_money_target_during_short_detector_gap(monkeypatch):
    _reset_game_state()
    now = [10.0]
    monkeypatch.setattr("dnf.game.time.time", lambda: now[0])

    game = Game(
        [{"money": {"xywh": [330.0, 300.0, 20.0, 20.0], "conf": 0.60}}],
        800,
        600,
        None,
    )
    game._player_xywh = [300.0, 300.0, 40.0, 80.0]

    detected = game._get_money_target()
    game._obj = []
    now[0] = 10.5
    cached = game._get_money_target()
    now[0] = 11.0
    expired = game._get_money_target()

    assert detected == {"xywh": [340.0, 310.0, 20.0, 20.0], "conf": 0.60}
    assert cached == detected
    assert expired is None
