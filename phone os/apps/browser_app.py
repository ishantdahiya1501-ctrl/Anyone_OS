"""Browser app with URL bar and content area."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea,
    QTextBrowser, QVBoxLayout, QWidget, QFrame,
)

from apps.base_app import AppTheme, PhoneAppScreen


BOOKMARKS = [
    ("PhoneOS Home", "https://phoneos.local"),
    ("Settings", "https://phoneos.local/settings"),
    ("Weather", "https://phoneos.local/weather"),
    ("News", "https://news.phoneos.local"),
]


class BrowserApp(PhoneAppScreen):
    def __init__(self, theme: AppTheme, parent=None) -> None:
        super().__init__("Browser", theme, "Web browser", parent)

        # URL bar
        url_bar = QFrame()
        url_bar.setStyleSheet(
            f"""
            QFrame {{
                background: {theme.surface};
                border-radius: 10px;
            }}
            """
        )
        url_layout = QHBoxLayout(url_bar)
        url_layout.setContentsMargins(12, 6, 12, 6)

        lock_icon = QLabel("🔒")
        lock_icon.setFont(QFont("Segoe UI", 14))
        lock_icon.setStyleSheet("background: transparent;")
        url_layout.addWidget(lock_icon)

        self.url_input = QLineEdit("https://phoneos.local")
        self.url_input.setFont(QFont("Segoe UI", 15))
        self.url_input.setStyleSheet(
            f"color: {theme.foreground.name()}; background: transparent; border: none;"
        )
        self.url_input.returnPressed.connect(self._navigate)
        url_layout.addWidget(self.url_input, 1)

        go_btn = QPushButton("→")
        go_btn.setFixedSize(36, 36)
        go_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        go_btn.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        go_btn.setStyleSheet(
            f"""
            QPushButton {{
                color: #FFFFFF;
                background: {theme.accent.name()};
                border: none;
                border-radius: 18px;
            }}
            QPushButton:pressed {{
                background: rgba({theme.accent.red()}, {theme.accent.green()}, {theme.accent.blue()}, 170);
            }}
            """
        )
        go_btn.clicked.connect(self._navigate)
        url_layout.addWidget(go_btn)
        self.content_layout.addWidget(url_bar)

        # Navigation controls
        nav_row = QHBoxLayout()
        nav_row.setSpacing(8)
        for icon, label in [("←", "Back"), ("→", "Forward"), ("🔄", "Refresh"), ("🏠", "Home")]:
            btn = QPushButton(f"{icon}")
            btn.setFixedSize(40, 40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 16))
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    color: {theme.foreground.name()};
                    background: {theme.surface};
                    border: none;
                    border-radius: 8px;
                }}
                QPushButton:pressed {{
                    background: {self.theme.muted};
                }}
                """
            )
            nav_row.addWidget(btn)
        nav_row.addStretch(1)
        self.content_layout.addLayout(nav_row)

        # Content area
        self.content_area = QTextBrowser()
        self.content_area.setOpenExternalLinks(False)
        self.content_area.setStyleSheet(
            f"""
            QTextBrowser {{
                color: {theme.foreground.name()};
                background: {theme.surface};
                border: none;
                border-radius: 8px;
                padding: 16px;
                font-size: 15px;
            }}
            """
        )
        self.content_area.setHtml(self._home_page(theme))
        self.content_area.setMinimumHeight(400)
        self.content_layout.addWidget(self.content_area, 1)

        # Bookmarks
        bm_title = QLabel("Bookmarks")
        bm_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        bm_title.setStyleSheet(f"color: {theme.foreground.name()}; background: transparent;")
        self.content_layout.addWidget(bm_title)

        for name, url in BOOKMARKS:
            card = self.add_card(f"🔗  {name}", url, 56)
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            card.mousePressEvent = lambda e, u=url: self._load_url(u)

        self.finish()

    def _home_page(self, theme: AppTheme) -> str:
        return f"""
        <div style="font-family: 'Segoe UI'; color: {theme.foreground.name()};">
            <h2 style="color: {theme.accent.name()};">PhoneOS Browser</h2>
            <p style="color: {self.theme.muted}; font-size: 14px;">Welcome to the PhoneOS web browser.</p>
            <hr style="border-color: {self.theme.muted};">
            <h3>Quick Links</h3>
            <ul>
                <li><a href="https://phoneos.local/settings" style="color: {theme.accent.name()};">System Settings</a></li>
                <li><a href="https://phoneos.local/weather" style="color: {theme.accent.name()};">Weather</a></li>
                <li><a href="https://news.phoneos.local" style="color: {theme.accent.name()};">News</a></li>
            </ul>
            <p style="color: {self.theme.muted}; font-size: 13px; margin-top: 24px;">
                Enter a URL above to navigate to a web page.
            </p>
        </div>
        """

    def _navigate(self) -> None:
        url = self.url_input.text().strip()
        if url:
            self._load_url(url)

    def _load_url(self, url: str) -> None:
        self.url_input.setText(url)
        self.content_area.setHtml(
            f"""
            <div style="font-family: 'Segoe UI'; color: {self.theme.foreground.name()};">
                <h2 style="color: {self.theme.accent.name()};">Loading...</h2>
                <p>Navigating to <b>{url}</b></p>
                <p style="color: {self.theme.muted};">This is a placeholder browser. Full web rendering can be added with QWebEngineView.</p>
            </div>
            """
        )
