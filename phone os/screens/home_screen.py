"""
PhoneOS home screen.

Production-oriented PyQt6 implementation of a lightweight Metro-inspired home
experience for a Raspberry Pi phone. The screen uses generated placeholders
when app icon assets are not available.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import (
    QEasingCurve,
    QPoint,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QRect,
    QRectF,
    QTimer,
    Qt,
    pyqtSignal,
)
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from apps.base_app import AppTheme, load_current_theme
from apps.alarm_app import AlarmApp
from apps.app_store_app import AppStoreApp
from apps.battery_app import BatteryApp
from apps.browser_app import BrowserApp
from apps.calculator_app import CalculatorApp
from apps.calendar_app import CalendarApp
from apps.camera_app import CameraApp
from apps.clock_app import ClockApp
from apps.files_app import FilesApp
from apps.gallery_app import GalleryApp
from apps.messages_app import MessagesApp
from apps.music_app import MusicApp
from apps.phone_app import PhoneApp
from apps.settings_app import SettingsApp
from apps.storage_app import StorageApp
from apps.weather_app import WeatherApp


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
class HomeSettings:
    theme: str = "dark"
    accent_color: str = "#0078D7"
    user_name: str = "Ishant"
    wallpaper: str = ""


@dataclass(frozen=True)
class TileDefinition:
    name: str
    icon_name: str
    columns: int = 1
    rows: int = 1
    live_type: str = ""


def load_settings() -> HomeSettings:
    if not SETTINGS_FILE.exists():
        return HomeSettings()

    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return HomeSettings()

    accent = data.get("accent_color", HomeSettings.accent_color)
    if isinstance(accent, str) and accent.lower() in ACCENT_COLORS:
        accent = ACCENT_COLORS[accent.lower()]

    return HomeSettings(
        theme=str(data.get("theme", "dark")).lower(),
        accent_color=str(accent),
        user_name=str(data.get("user_name", "Ishant")),
        wallpaper=str(data.get("wallpaper", "")),
    )


def readable_text_color(background: QColor) -> str:
    brightness = (background.red() * 299 + background.green() * 587 + background.blue() * 114) / 1000
    return "#111111" if brightness > 155 else "#FFFFFF"


class PlaceholderIcon(QWidget):
    """Draws an icon placeholder if the real asset file is missing."""

    def __init__(self, label: str, icon_path: Path, accent: QColor, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.label = label
        self.icon_path = icon_path
        self.accent = accent
        self.pixmap = QPixmap(str(icon_path))
        self.setFixedSize(36, 36)

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        if not self.pixmap.isNull():
            painter.drawPixmap(self.rect(), self.pixmap)
            return

        # Placeholder asset location. Replace with real icon later:
        # assets/icons/<app>_placeholder.png
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 54))
        painter.drawRoundedRect(QRectF(1, 1, 34, 34), 6, 6)
        painter.setBrush(QColor(self.accent.red(), self.accent.green(), self.accent.blue(), 210))
        painter.drawEllipse(QRectF(8, 6, 20, 20))
        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        painter.drawText(self.rect().adjusted(0, 14, 0, 0), Qt.AlignmentFlag.AlignCenter, self.label[:1].upper())


class PhoneStatusBar(QWidget):
    """Compact status bar with placeholder hardware values."""

    def __init__(self, foreground: QColor, accent: QColor, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.foreground = foreground
        self.accent = accent
        self.setFixedHeight(34)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        self.time_label = QLabel()
        self.time_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium))
        self.time_label.setStyleSheet(f"color: {foreground.name()};")
        layout.addWidget(self.time_label)
        layout.addStretch(1)

        for text in ("WiFi", "LTE", "87%"):
            label = QLabel(text)
            label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
            label.setStyleSheet(f"color: {foreground.name()};")
            layout.addWidget(label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_time)
        self.timer.start(30_000)
        self._update_time()

    def _update_time(self) -> None:
        self.time_label.setText(datetime.now().strftime("%H:%M"))


class MetroTile(QFrame):
    """Touch-friendly Metro tile with lightweight press feedback."""

    clicked = pyqtSignal(str)

    def __init__(
        self,
        definition: TileDefinition,
        accent: QColor,
        foreground: QColor,
        icon_root: Path,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.definition = definition
        self.accent = accent
        self.foreground = foreground
        self._press_animation: QPropertyAnimation | None = None
        self._normal_geometry: QRect | None = None
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(80 * definition.columns, 80 * definition.rows)

        tile_color = self._tile_color(definition.name)
        self.tile_color = tile_color
        text_color = readable_text_color(tile_color)
        self.setStyleSheet(
            f"""
            QFrame {{
                background: {tile_color.name()};
                border-radius: 8px;
            }}
            QLabel {{
                color: {text_color};
                background: transparent;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        icon_path = icon_root / definition.icon_name
        self.icon = PlaceholderIcon(definition.name, icon_path, accent)
        layout.addWidget(self.icon, 0, Qt.AlignmentFlag.AlignLeft)

        layout.addStretch(1)
        self.primary_label = QLabel(definition.name)
        self.primary_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.primary_label.setWordWrap(True)
        layout.addWidget(self.primary_label)

        self.secondary_label = QLabel("")
        self.secondary_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Normal))
        self.secondary_label.setWordWrap(True)
        layout.addWidget(self.secondary_label)

    def _tile_color(self, name: str) -> QColor:
        colors = {
            "Phone": self.accent,
            "Messages": QColor("#00B7C3"),
            "Camera": QColor("#5C2D91"),
            "Gallery": QColor("#E81123"),
            "Browser": QColor("#0078D7"),
            "Music": QColor("#D83B01"),
            "Files": QColor("#107C10"),
            "Settings": QColor("#505050"),
            "Calculator": QColor("#498205"),
            "Weather": QColor("#0099BC"),
            "Calendar": QColor("#B4009E"),
            "Battery": QColor("#10893E"),
            "Storage": QColor("#8764B8"),
            "Clock": QColor("#004E8C"),
            "Apps": QColor("#2D7D9A"),
        }
        return colors.get(name, self.accent)

    def update_live_content(self) -> None:
        now = datetime.now()
        live_type = self.definition.live_type
        if live_type == "clock":
            self.primary_label.setText(now.strftime("%H:%M"))
            self.secondary_label.setText("Clock")
        elif live_type == "weather":
            self.primary_label.setText("32 C")
            self.secondary_label.setText("Sunny")
        elif live_type == "battery":
            self.primary_label.setText("Battery")
            self.secondary_label.setText("87%")
        elif live_type == "storage":
            self.primary_label.setText("Storage")
            self.secondary_label.setText("12GB Free")
        elif live_type == "calendar":
            self.primary_label.setText(str(now.day))
            self.secondary_label.setText(now.strftime("%A"))

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.button() == Qt.MouseButton.LeftButton:
            self._animate_press(True)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.button() == Qt.MouseButton.LeftButton:
            self._animate_press(False)
            if self.rect().contains(event.position().toPoint()):
                self.clicked.emit(self.definition.name)
        super().mouseReleaseEvent(event)

    def _animate_press(self, pressed: bool) -> None:
        if not self.isVisible() or self.width() < 10 or self.height() < 10:
            return

        if self._normal_geometry is None or not pressed:
            self._normal_geometry = self.geometry()

        start = self.geometry()
        if pressed:
            target = self._normal_geometry.adjusted(4, 4, -4, -4)
        else:
            target = self._normal_geometry

        animation = QPropertyAnimation(self, b"geometry", self)
        animation.setDuration(90 if pressed else 130)
        animation.setStartValue(start)
        animation.setEndValue(target)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.finished.connect(lambda: setattr(self, "_press_animation", None))
        self._press_animation = animation
        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


