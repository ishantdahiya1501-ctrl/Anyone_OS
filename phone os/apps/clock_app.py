"""Clock app with live updating time and stopwatch."""

from __future__ import annotations

import time
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, QFrame

from apps.base_app import AppTheme, PhoneAppScreen


class ClockApp(PhoneAppScreen):
    def __init__(self, theme: AppTheme, parent=None) -> None:
        super().__init__("Clock", theme, "Time & stopwatch", parent)

        # Live clock display
        self.time_label = QLabel(datetime.now().strftime("%H:%M:%S"))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont("Segoe UI Light", 64, QFont.Weight.Light))
        self.time_label.setStyleSheet(
            f"color: {theme.foreground.name()}; background: {theme.surface}; "
            f"border-radius: 12px; padding: 24px;"
        )
        self.content_layout.addWidget(self.time_label)

        self.date_label = QLabel(datetime.now().strftime("%A, %d %B %Y"))
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setFont(QFont("Segoe UI", 18))
        self.date_label.setStyleSheet(f"color: {self.theme.muted}; background: transparent;")
        self.content_layout.addWidget(self.date_label)

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {self.theme.muted}; max-height: 1px;")
        self.content_layout.addWidget(sep)

        # Stopwatch section
        sw_title = QLabel("Stopwatch")
        sw_title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        sw_title.setStyleSheet(f"color: {theme.foreground.name()}; background: transparent;")
        self.content_layout.addWidget(sw_title)

        self.sw_label = QLabel("00:00:00.0")
        self.sw_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sw_label.setFont(QFont("Segoe UI Light", 40, QFont.Weight.Light))
        self.sw_label.setStyleSheet(
            f"color: {theme.accent.name()}; background: {theme.surface}; "
            f"border-radius: 12px; padding: 18px;"
        )
        self.content_layout.addWidget(self.sw_label)

        # Stopwatch controls
        ctrl = QHBoxLayout()
        self.sw_running = False
        self.sw_elapsed = 0
        self.sw_start_time = 0

        self.sw_start_btn = QPushButton("Start")
        self.sw_start_btn.setMinimumHeight(52)
        self.sw_start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sw_start_btn.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.sw_start_btn.setStyleSheet(
            f"QPushButton {{ color: #FFF; background: {theme.accent.name()}; border: none; border-radius: 8px; }}"
            f"QPushButton:pressed {{ background: rgba({theme.accent.red()}, {theme.accent.green()}, {theme.accent.blue()}, 170); }}"
        )
        self.sw_start_btn.clicked.connect(self._toggle_stopwatch)
        ctrl.addWidget(self.sw_start_btn)

        self.sw_reset_btn = QPushButton("Reset")
        self.sw_reset_btn.setMinimumHeight(52)
        self.sw_reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sw_reset_btn.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.sw_reset_btn.setStyleSheet(
            f"QPushButton {{ color: {theme.foreground.name()}; background: {theme.surface}; border: none; border-radius: 8px; }}"
            f"QPushButton:pressed {{ background: {self.theme.muted}; }}"
        )
        self.sw_reset_btn.clicked.connect(self._reset_stopwatch)
        ctrl.addWidget(self.sw_reset_btn)
        self.content_layout.addLayout(ctrl)

        # Lap times
        self.laps_layout = QVBoxLayout()
        self.laps_layout.setSpacing(6)
        self.content_layout.addLayout(self.laps_layout)

        self.lap_btn = QPushButton("Lap")
        self.lap_btn.setMinimumHeight(48)
        self.lap_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lap_btn.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        self.lap_btn.setVisible(False)
        self.lap_btn.setStyleSheet(
            f"QPushButton {{ color: {theme.foreground.name()}; background: {theme.surface}; border: none; border-radius: 8px; }}"
            f"QPushButton:pressed {{ background: {self.theme.muted}; }}"
        )
        self.lap_btn.clicked.connect(self._record_lap)
        self.content_layout.addWidget(self.lap_btn)

        self.lap_count = 0

        # Stopwatch timer
        self.sw_timer = QTimer(self)
        self.sw_timer.timeout.connect(self._update_stopwatch)

        self.finish()

    def _update_clock(self) -> None:
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S"))
        self.date_label.setText(now.strftime("%A, %d %B %Y"))

    def _toggle_stopwatch(self) -> None:
        if self.sw_running:
            self.sw_timer.stop()
            self.sw_running = False
            self.sw_start_btn.setText("Resume")
            self.lap_btn.setVisible(True)
        else:
            self.sw_start_time = time.time() - self.sw_elapsed
            self.sw_timer.start(50)
            self.sw_running = True
            self.sw_start_btn.setText("Stop")
            self.lap_btn.setVisible(True)

    def _reset_stopwatch(self) -> None:
        self.sw_timer.stop()
        self.sw_running = False
        self.sw_elapsed = 0
        self.sw_label.setText("00:00:00.0")
        self.sw_start_btn.setText("Start")
        self.lap_btn.setVisible(False)
        self.lap_count = 0
        while self.laps_layout.count():
            child = self.laps_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _update_stopwatch(self) -> None:
        self.sw_elapsed = time.time() - self.sw_start_time
        self.sw_label.setText(self._format_time(self.sw_elapsed))

    def _format_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        tenths = int((seconds * 10) % 10)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{tenths}"

    def _record_lap(self) -> None:
        self.lap_count += 1
        lap_text = f"Lap {self.lap_count}: {self._format_time(self.sw_elapsed)}"
        label = QLabel(lap_text)
        label.setFont(QFont("Segoe UI", 15))
        label.setStyleSheet(f"color: {self.theme.foreground.name()}; background: {self.theme.surface}; border-radius: 6px; padding: 8px 14px;")
        self.laps_layout.insertWidget(0, label)
