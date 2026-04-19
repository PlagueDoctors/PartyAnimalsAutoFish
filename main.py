# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。


from Monitor import GameMonitor
import ctypes, sys
import threading
import time
import pynput
import pyautogui

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# if not is_admin():
#     # 重新以管理员身份运行程序
#     ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
#     sys.exit()

class FishAuto:

    def __init__(self):
        self.monitor = GameMonitor.GameMonitor()

    def window_thread(self):
        self.monitor.window_monitor()

    def operation_thread(self):
        on_fishing = False
        while True:
            time.sleep(0.2)
            if not self.monitor.image_flag:
                time.sleep(0.5)
                continue

            start_flag = self.monitor.image_flag[0]
            got_fish_flag = self.monitor.image_flag[2]
            fish_done = self.monitor.image_flag[1]
            print(self.monitor.image_flag)
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
                time.sleep(0.1)
                if got_fish_flag:
                    while True:
                        got_fish_flag = self.monitor.image_flag[2]
                        fish_done = self.monitor.image_flag[1]
                        if fish_done:
                            print("fish_done")
                            time.sleep(1)
                            on_fishing = False
                            pyautogui.mouseDown()
                            time.sleep(0.1)
                            pyautogui.mouseUp()
                            break
                        print("polling--")
                        pyautogui.mouseDown()
                        # 维持按下状态 0.5 秒
                        time.sleep(1.5)
                        # 松开左键
                        pyautogui.mouseUp()
                        time.sleep(0.2)



    def on_press(self, key):

        if key == pynput.keyboard.Key.f8:
            print("\n[收到指令] 正在启动监视器...")

            monitor_t = threading.Thread(target=self.window_thread,daemon=True)
            operation_t = threading.Thread(target=self.operation_thread, daemon=True)
            monitor_t.start()
            operation_t.start()
            return False
        return False


    def start(self):
        print("程序已就绪。请切换到游戏画面，然后按下 [F8] 启动脚本。")
        with pynput.keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()
        while True:
            time.sleep(1)





# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    fishing = FishAuto()
    fishing.start()

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
