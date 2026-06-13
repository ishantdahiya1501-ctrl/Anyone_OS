"""PhoneOS application entry point."""

from __future__ import annotations

import traceback
import sys
from pathlib import Path

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QGraphicsOpacityEffect, QStackedWidget, QVBoxLayout, QWidget

from screens.home_screen import HomeScreen
from screens.lock_screen import LockScreen


ERROR_LOG = Path(__file__).resolve().parent / "phoneos_error.log"

# Phone dimensions — looks like a real phone on any screen
PHONE_WIDTH = 390
PHONE_HEIGHT = 844


def log_exception(exc_type, exc_value, exc_traceback) -> None:
    message = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    ERROR_LOG.write_text(message, encoding="utf-8")
    print(message, file=sys.stderr)


class PhoneOSWindow(QWidget):
    """Single phone-sized shell that switches from lock to home."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Window
        )
        self.setFixedSize(PHONE_WIDTH, PHONE_HEIGHT)
        self.setWindowTitle("PhoneOS")

        # Outer frame to simulate phone bezel
        self.outer = QVBoxLayout(self)
        self.outer.setContentsMargins(0, 0, 0, 0)
        self.outer.setSpacing(0)

        # Status bar placeholder at top
        self._build_status_bar()

        self.stack = QStackedWidget()
        self.outer.addWidget(self.stack, 1)

        self.lock_screen = LockScreen(self)
        self.home_screen: HomeScreen | None = None
        self.stack.addWidget(self.lock_screen)
        self.lock_screen.unlocked.connect(self.show_home_screen)

        self._active_animation: QPropertyAnimation | None = None

    def _build_status_bar(self) -> None:
        from PyQt6.QtWidgets import QHBoxLayout, QLabel
        bar = QWidget()
        bar.setFixedHeight(28)
        bar.setStyleSheet("background: #000000; border-top-left-radius: 16px; border-top-right-radius: 16px;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)
        notch = QLabel("PhoneOS")
        notch.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        notch.setStyleSheet("color: #888888; background: transparent;")
        layout.addWidget(notch, 0, Qt.AlignmentFlag.AlignCenter)
        self.outer.addWidget(bar)

    def show_home_screen(self) -> None:
        try:
            if self.home_screen is None:
                self.home_screen = HomeScreen(self)
                self.stack.addWidget(self.home_screen)

            self.stack.setCurrentWidget(self.home_screen)
            self.home_screen.setFocus()
            self._fade_in(self.home_screen)
        except Exception:
            ERROR_LOG.write_text(traceback.format_exc(), encoding="utf-8")
            raise

    def _fade_in(self, widget: QWidget) -> None:
        effect = QGraphicsOpacityEffect(widget)
        effect.setOpacity(0.0)
        widget.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setDuration(220)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.finished.connect(lambda: widget.setGraphicsEffect(None))
        animation.finished.connect(lambda: setattr(self, "_active_animation", None))
        self._active_animation = animation
        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


def main() -> None:
    sys.excepthook = log_exception
    app = QApplication([])
    app.setFont(QFont("Segoe UI", 10))

    window = PhoneOSWindow()

    # Center on screen
    screen = app.primaryScreen()
    if screen:
        geo = screen.geometry()
        x = (geo.width() - PHONE_WIDTH) // 2
        y = (geo.height() - PHONE_HEIGHT) // 2
        window.move(max(0, x), max(0, y))

    window.show()
    app.exec()


if __name__ == "__main__":
    main()
