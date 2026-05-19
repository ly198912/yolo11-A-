#! /usr/bin/env python
"""
@File    : detector.py
@Desc    : YOLO11 detector adapter for DNF.
"""

from __future__ import annotations

import os
import random
from pathlib import Path

import cv2
import numpy as np
import torch

from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator


class Detector:
    def __init__(self, device_type: str = "", weights: str | None = None, draw_detections: bool | None = None):
        self.img_size = int(os.getenv("DNF_YOLO_IMGSZ", "512"))
        self.conf_thres = float(os.getenv("DNF_YOLO_CONF", "0.35"))
        self.iou_thres = float(os.getenv("DNF_YOLO_IOU", "0.45"))
        self.draw_detections = (
            os.getenv("DNF_DRAW_DETECTIONS", "0") == "1" if draw_detections is None else draw_detections
        )
        self.hide_labels = False
        self.hide_conf = False
        self.class_conf_thres = {
            "boss": float(os.getenv("DNF_YOLO_CONF_BOSS", "0.65")),
            "door": float(os.getenv("DNF_YOLO_CONF_DOOR", "0.60")),
            "goods": float(os.getenv("DNF_YOLO_CONF_GOODS", "0.60")),
            "money": float(os.getenv("DNF_YOLO_CONF_MONEY", "0.60")),
            "monster": float(os.getenv("DNF_YOLO_CONF_MONSTER", "0.60")),
            "player": float(os.getenv("DNF_YOLO_CONF_PLAYER", "0.45")),
        }

        self.device = device_type or ("0" if torch.cuda.is_available() else "cpu")
        self.use_half = self.device != "cpu" and torch.cuda.is_available()
        if self.use_half:
            torch.backends.cudnn.benchmark = True
        default_weights = os.getenv("DNF_YOLO_WEIGHTS", "ds.pt")
        if weights:
            weights_path = Path(weights)
        else:
            weights_path = Path(default_weights)
            if not weights_path.is_absolute() and not weights_path.exists():
                weights_path = Path(__file__).resolve().parent / weights_path
        self.weights = str(weights_path)
        self.model = YOLO(self.weights)
        if hasattr(self.model, "fuse"):
            self.model.fuse()
        self.names = self.model.names
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(self.names))]

    @staticmethod
    def _normalize_label(label: str) -> str:
        label = str(label).strip().lower()
        if "door" in label:
            return "door"
        return label

    @staticmethod
    def _xyxy_to_xywh_top_left(xyxy: np.ndarray) -> list[float]:
        x1, y1, x2, y2 = [float(v) for v in xyxy]
        return [x1, y1, max(0.0, x2 - x1), max(0.0, y2 - y1)]

    def detect(self, img0: np.ndarray) -> tuple[np.ndarray | None, list | None]:
        """图片预测。 返回: - annotated_bgr: 画好框的 BGR 图像 - obj: [{'monster': {'xywh': [x, y, w, h], 'conf': 0.84}}, ...].
        """
        if img0 is None:
            return None, None

        img_bgr = cv2.cvtColor(img0, cv2.COLOR_RGB2BGR)
        result = self.model.predict(
            source=img_bgr,
            imgsz=self.img_size,
            conf=self.conf_thres,
            iou=self.iou_thres,
            device=self.device,
            half=self.use_half,
            max_det=40,
            verbose=False,
        )[0]

        annotator = Annotator(img_bgr.copy(), line_width=3, example=self.names) if self.draw_detections else None
        obj = []

        if result.boxes is not None and len(result.boxes) > 0:
            boxes_xyxy = result.boxes.xyxy.cpu().numpy()
            boxes_conf = result.boxes.conf.cpu().numpy()
            boxes_cls = result.boxes.cls.cpu().numpy().astype(int)

            for xyxy, conf, cls in zip(boxes_xyxy, boxes_conf, boxes_cls):
                raw_label = self.names[int(cls)]
                label = self._normalize_label(raw_label)
                conf = round(float(conf), 2)
                if conf < self.class_conf_thres.get(label, 0.75):
                    continue

                xywh = self._xyxy_to_xywh_top_left(xyxy)

                if annotator is not None:
                    annotator.box_label(
                        xyxy,
                        raw_label if self.hide_conf else f"{raw_label} {conf:.2f}",
                        color=tuple(self.colors[int(cls)]),
                    )
                obj.append({label: {"xywh": xywh, "conf": conf}})

        return annotator.result() if annotator is not None else img_bgr, obj
