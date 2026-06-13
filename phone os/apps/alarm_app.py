"""Alarm app with alarm management."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from apps.base_app import AppTheme, PhoneAppScreen


ALARMS = [
    {"time": "07:00", "label": "Weekday", "enabled": True},
    {"time": "08:30", "label": "Weekend", "enabled": False},
    {"time": "06:15", "label": "Gym", "enabled": True},
    {"time": "22:00", "label": "Sleep reminder", "enabled": False},
]


class AlarmSwitch(QPushButton):
    """Toggle switch for alarms."""
    toggled_state = pyqtSignal(bool)

    def __init__(self, checked: bool, accent, parent=None) -> None:
        super().__init__(parent)
        self._checked = checked
        self._accent = accent
        self.setFixedSize(56, 30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style()
        self.clicked.connect(self._toggle)

    def _toggle(self) -> None:
        self._checked = not self._checked
        self._update_style()
        self.toggled_state.emit(self._checked)

    def _update_style(self) -> None:
        bg = self._accent.name() if self._checked else "#666666"
        self.setStyleSheet(
            f"""
            QPushButton {{
                color: {'#FFFFFF' if self._checked else '#999999'};
                background: {bg};
                border: none;
                border-radius: 15px;
                font-size: 16px;
            }}
            """
        )
        self.setText("●" if self._checked else "○")


class AlarmCard(QFrame):
    """Single alarm entry with time, label, and toggle."""
    def __init__(self, alarm: dict, theme: AppTheme, parent=None) -> None:
        super().__init__(parent)
        self._theme = theme
        self.alarm = alarm
        self.setMinimumHeight(90)
        self.setStyleSheet(
            f"""
            QFrame {{
                background: {theme.surface};
                border-left: 5px solid {theme.accent.name() if alarm['enabled'] else '#555555'};
                border-radius: 8px;
            }}
            QLabel {{ background: transparent; color: {theme.foreground.name()}; }}
            """
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 10, 18, 10)

        time_box = QVBoxLayout()
        time_box.setSpacing(2)
        time_lbl = QLabel(alarm["time"])
        time_lbl.setFont(QFont("Segoe UI Light", 34, QFont.Weight.Light))
        if not alarm["enabled"]:
            time_lbl.setStyleSheet(f"color: {self.theme.muted}; background: transparent;")
        time_box.addWidget(time_lbl)
        label_lbl = QLabel(alarm["label"])
        label_lbl.setFont(QFont("Segoe UI", 14))
        label_lbl.setStyleSheet(f"color: {self.theme.muted}; background: transparent;")
        time_box.addWidget(label_lbl)
        layout.addLayout(time_box)

        layout.addStretch(1)

        self.switch = AlarmSwitch(alarm["enabled"], theme.accent)
        self.switch.toggled_state.connect(self._on_toggle)
        layout.addWidget(self.switch)

    def _on_toggle(self, enabled: bool) -> None:
        self.alarm["enabled"] = enabled
        border_color = self._theme.accent.name() if enabled else "#555555"
        self.setStyleSheet(
            f"""
            QFrame {{
                background: {self._theme.surface};
                border-left: 5px solid {border_color};
                border-radius: 8px;
            }}
            QLabel {{ background: transparent; color: {self._theme.foreground.name()}; }}
            """
        )


class AlarmApp(PhoneAppScreen):
    def __init__(self, theme: AppTheme, parent=None) -> None:
        super().__init__("Alarm", theme, "Alarms & timers", parent)

        self.alarms = [dict(a) for a in ALARMS]

        for alarm in self.alarms:
            card = AlarmCard(alarm, theme)
            self.content_layout.addWidget(card)

        self.add_action_button("New Alarm")
        self.finish()
