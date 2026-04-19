# -*- coding: utf-8 -*-
# @Author: Bluewindsspecs
# @Email : Bluewindsspecs@gmail.com

"""
@file:GameMonitor.py
@author:Bluewindsspecs
@time:2026/4/19 $ {TIME}
"""


import cv2
import numpy as np
import pyautogui
import win32gui, win32ui, win32con
from ctypes import windll
import time


class GameMonitor:

    def __init__(self):
        self.image_list = [
            "D:\\Python\\PartyAnimals\\resource\\start.png",
            "D:\\Python\\PartyAnimals\\resource\\fish_done.png",
            "D:\\Python\\PartyAnimals\\resource\\got_fish.png"
        ]
        self.image_config = [
            {"path": "D:\\Python\\PartyAnimals\\resource\\start.png",
             "roi": (978, 1257, 588, 156)},
            {"path": "D:\\Python\\PartyAnimals\\resource\\fish_done.png",
             "roi": (1331, 27, 435, 289),},
            {"path": "D:\\Python\\PartyAnimals\\resource\\got_fish.png",
             "roi": (1176, 502, 269, 345)}
        ]
        self.image_flag = []


    def window_monitor(self):
        print(f"正在监视窗口: 动物派对...")

        while True:
            try:
                # 1. 获取画面
                frame = self.get_window_screenshot()
                if frame is None:
                    break

                # 2. 检测并标注
                found, annotated_frame = self.detect_multiple_assets_with_roi(frame, self.image_config)

                self.image_flag = found

                #print(self.image_flag)
                # 3. 创建/更新监视器窗口
                # 可以使用 cv2.WINDOW_NORMAL 让窗口可以手动调整大小
                # cv2.namedWindow('Monitor', cv2.WINDOW_NORMAL)
                # cv2.imshow('Monitor', annotated_frame)
                #
                # # 4. 刷新频率 (1ms) 且检测退出键
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break
                # if cv2.getWindowProperty("Monitor", cv2.WND_PROP_VISIBLE) < 1:
                #     print("检测到监视窗口已关闭，正在退出程序...")
                #     break

            except Exception as e:
                print(f"错误: {e}")
                break

        cv2.destroyAllWindows()


    def get_window_screenshot(self):
        # 1. 找到窗口句柄
        window_title = "猛兽派对"
        hwnd = win32gui.FindWindow(None, window_title)
        if not hwnd:
            raise Exception(f"找不到窗口: {window_title}")

        # 解决部分窗口在高分屏下的缩放问题
        windll.user32.SetProcessDPIAware()

        # 2. 获取窗口尺寸
        left, top, right, bot = win32gui.GetWindowRect(hwnd)
        w = right - left
        h = bot - top

        # 3. 创建 DC (Device Context)
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        # 4. 创建位图对象
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
        saveDC.SelectObject(saveBitMap)

        # 5. 截图并存入位图 (使用 PrintWindow 可抓取后台窗口内容)
        # 0 代表只抓取窗口客户区，1 代表抓取整个窗口
        result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)

        # 6. 转为 OpenCV 格式 (NumPy 数组)
        signedIntsArray = saveBitMap.GetBitmapBits(True)
        img = np.frombuffer(signedIntsArray, dtype='uint8')
        img.shape = (h, w, 4)

        # 释放资源
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

        # 返回 BGR 格式 (去掉 Alpha 通道)
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    def detect_multiple_assets_robust(self, frame, image_paths, threshold=0.75, color_diff_limit=15):
        """
        针对透明PNG优化的多图检测函数
        :param frame:
        :param image_paths: 3个PNG路径列表
        :param threshold: 形状匹配阈值
        :param color_diff_limit: 颜色差异上限（越小越严，建议30-60）
        """
        found_statuses = []
        annotated_frame = frame.copy()
        # 标注颜色：绿、蓝、黄
        colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255)]

        for i, path in enumerate(image_paths):
            # 1. 加载图片及其透明通道
            img_with_alpha = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img_with_alpha is None or img_with_alpha.shape[2] != 4:
                print(f"错误: {path} 不是有效的透明PNG")
                found_statuses.append(False)
                continue

            template_bgr = img_with_alpha[:, :, 0:3]
            mask = img_with_alpha[:, :, 3]
            h, w = template_bgr.shape[:2]

            # 2. 形状匹配 (使用归一化平方差算法，对透明掩模支持最稳定)
            # 注意：TM_SQDIFF_NORMED 是越接近 0 越匹配
            res = cv2.matchTemplate(frame, template_bgr, cv2.TM_SQDIFF_NORMED, mask=mask)
            min_val, _, min_loc, _ = cv2.minMaxLoc(res)

            # 将得分转为 0~1 (1为完全匹配)
            shape_score = 1 - min_val

            is_match = False
            if shape_score >= threshold:
                # 3. 颜色二次验证：只计算非透明部分的平均颜色
                x, y = min_loc
                roi = frame[y:y + h, x:x + w]

                # 计算模板中非透明像素的平均值
                avg_temp = cv2.mean(template_bgr, mask=mask)[:3]
                # 计算当前画面中对应位置的平均值
                avg_roi = cv2.mean(roi, mask=mask)[:3]

                # 计算两个颜色的欧式距离
                color_dist = np.linalg.norm(np.array(avg_temp) - np.array(avg_roi))

                # 调试信息
                # print(f"[{path}] 形状得分:{shape_score:.2f}, 颜色差异:{color_dist:.1f}")

                if color_dist < color_diff_limit:
                    is_match = True

            # 4. 绘图与结果汇总
            if is_match:
                found_statuses.append(True)
                x, y = min_loc
                draw_color = colors[i % 3]
                cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), draw_color, 2)
                cv2.putText(annotated_frame, f"ID:{i} OK", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, draw_color, 2)
            else:
                found_statuses.append(False)

        return found_statuses, annotated_frame

    def detect_multiple_assets_with_roi(self, frame, assets_config, threshold=0.7, color_diff_limit=40):
        """
        为每张图设置独立范围的检测函数
        :param assets_config: 列表，格式为 [{'path': '1.png', 'roi': (x, y, w, h)}, ...]
        :param threshold: 形状匹配阈值
        :param color_diff_limit: 颜色差异上限
        :return: (found_statuses, annotated_frame)
        """
        found_statuses = []
        annotated_frame = frame.copy()

        # 颜色：绿、蓝、黄
        colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255)]

        for i, config in enumerate(assets_config):
            path = config['path']
            rx, ry, rw, rh = config['roi']  # 提取该图片专属的检测范围

            # 1. 裁剪感兴趣区域 (ROI)
            # 注意：OpenCV 裁剪语法是 [y1:y2, x1:x2]
            roi_frame = frame[ry:ry + rh, rx:rx + rw]

            # 2. 读取带透明通道的模板
            img_with_alpha = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img_with_alpha is None or img_with_alpha.shape[2] != 4:
                found_statuses.append(False)
                continue

            template_bgr = img_with_alpha[:, :, 0:3]
            mask = img_with_alpha[:, :, 3]
            h, w = template_bgr.shape[:2]

            # 3. 在 ROI 范围内进行形状匹配
            # 使用 TM_SQDIFF_NORMED，越接近 0 越匹配
            res = cv2.matchTemplate(roi_frame, template_bgr, cv2.TM_SQDIFF_NORMED, mask=mask)
            min_val, _, min_loc, _ = cv2.minMaxLoc(res)
            shape_score = 1 - min_val

            is_match = False
            if shape_score >= threshold:
                # 4. 颜色二次验证
                mx, my = min_loc
                # 获取 ROI 中匹配到的具体小块
                matched_roi = roi_frame[my:my + h, mx:mx + w]

                avg_temp = cv2.mean(template_bgr, mask=mask)[:3]
                avg_roi = cv2.mean(matched_roi, mask=mask)[:3]
                color_dist = np.linalg.norm(np.array(avg_temp) - np.array(avg_roi))

                if color_dist < color_diff_limit:
                    is_match = True

            # 5. 结果标注 (坐标需要加上 rx, ry 偏置还原到大图位置)
            if is_match:
                found_statuses.append(True)
                draw_x, draw_y = rx + min_loc[0], ry + min_loc[1]
                color = colors[i % 3]
                cv2.rectangle(annotated_frame, (draw_x, draw_y), (draw_x + w, draw_y + h), color, 2)
                cv2.putText(annotated_frame, f"ID:{i} OK", (draw_x, draw_y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            else:
                found_statuses.append(False)
                # 可选：在监视器画出监控区域的虚线框
                cv2.rectangle(annotated_frame, (rx, ry), (rx + rw, ry + rh), (0, 0, 255), 1)

        return found_statuses, annotated_frame





def test():
    mon = GameMonitor()
    mon.window_monitor()















