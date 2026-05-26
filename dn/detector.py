#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : detector.py
@Time    : 2024/6/29 下午6:18
@Author  : Lex
@Email   : 2983997560@qq.com
@Desc    : 
"""
import random

import cv2
import numpy as np
import torch
from ultralytics.utils.plotting import Annotator

from models.experimental import attempt_load
from utils.augmentations import letterbox
from utils.general import non_max_suppression, scale_boxes, xyxy2xywh
from utils.torch_utils import select_device


class Detector:
    def __init__(self, device_type=""):
        # 参数设置
        self.img_size = 640         # 图片大小
        self.conf_thres = 0.75      # 置信度
        self.iou_thres = 0.45       # IOU
        self.hide_labels = False    # 是否隐藏标签
        self.hide_conf = False      # 是否隐藏置信度

        self.weights = 'best.pt'
        self.device = device_type
        self.device = select_device(self.device)        # 获取CPU 或 CUDA, 默认是CUDA

        # 加载模型
        model = attempt_load(self.weights, device=self.device)
        # 如果不是CPU, 则使用半精度
        if self.device.type != 'cpu':
            model.half()

        self.model = model
        # 获取模型中的类别
        self.names = model.module.names if hasattr(model, 'module') else model.names
        # {0: 'player', 1: 'monster', 2: 'goods', 3: 'money', 4: 'door', 5: 'boss'}
        # 随机生成颜色, 用来标记不同的类别
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(self.names))]

    def detect(self, img0):
        """
        图片预测
        """
        obj = []
        if img0 is None:
            return None, None
        else:
            # 图片预处理
            img0 = cv2.cvtColor(img0, cv2.COLOR_RGB2BGR)                        # 转换颜色通道顺序 RGB to BGR
            img, ratio, (dw, dh) = letterbox(img0, new_shape=self.img_size)     # 调整图片大小, ratio: 缩放比例, dw, dh: 填充的宽度和高度
            img = img[:, :, ::-1].transpose(2, 0, 1)                            # 转换通道顺序, HWC to CHW, 转换成PyTorch格式
            img = np.ascontiguousarray(img)                                     # 确保内存是连续的
            img = torch.from_numpy(img).to(self.device).unsqueeze(0)            # 转换成Tensor, 并移动到指定设备, 添加一个维度
            img = img.half() if self.device.type != 'cpu' else img.float()
            img /= 255.0                                                        # 0 - 255 to 0.0 - 1.0

            # 模型预测
            pred = self.model(img, augment=False)[0]                            # 模型预测
            pred = pred.float()

            # 非极大值抑制
            det = non_max_suppression(pred, self.conf_thres, self.iou_thres)
            det = det[0]

            # 图片绘制标注
            annotator = Annotator(img0, line_width=3, example=self.names)

            # 如果检测到目标
            if det is not None and len(det):
                # 缩放检测结果, 使其适应原图
                det[:, :4] = scale_boxes(img.shape[2:], det[:, :4], img0.shape).round()

                # 打印检测结果, 并绘制标注
                for *xyxy, conf, cls in reversed(det):
                    xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4))).view(-1).tolist()
                    conf = round(float(conf), 2)
                    label = self.names[int(cls)]
                    annotator.box_label(xyxy, label, color=tuple(self.colors[int(cls)]))
                    obj.append({label: {'xywh': xywh, 'conf': conf}})
                    """
                       [
                           {'monster': {'xywh': [514.0, 533.0, 74.0, 110.0], 'conf': 0.84}}, 
                           {'monster': {'xywh': [440.0, 526.0, 68.0, 106.0], 'conf': 0.87}}, 
                           {'player': {'xywh': [889.0, 613.0, 116.0, 202.0], 'conf': 0.89}}
                       ]
                    """
            return img0, obj

