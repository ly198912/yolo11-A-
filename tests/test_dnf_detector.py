from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dnf.detector import Detector


class DummyBoxes:
    def __init__(self) -> None:
        self.xyxy = torch.tensor([[10.0, 20.0, 50.0, 80.0]])
        self.xywh = torch.tensor([[30.0, 50.0, 40.0, 60.0]])
        self.conf = torch.tensor([0.876])
        self.cls = torch.tensor([1.0])

    def __len__(self) -> int:
        return len(self.cls)


class DummyResult:
    def __init__(self) -> None:
        self.boxes = DummyBoxes()


class DummyYOLO:
    def __init__(self, weights: str) -> None:
        self.weights = weights
        self.names = {0: "player", 1: "monster"}
        self.predict_calls = []

    def predict(self, **kwargs):
        self.predict_calls.append(kwargs)
        return [DummyResult()]


def test_detector_uses_yolo11_predict_and_preserves_output_shape(monkeypatch) -> None:
    created_models = []

    def fake_yolo(weights: str):
        model = DummyYOLO(weights)
        created_models.append(model)
        return model

    monkeypatch.setattr("dnf.detector.YOLO", fake_yolo)

    detector = Detector(device_type="cpu", weights="dnf/shzn.pt")
    image_rgb = np.zeros((100, 120, 3), dtype=np.uint8)
    annotated, objects = detector.detect(image_rgb)

    assert annotated.shape == image_rgb.shape
    assert objects == [{"monster": {"xywh": [10.0, 20.0, 40.0, 60.0], "conf": 0.88}}]

    model = created_models[0]
    assert Path(model.weights).as_posix().endswith("dnf/shzn.pt")
    assert model.predict_calls[0]["source"].shape == image_rgb.shape
    assert model.predict_calls[0]["imgsz"] == 512
    assert model.predict_calls[0]["conf"] == 0.35
    assert model.predict_calls[0]["iou"] == 0.45
    assert model.predict_calls[0]["device"] == "cpu"
    assert model.predict_calls[0]["half"] is False
    assert model.predict_calls[0]["max_det"] == 40
