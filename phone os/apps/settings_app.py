"""Settings app with full system settings."""

from __future__ import annotations

import json

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPixmap
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea,
    QVBoxLayout, QWidget,
)

from apps.base_app import AppTheme, PhoneAppScreen, PROJECT_ROOT, SETTINGS_FILE, ACCENT_COLORS

# Solid color wallpapers as fallbacks when image files don't exist
SOLID_WALLPAPERS = [
    ("#0A0A14", "Midnight"),
    ("#0D1B2A", "Deep Sea"),
    ("#1B1B2F", "Navy"),
    ("#2D1B69", "Purple"),
    ("#1A1A2E", "Charcoal"),
    ("#16213E", "Slate"),
    ("#0F3460", "Ocean Blue"),
    ("#533483", "Amethyst"),
]


class ToggleSwitch(QPushButton):
    """Simple toggle switch widget."""
    toggled_state = pyqtSignal(bool)

    def __init__(self, checked: bool, accent: QColor, parent=None) -> None:
        super().__init__(parent)
        self._checked = checked
        self._accent = accent
        self.setFixedSize(48, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style()
        self.clicked.connect(self._toggle)

    def _toggle(self) -> None:
        self._checked = not self._checked
        self._update_style()
        self.toggled_state.emit(self._checked)

    def _update_style(self) -> None:
        bg = self._accent.name() if self._checked else "#666666"
        self.setText("●" if self._checked else "○")
        self.setStyleSheet(
            f"""
            QPushButton {{
                color: {'#FFFFFF' if self._checked else '#999999'};
                background: {bg};
                border: none;
                border-radius: 13px;
                font-size: 14px;
            }}
            """
        )


class ColorDot(QPushButton):
    """Color picker dot."""
    selected = pyqtSignal(str)

    def __init__(self, color_name: str, color_hex: str, selected_color: str, parent=None) -> None:
        super().__init__(parent)
        self.color_name = color_name
        self.color_hex = color_hex
        self.setFixedSize(38, 38)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        border = "3px solid #FFFFFF" if color_hex == selected_color else "3px solid transparent"
        self.setStyleSheet(
            f"""
            QPushButton {{
                background: {color_hex};
                border: {border};
                border-radius: 19px;
            }}
            QPushButton:pressed {{
                border: 3px solid #FFFFFF;
            }}
            """
        )
        self.clicked.connect(lambda: self.selected.emit(color_name))


class WallpaperTile(QPushButton):
    """A wallpaper thumbnail tile."""
    selected = pyqtSignal(str, str)  # path, name

    def __init__(self, path: str, name: str, is_current: bool, theme: AppTheme, parent=None) -> None:
        super().__init__(parent)
        self.wp_path = path
        self.wp_name = name
        self.setFixedSize(72, 72)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(name)

        # Try to load the image
        pixmap = QPixmap(str(PROJECT_ROOT / path))
        if pixmap.isNull():
            # Use solid color from name mapping
            color = QColor(path) if path.startswith("#") else QColor("#333333")
            border = f"3px solid {theme.accent.name()}" if is_current else "3px solid transparent"
            self.setStyleSheet(
                f"""
                QPushButton {{
                    background: {color.name()};
                    border: {border};
                    border-radius: 8px;
                }}
                QPushButton:pressed {{
                    border: 3px solid {theme.accent.name()};
                }}
                """
            )
        else:
            scaled = pixmap.scaled(72, 72, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                   Qt.TransformationMode.SmoothTransformation)
            border = f"3px solid {theme.accent.name()}" if is_current else "3px solid transparent"
            self.setStyleSheet(f"""
                QPushButton {{
                    border: {border};
                    border-radius: 8px;
                }}
                QPushButton:pressed {{
                    border: 3px solid {theme.accent.name()};
                }}
            """)
            # We'd need a custom paintEvent for rounded image buttons, so keep it simple

        self.clicked.connect(lambda: self.selected.emit(path, name))


class SettingsApp(PhoneAppScreen):
    settings_changed = pyqtSignal()

    def __init__(self, theme: AppTheme, parent=None) -> None:
        super().__init__("Settings", theme, "System settings", parent)
        self._current_settings = self._load_settings()
        self._theme = theme

        # ── Display ──────────────────────────────────────────────
        section = self._section_label("Display")
        self.content_layout.addWidget(section)

        # Dark Mode toggle
        theme_card = self._setting_row("Dark Mode")
        self.theme_toggle = ToggleSwitch(
            self._current_settings.get("theme", "dark") == "dark",
            theme.accent,
        )
        self.theme_toggle.toggled_state.connect(self._on_theme_toggle)
        theme_card.layout().addWidget(self.theme_toggle)
        self.content_layout.addWidget(theme_card)

        # Accent color
        accent_card = QFrame()
        accent_card.setMinimumHeight(72)
        accent_card.setStyleSheet(
            f"QFrame {{ background: {theme.surface}; border-radius: 8px; }}"
            f"QLabel {{ background: transparent; color: {theme.foreground.name()}; }}"
        )
        accent_layout = QVBoxLayout(accent_card)
        accent_layout.setContentsMargins(14, 8, 14, 8)
        accent_title = QLabel("Accent Color")
        accent_title.setFont(QFont("Segoe UI", 15, QFont.Weight.Medium))
        accent_layout.addWidget(accent_title)

        color_row = QHBoxLayout()
        color_row.setSpacing(8)
        current_accent = self._current_settings.get("accent_color", "#0078D7")
        for name, hex_val in ACCENT_COLORS.items():
            dot = ColorDot(name, hex_val, current_accent)
            dot.selected.connect(self._on_accent_select)
            color_row.addWidget(dot)
        color_row.addStretch(1)
        accent_layout.addLayout(color_row)
        self.content_layout.addWidget(accent_card)

        # ── Wallpaper Picker ─────────────────────────────────────
        self.content_layout.addWidget(self._section_label("Wallpaper"))

        wp_grid = QWidget()
        wp_grid.setStyleSheet(f"background: transparent;")
        wp_layout = QHBoxLayout(wp_grid)
        wp_layout.setContentsMargins(0, 4, 0, 4)
        wp_layout.setSpacing(8)

        current_wp = self._current_settings.get("wallpaper", "wallpaper.jpg")

        # Add solid color wallpapers
        for color_hex, name in SOLID_WALLPAPERS:
            is_cur = (current_wp == color_hex)
            tile = WallpaperTile(color_hex, name, is_cur, theme)
            tile.selected.connect(self._on_wallpaper_select)
            wp_layout.addWidget(tile)

        wp_layout.addStretch(1)
        self.content_layout.addWidget(wp_grid)

        wp_label = QLabel("Tap a swatch to change wallpaper")
        wp_label.setFont(QFont("Segoe UI", 11))
        wp_label.setStyleSheet(f"color: {self.theme.muted}; background: transparent;")
        self.content_layout.addWidget(wp_label)

        # ── Personalisation ──────────────────────────────────────
        self.content_layout.addWidget(self._section_label("Personalisation"))

        # User name
        name_card = QFrame()
        name_card.setMinimumHeight(72)
        name_card.setStyleSheet(
            f"QFrame {{ background: {theme.surface}; border-radius: 8px; }}"
            f"QLabel {{ background: transparent; color: {theme.foreground.name()}; }}"
        )
        name_layout = QHBoxLayout(name_card)
        name_layout.setContentsMargins(14, 8, 14, 8)
        name_label = QLabel("User Name")
        name_label.setFont(QFont("Segoe UI", 15, QFont.Weight.Medium))
        name_layout.addWidget(name_label)
        name_layout.addStretch(1)
        self.name_input = QLineEdit(self._current_settings.get("user_name", "Ishant"))
        self.name_input.setFixedWidth(140)
        self.name_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.name_input.setFont(QFont("Segoe UI", 14))
        self.name_input.setStyleSheet(
            f"color: {theme.foreground.name()}; background: transparent; border: none;"
        )
        self.name_input.returnPressed.connect(self._on_name_change)
        self.name_input.editingFinished.connect(self._on_name_change)
        name_layout.addWidget(self.name_input)
        self.content_layout.addWidget(name_card)

        # ── Connectivity ─────────────────────────────────────────
        self.content_layout.addWidget(self._section_label("Connectivity"))

        wifi_card = self._setting_row("WiFi")
        wifi_val = QLabel("Connected")
        wifi_val.setFont(QFont("Segoe UI", 13))
        wifi_val.setStyleSheet(f"color: {self.theme.muted}; background: transparent;")
        wifi_card.layout().addWidget(wifi_val)
        self.content_layout.addWidget(wifi_card)

        bt_card = self._setting_row("Bluetooth")
        bt_toggle = ToggleSwitch(False, theme.accent)
        bt_card.layout().addWidget(bt_toggle)
        self.content_layout.addWidget(bt_card)

        airplane_card = self._setting_row("Airplane Mode")
        airplane_toggle = ToggleSwitch(False, theme.accent)
        airplane_card.layout().addWidget(airplane_toggle)
        self.content_layout.addWidget(airplane_card)

        # ── Sound ────────────────────────────────────────────────
        self.content_layout.addWidget(self._section_label("Sound"))

        ring_card = self._setting_row("Ringtone")
        ring_val = QLabel("Default")
        ring_val.setFont(QFont("Segoe UI", 13))
        ring_val.setStyleSheet(f"color: {self.theme.muted}; background: transparent;")
        ring_card.layout().addWidget(ring_val)
        self.content_layout.addWidget(ring_card)

        vibrate_card = self._setting_row("Vibrate")
        vibrate_toggle = ToggleSwitch(True, theme.accent)
        vibrate_card.layout().addWidget(vibrate_toggle)
        self.content_layout.addWidget(vibrate_card)

        # ── System ───────────────────────────────────────────────
        self.content_layout.addWidget(self._section_label("System"))

        self.add_card("Battery", "87% — Estimated 9h 20m remaining", 68)
        self.add_card("Storage", "12GB Free of 32GB", 68)

        about_card = self._setting_row("About Phone")
        about_val = QLabel("PhoneOS v1.0.0")
        about_val.setFont(QFont("Segoe UI", 13))
        about_val.setStyleSheet(f"color: {self.theme.muted}; background: transparent;")
        about_card.layout().addWidget(about_val)
        self.content_layout.addWidget(about_card)

        self.finish()

    def _section_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        label.setStyleSheet(f"color: {self._theme.accent.name()}; background: transparent; margin-top: 8px;")
        return label

    def _setting_row(self, label: str) -> QFrame:
        row = QFrame()
        row.setMinimumHeight(56)
        row.setStyleSheet(
            f"""
            QFrame {{
                background: {self._theme.surface};
                border-radius: 8px;
            }}
            QLabel {{
                background: transparent;
                color: {self._theme.foreground.name()};
            }}
            """
        )
        layout = QHBoxLayout(row)
        layout.setContentsMargins(14, 6, 14, 6)
        name = QLabel(label)
        name.setFont(QFont("Segoe UI", 15, QFont.Weight.Medium))
        layout.addWidget(name)
        layout.addStretch(1)
        return row

    def _load_settings(self) -> dict:
        if not SETTINGS_FILE.exists():
            return {"theme": "dark", "accent_color": "#0078D7", "user_name": "Ishant"}
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"theme": "dark", "accent_color": "#0078D7", "user_name": "Ishant"}

    def _save_settings(self) -> None:
        SETTINGS_FILE.write_text(
            json.dumps(self._current_settings, indent=2), encoding="utf-8"
        )
        self.settings_changed.emit()

    def _on_theme_toggle(self, is_dark: bool) -> None:
        self._current_settings["theme"] = "dark" if is_dark else "light"
        self._save_settings()

    def _on_accent_select(self, color_name: str) -> None:
        self._current_settings["accent_color"] = ACCENT_COLORS[color_name]
        self._save_settings()

    def _on_name_change(self) -> None:
        name = self.name_input.text().strip()
        if name:
            self._current_settings["user_name"] = name
            self._save_settings()

    def _on_wallpaper_select(self, path: str, name: str) -> None:
        self._current_settings["wallpaper"] = path
        self._save_settings()