class QuickSettingsPanel(QWidget):
    """Swipe-down quick settings panel."""

    def __init__(self, accent: QColor, foreground: QColor, light_theme: bool, toggle_states: dict[str, bool], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._toggle_states = toggle_states
        self._accent = accent
        self._foreground = foreground
        bg = "rgba(245, 245, 245, 230)" if light_theme else "rgba(20, 20, 24, 230)"
        self.setStyleSheet(f"background: {bg}; border-bottom-left-radius: 16px; border-bottom-right-radius: 16px;")
        self.setFixedHeight(260)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 16)
        root.setSpacing(12)

        # Handle bar
        handle = QLabel("━")
        handle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        handle.setFont(QFont("Segoe UI", 10))
        handle.setStyleSheet(f"color: rgba({foreground.red()}, {foreground.green()}, {foreground.blue()}, 100); background: transparent;")
        root.addWidget(handle)

        # Quick toggle buttons
        toggles_row = QHBoxLayout()
        toggles_row.setSpacing(10)

        toggle_data = [
            ("📶", "WiFi"),
            ("📱", "BT"),
            ("✈️", "Flight"),
            ("🔦", "Flash"),
        ]

        for icon, label in toggle_data:
            btn_container = QVBoxLayout()
            btn_container.setSpacing(4)

            btn = QPushButton(icon)
            btn.setFixedSize(56, 56)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(QFont("Segoe UI Emoji", 20))
            btn._qs_label = label  # type: ignore[attr-defined]
            on = self._toggle_states.get(label, False)
            btn.setStyleSheet(self._toggle_style(on, accent, foreground))
            btn.clicked.connect(lambda checked=False, b=btn: self._on_toggle(b))
            btn_container.addWidget(btn, 0, Qt.AlignmentFlag.AlignCenter)

            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
            lbl.setStyleSheet(f"color: {foreground.name()}; background: transparent;")
            btn_container.addWidget(lbl)

            wrapper = QWidget()
            wrapper.setLayout(btn_container)
            toggles_row.addWidget(wrapper)

        toggles_row.addStretch(1)
        root.addLayout(toggles_row)

        # Brightness slider
        bright_row = QHBoxLayout()
        bright_row.setSpacing(8)
        sun_label = QLabel("☀️")
        sun_label.setFont(QFont("Segoe UI Emoji", 14))
        bright_row.addWidget(sun_label)

        brightness = QSlider(Qt.Orientation.Horizontal)
        brightness.setRange(0, 100)
        brightness.setValue(75)
        brightness.setStyleSheet(
            f"""
            QSlider::groove:horizontal {{
                height: 4px;
                background: rgba({foreground.red()}, {foreground.green()}, {foreground.blue()}, 60);
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {accent.name()};
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
            QSlider::sub-page:horizontal {{
                background: {accent.name()};
                border-radius: 2px;
            }}
            """
        )
        bright_row.addWidget(brightness, 1)
        root.addLayout(bright_row)

        # Volume slider
        vol_row = QHBoxLayout()
        vol_row.setSpacing(8)
        vol_label = QLabel("🔊")
        vol_label.setFont(QFont("Segoe UI Emoji", 14))
        vol_row.addWidget(vol_label)

        volume = QSlider(Qt.Orientation.Horizontal)
        volume.setRange(0, 100)
        volume.setValue(50)
        volume.setStyleSheet(brightness.styleSheet())
        vol_row.addWidget(volume, 1)
        root.addLayout(vol_row)

        # Bottom row: Settings shortcut + time
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 4, 0, 0)
        time_lbl = QLabel(datetime.now().strftime("%H:%M"))
        time_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        time_lbl.setStyleSheet(f"color: {foreground.name()}; background: transparent;")
        bottom_row.addWidget(time_lbl)
        bottom_row.addStretch(1)
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.setFont(QFont("Segoe UI", 11))
        settings_btn.setStyleSheet(
            f"""
            QPushButton {{
                color: {foreground.name()};
                background: rgba({foreground.red()}, {foreground.green()}, {foreground.blue()}, 40);
                border: none;
                border-radius: 12px;
                padding: 6px 12px;
            }}
            QPushButton:pressed {{
                background: rgba({foreground.red()}, {foreground.green()}, {foreground.blue()}, 80);
            }}
            """
        )
        bottom_row.addWidget(settings_btn)
        root.addLayout(bottom_row)

    @staticmethod
    def _toggle_style(on: bool, accent: QColor, fg: QColor) -> str:
        bg = accent.name() if on else "rgba(255,255,255,30)"
        return (
            f"""
            QPushButton {{
                color: {'#FFFFFF' if on else fg.name()};
                background: {bg};
                border: none;
                border-radius: 28px;
            }}
            QPushButton:pressed {{
                background: {accent.name()};
                color: #FFFFFF;
            }}
            """
        )

    def _on_toggle(self, btn: QPushButton) -> None:
        label = getattr(btn, "_qs_label", "")
        self._toggle_states[label] = not self._toggle_states.get(label, False)
        on = self._toggle_states[label]
        btn.setStyleSheet(self._toggle_style(on, self._accent, self._foreground))


