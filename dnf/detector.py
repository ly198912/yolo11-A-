#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : detector.py
@Desc    : YOLO11 detector adapter for DNF
"""
from __future__ import annotations

import random
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
import torch
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator


class Detector:
    def __init__(self, device_type: str = ""):
        self.img_size = 640
        self.conf_thres = 0.45
        self.iou_thres = 0.45
        self.hide_labels = False
        self.hide_conf = False
        self.class_conf_thres = {
            "boss": 0.75,
            "door": 0.75,
            "goods": 0.75,
            "money": 0.75,
            "monster": 0.75,
            "player": 0.55,
        }

        self.device = device_type or ("0" if torch.cuda.is_available() else "cpu")
        self.weights = str(Path(__file__).resolve().parent / "shzn.pt")
        self.model = YOLO(self.weights)
        self.names = self.model.names
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(self.names))]

    @staticmethod
    def _normalize_label(label: str) -> str:
        label = str(label).strip().lower()
        if "door" in label:
            return "door"
        return label

    @staticmethod
    def _xyxy_to_xywh_top_left(xyxy: np.ndarray) -> List[float]:
        x1, y1, x2, y2 = [float(v) for v in xyxy]
        return [x1, y1, max(0.0, x2 - x1), max(0.0, y2 - y1)]

    def detect(self, img0: np.ndarray) -> Tuple[np.ndarray | None, list | None]:
        """
        图片预测。
        返回:
        - annotated_bgr: 画好框的 BGR 图像
        - obj: [{'monster': {'xywh': [x, y, w, h], 'conf': 0.84}}, ...]
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
            verbose=False,
        )[0]

        annotator = Annotator(img_bgr.copy(), line_width=3, example=self.names)
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

                annotator.box_label(
                    xyxy,
                    raw_label if self.hide_conf else f"{raw_label} {conf:.2f}",
                    color=tuple(self.colors[int(cls)]),
                )
                obj.append({label: {"xywh": xywh, "conf": conf}})

        return annotator.result(), obj
