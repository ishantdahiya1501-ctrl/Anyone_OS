"""App Store app with app cards and categories."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPainter
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, QFrame

from apps.base_app import AppTheme, PhoneAppScreen


STORE_APPS = [
    {
        "name": "Notes",
        "desc": "Quick notes and to-do lists",
        "color": "#F7630C",
        "letter": "N",
        "rating": "4.5",
    },
    {
        "name": "Maps",
        "desc": "Navigation and local search",
        "color": "#107C10",
        "letter": "M",
        "rating": "4.2",
    },
    {
        "name": "Podcasts",
        "desc": "Listen to your favorite shows",
        "color": "#8764B8",
        "letter": "P",
        "rating": "4.7",
    },
    {
        "name": "Translate",
        "desc": "Real-time language translation",
        "color": "#0078D7",
        "letter": "T",
        "rating": "4.3",
    },
    {
        "name": "Fitness",
        "desc": "Track your workouts and health",
        "color": "#E81123",
        "letter": "F",
        "rating": "4.6",
    },
    {
        "name": "Recorder",
        "desc": "Voice and audio recorder",
        "color": "#00B7C3",
        "letter": "R",
        "rating": "4.1",
    },
]


class AppIcon(QWidget):
    """Colored app icon placeholder."""
    def __init__(self, letter: str, color: str, size: int = 56, parent=None) -> None:
        super().__init__(parent)
        self.letter = letter
        self.color = QColor(color)
        self.setFixedSize(size, size)

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self.color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 12, 12)
        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.letter)
        painter.end()


class StoreAppCard(QFrame):
    """App card for the store."""
    def __init__(self, app: dict, theme: AppTheme, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(80)
        self.setStyleSheet(
            f"""
            QFrame {{
                background: {theme.surface};
                border-radius: 10px;
            }}
            QLabel {{ background: transparent; color: {theme.foreground.name()}; }}
            """
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(14)

        icon = AppIcon(app["letter"], app["color"], 52)
        layout.addWidget(icon)

        info = QVBoxLayout()
        info.setSpacing(2)
        name = QLabel(app["name"])
        name.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        info.addWidget(name)

        desc = QLabel(app["desc"])
        desc.setFont(QFont("Segoe UI", 13))
        desc.setStyleSheet(f"color: {self.theme.muted}; background: transparent;")
        info.addWidget(desc)
        layout.addLayout(info, 1)

        right = QVBoxLayout()
        right.setSpacing(2)
        rating = QLabel(f"⭐ {app['rating']}")
        rating.setFont(QFont("Segoe UI", 12))
        rating.setAlignment(Qt.AlignmentFlag.AlignRight)
        right.addWidget(rating)

        install_btn = QPushButton("Get")
        install_btn.setFixedSize(72, 34)
        install_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        install_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        install_btn.setStyleSheet(
            f"""
            QPushButton {{
                color: #FFFFFF;
                background: {theme.accent.name()};
                border: none;
                border-radius: 17px;
            }}
            QPushButton:pressed {{
                background: rgba({theme.accent.red()}, {theme.accent.green()}, {theme.accent.blue()}, 170);
            }}
            """
        )
        right.addWidget(install_btn, 0, Qt.AlignmentFlag.AlignRight)
        layout.addLayout(right)


class AppStoreApp(PhoneAppScreen):
    def __init__(self, theme: AppTheme, parent=None) -> None:
        super().__init__("App Store", theme, "Discover apps", parent)

        # Search bar
        search_frame = QFrame()
        search_frame.setStyleSheet(
            f"QFrame {{ background: {theme.surface}; border-radius: 10px; }}"
        )
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(16, 10, 16, 10)
        search_icon = QLabel("🔍")
        search_icon.setFont(QFont("Segoe UI", 16))
        search_icon.setStyleSheet("background: transparent;")
        search_layout.addWidget(search_icon)
        search_text = QLabel("Search apps...")
        search_text.setFont(QFont("Segoe UI", 15))
        search_text.setStyleSheet(f"color: {self.theme.muted}; background: transparent;")
        search_layout.addWidget(search_text)
        self.content_layout.addWidget(search_frame)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {self.theme.muted}; max-height: 1px;")
        self.content_layout.addWidget(sep)

        # Featured section
        featured_title = QLabel("Featured Apps")
        featured_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        featured_title.setStyleSheet(f"color: {theme.foreground.name()}; background: transparent;")
        self.content_layout.addWidget(featured_title)

        # Featured banner
        banner = QFrame()
        banner.setMinimumHeight(120)
        banner.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {theme.accent.name()}, stop:1 rgba({theme.accent.red()}, {theme.accent.green()}, {theme.accent.blue()}, 120));
                border-radius: 12px;
            }}
            QLabel {{ background: transparent; color: #FFFFFF; }}
            """
        )
        banner_layout = QVBoxLayout(banner)
        banner_layout.setContentsMargins(20, 14, 20, 14)
        banner_title = QLabel("PhoneOS Essentials")
        banner_title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        banner_layout.addWidget(banner_title)
        banner_sub = QLabel("Essential apps for your PhoneOS experience")
        banner_sub.setFont(QFont("Segoe UI", 14))
        banner_sub.setStyleSheet("color: rgba(255,255,255,180); background: transparent;")
        banner_layout.addWidget(banner_sub)
        self.content_layout.addWidget(banner)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"background: {self.theme.muted}; max-height: 1px;")
        self.content_layout.addWidget(sep2)

        # App list
        apps_title = QLabel("Suggested")
        apps_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        apps_title.setStyleSheet(f"color: {theme.foreground.name()}; background: transparent;")
        self.content_layout.addWidget(apps_title)

        for app in STORE_APPS:
            card = StoreAppCard(app, theme)
            self.content_layout.addWidget(card)

        self.finish()
