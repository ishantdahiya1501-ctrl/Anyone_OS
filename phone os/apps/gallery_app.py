"""Gallery app with image grid."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)

from apps.base_app import AppTheme, PhoneAppScreen


PLACEHOLDER_COLORS = [
    ("#E81123", "Sunset"),
    ("#0078D7", "Ocean"),
    ("#107C10", "Forest"),
    ("#8764B8", "Lavender"),
    ("#F7630C", "Amber"),
    ("#00B7C3", "Sky"),
    ("#B4009E", "Bloom"),
    ("#498205", "Meadow"),
    ("#004E8C", "Midnight"),
    ("#D83B01", "Flame"),
    ("#2D7D9A", "Teal"),
    ("#5C2D91", "Plum"),
    ("#E81123", "Rose"),
    ("#0078D7", "Azure"),
    ("#107C10", "Emerald"),
    ("#8764B8", "Violet"),
]


class ThumbnailWidget(QWidget):
    """Color-based thumbnail placeholder."""
    def __init__(self, color: str, label: str, size: int = 120, parent=None) -> None:
        super().__init__(parent)
        self.color = QColor(color)
        self.label_text = label
        self.setFixedSize(size, size)

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self.color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)

        # Image icon placeholder
        painter.setPen(QPen(QColor(255, 255, 255, 120), 2))
        icon_rect = self.rect().adjusted(20, 15, -20, -25)
        painter.drawRect(icon_rect)

        painter.setPen(QColor(255, 255, 255, 200))
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        painter.drawText(
            self.rect().adjusted(0, 0, 0, -8),
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
            self.label_text,
        )


class GalleryApp(PhoneAppScreen):
    def __init__(self, theme: AppTheme, parent=None) -> None:
        super().__init__("Gallery", theme, "Photos & albums", parent)

        # Albums section
        album_title = QLabel("Albums")
        album_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        album_title.setStyleSheet(f"color: {theme.foreground.name()}; background: transparent;")
        self.content_layout.addWidget(album_title)

        albums = [
            ("Camera Roll", "24 items", "#E81123"),
            ("Screenshots", "6 items", "#0078D7"),
            ("Downloads", "3 items", "#107C10"),
            ("Wallpapers", "1 item", "#8764B8"),
        ]

        album_row = QHBoxLayout()
        album_row.setSpacing(10)
        for name, count, color in albums:
            card = QFrame()
            card.setFixedSize(150, 150)
            card.setStyleSheet(
                f"QFrame {{ background: {color}; border-radius: 10px; }}"
                f"QLabel {{ background: transparent; color: #FFFFFF; }}"
            )
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(14, 14, 14, 14)
            card_layout.addStretch(1)
            name_lbl = QLabel(name)
            name_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            name_lbl.setWordWrap(True)
            card_layout.addWidget(name_lbl)
            count_lbl = QLabel(count)
            count_lbl.setFont(QFont("Segoe UI", 11))
            count_lbl.setStyleSheet("color: rgba(255,255,255,180); background: transparent;")
            card_layout.addWidget(count_lbl)
            album_row.addWidget(card)
        album_row.addStretch(1)
        self.content_layout.addLayout(album_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {self.theme.muted}; max-height: 1px;")
        self.content_layout.addWidget(sep)

        # All photos grid
        photos_title = QLabel("All Photos")
        photos_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        photos_title.setStyleSheet(f"color: {theme.foreground.name()}; background: transparent;")
        self.content_layout.addWidget(photos_title)

        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(6)
        grid.setContentsMargins(0, 0, 0, 0)

        for i, (color, label) in enumerate(PLACEHOLDER_COLORS):
            thumb = ThumbnailWidget(color, label, 110)
            thumb.setCursor(Qt.CursorShape.PointingHandCursor)
            row, col = i // 3, i % 3
            grid.addWidget(thumb, row, col)

        for c in range(3):
            grid.setColumnStretch(c, 1)

        self.content_layout.addWidget(grid_widget)
        self.add_action_button("Open Camera")
        self.finish()
