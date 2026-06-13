"""
PhoneOS lock screen.

A lightweight, touch-first PyQt6 lock screen inspired by the clean typography
and high-contrast layout principles of Windows Phone, implemented as original
PhoneOS UI.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import (
    QEasingCurve,
    QEvent,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    QRectF,
    QTimer,
    Qt,
    pyqtProperty,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPen,
    QPixmap,
)
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
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
class LockScreenSettings:
    theme: str = "dark"
    accent_color: str = "#0078D7"
    wallpaper: str = "wallpaper.jpg"


class StatusIcons(QWidget):
    """Small custom-painted network and battery indicators."""

    def __init__(self, accent: QColor, foreground: QColor, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.accent = accent
        self.foreground = foreground
        self.battery_percent = 84
        self.setFixedHeight(34)
        self.setMinimumWidth(226)

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(self.foreground, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))

        x = 4
        y = self.height() / 2
        self._draw_wifi(painter, x, y)
        x += 44
        self._draw_signal(painter, x, y)
        x += 50
        self._draw_battery(painter, x, y)

        painter.setPen(self.foreground)
        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        painter.drawText(int(x + 48), 0, 54, self.height(), Qt.AlignmentFlag.AlignVCenter, f"{self.battery_percent}%")

    def _draw_wifi(self, painter: QPainter, x: float, y: float) -> None:
        for index, width in enumerate((26, 18, 10)):
            rect = QRectF(x + (26 - width) / 2, y - 14 + index * 6, width, width)
            painter.drawArc(rect, 40 * 16, 100 * 16)
        painter.setBrush(self.foreground)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(x + 12, y + 8, 4, 4))
        painter.setPen(QPen(self.foreground, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))

    def _draw_signal(self, painter: QPainter, x: float, y: float) -> None:
        painter.setBrush(self.foreground)
        painter.setPen(Qt.PenStyle.NoPen)
        for index, height in enumerate((6, 11, 16, 21)):
            painter.drawRoundedRect(QRectF(x + index * 8, y + 12 - height, 5, height), 1.5, 1.5)
        painter.setPen(QPen(self.foreground, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))

    def _draw_battery(self, painter: QPainter, x: float, y: float) -> None:
        outline = QRectF(x, y - 10, 36, 20)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(outline, 4, 4)
        painter.drawRoundedRect(QRectF(x + 38, y - 5, 4, 10), 1.5, 1.5)

        fill_width = max(3, 30 * self.battery_percent / 100)
        painter.setBrush(self.accent if self.battery_percent > 20 else QColor("#E81123"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QRectF(x + 3, y - 7, fill_width, 14), 2.5, 2.5)
        painter.setPen(QPen(self.foreground, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))


class NotificationCard(QFrame):
    """Compact translucent notification summary card."""

    def __init__(self, text: str, accent: QColor, light_theme: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        background = "rgba(255, 255, 255, 172)" if light_theme else "rgba(10, 10, 12, 138)"
        foreground = "#101010" if light_theme else "#FFFFFF"
        self.setStyleSheet(
            f"""
            QFrame {{
                background: {background};
                border-left: 4px solid {accent.name()};
                border-radius: 8px;
            }}
            QLabel {{
                color: {foreground};
                background: transparent;
                border: none;
                font-size: 18px;
                font-weight: 500;
            }}
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 10, 18, 10)
        label = QLabel(text)
        label.setWordWrap(False)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(label)


