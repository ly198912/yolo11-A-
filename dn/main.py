#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : main.py
@Time    : 2024/6/29 下午3:43
@Author  : Lex
@Email   : 2983997560@qq.com
@Desc    : 
"""
import time
import pyautogui
import cv2
import numpy as np
from loguru import logger
import pathlib

from dnf.game import Game

temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

from dnf.detector import Detector
device_type = ''
width = 1600
height = 900
yaml_direction = ['RIGHT', 'RIGHT', 'UP', 'RIGHT']

# 初始化检测器
detector = Detector(device_type)

while True:
    start_time = time.time()
    img = pyautogui.screenshot(region=(0, 0, width, height))  # 分别代表：左上角坐标，宽高
    # img = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)  # 转换颜色通道顺序
    # 1. 发送给模型进行推理预测, 获取推理结果
    img_np = np.array(img)
    img, obj = detector.detect(img_np)
    logger.info("obj: {}".format(obj))
    # 2. 获取推理后的结果, 进行游戏操作
    game = Game(obj, width, height, yaml_direction)
    game.run()
    # img 缩放成 640x360
    img = cv2.resize(img, (640, 360))
    cv2.imshow("112233", img)  # 显示截图
    logger.info("处理时间: {}".format(time.time() - start_time))
    # 检查是否按下 'q' 键以退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()