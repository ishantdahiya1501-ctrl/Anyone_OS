"""Weather app with weather display and forecast."""

from __future__ import annotations

from datetime import datetime, timedelta

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget, QFrame

from apps.base_app import AppTheme, PhoneAppScreen


WEATHER_CONDITIONS = [
    ("☀️", "Sunny", "Clear skies"),
    ("⛅", "Partly Cloudy", "Some cloud cover"),
    ("🌧️", "Light Rain", "Bring an umbrella"),
    ("🌤️", "Mostly Sunny", "Pleasant weather"),
    ("☁️", "Overcast", "Grey skies"),
]

FORECAST_DAYS = [
    ("Today", 32, "☀️", "Sunny"),
    ("Tomorrow", 29, "⛅", "Partly Cloudy"),
    ("Thursday", 27, "🌧️", "Light Rain"),
    ("Friday", 30, "🌤️", "Mostly Sunny"),
    ("Saturday", 28, "☁️", "Overcast"),
]


class WeatherIcon(QWidget):
    """Large weather icon display."""
    def __init__(self, emoji: str, temp: str, parent=None) -> None:
        super().__init__(parent)
        self.emoji = emoji
        self.temp = temp
        self.setFixedHeight(140)

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(QFont("Segoe UI Emoji", 52))
        painter.drawText(self.rect().adjusted(0, -10, 0, 0), Qt.AlignmentFlag.AlignCenter, self.emoji)

        painter.setFont(QFont("Segoe UI Light", 28, QFont.Weight.Light))
        painter.drawText(self.rect().adjusted(0, 50, 0, 0), Qt.AlignmentFlag.AlignCenter, self.temp)
        painter.end()


class ForecastCard(QFrame):
    """Single day forecast card."""
    def __init__(self, day: str, temp: int, icon: str, condition: str, theme: AppTheme, parent=None) -> None:
        super().__init__(parent)
        self.setFixedHeight(64)
        self.setStyleSheet(
            f"""
            QFrame {{
                background: {theme.surface};
                border-radius: 8px;
            }}
            QLabel {{ background: transparent; color: {theme.foreground.name()}; }}
            """
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)

        day_lbl = QLabel(day)
        day_lbl.setFont(QFont("Segoe UI", 15, QFont.Weight.Medium))
        day_lbl.setFixedWidth(90)
        layout.addWidget(day_lbl)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 20))
        icon_lbl.setFixedWidth(40)
        layout.addWidget(icon_lbl)

        cond_lbl = QLabel(condition)
        cond_lbl.setFont(QFont("Segoe UI", 14))
        cond_lbl.setStyleSheet(f"color: {self.theme.muted}; background: transparent;")
        layout.addWidget(cond_lbl, 1)

        temp_lbl = QLabel(f"{temp}°C")
        temp_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        temp_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(temp_lbl)


class WeatherApp(PhoneAppScreen):
    def __init__(self, theme: AppTheme, parent=None) -> None:
        super().__init__("Weather", theme, "Weather forecast", parent)

        current_temp = 32
        current_icon = "☀️"
        current_cond = "Sunny"
        feels_like = 34

        # Current weather card
        current_card = QFrame()
        current_card.setMinimumHeight(220)
        current_card.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba({theme.accent.red()}, {theme.accent.green()}, {theme.accent.blue()}, 200),
                    stop:1 rgba({theme.accent.red()}, {theme.accent.green()}, {theme.accent.blue()}, 80));
                border-radius: 14px;
            }}
            QLabel {{ background: transparent; }}
            """
        )
        curr_layout = QVBoxLayout(current_card)
        curr_layout.setContentsMargins(24, 16, 24, 16)
        curr_layout.setSpacing(4)

        # Location
        loc = QLabel("📍 PhoneOS City")
        loc.setFont(QFont("Segoe UI", 14))
        loc.setStyleSheet("color: rgba(255,255,255,180); background: transparent;")
        curr_layout.addWidget(loc)

        curr_layout.addWidget(WeatherIcon(current_icon, f"{current_temp}°C"))

        cond = QLabel(f"{current_cond}  •  Feels like {feels_like}°C")
        cond.setFont(QFont("Segoe UI", 16))
        cond.setStyleSheet("color: rgba(255,255,255,200); background: transparent;")
        curr_layout.addWidget(cond, 0, Qt.AlignmentFlag.AlignCenter)

        self.content_layout.addWidget(current_card)

        # Details row
        details = QHBoxLayout()
        details.setSpacing(8)
        for label, value in [("💧", "45%"), ("🌬️", "12 km/h"), ("👁️", "10 km")]:
            detail_card = QFrame()
            detail_card.setStyleSheet(
                f"QFrame {{ background: {theme.surface}; border-radius: 8px; }}"
                f"QLabel {{ background: transparent; color: {theme.foreground.name()}; }}"
            )
            detail_card.setFixedHeight(72)
            dc_layout = QVBoxLayout(detail_card)
            dc_layout.setContentsMargins(12, 8, 12, 8)
            dc_layout.setSpacing(2)
            icon = QLabel(label)
            icon.setFont(QFont("Segoe UI Emoji", 18))
            dc_layout.addWidget(icon, 0, Qt.AlignmentFlag.AlignCenter)
            val = QLabel(value)
            val.setFont(QFont("Segoe UI", 13))
            val.setStyleSheet(f"color: {self.theme.muted}; background: transparent;")
            dc_layout.addWidget(val, 0, Qt.AlignmentFlag.AlignCenter)
            details.addWidget(detail_card)
        self.content_layout.addLayout(details)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {self.theme.muted}; max-height: 1px;")
        self.content_layout.addWidget(sep)

        # 5-day forecast
        forecast_title = QLabel("5-Day Forecast")
        forecast_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        forecast_title.setStyleSheet(f"color: {theme.foreground.name()}; background: transparent;")
        self.content_layout.addWidget(forecast_title)

        for day, temp, icon, cond in FORECAST_DAYS:
            card = ForecastCard(day, temp, icon, cond, theme)
            self.content_layout.addWidget(card)

        self.finish()
