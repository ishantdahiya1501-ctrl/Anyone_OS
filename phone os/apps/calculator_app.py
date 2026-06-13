"""Calculator app with working computation."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QGridLayout, QLabel, QPushButton, QWidget

from apps.base_app import AppTheme, PhoneAppScreen


class CalculatorApp(PhoneAppScreen):
    def __init__(self, theme: AppTheme, parent=None) -> None:
        super().__init__("Calculator", theme, "Visual calculator", parent)
        self.expression = ""
        self.result_shown = False

        # Display
        self.display = QLabel("0")
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.display.setMinimumHeight(90)
        self.display.setMaximumHeight(100)
        self.display.setFont(QFont("Segoe UI Light", 46))
        self.display.setStyleSheet(
            f"color: {theme.foreground.name()}; background: {theme.surface}; "
            f"border-radius: 8px; padding: 0 18px;"
        )
        self.content_layout.addWidget(self.display)

        # Button grid
        buttons = [
            ("C", 3, 0, 1, 1, "#E81123"),
            ("⌫", 3, 1, 1, 1, theme.surface),
            ("%", 3, 2, 1, 1, theme.surface),
            ("÷", 3, 3, 1, 1, theme.accent.name()),
            ("7", 0, 0, 1, 1, theme.surface),
            ("8", 0, 1, 1, 1, theme.surface),
            ("9", 0, 2, 1, 1, theme.surface),
            ("×", 0, 3, 1, 1, theme.accent.name()),
            ("4", 1, 0, 1, 1, theme.surface),
            ("5", 1, 1, 1, 1, theme.surface),
            ("6", 1, 2, 1, 1, theme.surface),
            ("−", 1, 3, 1, 1, theme.accent.name()),
            ("1", 2, 0, 1, 1, theme.surface),
            ("2", 2, 1, 1, 1, theme.surface),
            ("3", 2, 2, 1, 1, theme.surface),
            ("+", 2, 3, 1, 1, theme.accent.name()),
            ("±", 3, 0, 1, 1, theme.surface),
            ("0", 3, 1, 1, 1, theme.surface),
            (".", 3, 2, 1, 1, theme.surface),
            ("=", 3, 3, 1, 1, "#107C10"),
        ]

        pad = QWidget()
        grid = QGridLayout(pad)
        grid.setSpacing(8)

        for text, row, col, rspan, cspan, bg in buttons:
            btn = self._make_button(text, bg, theme)
            grid.addWidget(btn, row, col, rspan, cspan)

        self.content_layout.addWidget(pad)
        self.finish()

    def _make_button(self, text: str, bg: str, theme: AppTheme) -> QPushButton:
        btn = QPushButton(text)
        btn.setMinimumHeight(68)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        is_op = text in ("+", "−", "×", "÷", "=")
        fg = "#FFFFFF" if is_op or bg == "#E81123" or bg == "#107C10" else theme.foreground.name()
        btn.setStyleSheet(
            f"""
            QPushButton {{
                color: {fg};
                background: {bg};
                border: none;
                border-radius: 8px;
            }}
            QPushButton:pressed {{
                background: rgba({QColor(bg).red()}, {QColor(bg).green()}, {QColor(bg).blue()}, 170);
            }}
            """
        )
        btn.clicked.connect(lambda checked=False, t=text: self._on_button(t))
        return btn

    def _on_button(self, text: str) -> None:
        if text == "C":
            self.expression = ""
            self.result_shown = False
            self.display.setText("0")
            return

        if text == "⌫":
            if self.expression:
                self.expression = self.expression[:-1]
            self.display.setText(self.expression or "0")
            return

        if text == "±":
            if self.expression:
                try:
                    val = float(self.expression)
                    self.expression = str(-val).rstrip("0").rstrip(".")
                    self.display.setText(self.expression)
                except ValueError:
                    pass
            return

        if text == "%":
            if self.expression:
                try:
                    val = float(self.expression) / 100
                    self.expression = str(val).rstrip("0").rstrip(".")
                    self.display.setText(self.expression)
                except ValueError:
                    pass
            return

        if text == "=":
            self._calculate()
            return

        if self.result_shown and text not in ("+", "−", "×", "÷"):
            self.expression = ""
            self.result_shown = False

        symbol_map = {"÷": "/", "×": "*", "−": "-"}
        self.expression += symbol_map.get(text, text)
        self.display.setText(self.expression)

    def _calculate(self) -> None:
        if not self.expression:
            return
        try:
            expr = self.expression.replace("×", "*").replace("÷", "/").replace("−", "-")
            result = eval(expr, {"__builtins__": {}}, {})
            if isinstance(result, float) and result == int(result) and abs(result) < 1e15:
                result = int(result)
            self.display.setText(str(result))
            self.expression = str(result)
            self.result_shown = True
        except (ZeroDivisionError, ValueError, SyntaxError, TypeError):
            self.display.setText("Error")
            self.expression = ""
            self.result_shown = True