class HomePage(QWidget):
    """Metro tile dashboard and launcher entry point."""

    tileActivated = pyqtSignal(str)

    def __init__(self, settings: HomeSettings, accent: QColor, light_theme: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = settings
        self.accent = accent
        self.light_theme = light_theme
        self.foreground = QColor("#111111" if light_theme else "#FFFFFF")
        self.background = QColor("#F4F4F4" if light_theme else "#101014")
        self.tiles: list[MetroTile] = []
        self.setStyleSheet(f"background: {self.background.name()};")

        self._qs_panel: QuickSettingsPanel | None = None
        self._qs_visible = False
        self._qs_animation: QPropertyAnimation | None = None
        self._press_start_y: float | None = None
        self._qs_toggle_states: dict[str, bool] = {"WiFi": True, "BT": False, "Flight": False, "Flash": False}

        self._build_ui()

        self.live_timer = QTimer(self)
        self.live_timer.timeout.connect(self.update_live_tiles)
        self.live_timer.start(1000)
        self.update_live_tiles()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 10, 20, 10)
        root.setSpacing(10)

        root.addWidget(PhoneStatusBar(self.foreground, self.accent))

        self._greeting_label = QLabel(self._greeting())
        self._greeting_label.setFont(QFont("Segoe UI Light", 28, QFont.Weight.Light))
        self._greeting_label.setStyleSheet(f"color: {self.foreground.name()};")
        root.addWidget(self._greeting_label)

        self.date_label = QLabel(datetime.now().strftime("%A, %d %B").replace(" 0", " "))
        self.date_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Normal))
        self.date_label.setStyleSheet(f"color: rgba({self.foreground.red()}, {self.foreground.green()}, {self.foreground.blue()}, 182);")
        root.addWidget(self.date_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        viewport = QWidget()
        viewport.setStyleSheet("background: transparent;")
        grid = QGridLayout(viewport)
        grid.setContentsMargins(0, 6, 0, 10)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)

        definitions = [
            TileDefinition("Phone", "phone_placeholder.png", 1, 1),
            TileDefinition("Messages", "messages_placeholder.png", 1, 1),
            TileDefinition("Camera", "camera_placeholder.png", 1, 1),
            TileDefinition("Gallery", "gallery_placeholder.png", 1, 1),
            TileDefinition("Browser", "browser_placeholder.png", 2, 1),
            TileDefinition("Weather", "weather_placeholder.png", 2, 1, "weather"),
            TileDefinition("Calendar", "calendar_placeholder.png", 1, 1, "calendar"),
            TileDefinition("Clock", "clock_placeholder.png", 1, 1, "clock"),
            TileDefinition("Music", "music_placeholder.png", 1, 1),
            TileDefinition("Files", "files_placeholder.png", 1, 1),
            TileDefinition("Battery", "battery_placeholder.png", 2, 1, "battery"),
            TileDefinition("Storage", "storage_placeholder.png", 2, 1, "storage"),
            TileDefinition("Calculator", "calculator_placeholder.png", 1, 1),
            TileDefinition("Settings", "settings_placeholder.png", 1, 1),
            TileDefinition("Apps", "apps_placeholder.png", 2, 1),
        ]

        row = 0
        col = 0
        icon_root = PROJECT_ROOT / "assets" / "icons"
        for definition in definitions:
            if col + definition.columns > 4:
                row += 1
                col = 0
            tile = MetroTile(definition, self.accent, self.foreground, icon_root)
            tile.clicked.connect(self.tileActivated)
            grid.addWidget(tile, row, col, definition.rows, definition.columns)
            self.tiles.append(tile)
            col += definition.columns
            if col >= 4:
                row += 1
                col = 0

        for column in range(4):
            grid.setColumnStretch(column, 1)
            grid.setColumnMinimumWidth(column, 80)

        scroll.setWidget(viewport)
        root.addWidget(scroll, 1)

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 4, 0, 0)
        bottom.addStretch(1)
        apps_button = QPushButton("All Apps")
        apps_button.setMinimumHeight(42)
        apps_button.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        apps_button.setStyleSheet(
            f"""
            QPushButton {{
                color: #FFFFFF;
                background: {self.accent.name()};
                border: none;
                border-radius: 8px;
                padding: 0 24px;
            }}
            QPushButton:pressed {{
                background: rgba({self.accent.red()}, {self.accent.green()}, {self.accent.blue()}, 170);
            }}
            """
        )
        apps_button.clicked.connect(lambda: self.tileActivated.emit("Apps"))
        bottom.addWidget(apps_button)
        root.addLayout(bottom)

    def _greeting(self) -> str:
        hour = datetime.now().hour
        if 5 <= hour < 12:
            prefix = "Good Morning"
        elif 12 <= hour < 18:
            prefix = "Good Afternoon"
        elif 18 <= hour < 22:
            prefix = "Good Evening"
        else:
            prefix = "Welcome Back"
        return f"{prefix}\n{self.settings.user_name}"

    def refresh_greeting(self, new_settings: HomeSettings) -> None:
        self.settings = new_settings
        self._greeting_label.setText(self._greeting())

    # ── Quick Settings panel (swipe down from top) ──────────────
    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_start_y = event.position().y()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._press_start_y is not None:
            dy = event.position().y() - self._press_start_y
            self._press_start_y = None
            # Swipe down from top 60px → open quick settings
            if not self._qs_visible and dy > 50 and event.position().y() < 80:
                self._show_quick_settings()
            elif self._qs_visible and dy < -30:
                self._hide_quick_settings()
        super().mouseReleaseEvent(event)

    def _show_quick_settings(self) -> None:
        if self._qs_visible:
            return
        self._qs_visible = True
        self._qs_panel = QuickSettingsPanel(self.accent, self.foreground, self.light_theme, self._qs_toggle_states, self)
        self._qs_panel.setGeometry(0, -270, self.width(), 270)
        self._qs_panel.show()
        self._qs_panel.raise_()

        # Connect settings button
        for btn in self._qs_panel.findChildren(QPushButton):
            if "Settings" in (btn.text() or ""):
                btn.clicked.connect(lambda: self._hide_and_open_settings())

        slide = QPropertyAnimation(self._qs_panel, b"pos", self)
        slide.setDuration(220)
        slide.setStartValue(QPoint(0, -270))
        slide.setEndValue(QPoint(0, 0))
        slide.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._qs_animation = slide
        slide.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _hide_quick_settings(self) -> None:
        if not self._qs_visible or self._qs_panel is None:
            return
        slide = QPropertyAnimation(self._qs_panel, b"pos", self)
        slide.setDuration(180)
        slide.setStartValue(QPoint(0, 0))
        slide.setEndValue(QPoint(0, -270))
        slide.setEasingCurve(QEasingCurve.Type.InCubic)

        def _cleanup() -> None:
            if self._qs_panel:
                self._qs_panel.deleteLater()
                self._qs_panel = None
            self._qs_visible = False
            self._qs_animation = None

        slide.finished.connect(_cleanup)
        self._qs_animation = slide
        slide.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _hide_and_open_settings(self) -> None:
        self._hide_quick_settings()
        QTimer.singleShot(200, lambda: self.tileActivated.emit("Settings"))

    def update_live_tiles(self) -> None:
        self.date_label.setText(datetime.now().strftime("%A, %d %B").replace(" 0", " "))
        for tile in self.tiles:
            tile.update_live_content()


