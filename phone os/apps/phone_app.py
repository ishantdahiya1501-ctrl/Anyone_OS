"""Phone app with working dial pad."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, QFrame

from apps.base_app import AppTheme, PhoneAppScreen


class PhoneApp(PhoneAppScreen):
    def __init__(self, theme: AppTheme, parent=None) -> None:
        super().__init__("Phone", theme, "Dialer", parent)
        self.number = ""

        # Number display
        self.display = QLabel("")
        self.display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display.setMinimumHeight(80)
        self.display.setFont(QFont("Segoe UI Light", 38))
        self.display.setStyleSheet(
            f"color: {theme.foreground.name()}; background: {theme.surface}; "
            f"border-radius: 8px; padding: 0 18px;"
        )
        self.content_layout.addWidget(self.display)

        # Dial pad
        pad = QWidget()
        grid = QGridLayout(pad)
        grid.setSpacing(10)

        keys = [
            ("1", ""), ("2", "ABC"), ("3", "DEF"),
            ("4", "GHI"), ("5", "JKL"), ("6", "MNO"),
            ("7", "PQRS"), ("8", "TUV"), ("9", "WXYZ"),
            ("*", ""), ("0", "+"), ("#", ""),
        ]

        for i, (num, letters) in enumerate(keys):
            row, col = i // 3, i % 3
            btn_container = QVBoxLayout()
            btn_container.setSpacing(0)

            num_btn = QPushButton(num)
            num_btn.setMinimumSize(88, 64)
            num_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            num_btn.setFont(QFont("Segoe UI", 26, QFont.Weight.Light))
            num_btn.setStyleSheet(
                f"""
                QPushButton {{
                    color: {theme.foreground.name()};
                    background: {theme.surface};
                    border: none;
                    border-radius: 32px;
                }}
                QPushButton:pressed {{
                    background: {self.theme.muted};
                }}
                """
            )
            num_btn.clicked.connect(lambda checked=False, n=num: self._add_digit(n))
            btn_container.addWidget(num_btn)

            if letters:
                letter_lbl = QLabel(letters)
                letter_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                letter_lbl.setFont(QFont("Segoe UI", 10))
                letter_lbl.setStyleSheet(f"color: {self.theme.muted}; background: transparent;")
                btn_container.addWidget(letter_lbl)

            wrapper = QWidget()
            wrapper.setLayout(btn_container)
            grid.addWidget(wrapper, row, col)

        self.content_layout.addWidget(pad)

        # Call and backspace buttons
        ctrl = QHBoxLayout()
        ctrl.setSpacing(16)

        backspace_btn = QPushButton("⌫")
        backspace_btn.setFixedSize(64, 64)
        backspace_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        backspace_btn.setFont(QFont("Segoe UI", 22))
        backspace_btn.setStyleSheet(
            f"QPushButton {{ color: {theme.foreground.name()}; background: transparent; border: none; border-radius: 32px; }}"
            f"QPushButton:pressed {{ background: {self.theme.muted}; }}"
        )
        backspace_btn.clicked.connect(self._backspace)
        ctrl.addWidget(backspace_btn)

        call_btn = QPushButton("📞")
        call_btn.setFixedSize(80, 80)
        call_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        call_btn.setFont(QFont("Segoe UI", 28))
        call_btn.setStyleSheet(
            f"""
            QPushButton {{
                color: #FFFFFF;
                background: #107C10;
                border: none;
                border-radius: 40px;
            }}
            QPushButton:pressed {{
                background: rgba(16, 124, 16, 170);
            }}
            """
        )
        call_btn.clicked.connect(self._make_call)
        ctrl.addWidget(call_btn)

        clear_btn = QPushButton("C")
        clear_btn.setFixedSize(64, 64)
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        clear_btn.setStyleSheet(
            f"QPushButton {{ color: #E81123; background: transparent; border: none; border-radius: 32px; }}"
            f"QPushButton:pressed {{ background: {self.theme.muted}; }}"
        )
        clear_btn.clicked.connect(self._clear_number)
        ctrl.addWidget(clear_btn)

        self.content_layout.addLayout(ctrl)

        # Recent calls
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {self.theme.muted}; max-height: 1px;")
        self.content_layout.addWidget(sep)

        self.add_card("Recent Calls", "")
        self.add_card("Mom", "08:42 — Missed")
        self.add_card("Ishant", "07:15 — 3 min")
        self.add_card("Service", "Yesterday — 1 min")
        self.finish()

    def _add_digit(self, digit: str) -> None:
        if len(self.number) < 15:
            self.number += digit
            self._update_display()

    def _backspace(self) -> None:
        if self.number:
            self.number = self.number[:-1]
            self._update_display()

    def _clear_number(self) -> None:
        self.number = ""
        self._update_display()

    def _update_display(self) -> None:
        if self.number:
            # Format number with spaces
            display = self.number
            self.display.setText(display)
        else:
            self.display.setText("")

    def _make_call(self) -> None:
        if self.number:
            self.display.setText(f"Calling {self.number}...")
