# PartyAnimals AI Agent Guide

## Overview
This Python project automates fishing mechanics in the game "Party Animals" (猛兽派对) using image recognition and simulated inputs. It monitors the game window for specific visual cues and performs mouse clicks accordingly.

## Architecture
- **Main Entry**: `main.py` - Orchestrates threads for monitoring and operations using `FishAuto` class.
- **Monitoring Module**: `Monitor/GameMonitor.py` - Captures game window screenshots via Windows APIs and detects template images within defined ROIs.
- **Data Flow**: `GameMonitor` sets `image_flag` list (booleans for start, fish_done, got_fish states). `FishAuto.operation_thread` reads flags to trigger clicks.
- **Why Modular**: Separates image detection from action logic for maintainability; uses threading to avoid blocking UI.

## Key Workflows
- **Setup**: Activate virtual environment (`.venv`), install dependencies: `pip install opencv-python pyautogui pynput pywin32`.
- **Run**: `python main.py`, switch to game window, press F8 to start threads.
- **Debug**: Uncomment cv2.imshow in `GameMonitor.window_monitor()` to visualize detections; check console for flag prints.
- **ROI Setup**: Use `Monitor/RoiTest.py` to manually select regions on screenshots for new images.

## Conventions & Patterns
- **Image Detection**: Template matching with transparency masks (cv2.matchTemplate + mask) and color verification. Example: `detect_multiple_assets_with_roi()` uses ROIs like `(978, 1257, 588, 156)` for start.png to limit search area.
- **Paths**: Absolute paths hardcoded in `GameMonitor.__init__()` for resources (e.g., `D:\\Python\\PartyAnimals\\resource\\start.png`).
- **Window Targeting**: Hardcoded title "猛兽派对"; uses win32gui for DPI-aware screenshots.
- **Threading**: Daemon threads for monitoring/operations; sleeps (0.2s) to balance responsiveness and CPU.
- **Inputs**: pyautogui for mouse (mouseDown/Up with delays); pynput for F8 trigger.

## Dependencies & Integration
- **External**: Game window must be visible; Windows-only (win32gui, ctypes).
- **Images**: PNGs in `resource/` with transparency; update ROIs in `image_config` for UI changes.
- **No CI/Tests**: Manual testing; validate detections by running and observing clicks.

Reference: `main.py` for logic, `Monitor/GameMonitor.py` for detection details.</content>
<parameter name="filePath">D:\Python\PartyAnimals\AGENTS.md
