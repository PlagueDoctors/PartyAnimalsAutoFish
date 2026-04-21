# PartyAnimals Auto Fishing Tool

A Python-based automation tool for the fishing mechanics in the game "Party Animals" (猛兽派对). Uses image recognition to monitor the game window and simulate mouse inputs for automated fishing.

## Features

- **Automated Fishing**: Detects fishing start cues and performs mouse clicks to catch fish.
- **Real-time Monitoring**: Captures game screenshots and analyzes for specific visual indicators.
- **Configurable Settings**: Tracks total fish count and values via Excel spreadsheet.
- **Hotkey Controls**: Start/stop fishing and other actions with keyboard shortcuts.
- **Threaded Operations**: Non-blocking monitoring and operation threads for smooth performance.

## Requirements

- Windows OS (uses Windows APIs for window capture)
- Python 3.8+
- Game "Party Animals" installed and running
- Virtual environment recommended

## Installation

1. Clone or download the project to your local machine.

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install opencv-python pyautogui pynput pywin32 pandas
   ```

## Usage

1. Ensure the game window is visible and titled "猛兽派对".

2. Run the main script:
   ```bash
   python main.py
   ```

3. Switch to the game window.

4. Press **F8** to start the fishing automation threads.

5. Press **F9** to stop all threads.

6. Press **Esc** to exit the program.

### Additional Controls

- **F7**: Start playing card clicking mode (rapid mouse clicks).

### Debugging

- Uncomment `cv2.imshow` in `Monitor/GameMonitor.py` to visualize image detections.
- Check console output for flag states and detection rates.

## Configuration

- **Config File**: `Monitor/config.json` stores total cookies and last fish data.
- **Fish Values**: `resource/fish_value.xlsx` contains fish names, qualities, and values.
- **Image Templates**: PNG files in `resource/` for detection (start.png, fish_done.png, got_fish.png).
- **ROIs**: Region of Interest coordinates defined in `GameMonitor.py` for template matching.

## Project Structure

```
PartyAnimals/
├── main.py                 # Main entry point and FishAuto class
├── Monitor/
│   ├── GameMonitor.py      # Image monitoring and detection logic
│   ├── RoiTest.py          # Tool for setting up ROIs
│   └── config.json         # Configuration data
├── resource/               # Image templates and data files
│   ├── start.png
│   ├── fish_done.png
│   ├── got_fish.png
│   └── fish_value.xlsx
└── AGENTS.md               # AI agent guide
```

## How It Works

1. **Monitoring Thread**: Continuously captures game window screenshots and performs template matching within defined ROIs to detect states (start fishing, fish caught, fishing done).

2. **Operation Thread**: Reads detection flags and simulates mouse clicks accordingly (e.g., hold mouse for fishing start, click for fish collection).

3. **Text Recognition**: Uses OCR-like methods to extract fish information from game text.

4. **Value Tracking**: Looks up fish values in the Excel sheet and updates totals.

## Troubleshooting

- Ensure the game is running in windowed mode with the correct title.
- Adjust ROI coordinates in `GameMonitor.py` if UI changes.
- Run as administrator if access issues occur (uncomment admin check in main.py).
- Check for DPI scaling issues with Windows APIs.

## Disclaimer

This tool is for educational and personal use only. Use at your own risk and ensure compliance with game terms of service.

## 中文说明

### 项目描述
这是一个基于 Python 的自动化工具，用于游戏 "Party Animals" (猛兽派对) 中的钓鱼机制。通过图像识别监控游戏窗口并模拟鼠标输入实现自动钓鱼。

### 功能特性
- **自动钓鱼**：检测钓鱼开始提示并执行鼠标点击捕鱼。
- **实时监控**：捕获游戏截图并分析特定视觉指示器。
- **可配置设置**：通过 Excel 表格跟踪总鱼数和价值。
- **热键控制**：使用键盘快捷键启动/停止钓鱼和其他操作。
- **线程操作**：非阻塞监控和操作线程以确保流畅性能。

### 系统要求
- Windows 操作系统（使用 Windows API 进行窗口捕获）
- Python 3.8+
- 安装并运行游戏 "Party Animals"
- 推荐使用虚拟环境

### 安装步骤
1. 将项目克隆或下载到本地计算机。

2. 创建并激活虚拟环境：
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. 安装依赖项：
   ```bash
   pip install opencv-python pyautogui pynput pywin32 pandas
   ```

### 使用方法
1. 确保游戏窗口可见且标题为 "猛兽派对"。

2. 运行主脚本：
   ```bash
   python main.py
   ```

3. 切换到游戏窗口。

4. 按 **F8** 启动钓鱼自动化线程。

5. 按 **F9** 停止所有线程。

6. 按 **Esc** 退出程序。

#### 附加控制
- **F7**：启动打牌点击模式（快速鼠标点击）。

#### 调试
- 在 `Monitor/GameMonitor.py` 中取消注释 `cv2.imshow` 以可视化图像检测。
- 检查控制台输出以查看标志状态和检测率。

### 配置
- **配置文件**：`Monitor/config.json` 存储总饼干和最后鱼类数据。
- **鱼类价值**：`resource/fish_value.xlsx` 包含鱼类名称、品质和价值。
- **图像模板**：`resource/` 中的 PNG 文件用于检测（start.png、fish_done.png、got_fish.png）。
- **ROI**：在 `GameMonitor.py` 中定义的模板匹配感兴趣区域坐标。

### 项目结构
```
PartyAnimals/
├── main.py                 # 主入口点和 FishAuto 类
├── Monitor/
│   ├── GameMonitor.py      # 图像监控和检测逻辑
│   ├── RoiTest.py          # ROI 设置工具
│   └── config.json         # 配置数据
├── resource/               # 图像模板和数据文件
│   ├── start.png
│   ├── fish_done.png
│   ├── got_fish.png
│   └── fish_value.xlsx
└── AGENTS.md               # AI 代理指南
```

### 工作原理
1. **监控线程**：持续捕获游戏窗口截图，并在定义的 ROI内进行模板匹配以检测状态（开始钓鱼、捕获鱼类、钓鱼完成）。

2. **操作线程**：读取检测标志并相应模拟鼠标点击（例如，钓鱼开始时按住鼠标，收集鱼类时点击）。

3. **文本识别**：使用类似 OCR 的方法从游戏文本中提取鱼类信息。

4. **价值跟踪**：在 Excel 表格中查找鱼类价值并更新总数。

### 故障排除
- 确保游戏以窗口模式运行且标题正确。
- 如果 UI 更改，调整 `GameMonitor.py` 中的 ROI 坐标。
- 如果出现访问问题，以管理员身份运行（取消注释 main.py 中的管理员检查）。
- 检查 Windows API 的 DPI 缩放问题。

### 免责声明
此工具仅供教育和个人使用。请自行承担风险，并确保遵守游戏服务条款。