class AppListPage(QWidget):
    """Windows Phone style alphabetical app list."""

    backRequested = pyqtSignal()
    appActivated = pyqtSignal(str)

    def __init__(self, accent: QColor, light_theme: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.accent = accent
        self.light_theme = light_theme
        self.foreground = QColor("#111111" if light_theme else "#FFFFFF")
        self.background = QColor("#F4F4F4" if light_theme else "#101014")
        self.apps = [
            "Alarm",
            "App Store",
            "Browser",
            "Calculator",
            "Calendar",
            "Camera",
            "Clock",
            "Files",
            "Gallery",
            "Messages",
            "Music",
            "Phone",
            "Settings",
            "Storage",
            "Weather",
        ]
        self.app_buttons: list[QPushButton] = []
        self.setStyleSheet(f"background: {self.background.name()};")
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 10, 20, 10)
        root.setSpacing(10)
        root.addWidget(PhoneStatusBar(self.foreground, self.accent))

        header = QHBoxLayout()
        back = QPushButton("<")
        back.setFixedSize(38, 38)
        back.setFont(QFont("Segoe UI", 24, QFont.Weight.Light))
        back.setStyleSheet(self._button_style(round_button=True))
        back.clicked.connect(self.backRequested)
        header.addWidget(back)

        title = QLabel("All Apps")
        title.setFont(QFont("Segoe UI Light", 28, QFont.Weight.Light))
        title.setStyleSheet(f"color: {self.foreground.name()};")
        header.addWidget(title)
        header.addStretch(1)
        root.addLayout(header)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search")
        self.search.setMinimumHeight(42)
        self.search.setFont(QFont("Segoe UI", 14))
        self.search.setStyleSheet(
            f"""
            QLineEdit {{
                color: {self.foreground.name()};
                background: {'#FFFFFF' if self.light_theme else '#202026'};
                border: 2px solid {self.accent.name()};
                border-radius: 8px;
                padding: 0 16px;
            }}
            """
        )
        self.search.textChanged.connect(self._filter_apps)
        root.addWidget(self.search)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(content)
        self.list_layout.setContentsMargins(0, 6, 0, 20)
        self.list_layout.setSpacing(8)
        self._populate_apps()
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

    def _button_style(self, round_button: bool = False) -> str:
        radius = 26 if round_button else 8
        return (
            f"QPushButton {{ color: #FFFFFF; background: {self.accent.name()}; "
            f"border: none; border-radius: {radius}px; }}"
            f"QPushButton:pressed {{ background: rgba({self.accent.red()}, {self.accent.green()}, {self.accent.blue()}, 170); }}"
        )

    def _populate_apps(self) -> None:
        current_letter = ""
        for app_name in sorted(self.apps):
            letter = app_name[0].upper()
            if letter != current_letter:
                current_letter = letter
                section = QLabel(letter)
                section.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
                section.setStyleSheet(f"color: {self.accent.name()}; margin-top: 12px;")
                self.list_layout.addWidget(section)

            button = QPushButton(app_name)
            button.setMinimumHeight(46)
            button.setFont(QFont("Segoe UI", 15, QFont.Weight.Normal))
            button.setStyleSheet(
                f"""
                QPushButton {{
                    color: {self.foreground.name()};
                    background: transparent;
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 18px;
                }}
                QPushButton:pressed {{
                    background: rgba({self.accent.red()}, {self.accent.green()}, {self.accent.blue()}, 90);
                }}
                """
            )
            button.clicked.connect(lambda checked=False, name=app_name: self.appActivated.emit(name))
            self.app_buttons.append(button)
            self.list_layout.addWidget(button)
        self.list_layout.addStretch(1)

    def _filter_apps(self, text: str) -> None:
        needle = text.strip().lower()
        for button in self.app_buttons:
            button.setVisible(needle in button.text().lower())


