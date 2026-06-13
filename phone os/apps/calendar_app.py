"""Calendar app with month grid view."""

from __future__ import annotations

import calendar
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from apps.base_app import AppTheme, PhoneAppScreen


class CalendarApp(PhoneAppScreen):
    def __init__(self, theme: AppTheme, parent=None) -> None:
        super().__init__("Calendar", theme, datetime.now().strftime("%B %Y"), parent)
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month

        # Month navigation
        nav = QHBoxLayout()
        prev_btn = QPushButton("<")
        prev_btn.setFixedSize(44, 44)
        prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        prev_btn.setFont(QFont("Segoe UI", 22, QFont.Weight.Light))
        prev_btn.setStyleSheet(
            f"QPushButton {{ color: {theme.foreground.name()}; background: transparent; border: none; border-radius: 22px; }}"
            f"QPushButton:pressed {{ background: {self.theme.muted}; }}"
        )
        prev_btn.clicked.connect(self._prev_month)
        nav.addWidget(prev_btn)

        self.month_label = QLabel(datetime.now().strftime("%B %Y"))
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.month_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.month_label.setStyleSheet(f"color: {theme.foreground.name()}; background: transparent;")
        nav.addWidget(self.month_label)

        next_btn = QPushButton(">")
        next_btn.setFixedSize(44, 44)
        next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        next_btn.setFont(QFont("Segoe UI", 22, QFont.Weight.Light))
        next_btn.setStyleSheet(
            f"QPushButton {{ color: {theme.foreground.name()}; background: transparent; border: none; border-radius: 22px; }}"
            f"QPushButton:pressed {{ background: {self.theme.muted}; }}"
        )
        next_btn.clicked.connect(self._next_month)
        nav.addWidget(next_btn)
        self.content_layout.addLayout(nav)

        # Day headers
        header_row = QHBoxLayout()
        for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            lbl = QLabel(day)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            lbl.setStyleSheet(f"color: {theme.accent.name()}; background: transparent; padding: 6px;")
            header_row.addWidget(lbl)
        self.content_layout.addLayout(header_row)

        # Grid
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(4)
        self.content_layout.addWidget(self.grid_widget)

        self._build_month()

        # Today info
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {self.theme.muted}; max-height: 1px;")
        self.content_layout.addWidget(sep)

        today = datetime.now()
        self.add_card(
            f"Today — {today.day}",
            f"{today.strftime('%A, %d %B %Y')}",
            90,
        )
        self.add_card("No events scheduled", "Your calendar is clear")
        self.add_action_button("New Event")
        self.finish()

    def _build_month(self) -> None:
        # Clear grid
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.month_label.setText(
            datetime(self.current_year, self.current_month, 1).strftime("%B %Y")
        )
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        today = datetime.now()
        is_current = self.current_year == today.year and self.current_month == today.month

        for row_idx, week in enumerate(cal):
            for col_idx, day in enumerate(week):
                if day == 0:
                    spacer = QLabel("")
                    spacer.setFixedSize(44, 44)
                    self.grid_layout.addWidget(spacer, row_idx, col_idx)
                    continue

                lbl = QLabel(str(day))
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl.setFixedSize(44, 44)
                lbl.setFont(QFont("Segoe UI", 15, QFont.Weight.Medium))

                if is_current and day == today.day:
                    lbl.setStyleSheet(
                        f"color: #FFFFFF; background: {self.theme.accent.name()}; "
                        f"border-radius: 22px; font-weight: bold;"
                    )
                else:
                    lbl.setStyleSheet(
                        f"color: {self.theme.foreground.name()}; background: transparent;"
                    )
                self.grid_layout.addWidget(lbl, row_idx, col_idx)

    def _prev_month(self) -> None:
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self._build_month()

    def _next_month(self) -> None:
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self._build_month()
