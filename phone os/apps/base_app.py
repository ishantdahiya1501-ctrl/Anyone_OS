"""Shared visual building blocks for PhoneOS apps."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SETTINGS_FILE = PROJECT_ROOT / "settings" / "settings.json"

ACCENT_COLORS = {
    "blue": "#0078D7",
    "cyan": "#00B7C3",
    "purple": "#8764B8",
    "orange": "#F7630C",
    "red": "#E81123",
    "green": "#107C10",
}


@dataclass(frozen=True)
class AppTheme:
    accent: QColor
    light_theme: bool = False

    @property
    def foreground(self) -> QColor:
        return QColor("#111111" if self.light_theme else "#FFFFFF")

    @property
    def muted(self) -> str:
        return "rgba(17, 17, 17, 170)" if self.light_theme else "rgba(255, 255, 255, 172)"

    @property
    def background(self) -> str:
        return "#F4F4F4" if self.light_theme else "#101014"

    @property
    def surface(self) -> str:
        return "#FFFFFF" if self.light_theme else "#202026"


def load_current_theme() -> AppTheme:
    """Load theme from settings.json."""
    if not SETTINGS_FILE.exists():
        return AppTheme(accent=QColor(ACCENT_COLORS["blue"]))
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return AppTheme(accent=QColor(ACCENT_COLORS["blue"]))

    accent_name = data.get("accent_color", ACCENT_COLORS["blue"])
    if isinstance(accent_name, str) and accent_name.lower() in ACCENT_COLORS:
        accent_name = ACCENT_COLORS[accent_name.lower()]
    accent = QColor(accent_name)
    if not accent.isValid():
        accent = QColor(ACCENT_COLORS["blue"])
    light = str(data.get("theme", "dark")).lower() == "light"
    return AppTheme(accent=accent, light_theme=light)


class PhoneAppScreen(QWidget):
    """Base visual shell for independent app screens with back navigation."""

    back_requested = pyqtSignal()

    def __init__(
        self,
        app_name: str,
        theme: AppTheme,
        subtitle: str = "Preview",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.app_name = app_name
        self.theme = theme
        self.subtitle = subtitle
        self.setStyleSheet(f"background: {theme.background};")

        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(0)

        # Fixed header
        header_widget = QWidget()
        header_widget.setFixedHeight(100)
        header_widget.setStyleSheet(f"background: {theme.background};")
        self.header_layout = QVBoxLayout(header_widget)
        self.header_layout.setContentsMargins(18, 14, 18, 0)
        self.header_layout.setSpacing(0)
        self._build_header()
        self.root.addWidget(header_widget)

        # Scrollable content area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(
            f"QScrollArea {{ border: none; background: {theme.background}; }}"
        )
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet(f"background: {theme.background};")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(18, 10, 18, 16)
        self.content_layout.setSpacing(10)
        self.scroll_area.setWidget(self.content_widget)
        self.root.addWidget(self.scroll_area, 1)

    def _build_header(self) -> None:
        top = QHBoxLayout()

        # Back button
        self.back_btn = QPushButton("<")
        self.back_btn.setFixedSize(34, 34)
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.setFont(QFont("Segoe UI", 20, QFont.Weight.Light))
        self.back_btn.setStyleSheet(
            f"""
            QPushButton {{
                color: {self.theme.foreground.name()};
                background: transparent;
                border: none;
                border-radius: 22px;
            }}
            QPushButton:pressed {{
                background: {self.theme.muted};
            }}
            """
        )
        self.back_btn.clicked.connect(self.back_requested.emit)
        top.addWidget(self.back_btn)

        # Title
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel(self.app_name)
        title.setFont(QFont("Segoe UI Light", 26, QFont.Weight.Light))
        title.setStyleSheet(f"color: {self.theme.foreground.name()}; background: transparent;")
        title_box.addWidget(title)

        subtitle = QLabel(self.subtitle)
        subtitle.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        subtitle.setStyleSheet(f"color: {self.theme.muted}; background: transparent;")
        title_box.addWidget(subtitle)
        top.addLayout(title_box)
        top.addStretch(1)

        time_label = QLabel(datetime.now().strftime("%H:%M"))
        time_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        time_label.setStyleSheet(f"color: {self.theme.foreground.name()}; background: transparent;")
        top.addWidget(time_label)
        self.header_layout.addLayout(top)

    def add_card(self, title: str, detail: str = "", height: int = 78) -> QFrame:
        card = QFrame()
        card.setMinimumHeight(height)
        card.setStyleSheet(
            f"""
            QFrame {{
                background: {self.theme.surface};
                border-left: 5px solid {self.theme.accent.name()};
                border-radius: 8px;
            }}
            QLabel {{
                background: transparent;
                color: {self.theme.foreground.name()};
            }}
            """
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 8, 14, 8)
        label = QLabel(title)
        label.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        label.setWordWrap(True)
        layout.addWidget(label)
        if detail:
            sub = QLabel(detail)
            sub.setFont(QFont("Segoe UI", 12))
            sub.setStyleSheet(f"color: {self.theme.muted}; background: transparent;")
            sub.setWordWrap(True)
            layout.addWidget(sub)
        self.content_layout.addWidget(card)
        return card

    def add_action_button(self, text: str, callback=None) -> QPushButton:
        button = QPushButton(text)
        button.setMinimumHeight(46)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        button.setStyleSheet(
            f"""
            QPushButton {{
                color: #FFFFFF;
                background: {self.theme.accent.name()};
                border: none;
                border-radius: 8px;
            }}
            QPushButton:pressed {{
                background: rgba({self.theme.accent.red()}, {self.theme.accent.green()}, {self.theme.accent.blue()}, 170);
            }}
            """
        )
        if callback is not None:
            button.clicked.connect(callback)
        self.content_layout.addWidget(button)
        return button

    def finish(self) -> None:
        self.content_layout.addStretch(1)