class HomeScreen(QWidget):
    """Main PhoneOS home surface with stacked navigation."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = load_settings()
        self.light_theme = self.settings.theme == "light"
        self.accent = QColor(self.settings.accent_color)
        if not self.accent.isValid():
            self.accent = QColor(ACCENT_COLORS["blue"])

        if parent is None:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setMinimumSize(360, 640)
        self.resize(390, 844)
        self._active_animation: QParallelAnimationGroup | QPropertyAnimation | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        root.addWidget(self.stack)

        self.home_page = HomePage(self.settings, self.accent, self.light_theme)
        self.app_list_page = AppListPage(self.accent, self.light_theme)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.app_list_page)

        self.home_page.tileActivated.connect(self._handle_tile)
        self.app_list_page.backRequested.connect(lambda: self._navigate_to(self.home_page, backward=True))
        self.app_list_page.appActivated.connect(self._handle_tile)

    _app_registry: dict[str, type] = {
        "Phone": PhoneApp,
        "Messages": MessagesApp,
        "Camera": CameraApp,
        "Gallery": GalleryApp,
        "Browser": BrowserApp,
        "Music": MusicApp,
        "Files": FilesApp,
        "Calculator": CalculatorApp,
        "Clock": ClockApp,
        "Calendar": CalendarApp,
        "Battery": BatteryApp,
        "Storage": StorageApp,
        "Weather": WeatherApp,
        "Alarm": AlarmApp,
        "App Store": AppStoreApp,
    }

    def _handle_tile(self, name: str) -> None:
        if name == "Apps":
            self._navigate_to(self.app_list_page)
        elif name == "Settings":
            self._show_app("Settings")
        elif name in self._app_registry:
            self._show_app(name)
        else:
            self._flash_current_page()

    def _show_app(self, name: str) -> None:
        app_class = self._app_registry.get(name)
        if app_class is None:
            self._flash_current_page()
            return

        theme = load_current_theme()
        app_widget = app_class(theme=theme, parent=self)
        self.stack.addWidget(app_widget)

        page_index = self.stack.indexOf(app_widget)

        width = max(1, self.stack.width())
        app_widget.setGeometry(self.stack.rect().translated(width, 0))
        app_widget.show()

        self.stack.setCurrentWidget(app_widget)

        slide = QPropertyAnimation(app_widget, b"pos", self)
        slide.setDuration(240)
        slide.setStartValue(QPoint(width, 0))
        slide.setEndValue(QPoint(0, 0))
        slide.setEasingCurve(QEasingCurve.Type.OutCubic)

        effect = QGraphicsOpacityEffect(app_widget)
        app_widget.setGraphicsEffect(effect)
        fade = QPropertyAnimation(effect, b"opacity", self)
        fade.setDuration(180)
        fade.setStartValue(0.3)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.Type.OutCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(slide)
        group.addAnimation(fade)
        group.finished.connect(lambda: app_widget.setGraphicsEffect(None))
        group.finished.connect(lambda: self.stack.setCurrentIndex(page_index))
        group.finished.connect(lambda: setattr(self, "_active_animation", None))
        self._active_animation = group
        group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)

        if hasattr(app_widget, "back_requested"):
            app_widget.back_requested.connect(lambda w=app_widget: self._close_app(w))

        # Live update: when SettingsApp saves, refresh home greeting
        if isinstance(app_widget, SettingsApp) and hasattr(app_widget, "settings_changed"):
            app_widget.settings_changed.connect(self._on_settings_changed)

    def _close_app(self, app_widget: QWidget) -> None:
        width = max(1, self.stack.width())

        home_index = self.stack.indexOf(self.home_page)

        slide = QPropertyAnimation(app_widget, b"pos", self)
        slide.setDuration(220)
        slide.setStartValue(QPoint(0, 0))
        slide.setEndValue(QPoint(width, 0))
        slide.setEasingCurve(QEasingCurve.Type.InCubic)

        effect = QGraphicsOpacityEffect(app_widget)
        app_widget.setGraphicsEffect(effect)
        fade = QPropertyAnimation(effect, b"opacity", self)
        fade.setDuration(180)
        fade.setStartValue(1.0)
        fade.setEndValue(0.3)
        fade.setEasingCurve(QEasingCurve.Type.InCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(slide)
        group.addAnimation(fade)

        def _cleanup() -> None:
            app_widget.setGraphicsEffect(None)
            self.stack.setCurrentIndex(home_index)
            self.stack.removeWidget(app_widget)
            app_widget.deleteLater()
            self._active_animation = None

        group.finished.connect(_cleanup)
        self._active_animation = group
        group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)
    def _navigate_to(self, page: QWidget, backward: bool = False) -> None:
        current = self.stack.currentWidget()
        if page is current:
            return

        width = max(1, self.stack.width())
        offset = -width if backward else width
        page_index = self.stack.indexOf(page)
        page.setGeometry(self.stack.rect().translated(offset, 0))
        page.show()

        self.stack.setCurrentWidget(page)
        slide = QPropertyAnimation(page, b"pos", self)
        slide.setDuration(240)
        slide.setStartValue(QPoint(offset, 0))
        slide.setEndValue(QPoint(0, 0))
        slide.setEasingCurve(QEasingCurve.Type.OutCubic)

        effect = QGraphicsOpacityEffect(page)
        page.setGraphicsEffect(effect)
        fade = QPropertyAnimation(effect, b"opacity", self)
        fade.setDuration(180)
        fade.setStartValue(0.3)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.Type.OutCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(slide)
        group.addAnimation(fade)
        group.finished.connect(lambda: page.setGraphicsEffect(None))
        group.finished.connect(lambda: self.stack.setCurrentIndex(page_index))
        group.finished.connect(lambda: setattr(self, "_active_animation", None))
        self._active_animation = group
        group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)

    def _on_settings_changed(self) -> None:
        """Re-read settings and refresh the home greeting live."""
        self.settings = load_settings()
        self.light_theme = self.settings.theme == "light"
        new_accent = QColor(self.settings.accent_color)
        if new_accent.isValid():
            self.accent = new_accent
        self.home_page.refresh_greeting(self.settings)

    def _flash_current_page(self) -> None:
        page = self.stack.currentWidget()
        effect = QGraphicsOpacityEffect(page)
        page.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setDuration(180)
        animation.setStartValue(0.72)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.finished.connect(lambda: page.setGraphicsEffect(None))
        animation.finished.connect(lambda: setattr(self, "_active_animation", None))
        self._active_animation = animation
        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override
        del event
        painter = QPainter(self)
        # Check if wallpaper is a solid color hex
        wp = self.settings.wallpaper if hasattr(self.settings, 'wallpaper') else ""
        if wp.startswith("#"):
            painter.fillRect(self.rect(), QColor(wp))
        else:
            gradient = QLinearGradient(0, 0, 0, self.height())
            if self.light_theme:
                gradient.setColorAt(0, QColor("#F4F4F4"))
                gradient.setColorAt(1, QColor("#E7E7E7"))
            else:
                gradient.setColorAt(0, QColor("#101014"))
                gradient.setColorAt(1, QColor("#050506"))
            painter.fillRect(self.rect(), gradient)


if __name__ == "__main__":
    app = QApplication([])
    home_screen = HomeScreen()
    home_screen.show()
    app.exec()