class UnlockIndicator(QWidget):
    """Bottom swipe affordance with a gentle pulsing fade."""

    def __init__(self, accent: QColor, foreground: QColor, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.accent = accent
        self.foreground = foreground
        self.setFixedHeight(96)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.58)
        self.setGraphicsEffect(self.opacity_effect)

        self.pulse = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        self.pulse.setDuration(1800)
        self.pulse.setStartValue(0.42)
        self.pulse.setEndValue(0.92)
        self.pulse.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.pulse.setLoopCount(-1)
        self.pulse.start()

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() / 2
        painter.setPen(QPen(self.accent, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(QPoint(int(center_x - 15), 22), QPoint(int(center_x), 8))
        painter.drawLine(QPoint(int(center_x + 15), 22), QPoint(int(center_x), 8))

        painter.setPen(self.foreground)
        painter.setFont(QFont("Segoe UI", 17, QFont.Weight.Medium))
        painter.drawText(self.rect().adjusted(0, 32, 0, 0), Qt.AlignmentFlag.AlignHCenter, "Swipe up to unlock")


class PinPanel(QWidget):
    """Touch-friendly temporary PIN entry panel."""

    pinAccepted = pyqtSignal()

    def __init__(self, accent: QColor, foreground: QColor, light_theme: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.expected_pin = "1234"
        self.entered_pin = ""
        self.accent = accent
        self.foreground = foreground
        self.light_theme = light_theme
        self._active_animation: QPropertyAnimation | None = None

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        scrim = "rgba(245, 245, 245, 216)" if light_theme else "rgba(0, 0, 0, 216)"
        self.setStyleSheet(f"PinPanel {{ background: {scrim}; }}")
        self._build_ui()
        self.hide()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 40, 30, 30)
        root.setSpacing(18)
        root.addStretch(1)

        title = QLabel("Enter PIN")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Light))
        title.setStyleSheet(f"color: {self.foreground.name()}; background: transparent;")
        root.addWidget(title)

        subtitle = QLabel("Temporary PIN: 1234")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        subtitle.setFont(QFont("Segoe UI", 12, QFont.Weight.Normal))
        subtitle.setStyleSheet(f"color: rgba({self.foreground.red()}, {self.foreground.green()}, {self.foreground.blue()}, 166);")
        root.addWidget(subtitle)

        self.dots_label = QLabel("○ ○ ○ ○")
        self.dots_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.dots_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Normal))
        self.dots_label.setStyleSheet(f"color: {self.accent.name()}; background: transparent;")
        root.addWidget(self.dots_label)

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.error_label.setFixedHeight(26)
        self.error_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Normal))
        self.error_label.setStyleSheet("color: #E81123; background: transparent;")
        root.addWidget(self.error_label)

        keypad = QGridLayout()
        keypad.setHorizontalSpacing(16)
        keypad.setVerticalSpacing(16)
        for index, text in enumerate(("1", "2", "3", "4", "5", "6", "7", "8", "9")):
            keypad.addWidget(self._make_key(text), index // 3, index % 3)
        keypad.addWidget(self._make_key("⌫"), 3, 0)
        keypad.addWidget(self._make_key("0"), 3, 1)
        keypad.addWidget(self._make_key("OK"), 3, 2)
        root.addLayout(keypad)
        root.addStretch(2)

    def _make_key(self, text: str) -> QPushButton:
        button = QPushButton(text)
        button.setMinimumSize(72, 56)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFont(QFont("Segoe UI", 18 if text.isdigit() else 14, QFont.Weight.Medium))
        background = "rgba(255, 255, 255, 148)" if self.light_theme else "rgba(255, 255, 255, 34)"
        pressed = self.accent.name()
        button.setStyleSheet(
            f"""
            QPushButton {{
                color: {self.foreground.name()};
                background: {background};
                border: 1px solid rgba(255, 255, 255, 36);
                border-radius: 8px;
            }}
            QPushButton:pressed {{
                background: {pressed};
            }}
            """
        )
        button.clicked.connect(lambda checked=False, value=text: self._handle_key(value))
        return button

    def _handle_key(self, value: str) -> None:
        self.error_label.setText("")
        if value == "⌫":
            self.entered_pin = self.entered_pin[:-1]
        elif value == "OK":
            self._check_pin()
            return
        elif len(self.entered_pin) < 4:
            self.entered_pin += value

        self._update_dots()
        if len(self.entered_pin) == 4:
            self._check_pin()

    def _update_dots(self) -> None:
        filled = "● " * len(self.entered_pin)
        empty = "○ " * (4 - len(self.entered_pin))
        self.dots_label.setText((filled + empty).strip())

    def _check_pin(self) -> None:
        if self.entered_pin == self.expected_pin:
            self.pinAccepted.emit()
            return

        self.entered_pin = ""
        self._update_dots()
        self.error_label.setText("Incorrect PIN")
        self._shake()

    def _shake(self) -> None:
        start_pos = self.pos()
        animation = QPropertyAnimation(self, b"pos", self)
        animation.setDuration(150)
        animation.setStartValue(start_pos + QPoint(-10, 0))
        animation.setKeyValueAt(0.5, start_pos + QPoint(10, 0))
        animation.setEndValue(start_pos)
        animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        animation.finished.connect(lambda: setattr(self, "_active_animation", None))
        self._active_animation = animation
        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def reset(self) -> None:
        self.entered_pin = ""
        self.error_label.setText("")
        self._update_dots()


class LockScreen(QWidget):
    """Fullscreen PhoneOS lock screen widget."""

    unlocked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = self._load_settings()
        self.theme_is_light = self.settings.theme.lower() == "light"
        self.accent = QColor(self.settings.accent_color)
        if not self.accent.isValid():
            self.accent = QColor(ACCENT_COLORS["blue"])

        self.foreground = QColor("#111111" if self.theme_is_light else "#FFFFFF")
        self.secondary = QColor(32, 32, 32, 210) if self.theme_is_light else QColor(255, 255, 255, 178)
        self.wallpaper = self._load_wallpaper(self.settings.wallpaper)

        self.press_pos: QPoint | None = None
        self.current_drag = 0
        self.unlocking = False
        self.unlock_threshold = 210
        self._screen_opacity = 1.0
        self._active_animation: QParallelAnimationGroup | None = None

        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setMouseTracking(False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.content_opacity = QGraphicsOpacityEffect(self)
        self.content_opacity.setOpacity(1.0)

        self._build_ui()
        self.pin_panel = PinPanel(self.accent, self.foreground, self.theme_is_light, self)
        self.pin_panel.pinAccepted.connect(self._animate_unlock)
        self._start_clock()

    def _get_screen_opacity(self) -> float:
        return self._screen_opacity

    def _set_screen_opacity(self, opacity: float) -> None:
        self._screen_opacity = max(0.0, min(1.0, opacity))
        self.update()

    screenOpacity = pyqtProperty(float, fget=_get_screen_opacity, fset=_set_screen_opacity)

    def _load_settings(self) -> LockScreenSettings:
        if not SETTINGS_FILE.exists():
            return LockScreenSettings()

        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return LockScreenSettings()

        accent = data.get("accent_color", LockScreenSettings.accent_color)
        if isinstance(accent, str) and accent.lower() in ACCENT_COLORS:
            accent = ACCENT_COLORS[accent.lower()]

        return LockScreenSettings(
            theme=str(data.get("theme", "dark")).lower(),
            accent_color=str(accent),
            wallpaper=str(data.get("wallpaper", "wallpaper.jpg")),
        )

    def _load_wallpaper(self, configured_path: str) -> QPixmap:
        # Support solid color hex values from wallpaper picker
        if configured_path.startswith("#"):
            fallback = QPixmap(390, 844)
            fallback.fill(QColor(configured_path))
            return fallback

        candidates = [
            PROJECT_ROOT / configured_path,
            PROJECT_ROOT / "wallper.jpg",
            PROJECT_ROOT / "wallpaper.jpg",
            PROJECT_ROOT / "wallpapers" / "default.jpg",
        ]

        for path in candidates:
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                return pixmap

        fallback = QPixmap(390, 844)
        fallback.fill(QColor("#111111"))
        return fallback

    def _build_ui(self) -> None:
        self.content = QWidget(self)
        self.content.setGraphicsEffect(self.content_opacity)
        self.content.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        root = QVBoxLayout(self.content)
        root.setContentsMargins(28, 16, 28, 28)
        root.setSpacing(0)

        top = QHBoxLayout()
        top.addStretch(1)
        top.addWidget(StatusIcons(self.accent, self.foreground))
        root.addLayout(top)

        root.addSpacing(60)

        self.time_label = QLabel()
        self.time_label.setStyleSheet(f"color: {self.foreground.name()}; background: transparent;")
        self.time_label.setFont(QFont("Segoe UI Light", 72, QFont.Weight.Light))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        root.addWidget(self.time_label)

        self.day_label = QLabel()
        self.day_label.setStyleSheet(f"color: rgba({self.foreground.red()}, {self.foreground.green()}, {self.foreground.blue()}, 222);")
        self.day_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Normal))
        root.addWidget(self.day_label)

        self.date_label = QLabel()
        self.date_label.setStyleSheet(f"color: rgba({self.foreground.red()}, {self.foreground.green()}, {self.foreground.blue()}, 194);")
        self.date_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Normal))
        root.addWidget(self.date_label)

        root.addStretch(1)

        cards = QWidget()
        cards.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        cards_layout = QVBoxLayout(cards)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(10)
        for text in ("3 unread messages", "1 missed call", "Weather update"):
            cards_layout.addWidget(NotificationCard(text, self.accent, self.theme_is_light))
        root.addWidget(cards)

        root.addSpacing(36)
        root.addWidget(UnlockIndicator(self.accent, self.foreground))

        self._update_time()

    def _start_clock(self) -> None:
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_time)
        self.clock_timer.start(30_000)
        self._update_time()

    def _update_time(self) -> None:
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M"))
        self.day_label.setText(now.strftime("%A"))
        self.date_label.setText(f"{now.day} {now.strftime('%B')}")

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        self.content.setGeometry(self.rect().translated(0, self.current_drag))
        self.pin_panel.setGeometry(self.rect())

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setOpacity(self._screen_opacity)

        self._paint_wallpaper(painter)
        self._paint_overlay(painter)

    def _paint_wallpaper(self, painter: QPainter) -> None:
        if self.wallpaper.isNull():
            painter.fillRect(self.rect(), QColor("#111111"))
            return

        scaled = self.wallpaper.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)

    def _paint_overlay(self, painter: QPainter) -> None:
        gradient = QLinearGradient(0, 0, 0, self.height())
        if self.theme_is_light:
            gradient.setColorAt(0.0, QColor(255, 255, 255, 74))
            gradient.setColorAt(0.45, QColor(255, 255, 255, 38))
            gradient.setColorAt(1.0, QColor(255, 255, 255, 132))
        else:
            gradient.setColorAt(0.0, QColor(0, 0, 0, 96))
            gradient.setColorAt(0.48, QColor(0, 0, 0, 60))
            gradient.setColorAt(1.0, QColor(0, 0, 0, 178))
        painter.fillRect(self.rect(), gradient)

    def event(self, event) -> bool:
        if event.type() == QEvent.Type.TouchBegin:
            points = event.points()
            if points:
                self._begin_drag(points[0].position().toPoint())
                event.accept()
                return True

        if event.type() == QEvent.Type.TouchUpdate:
            points = event.points()
            if points:
                self._update_drag(points[0].position().toPoint())
                event.accept()
                return True

        if event.type() == QEvent.Type.TouchEnd:
            self._finish_drag()
            event.accept()
            return True

        return super().event(event)

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.button() == Qt.MouseButton.LeftButton:
            self._begin_drag(event.position().toPoint())

    def mouseMoveEvent(self, event) -> None:  # noqa: N802 - Qt override
        if self.press_pos is not None:
            self._update_drag(event.position().toPoint())

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.button() == Qt.MouseButton.LeftButton:
            self._finish_drag()

    def _begin_drag(self, pos: QPoint) -> None:
        if self.unlocking:
            return
        self.press_pos = pos
        self.current_drag = 0

    def _update_drag(self, pos: QPoint) -> None:
        if self.press_pos is None or self.unlocking:
            return

        delta_y = pos.y() - self.press_pos.y()
        self.current_drag = min(0, max(-280, int(delta_y * 0.72)))
        self.content.move(0, self.current_drag)
        self.content_opacity.setOpacity(max(0.42, 1.0 - abs(self.current_drag) / 390))

    def _finish_drag(self) -> None:
        if self.press_pos is None or self.unlocking:
            return

        should_unlock = abs(self.current_drag) >= self.unlock_threshold
        self.press_pos = None

        if should_unlock:
            self._show_pin_panel()
        else:
            self._animate_restore()

    def _show_pin_panel(self) -> None:
        self.unlocking = True
        self.pin_panel.reset()
        self.pin_panel.setGeometry(self.rect().translated(0, self.height()))
        self.pin_panel.show()
        self.pin_panel.raise_()

        panel_slide = QPropertyAnimation(self.pin_panel, b"pos", self)
        panel_slide.setDuration(280)
        panel_slide.setStartValue(QPoint(0, self.height()))
        panel_slide.setEndValue(QPoint(0, 0))
        panel_slide.setEasingCurve(QEasingCurve.Type.OutCubic)

        content_slide = QPropertyAnimation(self.content, b"pos", self)
        content_slide.setDuration(280)
        content_slide.setStartValue(self.content.pos())
        content_slide.setEndValue(QPoint(0, -80))
        content_slide.setEasingCurve(QEasingCurve.Type.OutCubic)

        fade = QPropertyAnimation(self.content_opacity, b"opacity", self)
        fade.setDuration(240)
        fade.setStartValue(self.content_opacity.opacity())
        fade.setEndValue(0.0)
        fade.setEasingCurve(QEasingCurve.Type.OutCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(panel_slide)
        group.addAnimation(content_slide)
        group.addAnimation(fade)
        group.finished.connect(lambda: setattr(self, "current_drag", 0))
        group.finished.connect(lambda: setattr(self, "unlocking", False))
        group.finished.connect(self._clear_animation)
        self._active_animation = group
        group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)

    def _animate_restore(self) -> None:
        slide = QPropertyAnimation(self.content, b"pos", self)
        slide.setDuration(220)
        slide.setStartValue(self.content.pos())
        slide.setEndValue(QPoint(0, 0))
        slide.setEasingCurve(QEasingCurve.Type.OutCubic)

        fade = QPropertyAnimation(self.content_opacity, b"opacity", self)
        fade.setDuration(180)
        fade.setStartValue(self.content_opacity.opacity())
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.Type.OutCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(slide)
        group.addAnimation(fade)
        group.finished.connect(lambda: setattr(self, "current_drag", 0))
        group.finished.connect(self._clear_animation)
        self._active_animation = group
        group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)

    def _animate_unlock(self) -> None:
        self.unlocking = True

        slide = QPropertyAnimation(self.content, b"pos", self)
        slide.setDuration(360)
        slide.setStartValue(self.content.pos())
        slide.setEndValue(QPoint(0, -self.height()))
        slide.setEasingCurve(QEasingCurve.Type.InCubic)

        fade = QPropertyAnimation(self.content_opacity, b"opacity", self)
        fade.setDuration(280)
        fade.setStartValue(self.content_opacity.opacity())
        fade.setEndValue(0.0)
        fade.setEasingCurve(QEasingCurve.Type.InOutSine)

        screen_fade = QPropertyAnimation(self, b"screenOpacity", self)
        screen_fade.setDuration(360)
        screen_fade.setStartValue(self._screen_opacity)
        screen_fade.setEndValue(0.0)
        screen_fade.setEasingCurve(QEasingCurve.Type.InOutSine)

        group = QParallelAnimationGroup(self)
        group.addAnimation(slide)
        group.addAnimation(fade)
        group.addAnimation(screen_fade)

        if self.pin_panel.isVisible():
            pin_effect = QGraphicsOpacityEffect(self.pin_panel)
            pin_effect.setOpacity(1.0)
            self.pin_panel.setGraphicsEffect(pin_effect)

            pin_slide = QPropertyAnimation(self.pin_panel, b"pos", self)
            pin_slide.setDuration(360)
            pin_slide.setStartValue(self.pin_panel.pos())
            pin_slide.setEndValue(QPoint(0, -self.height()))
            pin_slide.setEasingCurve(QEasingCurve.Type.InCubic)

            pin_fade = QPropertyAnimation(pin_effect, b"opacity", self)
            pin_fade.setDuration(260)
            pin_fade.setStartValue(1.0)
            pin_fade.setEndValue(0.0)
            pin_fade.setEasingCurve(QEasingCurve.Type.InOutSine)

            group.addAnimation(pin_slide)
            group.addAnimation(pin_fade)

        group.finished.connect(self._emit_unlocked)
        group.finished.connect(self._clear_animation)
        self._active_animation = group
        group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)

    def _emit_unlocked(self) -> None:
        self.unlocked.emit()

    def _clear_animation(self) -> None:
        self._active_animation = None


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(PROJECT_ROOT))
    from main import main

    main()
