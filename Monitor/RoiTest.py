# -*- coding: utf-8 -*-
# @Author: Bluewindsspecs
# @Email : Bluewindsspecs@gmail.com

"""
@file:RoiTest.py
@author:Bluewindsspecs
@time:2026/4/19 $ {TIME}
"""

import cv2


def get_roi_manually(image_path):
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        print("找不到图片！")
        return

    # 弹出窗口，用鼠标画框
    # 按下 ENTER 或 SPACE 确认，按下 C 取消
    roi = cv2.selectROI("Select ROI", img, showCrosshair=True, fromCenter=False)

    # roi 的返回值是 (x, y, w, h)
    print(f"你选择的 ROI 坐标是: {roi}")

    cv2.destroyAllWindows()
    return roi


roi = get_roi_manually("E:\\Steam\\userdata\\180269546\\760\\remote\\1260320\\screenshots\\20260419161809_1.jpg")










