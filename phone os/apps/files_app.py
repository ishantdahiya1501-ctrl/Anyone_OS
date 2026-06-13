"""Files app with simple file browser."""

from __future__ import annotations

import os
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from apps.base_app import AppTheme, PhoneAppScreen, PROJECT_ROOT


class FilesApp(PhoneAppScreen):
    def __init__(self, theme: AppTheme, parent=None) -> None:
        super().__init__("Files", theme, "File manager", parent)
        self._theme = theme
        self.current_path = Path.home()
        self.breadcrumb = [self.current_path]

        # Breadcrumb navigation
        self.breadcrumb_widget = QWidget()
        self.breadcrumb_layout = QHBoxLayout(self.breadcrumb_widget)
        self.breadcrumb_layout.setContentsMargins(0, 0, 0, 0)
        self.breadcrumb_layout.setSpacing(4)
        self.content_layout.addWidget(self.breadcrumb_widget)
        self._update_breadcrumb()

        # File list container
        self.file_list_widget = QWidget()
        self.file_list_layout = QVBoxLayout(self.file_list_widget)
        self.file_list_layout.setContentsMargins(0, 0, 0, 0)
        self.file_list_layout.setSpacing(4)
        self.content_layout.addWidget(self.file_list_widget)

        self._browse_to(self.current_path)
        self.finish()

    def _update_breadcrumb(self) -> None:
        while self.breadcrumb_layout.count():
            child = self.breadcrumb_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for i, part in enumerate(self.breadcrumb):
            if i > 0:
                sep = QLabel("›")
                sep.setFont(QFont("Segoe UI", 14))
                sep.setStyleSheet(f"color: {self.theme.muted}; background: transparent;")
                self.breadcrumb_layout.addWidget(sep)

            btn = QPushButton(part.name if part != self.breadcrumb[0] else "🏠 Home")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium if i == len(self.breadcrumb) - 1 else QFont.Weight.Normal))
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    color: {self.theme.accent.name() if i == len(self.breadcrumb) - 1 else self.theme.foreground.name()};
                    background: transparent;
                    border: none;
                    padding: 4px 6px;
                    border-radius: 4px;
                }}
                QPushButton:pressed {{
                    background: {self.theme.muted};
                }}
                """
            )
            idx = i
            btn.clicked.connect(lambda checked, idx=idx: self._navigate_to_index(idx))
            self.breadcrumb_layout.addWidget(btn)

        self.breadcrumb_layout.addStretch(1)

    def _navigate_to_index(self, index: int) -> None:
        self.current_path = self.breadcrumb[index]
        self.breadcrumb = self.breadcrumb[: index + 1]
        self._update_breadcrumb()
        self._browse_to(self.current_path)

    def _browse_to(self, path: Path) -> None:
        # Clear file list
        while self.file_list_layout.count():
            child = self.file_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Parent directory button
        if self.current_path != self.current_path.parent:
            parent_card = self._make_entry("📁", "..", "Parent directory", True)
            parent_card.setCursor(Qt.CursorShape.PointingHandCursor)
            parent_card.mousePressEvent = lambda e: self._go_up()
            self.file_list_layout.addWidget(parent_card)

        try:
            entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except PermissionError:
            err = QLabel("Permission denied")
            err.setFont(QFont("Segoe UI", 16))
            err.setStyleSheet(f"color: #E81123; background: transparent; padding: 18px;")
            self.file_list_layout.addWidget(err)
            return

        dirs = [e for e in entries if e.is_dir()][:50]
        files = [e for e in entries if e.is_file()][:50]

        for d in dirs:
            count = "folder"
            try:
                items = list(d.iterdir())
                count = f"{len(items)} items"
            except PermissionError:
                count = "inaccessible"
            card = self._make_entry("📁", d.name, count, True)
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            card.mousePressEvent = lambda e, p=d: self._enter_dir(p)
            self.file_list_layout.addWidget(card)

        for f in files:
            size = self._human_size(f.stat().st_size)
            ext = f.suffix.lower()
            icon = self._file_icon(ext)
            card = self._make_entry(icon, f.name, size, False)
            self.file_list_layout.addWidget(card)

        if not dirs and not files:
            empty = QLabel("This folder is empty")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setFont(QFont("Segoe UI", 16))
            empty.setStyleSheet(f"color: {self.theme.muted}; background: transparent; padding: 40px;")
            self.file_list_layout.addWidget(empty)

        self.file_list_layout.addStretch(1)

    def _make_entry(self, icon: str, name: str, detail: str, is_dir: bool) -> QFrame:
        card = QFrame()
        card.setMinimumHeight(64)
        card.setStyleSheet(
            f"""
            QFrame {{
                background: {self.theme.surface};
                border-left: 4px solid {'#0078D7' if is_dir else self.theme.muted};
                border-radius: 6px;
            }}
            QLabel {{ background: transparent; color: {self.theme.foreground.name()}; }}
            """
        )
        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 8, 14, 8)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI", 20))
        icon_lbl.setFixedWidth(36)
        layout.addWidget(icon_lbl)

        name_lbl = QLabel(name)
        name_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Medium if is_dir else QFont.Weight.Normal))
        name_lbl.setWordWrap(True)
        layout.addWidget(name_lbl, 1)

        detail_lbl = QLabel(detail)
        detail_lbl.setFont(QFont("Segoe UI", 13))
        detail_lbl.setStyleSheet(f"color: {self.theme.muted}; background: transparent;")
        layout.addWidget(detail_lbl, 0, Qt.AlignmentFlag.AlignRight)

        return card

    def _enter_dir(self, path: Path) -> None:
        self.current_path = path
        self.breadcrumb.append(path)
        self._update_breadcrumb()
        self._browse_to(path)

    def _go_up(self) -> None:
        if len(self.breadcrumb) > 1:
            self.breadcrumb.pop()
            self.current_path = self.breadcrumb[-1]
            self._update_breadcrumb()
            self._browse_to(self.current_path)

    def _human_size(self, size: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def _file_icon(self, ext: str) -> str:
        icons = {
            ".py": "🐍", ".js": "📜", ".html": "🌐", ".css": "🎨",
            ".jpg": "🖼️", ".png": "🖼️", ".gif": "🖼️",
            ".mp3": "🎵", ".wav": "🎵", ".mp4": "🎬", ".avi": "🎬",
            ".pdf": "📄", ".doc": "📝", ".docx": "📝", ".txt": "📝",
            ".zip": "📦", ".rar": "📦",
        }
        return icons.get(ext, "📄")
