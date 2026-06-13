"""Camera app with viewfinder placeholder."""

from __future__ import annotations

import random

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, QFrame

from apps.base_app import AppTheme, PhoneAppScreen


class ViewfinderWidget(QWidget):
    """Simulated camera viewfinder with animated noise."""
    def __init__(self, theme: AppTheme, parent=None) -> None:
        super().__init__(parent)
        self.theme = theme
        self.setMinimumHeight(380)
        self.dots = [(random.randint(0, 300), random.randint(0, 380), random.randint(20, 80)) for _ in range(40)]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(120)

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Dark background
        painter.fillRect(self.rect(), QColor("#0A0A0A"))

        # Simulated camera feed pattern
        for x, y, alpha in self.dots:
            color = QColor(self.theme.accent.red(), self.theme.accent.green(), self.theme.accent.blue(), alpha)
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            size = random.randint(2, 8)
            painter.drawEllipse(x, y, size, size)

        # Grid lines
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        w, h = self.width(), self.height()
        for i in range(1, 3):
            painter.drawLine(w * i // 3, 0, w * i // 3, h)
            painter.drawLine(0, h * i // 3, w, h * i // 3)

        # Center focus circle
        painter.setPen(QPen(QColor(255, 255, 255, 100), 2))
        cx, cy = w // 2, h // 2
        painter.drawEllipse(cx - 40, cy - 40, 80, 80)

        # "Camera Preview" text
        painter.setPen(QColor(255, 255, 255, 140))
        painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Normal))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "📷  Camera Preview")
        painter.end()


class CameraApp(PhoneAppScreen):
    def __init__(self, theme: AppTheme, parent=None) -> None:
        super().__init__("Camera", theme, "Viewfinder", parent)

        # Viewfinder
        self.viewfinder = ViewfinderWidget(theme)
        self.content_layout.addWidget(self.viewfinder)

        # Mode selector
        modes = QHBoxLayout()
        modes.setSpacing(8)
        for mode in ("Photo", "Video", "Portrait", "Night"):
            btn = QPushButton(mode)
            btn.setMinimumHeight(36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold if mode == "Photo" else QFont.Weight.Normal))
            is_active = mode == "Photo"
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    color: {'#FFFFFF' if is_active else theme.foreground.name()};
                    background: {theme.accent.name() if is_active else theme.surface};
                    border: none;
                    border-radius: 18px;
                    padding: 0 16px;
                }}
                QPushButton:pressed {{
                    background: {theme.accent.name()};
                    color: #FFFFFF;
                }}
                """
            )
            modes.addWidget(btn)
        self.content_layout.addLayout(modes)

        # Capture controls
        ctrl = QHBoxLayout()
        ctrl.setSpacing(24)
        ctrl.addStretch(1)

        # Gallery thumbnail
        gallery_btn = QPushButton("🖼️")
        gallery_btn.setFixedSize(52, 52)
        gallery_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        gallery_btn.setStyleSheet(
            f"QPushButton {{ color: {theme.foreground.name()}; background: {theme.surface}; border: none; border-radius: 8px; font-size: 22px; }}"
        )
        ctrl.addWidget(gallery_btn)

        # Capture button
        capture_btn = QPushButton("")
        capture_btn.setFixedSize(76, 76)
        capture_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        capture_btn.setStyleSheet(
            f"""
            QPushButton {{
                color: #FFFFFF;
                background: transparent;
                border: 4px solid #FFFFFF;
                border-radius: 38px;
            }}
            QPushButton:pressed {{
                background: rgba(255, 255, 255, 80);
            }}
            """
        )
        ctrl.addWidget(capture_btn)

        # Switch camera
        switch_btn = QPushButton("🔄")
        switch_btn.setFixedSize(52, 52)
        switch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        switch_btn.setStyleSheet(
            f"QPushButton {{ color: {theme.foreground.name()}; background: {theme.surface}; border: none; border-radius: 8px; font-size: 22px; }}"
        )
        ctrl.addWidget(switch_btn)

        ctrl.addStretch(1)
        self.content_layout.addLayout(ctrl)

        # Settings row
        settings_row = QHBoxLayout()
        for label in ("HDR", "Timer", "Grid", "Flash"):
            btn = QPushButton(label)
            btn.setMinimumHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    color: {theme.foreground.name()};
                    background: {theme.surface};
                    border: none;
                    border-radius: 8px;
                    padding: 0 14px;
                }}
                QPushButton:pressed {{
                    background: {self.theme.muted};
                }}
                """
            )
            settings_row.addWidget(btn)
        self.content_layout.addLayout(settings_row)
        self.finish()
