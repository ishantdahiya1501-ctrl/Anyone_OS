"""Battery app with battery info and visual bars."""

from __future__ import annotations

import subprocess
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, QFrame

from apps.base_app import AppTheme, PhoneAppScreen


def get_battery_info() -> dict:
    """Try to get real battery info on Windows."""
    if sys.platform == "win32":
        try:
            flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            result = subprocess.run(
                ["wmic", "path", "Win32_Battery", "get", "EstimatedChargeRemaining,BatteryStatus", "/format:csv"],
                capture_output=True, text=True, timeout=3,
                creationflags=flags,
            )
            lines = result.stdout.strip().split("\n")
            for line in lines[1:]:
                parts = line.strip().split(",")
                if len(parts) >= 3:
                    percent = int(parts[1])
                    charging = parts[2].strip() == "2"
                    return {"percent": min(100, max(0, percent)), "charging": charging}
        except (subprocess.SubprocessError, ValueError, OSError):
            pass
    return {"percent": 87, "charging": False}


class BatteryBar(QWidget):
    """Visual battery level bar."""
    def __init__(self, percent: int, color: QColor, label: str = "", parent=None) -> None:
        super().__init__(parent)
        self.percent = percent
        self.color = color
        self.label_text = label
        self.setFixedHeight(36)

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.setBrush(QColor(40, 40, 46))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), 12, 6, 6)

        # Fill
        fill_w = int(self.width() * self.percent / 100)
        painter.setBrush(self.color)
        painter.drawRoundedRect(0, 0, fill_w, 12, 6, 6)

        # Label
        painter.setPen(QColor(255, 255, 255, 200))
        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        painter.drawText(0, 16, self.width(), 20, Qt.AlignmentFlag.AlignLeft, f"{self.label_text}  {self.percent}%")
        painter.end()


class BatteryApp(PhoneAppScreen):
    def __init__(self, theme: AppTheme, parent=None) -> None:
        super().__init__("Battery", theme, "Power info", parent)

        info = get_battery_info()
        percent = info["percent"]
        charging = info["charging"]

        # Battery level display
        level_card = QFrame()
        level_card.setMinimumHeight(160)
        level_card.setStyleSheet(
            f"""
            QFrame {{ background: {theme.surface}; border-radius: 12px; }}
            QLabel {{ background: transparent; }}
            """
        )
        level_layout = QVBoxLayout(level_card)
        level_layout.setContentsMargins(24, 20, 24, 20)
        level_layout.setSpacing(6)

        pct_label = QLabel(f"{percent}%")
        pct_label.setFont(QFont("Segoe UI Light", 56, QFont.Weight.Light))
        pct_label.setStyleSheet(f"color: {theme.foreground.name()};")
        level_layout.addWidget(pct_label, 0, Qt.AlignmentFlag.AlignCenter)

        status_text = "Charging ⚡" if charging else f"Estimated {int(percent * 0.65)}h {int((percent * 0.65 % 1) * 60)}m remaining"
        status_label = QLabel(status_text)
        status_label.setFont(QFont("Segoe UI", 16))
        status_label.setStyleSheet(f"color: {self.theme.muted};")
        level_layout.addWidget(status_label, 0, Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(level_card)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {self.theme.muted}; max-height: 1px;")
        self.content_layout.addWidget(sep)

        # Usage breakdown
        usage_title = QLabel("Battery Usage")
        usage_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        usage_title.setStyleSheet(f"color: {theme.foreground.name()}; background: transparent;")
        self.content_layout.addWidget(usage_title)

        usages = [
            ("Display", 42, QColor("#0078D7")),
            ("Apps", 28, QColor("#107C10")),
            ("System", 15, QColor("#8764B8")),
            ("WiFi", 8, QColor("#00B7C3")),
            ("Standby", 7, QColor("#F7630C")),
        ]

        for label, pct, color in usages:
            self.content_layout.addWidget(BatteryBar(pct, color, label))

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"background: {self.theme.muted}; max-height: 1px;")
        self.content_layout.addWidget(sep2)

        # Battery saver
        saver_card = QFrame()
        saver_card.setMinimumHeight(72)
        saver_card.setStyleSheet(
            f"QFrame {{ background: {theme.surface}; border-radius: 8px; }}"
            f"QLabel {{ background: transparent; color: {theme.foreground.name()}; }}"
        )
        saver_layout = QHBoxLayout(saver_card)
        saver_layout.setContentsMargins(18, 10, 18, 10)
        saver_text = QLabel("Battery Saver")
        saver_text.setFont(QFont("Segoe UI", 17, QFont.Weight.Medium))
        saver_layout.addWidget(saver_text)
        saver_layout.addStretch(1)
        saver_status = QLabel("Off")
        saver_status.setFont(QFont("Segoe UI", 15))
        saver_status.setStyleSheet(f"color: {self.theme.muted}; background: transparent;")
        saver_layout.addWidget(saver_status)
        self.content_layout.addWidget(saver_card)

        self.add_card("Screen On Time", "4h 23m since last charge")
        self.add_card("Temperature", "31°C — Normal")
        self.finish()
