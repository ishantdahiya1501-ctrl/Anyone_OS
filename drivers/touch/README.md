# Touchscreen Driver Notes

PhoneOS uses Linux input events (`/dev/input/event*`) with LVGL `evdev` backend.

Calibration and per-panel tuning should be added here as panel-specific scripts or udev rules.