#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : game.py
@Time    : 2024/6/30 上午12:08
@Author  : Lex
@Email   : 2983997560@qq.com
@Desc    : 
"""
import time

import pydirectinput
# pip install pydirectinput
from loguru import logger


class Game:
    _action_cache = None
    _player = None
    _pre_player = None
    _index = 0

    def __init__(self, obj, width, height, direction):
        self._obj = obj
        self._width = width
        self._height = height
        self._player_xywh = None
        self._attack_x = 100
        self._attack_y = 100
        self._move_x = 20
        self._move_y = 20
        self._direction = direction

    def _get_cls(self, cls_name):
        """
        获取指定名称的对象内容
        """
        cls_obj = None
        for item in self._obj:
            if cls_name in item:
                cls_obj = item
                break
        if cls_obj is None:
            return None
        return cls_obj[cls_name]

    def _get_clss(self, cls_name):
        """
        获取指定名称的对象内容 序列
        """
        cls_objs = []
        for item in self._obj:
            if cls_name in item:
                cls_objs.append(item[cls_name])
        return cls_objs

    def _get_nearest(self, cls_objs, direct=None):
        """
        获取最近的对象
        """
        nearest = None
        min_distance = float('inf')

        if len(cls_objs) == 1:
            nearest = cls_objs[0]
        else:
            for item in cls_objs:
                # 计算目标中心点
                obj_x = item['xywh'][0] + item['xywh'][2] / 2
                obj_y = item['xywh'][1] + item['xywh'][3] / 2

                player_x = self._player_xywh[0]
                player_y = self._player_xywh[1]

                # 计算玩家和目标的距离
                dx = obj_x - player_x
                dy = obj_y - player_y

                # 方向只用来特殊情况下查找门
                if direct:
                    # 如果有方向, 则只计算指定方向的目标
                    if direct.lower() == "right" and dx <= 0:
                        continue
                    elif direct.lower() == "left" and dx >= 0:
                        continue
                    elif direct.lower() == "up" and dy >= 0:
                        continue
                    elif direct.lower() == "down" and dy <= 0:
                        continue

                distance = (dx ** 2 + dy ** 2) ** 0.5  # 计算两点之间的距离, 使用三角函数计算

                if distance < min_distance:
                    min_distance = distance
                    nearest = item

        if nearest:
            # 计算目标中心点坐标
            nearest['xywh'][0] = nearest['xywh'][0] + nearest['xywh'][2] / 2
            nearest['xywh'][1] = nearest['xywh'][1] + nearest['xywh'][3] / 2
        # {'xywh': [514.0, 533.0, 74.0, 110.0], 'conf': 0.84}
        return nearest

    def _key_press(self, key):
        """
        按键
        """
        pydirectinput.keyDown(key)
        time.sleep(0.1)
        pydirectinput.keyUp(key)
        time.sleep(0.1)

    def _get_direction(self, obj_box):
        """
        获取目标相对于玩家的方向
        """
        dx = obj_box[0] - self._player_xywh[0]
        dy = obj_box[1] - self._player_xywh[1]

        # 如果目标在玩家的上方
        if dy < 0:
            # 如果y方向的距离差值小于阈值
            if abs(dy) < 20:
                return "RIGHT" if dx > 0 else "LEFT"
            # 如果玩家到目标的y距离小于x距离, 则优先侧向移动
            if self._player_xywh[1] - obj_box[1] < abs(dx):
                return "RIGHT_UP" if dx > 0 else "LEFT_UP"
            return "UP"

        # 如果目标在玩家的下方
        elif dy > 0:
            if abs(dy) < 20:
                return "RIGHT" if dx > 0 else "LEFT"
            if dy < abs(dx):
                return "RIGHT_DOWN" if dx > 0 else "LEFT_DOWN"
            return "DOWN"

        # 如果怪物在玩家的同一个Y轴上, (dy == 0)
        return None

    def _move(self, direction, is_slow=False, _action_cache=None, press_time=0.1, release_time=0.1):
        """
        移动
        """
        logger.info("当前方向: {}, 缓存方向: {}".format(direction, _action_cache))
        # 释放当前缓存的动作, 避免按键冲突
        if _action_cache and direction != _action_cache:
            # 当前缓存的动作不是简单方向, 分解
            if _action_cache not in ["UP", "DOWN", "LEFT", "RIGHT"]:
                for action in _action_cache.strip().split("_"):
                    logger.info("循环释放方向键: {}".format(action))
                    pydirectinput.keyUp(action.lower())
            else:
                # 释放方向键
                logger.info("释放方向键: {}".format(_action_cache))
                pydirectinput.keyUp(_action_cache.lower())

        # 按下当前的方向键
        for action in direction.strip().split("_"):
            logger.info("按下方向键: {}".format(action))
            pydirectinput.keyDown(action.lower())

        if not is_slow:
            time.sleep(press_time)
            for action in direction.strip().split("_"):
                logger.info("快速_循环释放方向键: {}".format(action))
                pydirectinput.keyUp(action.lower())
            time.sleep(release_time)
            for action in direction.strip().split("_"):
                logger.info("快速_循环按下方向键: {}".format(action))
                pydirectinput.keyDown(action.lower())

        _action_cache = direction
        logger.info("当前缓存的动作: {}".format(_action_cache))
        return _action_cache

    def _kill_monster(self, obj_box):
        """
        打怪
        """
        # 处于攻击范围内
        if abs(obj_box[0] - self._player_xywh[0]) < self._attack_x and abs(obj_box[1] - self._player_xywh[1]) < self._attack_y:
            logger.info("在攻击范围内, 开始攻击")
            # 判断面向
            direction = self._get_direction(obj_box)
            face = None
            if direction:
                for item in direction.split("_"):
                    if "RIGHT" in item:
                        face = "RIGHT"
                    elif "LEFT" in item:
                        face = "LEFT"
                    break

            if face:
                # 调整面向
                logger.info("调整面向: {}".format(face))
                self._key_press(face.lower())

            # 攻击
            self._key_press("x")
            logger.info("攻击完成")

            # 攻击完成以后, 将缓存的动作清空
            if not Game._action_cache:
                pass
            elif Game._action_cache not in ["UP", "DOWN", "LEFT", "RIGHT"]:
                for action in Game._action_cache.strip().split("_"):
                    logger.info("攻击范围内_释放方向键: {}".format(action))
                    pydirectinput.keyUp(action.lower())
            elif Game._action_cache:
                logger.info("攻击范围内_释放方向键: {}".format(Game._action_cache))
                pydirectinput.keyUp(Game._action_cache.lower())
            Game._action_cache = None
        else:
            # 不在攻击范围内
            # 获取目标相对于玩家的方向
            direction = self._get_direction(obj_box)
            logger.info("打怪, 方向是: {}".format(direction))
            if direction:
                Game._action_cache = self._move(direction, is_slow=True, _action_cache=Game._action_cache)

    def _pick_up(self, obj_box):
        """
        拾取物品
        """
        # 处于拾取范围内
        if abs(obj_box[0] - self._player_xywh[0]) < self._move_x and abs(obj_box[1] - self._player_xywh[1]) < self._move_y:
            logger.info("在拾取范围内, 开始拾取")
            # 拾取
            self._key_press("f")
            logger.info("拾取完成")

            if not Game._action_cache:
                pass
            elif Game._action_cache not in ["UP", "DOWN", "LEFT", "RIGHT"]:
                for action in Game._action_cache.strip().split("_"):
                    logger.info("攻击范围内_释放方向键: {}".format(action))
                    pydirectinput.keyUp(action.lower())
            elif Game._action_cache:
                logger.info("攻击范围内_释放方向键: {}".format(Game._action_cache))
                pydirectinput.keyUp(Game._action_cache.lower())
            Game._action_cache = None
        else:
            direction = self._get_direction(obj_box)
            if direction:
                Game._action_cache = self._move(direction, is_slow=True, _action_cache=Game._action_cache)

    def _move_to_door(self, obj_box):
        """
        移动到门
        """
        # 如果门的位置小于截图的一半, 说明人物现在在地图的左侧, 需要向右移动
        if obj_box[0] < self._width / 2:
            self._move("RIGHT")

        # 判断门的位置相对于人物的位置
        direction = self._get_direction(obj_box)
        if direction:
            Game._action_cache = self._move(direction, _action_cache=Game._action_cache)

    def _check_position(self):
        """
        检查是否已经移动到下一个门
        """
        player_x = self._player_xywh[0]
        player_y = self._player_xywh[1]

        if player_x < self._width / 2:
            if player_y < self._height / 2:
                return "LEFT_UP"
            else:
                return "LEFT_DOWN"
        else:
            if player_y < self._height / 2:
                return "RIGHT_UP"
            else:
                return "RIGHT_DOWN"

    def run(self):
        """
        游戏操作入口
        """
        # 1.1 获取玩家对象
        Game._player = self._get_cls('player')  # {'xywh': [889.0, 613.0, 116.0, 202.0], 'conf': 0.89}
        if Game._player is None:
            Game._player = Game._pre_player
        Game._pre_player = Game._player

        try:
            # 1.2 计算玩家中心点坐标
            self._player_xywh = Game._player['xywh']
            self._player_xywh[0] = self._player_xywh[0] + self._player_xywh[2] / 2
            self._player_xywh[1] = self._player_xywh[1] + self._player_xywh[3] / 2
            print("玩家坐标: {}".format(self._player_xywh))

            # 2.2 打boss
            boss = self._get_clss('boss')
            if boss:
                nearest_boss = self._get_nearest(boss)
                # 打boss
                self._kill_monster(nearest_boss["xywh"])
                logger.info("打boss")
                return

            # 2.1 打小怪
            monsters = self._get_clss('monster')
            if monsters:
                # 获取最近的目标
                nearest_monster = self._get_nearest(monsters)
                # {'xywh': [514.0, 533.0, 74.0, 110.0], 'conf': 0.84}
                # 打怪
                self._kill_monster(nearest_monster["xywh"])
                logger.info("打小怪")
                return

            # 3.1 拾取物品
            goods = self._get_clss('goods')
            if goods:
                nearest_goods = self._get_nearest(goods)
                self._pick_up(nearest_goods["xywh"])
                # 拾取物品
                logger.info("拾取物品")
                return

            # 3.2 拾取金币
            money = self._get_clss('money')
            if money:
                nearest_money = self._get_nearest(money)
                self._pick_up(nearest_money["xywh"])
                # 拾取金币
                logger.info("拾取金币")
                return

            # 4 移动到下一个门
            doors = self._get_clss('door')
            if doors:
                if Game._index > 0:
                    # 检查是否已经移动到下一个门
                    position = self._check_position()
                    logger.info("当前位置: {}".format(position))
                    for item in position.split("_"):
                        # 判断要移动的门的方向和所在位置的方向是否一致
                        if self._direction[Game._index] == item:
                            Game._index += 1
                logger.info("门存在")
                logger.info("当前门的index: {}".format(Game._index))
                nearest_door = self._get_nearest(doors, direct=self._direction[Game._index])
                self._move_to_door(nearest_door["xywh"])
                logger.info("移动到下一个门")
                return
        except Exception as e:
            pass
        # 5 如果什么目标都没有, 向下一个门移动
        logger.warning("什么都没有, 向下一个门移动")
        self._move("RIGHT")