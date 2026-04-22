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
import win32gui, win32ui, win32con
from ctypes import windll
import easyocr
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import FishAuto


class GameMonitor:

    def __init__(self):
        self.master: FishAuto = None
        self.image_list = [
            "D:\\Python\\PartyAnimals\\resource\\start.png",
            "D:\\Python\\PartyAnimals\\resource\\fish_done.png",
            "D:\\Python\\PartyAnimals\\resource\\got_fish.png"
        ]
        self.fishing_image = [
            {"path": "D:\\Python\\PartyAnimals\\resource\\start.png",
             "roi": (978, 1257, 588, 156)},
            {"path": "D:\\Python\\PartyAnimals\\resource\\fish_done.png",
             "roi": (1331, 27, 435, 289),},
            {"path": "D:\\Python\\PartyAnimals\\resource\\got_fish.png",
             "roi": (976, 406, 631, 481)}
        ]
        self.image_flag = []
        self.found_rate = []
        self.screen = None
        self.got_fish_text_roi = (1137, 77, 492, 152)
        self.reader = easyocr.Reader(['ch_sim', 'en'], gpu=True, verbose=False)

    def text_monitor(self):
        if self.screen is None:
            return None
        text_caught = self.extract_text_from_roi(self.screen, self.got_fish_text_roi)
        return text_caught

    def window_monitor(self):
        print(f"正在监视窗口: 动物派对...")

        while self.master.isrunning:
            try:
                # 1. 获取画面
                self.screen = self.get_window_screenshot()
                if self.screen is None:
                    break

                # 2. 检测并标注
                found_statuses, found_rate, annotated_frame = self.detect_multiple_assets_with_roi(self.screen, self.fishing_image)

                self.image_flag = found_statuses
                self.found_rate = found_rate

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

    def detect_multiple_assets_robust(self, screen_img, image_paths, threshold=0.75, color_diff_limit=15):
        """
        针对透明PNG优化的多图检测函数
        :param screen_img:
        :param image_paths: 3个PNG路径列表
        :param threshold: 形状匹配阈值
        :param color_diff_limit: 颜色差异上限（越小越严，建议30-60）
        """
        found_statuses = []
        annotated_frame = np.array(screen_img, copy=True)
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
            res = cv2.matchTemplate(screen_img, template_bgr, cv2.TM_SQDIFF_NORMED, mask=mask)
            min_val, _, min_loc, _ = cv2.minMaxLoc(res)

            # 将得分转为 0~1 (1为完全匹配)
            shape_score = 1 - min_val

            is_match = False
            if shape_score >= threshold:
                # 3. 颜色二次验证：只计算非透明部分的平均颜色
                x, y = min_loc
                roi = screen_img[y:y + h, x:x + w]

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
                # x, y = min_loc
                # draw_color = colors[i % 3]
                # cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), draw_color, 2)
                # cv2.putText(annotated_frame, f"ID:{i} OK", (x, y - 10),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.6, draw_color, 2)
            else:
                found_statuses.append(False)

        return found_statuses, None

    def detect_multiple_assets_with_roi(self, screen_img, assets_config, threshold=0.70, color_diff_limit=35):
        """
        为每张图设置独立范围的检测函数
        :param screen_img:
        :param assets_config: 列表，格式为 [{'path': '1.png', 'roi': (x, y, w, h)}, ...]
        :param threshold: 形状匹配阈值
        :param color_diff_limit: 颜色差异上限
        :return: (found_statuses, annotated_frame)
        """
        found_statuses = []
        detailed_data = []
        annotated_frame = np.array(screen_img, copy=True)

        # 颜色：绿、蓝、黄
        colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255)]

        for i, config in enumerate(assets_config):
            path = config['path']
            rx, ry, rw, rh = config['roi']  # 提取该图片专属的检测范围

            # 1. 裁剪感兴趣区域 (ROI)
            # 注意：OpenCV 裁剪语法是 [y1:y2, x1:x2]
            roi_frame = screen_img[ry:ry + rh, rx:rx + rw]

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
            color_dist = 999.0
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
            shape_score = round(1 - min_val, 2)
            color_dist = round(float(color_dist), 1)
            detailed_data.append((shape_score, color_dist))
            if is_match:
                found_statuses.append(True)
                # draw_x, draw_y = rx + min_loc[0], ry + min_loc[1]
                # color = colors[i % 3]
                # cv2.rectangle(annotated_frame, (draw_x, draw_y), (draw_x + w, draw_y + h), color, 2)
                # cv2.putText(annotated_frame, f"ID:{i} OK", (draw_x, draw_y - 10),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            else:
                found_statuses.append(False)
                # 可选：在监视器画出监控区域的虚线框
                # cv2.rectangle(annotated_frame, (rx, ry), (rx + rw, ry + rh), (0, 0, 255), 1)

        return found_statuses, detailed_data, None

    def extract_text_from_roi(self, screen_img, roi):
        """
        提取指定ROI区域的文字
        :param screen_img: 原始画面
        :param roi: (x, y, w, h)
        :param lang: 'eng' (英文/数字), 'chi_sim' (简体中文)
        :return: 识别出的字符串
        """
        try:
            rx, ry, rw, rh = roi
            roi_img = screen_img[ry:ry + rh, rx:rx + rw]

            # EasyOCR 不需要复杂的二值化，直接传入原图或小幅放大
            # 识别结果是一个列表，包含 (坐标, 内容, 置信度)
            results = self.reader.readtext(roi_img, detail=0)  # detail=0 只返回文字内容

            # 将识别出的多行内容合并
            full_text = "".join(results)
            # 5. 后处理：只保留我们需要的内容
            return full_text
        except Exception as e:
            print(f"OCR 识别出错: {e}")
            return ""



def test():
    img = r"E:\\Steam\\userdata\\180269546\\760\\remote\\1260320\\screenshots\\20260419182516_1.jpg"
    img = cv2.imread(img)
    mon = GameMonitor()
    text = mon.extract_text_from_roi(img, mon.got_fish_text_roi)
    print(text)
    print(mon.got_fish_text_roi)















