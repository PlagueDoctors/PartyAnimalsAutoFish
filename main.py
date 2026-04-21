

from pynput import keyboard
from Monitor import GameMonitor
import ctypes
import threading
import time
import pynput
import pyautogui
import re
import json
import os
import pandas as pd


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def kill_thread(thread):
    if not thread.is_alive():
                return
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident),
        ctypes.py_object(SystemExit)
    )
    if res == 0:
        print("无效线程ID")
    elif res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread.ident), None
        )


# if not is_admin():
#     # 重新以管理员身份运行程序
#     ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
#     sys.exit()

class FishAuto:

    def __init__(self):
        self.monitor = GameMonitor.GameMonitor()
        self.monitor_t = None
        self.fishing_operation_t = None
        self.playing_card_t = None
        self.config_file = "D:\\Python\\PartyAnimals\\Monitor\\config.json"
        self.config_data = self.load()
        self.value_table = pd.read_excel("D:\\Python\\PartyAnimals\\resource\\fish_value.xlsx")
        self.value_table = self.value_table.set_index(["鱼类名称", "属性"])

    def load(self):
        """读取配置文件"""
        if not os.path.exists(self.config_file):
            # 如果文件不存在，返回一个默认值
            return {"total_cookies": 0, "last_fish": "None"}
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_config(self):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config_data, f, ensure_ascii=False, indent=4)


    def window_thread(self):
        self.monitor.window_monitor()

    def fishing_operation_thread(self):
        on_fishing = False
        total_value = 0
        print("--")
        time_out = 150
        while True:
            time.sleep(0.2)
            if not self.monitor.image_flag:
                time.sleep(0.5)
                continue

            if time_out <= 0:
                time_out = 150
                on_fishing = False

            start_flag = self.monitor.image_flag[0]
            got_fish_flag = self.monitor.image_flag[2]
            fish_done = self.monitor.image_flag[1]
            print(f"\r{self.monitor.image_flag} {self.monitor.found_rate}", end="")
            if start_flag and not on_fishing:
                time.sleep(2)
                pyautogui.mouseDown()
                # 维持按下状态 0.5 秒
                time.sleep(1)
                # 松开左键
                pyautogui.mouseUp()
                print("done start")
                on_fishing = True
            if on_fishing:
                time_out -= 1
                time.sleep(0.1)
                if got_fish_flag:
                    count = 0
                    while True:
                        count += 1
                        if count >= 10:
                            break
                        got_fish_flag = self.monitor.image_flag[2]
                        fish_done = self.monitor.image_flag[1]
                        if fish_done:
                            self.config_data["total_count"] += 1
                            fish_info = self.monitor.text_monitor()
                            fish_name, fish_quality = self.got_fish_info(fish_info)
                            # fish_value = self.look_up_fish_value(fish_name, fish_quality)
                            self.save_config()
                            print(f"fish_done: {fish_name}, {fish_quality}, 价值: ")
                            # self.config_data["total_value"] += fish_value
                            time.sleep(1)
                            on_fishing = False
                            pyautogui.mouseDown()
                            time.sleep(0.1)
                            pyautogui.mouseUp()
                            break
                        print("polling--")
                        pyautogui.mouseDown()
                        # 维持按下状态 0.5 秒
                        time.sleep(1)
                        # 松开左键
                        pyautogui.mouseUp()
                        time.sleep(0.4)

    def playing_card_thread(self):
        while True:
            time.sleep(0.3)
            pyautogui.mouseDown()
            time.sleep(0.05)
            pyautogui.mouseUp()

    def got_fish_info(self, info_text):
        fish_name = re.search(r"(钓到了|首次捕获: \s?)([\u4e00-\u9fa5]+)(标准|稀有|史诗|传奇|非凡)", info_text)
        if fish_name:
            fish_name = fish_name.group(2)
        fish_quality = re.search(r"(标准|稀有|史诗|传奇|非凡)", info_text)
        if fish_quality:
            fish_quality = fish_quality.group(1)
        return fish_name, fish_quality

    def look_up_fish_value(self,fish_name, fish_quality):
        if fish_name:
            if not fish_quality:
                fish_quality = "无品质"
            value = self.value_table.loc[(fish_name, fish_quality), "价值"]
            return value
        return 0


    def on_press(self, key: keyboard.Key | keyboard.KeyCode | None) -> bool | None:

        if key == pynput.keyboard.Key.f8:
            print("\n[收到指令] 正在启动监视器...")

            self.monitor_t = threading.Thread(target=self.window_thread,daemon=True)
            self.fishing_operation_t = threading.Thread(target=self.fishing_operation_thread, daemon=True)
            self.monitor_t.start()
            self.fishing_operation_t.start()

        if key == pynput.keyboard.Key.f7:
            print("开始点击")
            self.playing_card_t = threading.Thread(target=self.playing_card_thread, daemon=True)
            self.playing_card_t.start()

        if key == pynput.keyboard.Key.f9:
            print("停止")
            if self.monitor_t is not None:
                kill_thread(self.monitor_t)
            if self.fishing_operation_t is not None:
                kill_thread(self.fishing_operation_t)
            if self.playing_card_t is not None:
                kill_thread(self.playing_card_t)

        if key == pynput.keyboard.Key.esc:
            return False

        return None


    def start(self):
        print("程序已就绪。请切换到游戏画面，然后按下 [F8] 启动钓鱼，[F7]开始打牌点击。")
        with pynput.keyboard.Listener(on_press=self.on_press) as listener: # type: ignore
            listener.join()
        while True:
            time.sleep(1)




if __name__ == '__main__':
    fishing = FishAuto()
    fishing.start()


